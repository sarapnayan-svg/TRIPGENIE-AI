"""
TripGenie AI — RAG Pipeline Demonstration & Viva Test.

Demonstrates all 8 stages of the Retrieval-Augmented Generation system:
1. User Query
2. Query Processing
3. Embedding Generation
4. Vector Similarity Search
5. Context / Metadata Filtering
6. Top-K Retrieval & Source Tracking
7. Prompt Construction
8. Final Grounded LLM Response
"""

import sys
import os
import json

# Ensure app package is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

sys.stdout.reconfigure(encoding="utf-8")

from app.rag import QueryProcessor, EmbeddingManager, VectorStore, ContextFilter, ContextFormatter, rag_engine
from app.llm import generate_itinerary


def run_rag_demonstration():
    print("=" * 80)
    print("🎓 TRIPGENIE AI — RETRIEVAL-AUGMENTED GENERATION (RAG) PIPELINE TEST")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. USER QUERY
    # -------------------------------------------------------------------------
    user_query = "Looking for a 4-day vacation in Kerala for 2 people with backwaters, tea plantations, and authentic seafood. Budget is Rs 60,000."
    destination = "Kerala"
    days = 4
    travelers = 2
    budget = 60000
    interests = ["nature", "food", "relaxation"]
    travel_style = "balanced"

    print("\n" + "─" * 80)
    print("STAGE 1: USER QUERY & INTENT")
    print("─" * 80)
    print(f"  User Query:      \"{user_query}\"")
    print(f"  Destination:     {destination}")
    print(f"  Duration:        {days} Days")
    print(f"  Travelers:       {travelers} People")
    print(f"  Budget:          ₹{budget:,}")
    print(f"  Interests:       {', '.join(interests)}")
    print(f"  Travel Style:    {travel_style}")

    # -------------------------------------------------------------------------
    # 2. QUERY PROCESSING
    # -------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("STAGE 2: QUERY PROCESSING")
    print("─" * 80)
    processed = QueryProcessor.process(user_query, destination=destination)
    print(f"  • Cleaned Query:        \"{processed['cleaned_query']}\"")
    print(f"  • Target Destination:   {processed['target_destination']}")
    print(f"  • Inferred Categories:  {processed['suggested_categories']}")

    # -------------------------------------------------------------------------
    # 3. EMBEDDING GENERATION
    # -------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("STAGE 3: EMBEDDING GENERATION")
    print("─" * 80)
    query_vector = rag_engine.embedding_mgr.encode_query(processed["cleaned_query"])
    norm = float(query_vector @ query_vector)
    print(f"  • Embedding Model:      {rag_engine.embedding_mgr.model_name}")
    print(f"  • Vector Dimension:     {query_vector.shape[0]} dimensions")
    print(f"  • Vector L2 Norm:       {norm:.4f} (Normalized Unit Vector)")
    print(f"  • First 5 Dimensions:   {list(query_vector[:5].round(4))}")

    # -------------------------------------------------------------------------
    # 4 & 5. VECTOR SIMILARITY SEARCH & METADATA FILTERING
    # -------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("STAGE 4 & 5: VECTOR SIMILARITY SEARCH & METADATA FILTERING")
    print("─" * 80)
    raw_scores = rag_engine.vector_store.search(query_vector)
    print(f"  • Total Documents in Vector Store: {len(rag_engine.documents)} chunks")
    print(f"  • Similarity Metric:               Normalized Cosine Dot-Product")
    print(f"  • Destination Boost Applied:       +0.15 for '{destination}'")

    retrieved_chunks = ContextFilter.filter_and_rank(
        scores=raw_scores,
        documents=rag_engine.documents,
        destination=destination,
        categories=processed["suggested_categories"],
        top_k=6,
    )

    # -------------------------------------------------------------------------
    # 6. RETRIEVED RELEVANT DOCUMENTS (TOP-K)
    # -------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print(f"STAGE 6: RETRIEVED RELEVANT TRAVEL DOCUMENTS (Top-{len(retrieved_chunks)})")
    print("─" * 80)
    for rank, doc in enumerate(retrieved_chunks, 1):
        print(f"\n  [Rank {rank}] Chunk ID: {doc['id']} (Score: {doc['score']:.3f} | Cosine: {doc['raw_cosine_score']:.3f})")
        print(f"    • Place Name:       {doc.get('place_name')}")
        print(f"    • Category:         {doc.get('category').upper()}")
        print(f"    • Location:         {doc.get('location')}")
        print(f"    • Activities:       {', '.join(doc.get('activities', []))}")
        print(f"    • Estimated Cost:   {doc.get('estimated_cost')}")
        print(f"    • Best Time:        {doc.get('best_time')}")
        print(f"    • Duration:         {doc.get('duration')}")
        print(f"    • Travel Tips:      {doc.get('travel_tips')}")
        print(f"    • Description:      {doc.get('description')}")

    # -------------------------------------------------------------------------
    # 7. PROMPT CONSTRUCTION
    # -------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("STAGE 7: PROMPT CONSTRUCTION (Grounding Block)")
    print("─" * 80)
    formatted_context = ContextFormatter.format(retrieved_chunks[:3])
    print("  Injecting Retrieved Knowledge Chunks into System Prompt:\n")
    for line in formatted_context.split("\n"):
        print(f"    | {line}")

    # -------------------------------------------------------------------------
    # 8. FINAL LLM RESPONSE (STRUCTURED TRAVEL PLAN)
    # -------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("STAGE 8: FINAL STRUCTURED TRAVEL PLAN (Grounded Generation)")
    print("─" * 80)

    final_plan = generate_itinerary(
        destination=destination,
        days=days,
        travelers=travelers,
        budget=budget,
        interests=interests,
        context_chunks=retrieved_chunks,
        travel_style=travel_style,
    )

    print(f"\n  Trip Summary:")
    print(f"  {final_plan.get('summary')}\n")

    print("  Day-by-Day Grounded Schedule:")
    for day in final_plan.get("days", []):
        print(f"\n    📅 {day['title']} (Est. Cost: ₹{day.get('estimated_cost', 0):,.0f})")
        print(f"       Description: {day['description']}")
        print(f"       📍 Places:    {day.get('places')}")
        print(f"       ⚡ Activities: {day.get('activities')}")
        print(f"       🍽️ Food:       {day.get('food_recommendations')}")

    print("\n  Allocated Budget Breakdown:")
    for cat, amt in final_plan.get("budget_breakdown", {}).items():
        print(f"    • {cat.capitalize():12}: ₹{amt:,.0f}")

    print("\n  Verified Travel Tips:")
    for tip in final_plan.get("travel_tips", []):
        print(f"    💡 {tip}")

    print("\n  Packing Recommendations:")
    for tip in final_plan.get("packing_tips", []):
        print(f"    🎒 {tip}")

    print(f"\n  Provenance / Generated By: {final_plan.get('generated_by')}")
    print(f"  Retrieved Sources Tracked: {len(retrieved_chunks)} Knowledge Chunks")

    print("\n" + "=" * 80)
    print("✅ RAG PIPELINE DEMONSTRATION EXECUTED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    run_rag_demonstration()
