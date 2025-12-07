import { useState } from 'react';
import { Send, Lightbulb, MessageCircle, HelpCircle } from 'lucide-react';
import { Sheet } from '../ui/Sheet';
import { useFlowStore } from '../../store/flowStore';
import { offlineQueue } from '../../services/offlineQueue';
import './NotesSheet.css';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  initialText?: string; // New prop
}

// Map UI note types to backend resonance signals (best effort)
const TYPE_MAPPING = {
  thought: { label: 'Thought', icon: MessageCircle, resonance: 'curious' }, // generic
  question: { label: 'Question', icon: HelpCircle, resonance: 'unclear' }, // explicitly asking
  insight: { label: 'Insight', icon: Lightbulb, resonance: 'connected' }, // connection made
} as const;

type NoteType = keyof typeof TYPE_MAPPING;

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      className={`notes-chip ${active ? 'active' : ''}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

export function NotesSheet({ isOpen, onClose, initialText }: Props) {
  const { currentEntity, userId } = useFlowStore();
  const [noteInput, setNoteInput] = useState(initialText || '');
  const [noteType, setNoteType] = useState<NoteType>('thought');

  useEffect(() => {
    if (initialText) {
      setNoteInput(initialText);
    } else {
      setNoteInput(''); // Clear if initialText becomes null/undefined
    }
  }, [initialText]);

  const handleSubmit = () => {
    if (!noteInput.trim()) return;
    
    // Create operation for offline queue
    offlineQueue.enqueue({
      userId: userId || 'anonymous',
      operationType: 'note',
      endpoint: '/personal/sparks',
      payload: {
        title: `${TYPE_MAPPING[noteType].label}: ${noteInput.slice(0, 30)}${noteInput.length > 30 ? '...' : ''}`,
        content: noteInput,
        resonance_signal: TYPE_MAPPING[noteType].resonance,
        energy_level: 'medium',
        source_id: currentEntity?.id,
      }
    });
    
    console.log('Note queued for offline sync');
    setNoteInput('');
    onClose();
  };

  return (
    <Sheet isOpen={isOpen} onClose={onClose} snapPoints={['60%']}>
        <div className="notes-sheet-content">
          <div className="notes-type-chips">
            {(Object.keys(TYPE_MAPPING) as NoteType[]).map((type) => {
              const Config = TYPE_MAPPING[type];
              const Icon = Config.icon;
              return (
                <Chip 
                  key={type} 
                  active={noteType === type} 
                  onClick={() => setNoteType(type)}
                >
                  <Icon size={14} />
                  {Config.label}
                </Chip>
              );
            })}
          </div>

          <textarea
            className="notes-sheet-input"
            placeholder="What are you thinking?"
            value={noteInput}
            onChange={(e) => setNoteInput(e.target.value)}
            rows={6}
            autoFocus
          />

          {currentEntity && (
            <div className="notes-context">
              Connected to: <strong>{currentEntity.name}</strong>
            </div>
          )}

          <div className="notes-sheet-footer">
            <button onClick={onClose} className="ies-btn ies-btn-ghost">
              Cancel
            </button>
            <button 
              onClick={handleSubmit} 
              className="ies-btn ies-btn-primary"
              disabled={!noteInput.trim()}
            >
              <Send size={16} /> Capture
            </button>
          </div>
        </div>
    </Sheet>
  );
}
