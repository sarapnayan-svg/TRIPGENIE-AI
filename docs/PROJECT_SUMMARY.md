# Final-Year Project Summary — TripGenie AI

## 1. Project Title
**TripGenie AI — Intelligent AI Travel Planner Using Large Language Models (LLM) and Retrieval-Augmented Generation (RAG)**

## 2. Academic & Industry Domain
- **Domain**: Applied Artificial Intelligence, Natural Language Processing (NLP), Information Retrieval (IR), and Full-Stack Software Engineering.
- **Specialization**: Grounded Generative AI, Retrieval-Augmented Generation, and Deterministic Financial Planning.

---

## 3. Problem Statement
Commercial trip planning tools and conversational LLMs suffer from three critical shortcomings:
1. **Hallucination & Fabrication**: General-purpose LLMs frequently recommend non-existent landmarks, permanently closed venues, or impossible daily transit routes.
2. **Financial Inaccuracy**: Traditional AI chatbots guess or approximate trip expenses without considering traveler counts, lodging room multipliers, seasonal rates, or vehicle fuel costs.
3. **Lack of Verifiable Grounding**: Travelers are presented with unstructured walls of text lacking source attribution, real-time meteorological observations, or verified GPS waypoints.

---

## 4. Project Objectives
1. **Eliminate Hallucinations**: Implement a modular RAG pipeline using dense semantic embeddings to ground generative models in verified travel document chunks.
2. **Deterministic Financial Modeling**: Build a multi-tier budget estimation engine dividing expenses across 5 discrete categories with dynamic deficit resolution.
3. **Multimodal Spatial & Weather Integration**: Provide live WMO meteorological readings and OpenStreetMap GPS waypoints with Haversine distance calculations.
4. **Offline Document Portability**: Enable zero-server client-side vector PDF generation allowing travelers to export formatted travel dossiers offline.
5. **Production Reliability**: Deliver a high-performance web application featuring persistent authentication, error normalization, and responsive design across all viewports.

---

## 5. Proposed Solution
TripGenie AI decouples generative synthesis from factual retrieval:
- **Retrieval Engine**: Converts user travel intent into 384-dimensional dense vectors using `sentence-transformers/all-MiniLM-L6-v2` and searches an indexed matrix via cosine dot-product.
- **Deterministic Budget Engine**: Calculates exact tariffs for accommodation, local transit, food, and activities with automatic cost-saving alternative suggestions.
- **Generative Synthesis**: Feeds retrieved factual chunks into Anthropic Claude (`claude-3-5-sonnet-20241022`) to generate day-by-day itineraries in validated JSON schemas.
- **Client Presentation**: A modern React 19 interface displaying daily visual timelines, Leaflet route waypoints, hotel recommendations with proximity scores, and client-side PDF export.

---

## 6. System Architecture & Modules

### Module 1: Client Layer (Frontend SPA)
- **Framework**: React 19 with Vite 5 and Tailwind CSS.
- **Key Components**:
  - `TripForm`: Validates destination, traveler count (1–20), duration (1–14 days), and budget (₹2,000+).
  - `Itinerary`: Day-by-day timeline with food recommendations, landmark highlights, and RAG grounding source drawer.
  - `BudgetChart`: 5-category financial visualization with deficit indicators and cost-saving tips.
  - `Hotels` & `HotelCard`: Verified accommodation catalog with proximity-to-attractions ranking.
  - `MapView`: Leaflet.js interactive maps with custom numbered day-route pins.
  - `WeatherCard`: Live atmospheric readings (temp, humidity, rain chance) from Open-Meteo API.
  - `ChatBot`: Context-aware conversational agent maintaining message history and citations.
  - `pdfExporter.js`: In-browser PDF generation engine utilizing `jsPDF` and `jspdf-autotable`.

### Module 2: Application Programming Interface (FastAPI Backend)
- **Framework**: FastAPI (Python 3.11) with Uvicorn ASGI server.
- **Authentication**: JWT tokens (HS256) with salted `bcrypt` password hashing.
- **Database Layer**: SQLAlchemy 2 ORM supporting PostgreSQL in production with automatic fallback to local SQLite (`tripgenie.db`).

### Module 3: Knowledge Base & RAG Engine (`app/rag.py`)
- **Knowledge Base**: Curated, verified destination facts (Goa, Jaipur, Kerala, Manali, Rishikesh).
- **Embeddings**: `all-MiniLM-L6-v2` generating normalized 384-dim dense vectors.
- **Search**: In-memory dot-product cosine similarity with destination and intent score boosting (+0.15).

### Module 4: Deterministic Budget Engine (`app/budget_planner.py`)
- Standardized formulas for rooms required ($\lceil\text{travelers}/2\rceil$), nights ($\text{days}-1$), transit tariffs, and a 7% miscellaneous cushion.
- Automated deficit detection and rule-based optimization suggestions.

---

## 7. Technology Stack Summary

| Layer | Technologies Used |
|---|---|
| **Frontend** | React 19, JavaScript (ESM), Vite 5, Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| **AI / NLP** | Anthropic Claude Messages API (`claude-3-5-sonnet-20241022`) |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions) |
| **Database** | SQLite (local dev) / PostgreSQL (production) via SQLAlchemy 2 |
| **Security** | Bcrypt password hashing, PyJWT authentication tokens, CORS middleware |
| **APIs** | Open-Meteo Global Weather API, CartoDB / OpenStreetMap |
| **Export** | `jsPDF` and `jspdf-autotable` (client-side PDF generation) |

---

## 8. Expected vs. Actual Outputs

| Feature | Expected Output | Actual Implemented Result | Status |
|---|---|---|---|
| **Itinerary Generation** | Structured daily plan without hallucinations | RAG-grounded day-by-day timeline with attraction details & cosine similarity citations | **Verified** |
| **Budget Planning** | Transparent financial breakdown | 5-category breakdown with exact per-person costs and deficit optimization rules | **Verified** |
| **Live Weather** | Real-time weather observation | Live temperature, humidity, wind, and 5-day rain chance from Open-Meteo API | **Verified** |
| **Hotel Recommendations** | Authentic accommodations | Catalog of verified properties with pricing and distance-to-itinerary pins | **Verified** |
| **Interactive Map** | Spatial visualization | Leaflet map displaying daily route sequence and GPS markers | **Verified** |
| **Document Export** | Downloadable itinerary document | Client-side vector PDF with Indian currency (`₹`), multi-page layout, and footers | **Verified** |
| **User Accounts** | User persistence | Secure signup/login with JWT and saved trips history in SQLite/PostgreSQL | **Verified** |

---

## 9. Limitations

1. **Indexed Catalog Scope**: The knowledge base is currently indexed for 5 major Indian tourist destinations. Unindexed destinations utilize general LLM knowledge.
2. **Vector Index In-Memory**: Embeddings are held in an in-memory NumPy matrix; scaling beyond 50,000 document chunks will require dedicated vector databases.
3. **Static Knowledge Ingestion**: Travel documents are updated through codebase ingestion rather than continuous live web crawling.

---

## 10. Future Scope & Enhancements

1. **Multi-City & International Expansion**: Ingest and index international travel hubs (e.g. Dubai, Singapore, Tokyo, London).
2. **Live Flight & Rail Booking APIs**: Direct integration with IRCTC, Amadeus, or Skyscanner APIs for real-time ticket pricing.
3. **Collaborative Group Trip Planning**: Real-time multi-user editing via WebSockets where multiple travelers can vote on activities.
4. **Vector Database Migration**: Transition to pgvector or Qdrant for horizontal scalability as the document base grows.
