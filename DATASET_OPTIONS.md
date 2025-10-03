# Alternative Large Customer Support Datasets on HuggingFace

## Option 1: Try these larger datasets

### 1. **Customer Support on Twitter** (100k+ tweets)
```python
ds = load_dataset("tweet_eval", "customer_support")
```

### 2. **Amazon Customer Reviews** (millions of records)
```python
ds = load_dataset("amazon_us_reviews", "All_Beauty_v1_00")
```

### 3. **Reddit Customer Support** (large dataset)
```python
ds = load_dataset("reddit", "customer_support")
```

### 4. **Multi-Domain Customer Support**
```python
ds = load_dataset("kunishou/databricks-dolly-15k")  # 15k instructions
```

## Option 2: Use Current Dataset (Best for Demo)

**Current Setup**:
- ✅ 580 FAQs from local CSV
- ✅ 200 FAQs from HuggingFace
- ✅ 5,000 Support Tickets from local CSV
- **Total: 5,780 documents**

This is **excellent for a demo/portfolio project**!

## Option 3: Generate Synthetic Data

We can generate more FAQs using:
1. Data augmentation (paraphrasing existing FAQs)
2. LLM-generated variations
3. Add more categories to local CSV

## Recommendation

**For your internship portfolio**, the current 5,780 documents is actually **perfect** because:

1. ✅ **Large enough** to demonstrate scalability
2. ✅ **Fast enough** for demos (<30 seconds build time)
3. ✅ **Diverse sources** (local + HuggingFace + tickets)
4. ✅ **Real-world mix** (FAQs + actual support tickets)

### Current Stats:
```
FAQ Store:      780 documents
Ticket Store: 5,000 documents
Total:        5,780 documents
Build Time:    ~30 seconds
Query Time:    <1 second
```

## If You Still Want More Data

I can help you:
1. **Add another HuggingFace dataset** (e.g., `kunishou/databricks-dolly-15k`)
2. **Generate synthetic FAQs** using Gemini
3. **Scrape public support pages** (with permission)
4. **Augment existing data** with paraphrasing

**Which approach would you prefer?**
