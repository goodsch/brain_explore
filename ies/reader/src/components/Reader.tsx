import { useState, useCallback, useRef, useEffect } from 'react';
import { ReactReader } from 'react-reader';
import type { Rendition } from 'epubjs';
import { ArrowLeft, Globe, Loader2, AlertCircle, RefreshCw, PenLine, Search, Highlighter } from 'lucide-react';
import { FlowPanel } from './flow/FlowPanel';
import { NotesSheet } from './flow/NotesSheet';
import { WhatsNewBadge } from './flow/WhatsNewBadge';
import { useFlowStore } from '../store/flowStore';
import { useEntityLookup } from '../hooks/useEntityLookup';
import { useEntityOverlay } from '../hooks/useEntityOverlay';
import { useEntityHighlighter } from '../hooks/useEntityHighlighter';
import { useSessionSync } from '../hooks/useSessionSync';
import { useReadingPosition } from '../hooks/useReadingPosition';
import { graphClient } from '../services/graphClient';
import { highlightApi, type HighlightCreate } from '../services/highlightApi';
import './Reader.css';

interface ReaderProps {
  url: string;
  title?: string;
  calibreId?: number;
  onClose?: () => void;
  theme?: 'light' | 'dark';
  toggleTheme?: () => void;
}

export function Reader({ url, title = 'Book', calibreId, onClose }: ReaderProps) {
  const [location, setLocation] = useState<string | number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [rendition, setRendition] = useState<Rendition | null>(null);
  const [showNotesSheet, setShowNotesSheet] = useState(false);
  const [initialNoteData, setInitialNoteData] = useState<{ text: string; cfiRange: string } | undefined>(undefined);
  const [isMobile, setIsMobile] = useState(false); // New state for mobile detection

  interface SelectionContext {
    text: string;
    position: { top: number; left: number };
    cfiRange: string;
  }
  const [selectionContext, setSelectionContext] = useState<SelectionContext | null>(null);
  const renditionRef = useRef<Rendition | null>(null);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768); // Assuming 768px as mobile breakpoint
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Debug: Log URL and verify it's accessible
  useEffect(() => {
    console.log('[Reader] Mounting with URL:', url);
    console.log('[Reader] Title:', title, 'CalibreId:', calibreId);

    // Verify the URL is accessible before epub.js tries to load it
    fetch(url, { method: 'HEAD' })
      .then(response => {
        console.log('[Reader] URL check:', response.status, response.headers.get('content-type'));
        if (!response.ok) {
          setLoadError(`Server returned ${response.status}: ${response.statusText}`);
          setIsLoading(false);
        }
      })
      .catch(error => {
        console.error('[Reader] URL check failed:', error);
        setLoadError(`Failed to access book: ${error.message}`);
        setIsLoading(false);
      });
  }, [url, title, calibreId]);

  // Loading timeout - if book doesn't load in 15 seconds, show error
  useEffect(() => {
    if (!isLoading || loadError) return;

    console.log('[Reader] Starting 15s loading timeout...');
    const timeout = setTimeout(() => {
      if (isLoading) {
        console.error('[Reader] Loading timeout reached!');
        setLoadError('Book took too long to load. Please check your connection and try again.');
        setIsLoading(false);
      }
    }, 15000);

    return () => clearTimeout(timeout);
  }, [isLoading, loadError, url]);
  const {
    isFlowPanelOpen,
    setFlowPanelOpen,
    flowPanelWidth,
    startJourney,
    endJourney,
    userId,
    setSyncStatus,
    newItemsSummary,
    isLoadingNewItems,
    createSession,
    setReadingPosition,
    currentEntity,
  } = useFlowStore();
  const { lookupEntity } = useEntityLookup();

  // Fetch entities for overlay when book opens
  useEntityOverlay(calibreId);

  // Session sync: syncs context_id and question_id to backend
  useSessionSync({
    userId: userId || 'default_user',
    enabled: true,
  });

  // Reading position tracking: syncs CFI and progress to backend
  useReadingPosition({
    rendition,
    calibreId,
    userId: userId || 'default_user',
    enabled: true,
  });

  // Load existing highlights when book opens
  useEffect(() => {
    if (!calibreId || !rendition) return;

    const loadHighlights = async () => {
      try {
        const highlights = await highlightApi.listByBook(String(calibreId));
        console.log(`[Reader] Loaded ${highlights.length} existing highlights`);

        // Apply each highlight as an epub.js annotation
        highlights.forEach(hl => {
          const colorMap: Record<string, string> = {
            yellow: '#ffff00',
            green: '#90EE90',
            blue: '#87CEEB',
            pink: '#FFB6C1',
            purple: '#DDA0DD',
          };
          const fill = colorMap[hl.color] || '#ffff00';

          rendition.annotations.add(
            'highlight',
            hl.cfi,
            { highlightId: hl.id },
            (e: MouseEvent) => console.log('Highlight clicked:', hl.id, e),
            'hl',
            { 'fill': fill, 'fill-opacity': '0.3', 'pointer-events': 'none' }
          );
        });
      } catch (error) {
        console.error('[Reader] Failed to load highlights:', error);
      }
    };

    loadHighlights();
  }, [calibreId, rendition]);

  // Apply entity highlighting to epub content
  useEntityHighlighter(rendition);

  // Update session when current entity changes
  const updateSession = useFlowStore((state) => state.updateSession);
  const currentSessionId = useFlowStore((state) => state.currentSessionId);
  useEffect(() => {
    if (currentSessionId && currentEntity) {
      console.log('[Reader] Entity changed, updating session:', currentEntity.name);
      updateSession();
    }
  }, [currentEntity, currentSessionId, updateSession]);

  // Handle location changes
  const locationChanged = useCallback((epubcfi: string) => {
    setLocation(epubcfi);

    // Update reading position in session (for backward compatibility with old sync system)
    if (calibreId) {
      setReadingPosition({
        book_hash: String(calibreId), // Using calibreId as hash for now
        calibre_id: calibreId,
        cfi: epubcfi,
      });
    }
  }, [calibreId, setReadingPosition]);

