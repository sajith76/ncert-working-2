# Subject-Wise Database with Namespaces - REVISED ARCHITECTURE

## 🎯 Problem: Pinecone Free Tier Limitation

**Issue:** Pinecone free tier allows only 5 serverless indexes
- We have: 3 existing (ncert-learning-rag, ncert-web-content, intel-working)
- We need: 7 subject-specific indexes
- **Can't create more indexes!**

## 💡 Solution: Use Namespaces Within One Index

Pinecone recommends using **namespaces** to partition data within a single index. This is actually BETTER!

### **Revised Architecture**

```
One Pinecone Index: ncert-all-subjects
├── Namespace: mathematics
│   ├── Class 5 content
│   ├── Class 6 content
│   ├── ...
│   └── Class 12 content
├── Namespace: physics
│   ├── Class 9 content
│   ├── Class 10 content
│   ├── Class 11 content
│   └── Class 12 content
├── Namespace: chemistry
├── Namespace: biology
├── Namespace: social-science
├── Namespace: english
└── Namespace: hindi
```

### **Benefits of Namespace Approach**

| Feature | Multiple Indexes | Single Index + Namespaces |
|---------|-----------------|---------------------------|
| **Cost** | ❌ Hits free tier limit | ✅ Within free tier |
| **Speed** | Slower (multiple connections) | ✅ Faster (single connection) |
| **Management** | Complex (7 indexes) | ✅ Simple (1 index) |
| **Queries** | Must query each separately | ✅ Can query namespace directly |
| **Scalability** | ❌ Limited by index count | ✅ Unlimited namespaces |
| **Cross-subject search** | Difficult | ✅ Easy |

## 🏗️ Implementation Plan (Revised)

### **Option 1: Use Existing Index with Namespaces**

**Pros:**
- No need to create new index
- Start populating immediately
- Keeps existing data

**Cons:**
- Name "ncert-learning-rag" not descriptive for multi-subject use

### **Option 2: Create One New Index with Namespaces**

**Pros:**
- Clean start with proper naming: "ncert-all-subjects"
- Better organization

**Cons:**
- Must delete one existing index first
- Need to migrate old data

## 🚀 **Recommended: Option 2 (Clean Architecture)**

### Step 1: Clean Up Old Indexes
```python
# Delete deprecated indexes:
- ncert-learning-rag (OLD chapter-based)
- intel-working (not needed)

# Keep:
- ncert-web-content (for DeepDive web scraping)
```

### Step 2: Create One Master Index
```python
Index: ncert-all-subjects
Dimension: 768
Metric: cosine
Namespaces: [mathematics, physics, chemistry, biology, social-science, english, hindi]
```

### Step 3: Enhanced Metadata Schema
```python
{
    # Namespace determines subject
    "class": "11",
    "chapter": "5",
    "chapter_name": "Laws of Motion",
    "topic": "Newton's Third Law",
    "difficulty": "intermediate",
    "prerequisite_classes": ["9", "10"],
    "tags": ["mechanics", "laws", "force"]
}
```

### Step 4: Query Pattern
```python
# Query specific subject
results = index.query(
    vector=embedding,
    namespace="physics",  # Subject as namespace
    filter={"class": {"$in": ["9", "10", "11"]}},
    top_k=10
)

# Cross-subject query (if needed)
all_results = []
for namespace in ["physics", "chemistry"]:
    results = index.query(
        vector=embedding,
        namespace=namespace,
        filter=filters,
        top_k=5
    )
    all_results.extend(results.matches)
```

## 📊 Comparison: Old vs New

### **Old Architecture (Chapter-Based)**
```
ncert-learning-rag
└── Vectors: 2193
    └── Metadata: {class: "6", subject: "Social Science", lesson_number: "07"}
    
Problem: Can't access other classes or subjects easily
```

### **New Architecture (Subject + Namespace)**
```
ncert-all-subjects
├── mathematics (namespace)
│   └── Class 5-12 content with metadata
├── physics (namespace)
│   └── Class 9-12 content with metadata
└── ... (other subjects)

Benefit: Query any class, any subject, progressive learning!
```

## 🎯 Next Actions

1. **Delete old indexes** to free up space
2. **Create `ncert-all-subjects` index**
3. **Migrate data** to namespaces
4. **Update backend code** to use namespaces
5. **Test cross-class queries**

## 💻 Code Changes Required

### mongo.py
```python
# OLD
self.index.query(vector=vector, filter={"class": "6", "lesson_number": "07"})

# NEW
self.index.query(
    vector=vector,
    namespace="social-science",  # Subject as namespace
    filter={"class": {"$in": ["5", "6", "7"]}}  # Multi-class query
)
```

### rag_service.py
```python
# Progressive learning query
def query_progressive(student_class, subject, query):
    # Determine classes to search
    classes = get_prerequisite_classes(student_class)
    
    # Query subject namespace with multi-class filter
    results = subject_db.query(
        namespace=subject.lower().replace(" ", "-"),
        vector=embedding,
        filter={"class": {"$in": classes}},
        top_k=15
    )
```

## 🌟 Advantages Summary

1. **✅ Stays within free tier** - Only need 2 indexes total (all-subjects + web-content)
2. **✅ Better performance** - Single connection, faster queries
3. **✅ Easier management** - One index to monitor
4. **✅ Unlimited subjects** - Can add more namespaces anytime
5. **✅ Progressive learning** - Easy multi-class queries
6. **✅ Clean architecture** - Proper organization

This is the **production-ready** solution! 🚀
