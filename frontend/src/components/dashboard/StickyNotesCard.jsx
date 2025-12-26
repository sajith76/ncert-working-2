import { useState } from "react";
import { StickyNote, Plus, X, Edit2, Check } from "lucide-react";

/**
 * StickyNotesCard Component
 * 
 * Personal sticky notes for quick reminders.
 * 
 * TODO: Backend Integration
 * - CRUD operations for sticky notes API
 * - Sync notes across devices
 * - Add color customization
 */

export default function StickyNotesCard() {
  // Dummy data - TODO: Replace with API data
  const [notes, setNotes] = useState([
    { id: 1, text: "Review Chapter 5 before test", color: "#ffc801" },
    { id: 2, text: "Submit homework by Friday", color: "#f928a9" },
    { id: 3, text: "Practice algebra problems", color: "#00d9ff" },
  ]);
  const [newNote, setNewNote] = useState("");
  const [isAdding, setIsAdding] = useState(false);

  const colors = ["#ffc801", "#f928a9", "#00d9ff", "#b4ff06", "#ef4444"];

  const handleAddNote = () => {
    if (!newNote.trim()) return;
    
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    
    // TODO: Replace with API call
    // await api.post('/notes/sticky', { text: newNote, color: randomColor });
    
    setNotes([
      ...notes,
      { id: Date.now(), text: newNote, color: randomColor }
    ]);
    setNewNote("");
    setIsAdding(false);
  };

  const handleDeleteNote = (id) => {
    // TODO: Replace with API call
    // await api.delete(`/notes/sticky/${id}`);
    
    setNotes(notes.filter(note => note.id !== id));
  };

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <StickyNote className="w-5 h-5 text-yellow-500" />
          <h3 className="text-lg font-semibold text-gray-800">Sticky Notes</h3>
        </div>
        <button
          onClick={() => setIsAdding(!isAdding)}
          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        >
          {isAdding ? (
            <X className="w-5 h-5 text-gray-500" />
          ) : (
            <Plus className="w-5 h-5 text-gray-500" />
          )}
        </button>
      </div>

      {/* Add Note Form */}
      {isAdding && (
        <div className="mb-4 flex gap-2">
          <input
            type="text"
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Write a note..."
            className="flex-1 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-yellow-200"
            onKeyDown={(e) => e.key === 'Enter' && handleAddNote()}
            autoFocus
          />
          <button
            onClick={handleAddNote}
            className="px-3 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
          >
            <Check className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Notes Grid */}
      <div className="grid grid-cols-1 gap-2">
        {notes.length === 0 ? (
          <p className="text-center text-gray-400 py-4">
            No sticky notes yet. Add one!
          </p>
        ) : (
          notes.map((note) => (
            <div
              key={note.id}
              className="relative p-3 rounded-xl text-sm font-medium text-gray-800 group"
              style={{ backgroundColor: `${note.color}30` }}
            >
              <div 
                className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
                style={{ backgroundColor: note.color }}
              />
              <span className="pl-2">{note.text}</span>
              <button
                onClick={() => handleDeleteNote(note.id)}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-white/50 transition-all"
              >
                <X className="w-3 h-3 text-gray-500" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
