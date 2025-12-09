'use client';

import React, { useState } from 'react';
import { Sheet } from '../ui/Sheet';
import { useFlowStore } from '../../store/flowStore'; // Corrected path
import { LuSend, LuPenLine, LuLightbulb, LuHelpCircle } from 'lucide-react'; // From package.json
import clsx from 'clsx';
// Assuming useTranslation is available globally or imported from a common hook
// For now, I'll mock it or find its actual path later if needed.
// import { useTranslation } from '../../hooks/useTranslation'; // Assuming this path
import './notes-sheet.css'; // Import the new CSS

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

type NoteType = 'thought' | 'question' | 'insight';

export function NotesSheet({ isOpen, onClose }: Props) {
  // const _ = useTranslation(); // Temporarily disabled until path is confirmed
  const _ = (text: string) => text; // Mock translation function
  const { currentEntity, addJourneyMark } = useFlowStore();
  const [noteInput, setNoteInput] = useState('');
  const [noteType, setNoteType] = useState<NoteType>('thought');

  const handleSubmit = () => {
    if (!noteInput.trim()) return;

    // Add as a mark to the current journey
    // If no journey is active, this might need handling, but we assume flow is somewhat active
    if (currentEntity) {
      addJourneyMark({
        type: noteType === 'question' ? 'question' : 'annotation', // Simplified mapping
        entityId: currentEntity.id,
        content: `[${noteType.toUpperCase()}] ${noteInput}`,
        // Assuming currentBookId and selectedText are available from a broader context or props if needed
      });
    } else {
      // Fallback if no entity - maybe just log or add to a general note store?
      // For now, we'll log it as a limit of current implementation
      console.log('Note captured (no entity):', { type: noteType, content: noteInput });
      // TODO: Implement a way to capture notes without an entity, perhaps to a general "inbox"
    }

    setNoteInput('');
    onClose();
  };

  return (
    <Sheet isOpen={isOpen} onClose={onClose} title={_('Capture Note')}>
      <div className="flex flex-col gap-4">
        {/* Note type chips */}
        <div className="flex gap-2 mb-4">
          <button
            className={clsx(
              'btn btn-sm', // Custom CSS classes
              noteType === 'thought' ? 'notes-type-chips-active-thought' : 'btn-ghost'
            )}
            onClick={() => setNoteType('thought')}
          >
            <LuPenLine size={16} /> {_('Thought')}
          </button>
          <button
            className={clsx(
              'btn btn-sm',
              noteType === 'question' ? 'notes-type-chips-active-question' : 'btn-ghost'
            )}
            onClick={() => setNoteType('question')}
          >
            <LuHelpCircle size={16} /> {_('Question')}
          </button>
          <button
            className={clsx(
              'btn btn-sm',
              noteType === 'insight' ? 'notes-type-chips-active-insight' : 'btn-ghost'
            )}
            onClick={() => setNoteType('insight')}
          >
            <LuLightbulb size={16} /> {_('Insight')}
          </button>
        </div>

        {/* Large touch-friendly textarea */}
        <textarea
          className="input h-32 w-full text-base resize-none" // Custom CSS classes, resize-none from Tailwind for textarea
          placeholder={_('What are you thinking?')}
          value={noteInput}
          onChange={(e) => setNoteInput(e.target.value)}
          autoFocus={isOpen}
        />

        {/* Context indicator */}
        {currentEntity && (
          <div className="text-sm text-text-secondary mt-2">
            {_('Connected to')}: <span className="font-semibold">{currentEntity.name}</span>
          </div>
        )}

        {/* Submit bar */}
        <div className="flex justify-end gap-2 mt-4">
          <button onClick={onClose} className="btn btn-ghost">
            {_('Cancel')}
          </button>
          <button onClick={handleSubmit} className="btn btn-primary">
            <LuSend size={16} /> {_('Capture')}
          </button>
        </div>
      </div>
    </Sheet>
  );
}