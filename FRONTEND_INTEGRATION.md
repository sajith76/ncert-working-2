# Frontend-Backend Integration Summary

## Changes Made (December 26, 2025)

### 1. Folder Renamed
- `client/` → `frontend/` (to match the frontend-u1 branch naming)

### 2. Lessons Configuration Updated
**File:** `frontend/src/constants/lessons.js`

- Added **Mathematics chapters** (Class 6) with real PDF paths (`/fegp1XX.pdf`)
- Kept **Social Science chapters** (Class 6) with PDF paths (`/fees1XX.pdf`)
- Added `getLessonsBySubject(subject)` function to dynamically load lessons
- Added `SUBJECTS_WITH_RAG` array to track which subjects have AI support
- Mathematics is now the default (has backend RAG support)

**Available Subjects:**
| Subject | PDFs | AI Support |
|---------|------|------------|
| Mathematics | ✅ `/fegp101-110.pdf` | ✅ Full RAG |
| Social Science | ✅ `/fees101-114.pdf` | ❌ Read only |

### 3. BookToBot Page Updated
**File:** `frontend/src/pages/BookToBot.jsx`

- Now dynamically loads lessons based on `user.preferredSubject`
- Added warning banner when using subjects without AI support
- Lessons update automatically when user changes subject in settings

### 4. AI Components Updated

#### AIPanel.jsx (`frontend/src/features/annotations/AIPanel.jsx`)
- Uses `currentLesson.subject` for API calls (not hardcoded)
- Falls back to `user.preferredSubject` if lesson doesn't have subject
- Added debug logging for API calls

#### StudentChatbot.jsx (`frontend/src/features/annotations/StudentChatbot.jsx`)
- Uses lesson's subject for API calls
- Uses ReactMarkdown for proper formatting
- Added debug logging

#### ChatbotPanel.jsx (`frontend/src/components/dashboard/ChatbotPanel.jsx`)
- Added ReactMarkdown import
- Fixed renderMessageContent to use ReactMarkdown with Tailwind prose
- Uses Mathematics as default subject (has RAG support)
- Added debug logging

### 5. User Store Updated
**File:** `frontend/src/stores/userStore.js`

- Default `classLevel`: 6 (matches Math PDFs)
- Default `preferredSubject`: "Mathematics" (has RAG support)
- Logout resets to Mathematics

---

## Current Data Flow

```
User Settings (userStore)
    ↓
    classLevel: 6
    preferredSubject: "Mathematics"
    ↓
BookToBot Page
    ↓
    getLessonsBySubject("Mathematics")
    ↓
    MATH_LESSONS (10 chapters)
    ↓
    currentLesson = { number: 1, subject: "Mathematics", pdfUrl: "/fegp101.pdf" }
    ↓
PDFViewer / AIPanel / StudentChatbot
    ↓
    API Call: {
        class_level: 6,
        subject: "Mathematics",
        chapter: 1
    }
    ↓
Backend (Pinecone: mathematics namespace)
    ↓
    49,421 vectors searched
    ↓
    AI Response
```

---

## Database Status

### Pinecone Indexes
| Index | Namespace | Vectors | Purpose |
|-------|-----------|---------|---------|
| ncert-all-subjects | mathematics | 49,421 | Textbook content |
| ncert-llm | - | 40 | Cached AI answers |
| ncert-web-content | - | 0 | Web scraped content |

### MongoDB Atlas
- User data
- Notes
- Annotations history

---

## API Endpoints Used

### 1. Student Chat
```
POST /api/chat/student
{
    "question": "What is perimeter?",
    "class_level": 6,
    "subject": "Mathematics",
    "chapter": 1,
    "mode": "quick" | "deepdive"
}
```

### 2. Annotation Processing
```
POST /api/annotation/
{
    "selected_text": "perimeter",
    "action": "define" | "elaborate" | "stick_flow",
    "class_level": 6,
    "subject": "Mathematics",
    "chapter": 1
}
```

---

## How to Test

1. **Start Backend:**
   ```powershell
   cd d:\Projects\ncert-working-2
   .\start_backend.ps1
   ```

2. **Start Frontend:**
   ```powershell
   cd d:\Projects\ncert-working-2\frontend
   npm run dev
   ```

3. **Test Flow:**
   - Open http://localhost:5173/
   - Login as Student
   - Complete onboarding (or skip if already done)
   - Go to Dashboard → Book to Bot
   - You should see Mathematics chapters
   - Open a chapter PDF
   - Select text → Click Define/Elaborate
   - Open AI Chat → Ask a question

---

## Features Working

✅ **Dashboard**
- Shows user name, class level, subject
- Progress card (mock data for now)
- Streak card (mock data)
- Notes deck
- Sticky notes
- AI Chat button

✅ **Book to Bot**
- PDF viewer with Mathematics chapters
- Text selection → AI Assistant panel
- Define / Stick Flow / Elaborate actions
- Floating chatbot (Quick & DeepDive modes)
- Lesson navigation sidebar

✅ **AI Features**
- Text annotations (Define, Elaborate, Stick Flow)
- Chatbot (Quick & DeepDive modes)
- Cache optimization (duplicate questions use cached answers)
- ReactMarkdown for proper formatting

---

## Known Limitations

1. **Mathematics Only for AI**
   - Only Mathematics subject has RAG/AI support
   - Social Science PDFs available but AI won't work well

2. **Class 6 Content**
   - Current PDFs are for Class 6
   - Other class levels will query but may not find content

3. **Mock Data**
   - Progress, streaks, chat history are mock
   - Notes deck uses sample data

---

## Next Steps (Future)

1. Add more subjects to Pinecone (Science, Social Science)
2. Add more class levels
3. Implement real progress tracking
4. Add user authentication with backend
5. Store chat history in MongoDB
6. Implement note-taking with backend sync
