"""
Simple test script to verify your setup without needing the full API.
Run this to test core functionality.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("🧪 SupportRAG - Basic Functionality Test")
print("=" * 60)

# Test 1: Check environment
print("\n[1/5] Checking environment...")
try:
    from src.config import settings
    print(f"✅ Config loaded")
    print(f"   - Embedding model: {settings.embedding_model}")
    print(f"   - LLM provider: {settings.llm_provider}")
    print(f"   - Vector DB path: {settings.vector_db_path}")
    
    if settings.validate_api_keys():
        print(f"✅ API key configured")
    else:
        print(f"⚠️  API key not found in .env file")
        print(f"   Add GEMINI_API_KEY or OPENAI_API_KEY to .env")
except Exception as e:
    print(f"❌ Error loading config: {e}")
    sys.exit(1)

# Test 2: Test embeddings
print("\n[2/5] Testing embedding service...")
try:
    from src.core.embeddings import get_embedding_service
    
    embedding_service = get_embedding_service()
    test_text = "How do I reset my password?"
    embedding = embedding_service.embed_text(test_text)
    
    print(f"✅ Embeddings working")
    print(f"   - Model: {embedding_service.model_name}")
    print(f"   - Dimension: {embedding_service.get_embedding_dimension()}")
    print(f"   - Test embedding shape: {embedding.shape}")
except Exception as e:
    print(f"❌ Error with embeddings: {e}")
    sys.exit(1)

# Test 3: Test vector database
print("\n[3/5] Testing vector database...")
try:
    from src.core.vectordb import get_vector_db
    from src.models.schemas import FAQItem
    
    vector_db = get_vector_db()
    
    # Check if database has data
    total_faqs = vector_db.get_total_faqs()
    
    if total_faqs == 0:
        print(f"⚠️  Vector database is empty")
        print(f"   Run: python scripts\\init_vectordb.py")
    else:
        print(f"✅ Vector database loaded")
        print(f"   - Total FAQs: {total_faqs}")
        
        # Test search
        results = vector_db.search("password reset", top_k=3)
        print(f"   - Search test: Found {len(results)} results")
        
        if results:
            top_faq, top_score = results[0]
            print(f"   - Top result: '{top_faq.question}' (score: {top_score:.3f})")
            
except Exception as e:
    print(f"❌ Error with vector database: {e}")

# Test 4: Test LLM (only if API key is available)
print("\n[4/5] Testing LLM service...")
try:
    if not settings.validate_api_keys():
        print(f"⏭️  Skipping LLM test (no API key)")
    else:
        from src.core.llm import get_llm_service
        
        llm_service = get_llm_service()
        print(f"✅ LLM service initialized")
        print(f"   - Provider: {llm_service.provider}")
        
        # Optional: Test generation (costs API credits)
        test_generation = input("\n   Test LLM generation? (y/n): ").lower() == 'y'
        
        if test_generation:
            test_prompt = "What is 2+2?"
            response = llm_service.llm.generate(test_prompt)
            print(f"   - Test generation: {response[:50]}...")
            print(f"✅ LLM generation working")
        else:
            print(f"   - Skipped generation test")
            
except Exception as e:
    print(f"⚠️  LLM service issue: {e}")
    print(f"   This is OK if you haven't added an API key yet")

# Test 5: Test full RAG pipeline (if database has data)
print("\n[5/5] Testing RAG pipeline...")
try:
    if total_faqs == 0:
        print(f"⏭️  Skipping RAG test (database empty)")
    elif not settings.validate_api_keys():
        print(f"⏭️  Skipping RAG test (no API key)")
    else:
        from src.core.rag_pipeline import get_rag_pipeline
        from src.models.schemas import QueryRequest
        
        rag = get_rag_pipeline()
        print(f"✅ RAG pipeline initialized")
        
        # Test query
        test_query = input("\n   Ask a question (or press Enter to skip): ").strip()
        
        if test_query:
            request = QueryRequest(question=test_query, top_k=3)
            response = rag.query(request)
            
            print(f"\n   📝 Question: {test_query}")
            print(f"   💡 Answer: {response.answer}")
            print(f"   📊 Confidence: {response.confidence_score:.2%}")
            print(f"   🚨 Escalated: {response.escalated}")
            print(f"   ⏱️  Latency: {response.latency_ms:.0f}ms")
            print(f"   📚 Citations: {len(response.citations)}")
            
            if response.citations:
                print(f"\n   Sources:")
                for i, citation in enumerate(response.citations[:2], 1):
                    print(f"      {i}. {citation.question} ({citation.similarity_score:.2%})")
            
            print(f"\n✅ RAG pipeline working perfectly!")
        else:
            print(f"   - Skipped query test")
            
except Exception as e:
    print(f"❌ Error with RAG pipeline: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)

if total_faqs > 0 and settings.validate_api_keys():
    print("✅ All systems operational!")
    print("\n🚀 Ready to start:")
    print("   1. Terminal 1: uvicorn src.api.main:app --reload")
    print("   2. Terminal 2: streamlit run frontend\\app.py")
    print("   3. Open: http://localhost:8501")
elif total_faqs == 0:
    print("⚠️  Setup needed:")
    print("\n📝 Next step:")
    print("   python scripts\\init_vectordb.py")
elif not settings.validate_api_keys():
    print("⚠️  API key needed:")
    print("\n📝 Next steps:")
    print("   1. Get API key: https://makersuite.google.com/app/apikey")
    print("   2. Add to .env: GEMINI_API_KEY=your_key_here")
    print("   3. Rerun this test")
else:
    print("⚠️  Some components need attention")
    print("   Check the errors above")

print("=" * 60)
