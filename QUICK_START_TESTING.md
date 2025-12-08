# Quick Start Guide - Test Class 6 Math

## 🚀 Start the Frontend

```bash
cd client
npm run dev
```

The app will open at: `http://localhost:5173`

---

## 🧹 IMPORTANT: Clear Browser Cache First!

Since you were viewing Social Science before, you need to clear the stored settings:

### Method 1: Clear localStorage (Recommended)
1. Open browser DevTools: Press `F12`
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Find **Local Storage** in the left sidebar
4. Click on `http://localhost:5173`
5. Find the key `user-storage`
6. Right-click → **Delete**
7. **Refresh the page** (`F5`)

### Method 2: Quick Code (Run in Browser Console)
1. Press `F12` to open DevTools
2. Go to **Console** tab
3. Paste this and press Enter:
```javascript
localStorage.removeItem('user-storage');
location.reload();
```

---

## ✅ What You Should See

### 1. **Settings Panel** (Click gear icon ⚙️):
- **Class Level**: 6 should be selected
- **Preferred Subject**: **Mathematics** should be selected

### 2. **Lesson Sidebar** (Left side):
You should now see 10 Math chapters:
```
📘 1. Knowing Our Numbers
📘 2. Whole Numbers
📘 3. Playing with Numbers
📘 4. Integers
📘 5. Fractions
📘 6. Decimals
📘 7. Algebra
📘 8. Ratio and Proportion
📘 9. Understanding Elementary Shapes
📘 10. Mensuration
```

### 3. **PDF Viewer** (Center):
- Click on Chapter 1
- Should load the Math PDF (`fegp101.pdf`)
- Should show NCERT Class 6 Mathematics content

---

## 🧪 Test the System

### Test 1: Basic Highlighting
1. Click on **Chapter 3: Playing with Numbers**
2. Highlight any text (e.g., "factor")
3. Click **"Define"** or **"Elaborate"**
4. You should get an explanation from the Math textbook

### Test 2: Quick vs DeepDive
1. Highlight: "What is a fraction?"
2. Try **Quick mode** first → Should get focused answer from Class 6
3. Try **DeepDive mode** → Should get comprehensive answer from Classes 5-6

### Test 3: Student Chatbot
1. Click the **chat icon** (bottom right)
2. Ask: "What is the difference between factors and multiples?"
3. Try both modes:
   - **Quick**: Fast, focused answer
   - **DeepDive**: Comprehensive, builds from basics

### Test 4: Cross-Chapter Questions
1. Ask: "How are fractions and decimals related?"
2. System should pull content from both Chapter 5 (Fractions) and Chapter 6 (Decimals)

---

## 🎯 Expected Behavior

### Quick Mode:
- **Speed**: 1-3 seconds
- **Sources**: Class 6 Math only
- **Answer**: Direct, focused
- **Best for**: Homework help, quick clarification

### DeepDive Mode:
- **Speed**: 4-6 seconds
- **Sources**: Classes 5 & 6 Math + web content
- **Answer**: Comprehensive, structured with:
  - 🌱 **Fundamentals** (Class 5 basics if relevant)
  - 🎓 **Core Concept** (Class 6 content)
  - 🔍 **Deep Dive** (applications, examples)
  - 💡 **Key Takeaways**
- **Best for**: Complete understanding, exam prep

---

## 🐛 Troubleshooting

### Problem: Still showing Social Science
**Solution**: Clear localStorage (see steps above)

### Problem: PDFs not loading
**Solution**: 
1. Check console for errors (F12 → Console tab)
2. Verify PDFs are in `client/public/` folder
3. Try hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)

### Problem: AI not responding
**Solution**:
1. Make sure backend is running: `cd backend` → `python -m uvicorn app.main:app --reload`
2. Check backend URL in `client/src/services/api.js` (should be `http://localhost:8000`)
3. Check browser console for API errors

### Problem: "No answer found"
**Solution**: This is expected for some queries since:
- Your Pinecone has 49,421 Math vectors (Classes 5-12)
- Class 6 specific content is there
- If you get "No answer found", try:
  - Rephrasing the question
  - Highlighting different text from the textbook
  - Using keywords from the chapter

---

## 📊 Check Backend Connection

### Verify Pinecone Data:
1. Open your Pinecone dashboard
2. Go to **ncert-all-subjects** index
3. Check **mathematics** namespace
4. Should show: 49,421 vectors

### Test Backend API:
Open in browser: `http://localhost:8000/docs`

Try this endpoint:
```
POST /chat/student
{
  "question": "What is a factor?",
  "class_level": 6,
  "subject": "Mathematics",
  "chapter": 3,
  "mode": "quick"
}
```

---

## 🎉 Success Indicators

You'll know it's working when:

✅ Settings show "Mathematics" as selected subject
✅ Lesson sidebar shows 10 Math chapters
✅ PDFs load with Math content
✅ Highlighting gives Math-related explanations
✅ Student chatbot answers Math questions
✅ Backend logs show queries to "mathematics" namespace
✅ Answers reference "Class 6" content

---

## 📝 Sample Questions to Test

### Chapter 1 - Knowing Our Numbers:
- "What is place value?"
- "How to compare large numbers?"

### Chapter 3 - Playing with Numbers:
- "What is the difference between factors and multiples?"
- "What is a prime number?"

### Chapter 5 - Fractions:
- "How to add fractions?"
- "What is an equivalent fraction?"

### Chapter 7 - Algebra:
- "What is a variable?"
- "How to solve simple equations?"

### Chapter 10 - Mensuration:
- "What is the formula for area of a rectangle?"
- "What is perimeter?"

---

Start the frontend and try it out! 🚀
