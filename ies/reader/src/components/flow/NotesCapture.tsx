/**
 * NotesCapture Component
 *
 * Quick capture UI for thoughts, annotations, and insights during reading.
 * Part of the ADHD-friendly design philosophy: low friction capture.
 *
 * Key features:
 * - Single input field for immediate capture
 * - Notes associated with current entity context
 * - List of captured notes for the session
 */

import { useState } from 'react';
import { PenLine, Send, Trash2 } from 'lucide-react';
import { useFlowStore } from '../../store/flowStore';

interface CapturedNote {
  id: string;
  content: string;
  entityId?: string;
  entityName?: string;
  timestamp: string;
}

export function NotesCapture() {
  const { currentEntity, addJourneyStep } = useFlowStore();
  const [noteInput, setNoteInput] = useState('');
  const [capturedNotes, setCapturedNotes] = useState<CapturedNote[]>([]);

  const handleSubmitNote = () => {
    const trimmedNote = noteInput.trim();
    if (!trimmedNote) return;

    // Create the note
    const newNote: CapturedNote = {
      id: `note-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      content: trimmedNote,
      entityId: currentEntity?.id,
      entityName: currentEntity?.name,
      timestamp: new Date().toISOString(),
    };

    // Add to local notes list
    setCapturedNotes((prev) => [newNote, ...prev]);

    // Track in journey if we have an entity context
    if (currentEntity) {
      addJourneyStep(currentEntity.id, currentEntity.name, `[Note] ${trimmedNote}`);
    }

    // Clear input
    setNoteInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Submit on Cmd/Ctrl+Enter
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmitNote();
    }
  };

  const handleDeleteNote = (noteId: string) => {
    setCapturedNotes((prev) => prev.filter((n) => n.id !== noteId));
  };

  const formatTimestamp = (iso: string): string => {
    const date = new Date(iso);
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <section className="flow-section">
      <h4 className="flow-section-title">
        <PenLine size={14} />
        Capture Thoughts
      </h4>

      {/* Quick capture input */}
      <div className="notes-capture-input">
        <textarea
          className="notes-capture-textarea"
          placeholder={
            currentEntity
              ? `Note about "${currentEntity.name}"... (Cmd+Enter)`
              : 'Capture a thought... (Cmd+Enter)'
          }
          rows={2}
          value={noteInput}
          onChange={(e) => setNoteInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <div className="notes-capture-footer">
          {currentEntity && (
            <span className="notes-capture-context">
              Context: {currentEntity.name}
            </span>
          )}
          <button
            className="notes-capture-submit"
            onClick={handleSubmitNote}
            disabled={!noteInput.trim()}
          >
            <Send size={14} />
            Capture
          </button>
        </div>
      </div>

      {/* Captured notes list */}
      {capturedNotes.length > 0 && (
        <div className="notes-captured-list">
          <div className="notes-captured-header">
            <span className="notes-captured-count">
              {capturedNotes.length} {capturedNotes.length === 1 ? 'note' : 'notes'} this session
            </span>
          </div>
          <ul className="notes-captured-items">
            {capturedNotes.map((note) => (
              <li key={note.id} className="notes-captured-item">
                <div className="notes-captured-item-content">
                  <p className="notes-captured-text">{note.content}</p>
                  <div className="notes-captured-meta">
                    {note.entityName && (
                      <span className="notes-captured-entity">{note.entityName}</span>
                    )}
                    <span className="notes-captured-time">{formatTimestamp(note.timestamp)}</span>
                  </div>
                </div>
                <button
                  className="notes-captured-delete"
                  onClick={() => handleDeleteNote(note.id)}
                  title="Delete note"
                >
                  <Trash2 size={14} />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
