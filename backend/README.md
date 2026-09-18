# TripGenie AI — RAG + LLM Backend

Backend for the "Intelligent AI Travel Planner using LLMs and Retrieval-Augmented
Generation (RAG)" project. It generates day-by-day itineraries and answers
follow-up questions by grounding Claude's responses in a curated travel
knowledge base, instead of letting the model invent facts freely.

## Architecture

```
User request (destination, days, budget, interests)
        │
        ▼
 ┌─────────────────┐   1. embed the query with a sentence-transformer
 │   rag.py         │   2. cosine-similarity search over pre-embedded
 │  (Retriever)     │      knowledge base chunks
 └─────────────────┘   3. return top-k relevant chunks
        │
        ▼
 ┌─────────────────┐   4. inject retrieved chunks + trip details into
 │   llm.py         │      a prompt sent to Claude
 │  (Generator)     │   5. Claude returns a grounded, structured itinerary
 └─────────────────┘
        │
        ▼
 ┌─────────────────┐
 │   main.py         │  FastAPI endpoints wire it all together
 │  (API layer)      │
 └─────────────────┘
```

This is the standard **Retrieve → Augment → Generate** pipeline:
- **Retrieve**: `app/rag.py` embeds `app/knowledge_base.py` once at startup
  using `sentence-transformers/all-MiniLM-L6-v2`, stores the embeddings as an
  in-memory numpy matrix (a minimal vector store), and ranks documents by
  cosine similarity against the query.
- **Augment**: `app/llm.py` formats the retrieved chunks into a `CONTEXT`
  block and inserts it into the system/user prompt.
- **Generate**: Claude (via the Anthropic API) produces the itinerary or chat
  reply, instructed to stay grounded in the provided context.

## Setup

```bash
cd tripgenie-backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your key from https://console.anthropic.com/

uvicorn app.main:app --reload
```

The API will be live at `http://127.0.0.1:8000`. Interactive docs (Swagger UI)
are auto-generated at `http://127.0.0.1:8000/docs`.

## Endpoints

| Method | Path                | Purpose                                      |
|--------|---------------------|-----------------------------------------------|
| GET    | `/api/health`       | Health check + list of known destinations     |
| GET    | `/api/destinations` | Destinations covered by the knowledge base     |
| POST   | `/api/plan-trip`    | Generate a RAG-grounded itinerary              |
| POST   | `/api/chat`         | Ask follow-up questions about a planned trip   |

### Example: plan a trip

```bash
curl -X POST http://127.0.0.1:8000/api/plan-trip \
  -H "Content-Type: application/json" \
  -d '{
        "destination": "Goa",
        "days": 5,
        "travelers": 4,
        "budget": 100000,
        "interests": ["beach", "adventure", "food"]
      }'
```

### Example: follow-up chat

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
        "message": "What should I pack for the water sports day?",
        "trip": {"destination": "Goa", "days": 5}
      }'
```

## Knowledge base

`app/knowledge_base.py` currently covers Goa, Kerala, Manali, Jaipur, and
Rishikesh, with chunks tagged by category (overview, attractions, food, stay,
budget, best_time, tips). Add more destinations by appending dicts with the
same shape — no code changes needed elsewhere, since the index rebuilds from
this list at startup.

For the project report, this is a good place to describe how you'd scale the
knowledge base in a real deployment: scraping travel guides, pulling
structured data from a hotels/places API, and re-embedding on a schedule.

## Connecting the frontend

The `tripgenie.html` frontend can call this API instead of (or alongside) its
client-side logic — point its "Plan My Trip" handler at
`POST http://127.0.0.1:8000/api/plan-trip` and render the returned JSON.
Remember to run the backend with CORS enabled (already configured in
`main.py`) so the browser-based frontend can reach it.

## Notes for your report / viva

- **Why RAG instead of only prompting the LLM?** It keeps recommendations
  grounded in a controlled, verifiable data source instead of letting the
  model hallucinate hotel names or prices, and it lets you cite which
  document chunks supported each answer (`sources` field in every response).
- **Why sentence-transformers instead of an API-based embedding model?**
  Runs locally with no extra API cost or key, and is fast enough for a
  knowledge base of this size. For a larger corpus, swap in FAISS or a
  managed vector DB — the `retrieve()` interface in `rag.py` wouldn't need to
  change.
- **Model used**: Claude (`claude-sonnet-5` by default, configurable via the
  `LLM_MODEL` env var).