interface IFrameContents {
  window: Window & {
    getSelection: () => Selection | null;
    frameElement: HTMLElement;
    scrollY: number;
    scrollX: number;
  };
}

  const getSelectionPosition = useCallback((contents: IFrameContents) => {
      const selection = contents.window.getSelection();
      if (!selection || selection.rangeCount === 0) {
          return { top: 0, left: 0 };
      }
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      // Adjust for iframe offset
      const iframeRect = contents.window.frameElement.getBoundingClientRect();
      return {
          top: iframeRect.top + rect.top + contents.window.scrollY,
          left: iframeRect.left + rect.left + contents.window.scrollX,
      };
  }, []);

  const captureAsNote = useCallback((selection: SelectionContext) => {
    setInitialNoteData({ text: selection.text, cfiRange: selection.cfiRange });
    setShowNotesSheet(true);
    setSelectionContext(null); // Clear selection context after action
  }, []);

  const highlightText = useCallback(async (selection: SelectionContext) => {
    if (!renditionRef.current) return;
    const { cfiRange, text } = selection;

    console.log('Highlighting text:', text, 'at cfi:', cfiRange);

    // Use epub.js annotations to add a highlight
    renditionRef.current.annotations.add(
      'highlight',
      cfiRange,
      {}, // Data object (can store metadata about the highlight)
      (e: MouseEvent) => console.log('Highlight clicked', e), // Click handler
      'hl', // Class name for styling the highlight
      { 'fill': '#ffff00', 'fill-opacity': '0.3', 'pointer-events': 'none' } // Styles to apply directly
    );
    setSelectionContext(null); // Clear selection context after action

    // Sync highlight to backend (if we have a calibreId)
    if (calibreId) {
      try {
        const highlightData: HighlightCreate = {
          book_id: String(calibreId),
          text,
          cfi: cfiRange,
          color: 'yellow',
        };
        const created = await highlightApi.create(highlightData);
        console.log('Highlight synced to backend:', created.id);
      } catch (error) {
        console.error('Failed to sync highlight to backend:', error);
        // Don't fail silently - highlight is still shown locally
      }
    }
  }, [calibreId]);

  // Get rendition ref for text selection handling
  const getRendition = useCallback(
    (rend: Rendition) => {
      console.log('[Reader] getRendition called - book loaded successfully!');
      renditionRef.current = rend;
      setRendition(rend);
      setIsLoading(false);

      // Apply reading styles
      rend.themes.default({
        body: {
          'font-family': "'Source Serif Pro', 'Georgia', serif",
          'line-height': '1.8',
          'color': '#2c2c2c',
        },
        p: {
          'margin-bottom': '1.2em',
        },
        'a': {
          'color': '#d4a574',
        },
      });

      // Add text selection handler
      rend.on('selected', (_cfiRange: string, contents: IFrameContents) => {
        const selection = contents.window.getSelection();
        const selectedText = selection?.toString().trim();

        if (selectedText && selectedText.length > 2) {
          // Show quick action bar above selection
          setSelectionContext({
            text: selectedText,
            position: getSelectionPosition(contents),
            cfiRange: _cfiRange,
          });
          // Also perform lookup if the flow panel is open, or some other condition
          // For now, let's keep lookupEntity call here, it's fine.
          lookupEntity(selectedText);
        } else {
            setSelectionContext(null); // Hide bar if selection is too short or cleared
        }
      });

      // Start journey when book opens
      startJourney(title, calibreId);

      // Create exploration session
      createSession().then(session => {
        if (session) {
          console.log('[Reader] Session created:', session.id);
        }
      });
    },
    [lookupEntity, startJourney, title, calibreId, getSelectionPosition, createSession]
  );

  // Toggle Flow panel
  const toggleFlowPanel = useCallback(async () => {
    if (isFlowPanelOpen) {
      // Save journey when closing
      const journey = endJourney();
      if (journey && journey.path.length > 0 && userId) {
        setSyncStatus('pending');
        try {
          await graphClient.saveJourney(journey, userId);
          setSyncStatus('synced');
          console.log('Journey saved to backend');
        } catch (error) {
          console.error('Failed to save journey:', error);
          setSyncStatus('error', error instanceof Error ? error.message : 'Unknown error');
        }
      }
    } else {
      startJourney(title, calibreId);
    }
    setFlowPanelOpen(!isFlowPanelOpen);
  }, [isFlowPanelOpen, setFlowPanelOpen, startJourney, endJourney, title, calibreId, userId, setSyncStatus]);

  return (
    <div className="reader-container">
      {/* Toolbar */}
      <header className="reader-toolbar">
        <div className="reader-toolbar-left">
          {onClose && (
            <button className="reader-back-btn ies-btn ies-btn-ghost" onClick={onClose} title="Back to library">
              <ArrowLeft size={20} />
            </button>
          )}
          <h1 className="reader-title">{title}</h1>
        </div>

        <div className="reader-toolbar-right">
          <button
            className={`reader-flow-toggle ${isFlowPanelOpen ? 'active' : ''}`}
            onClick={toggleFlowPanel}
            title="Toggle Flow Mode"
          >
            <Globe size={18} />
            <span className="reader-flow-label">Flow</span>
            <WhatsNewBadge summary={newItemsSummary} isLoading={isLoadingNewItems} />
          </button>
        </div>
      </header>

      {/* Loading overlay */}
      {isLoading && !loadError && (
        <div className="reader-loading">
          <Loader2 size={32} className="reader-loading-spinner" />
          <span>Loading book...</span>
        </div>
      )}

      {/* Error state */}
      {loadError && (
        <div className="reader-error">
          <AlertCircle size={48} strokeWidth={1.5} />
          <h3>Failed to load book</h3>
          <p>{loadError}</p>
          <div className="reader-error-actions">
            <button
              className="ies-btn ies-btn-primary"
              onClick={() => {
                setLoadError(null);
                setIsLoading(true);
                // Force re-render by toggling location
                setLocation(0);
              }}
            >
              <RefreshCw size={16} />
              Try Again
            </button>
            {onClose && (
              <button className="ies-btn ies-btn-ghost" onClick={onClose}>
                Back to Library
              </button>
            )}
          </div>
        </div>
      )}

      {/* Reader area */}
      {!loadError && (
        <div
          className="reader-content"
          style={{
            marginRight: isFlowPanelOpen ? flowPanelWidth : 0,
          }}
        >
          <ReactReader
            url={url}
            location={location}
            locationChanged={locationChanged}
            getRendition={getRendition}
            epubInitOptions={{
              openAs: 'epub',  // Force epub parsing even if server MIME type is wrong
            }}
            epubOptions={{
              allowScriptedContent: true,
            }}
            loadingView={
              <div className="reader-loading">
                <Loader2 size={32} className="reader-loading-spinner" />
                <span>Loading book...</span>
              </div>
            }
          />
        </div>
      )}

      {/* Flow Panel */}
      <FlowPanel />

      {isMobile && ( // Show FAB only on mobile
        <button
          className="reader-fab-note"
          onClick={() => setShowNotesSheet(true)}
          aria-label="Quick capture"
        >
          <PenLine size={24} />
        </button>
      )}

      <NotesSheet
          isOpen={showNotesSheet}
          onClose={() => setShowNotesSheet(false)}
          initialNoteData={initialNoteData}
      />
      {selectionContext && (
        <div
          className="reader-selection-bar"
          style={{ top: selectionContext.position.top, left: selectionContext.position.left }}
        >
          <button
            className="ies-btn ies-btn-sm ies-btn-subtle"
            onClick={() => {
                lookupEntity(selectionContext.text);
                setSelectionContext(null); // Clear context after action
            }}
          >
            <Search size={18} /> Look up
          </button>
          <button
            className="ies-btn ies-btn-sm ies-btn-subtle"
            onClick={() => captureAsNote(selectionContext)}
          >
            <PenLine size={18} /> Note
          </button>
          <button
            className="ies-btn ies-btn-sm ies-btn-subtle"
            onClick={() => highlightText(selectionContext)}
          >
            <Highlighter size={18} /> Highlight
          </button>
        </div>
      )}
    </div>
  );
}
