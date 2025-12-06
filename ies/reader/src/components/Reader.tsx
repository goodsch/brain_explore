import { useState, useCallback, useRef } from 'react';
import { ReactReader } from 'react-reader';
import type { Rendition } from 'epubjs';
import { ArrowLeft, Globe, Loader2 } from 'lucide-react';
import { FlowPanel } from './flow/FlowPanel';
import { useFlowStore } from '../store/flowStore';
import { useEntityLookup } from '../hooks/useEntityLookup';
import { graphClient } from '../services/graphClient';
import './Reader.css';

interface ReaderProps {
  url: string;
  title?: string;
  calibreId?: number;
  onClose?: () => void;
}

export function Reader({ url, title = 'Book', calibreId, onClose }: ReaderProps) {
  const [location, setLocation] = useState<string | number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const renditionRef = useRef<Rendition | null>(null);
  const {
    isFlowPanelOpen,
    setFlowPanelOpen,
    flowPanelWidth,
    startJourney,
    endJourney,
    userId,
    setSyncStatus,
  } = useFlowStore();
  const { lookupEntity } = useEntityLookup();

  // Handle location changes
  const locationChanged = useCallback((epubcfi: string) => {
    setLocation(epubcfi);
  }, []);

  // Get rendition ref for text selection handling
  const getRendition = useCallback(
    (rendition: Rendition) => {
      renditionRef.current = rendition;
      setIsLoading(false);

      // Apply reading styles
      rendition.themes.default({
        body: {
          'font-family': "'Crimson Pro', 'Georgia', serif",
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
      rendition.on('selected', (_cfiRange: string, contents: any) => {
        const selection = contents.window.getSelection();
        const selectedText = selection?.toString().trim();

        if (selectedText && selectedText.length > 2) {
          // Look up entity in knowledge graph
          lookupEntity(selectedText);
        }
      });

      // Start journey when book opens
      startJourney(title, calibreId);
    },
    [lookupEntity, startJourney, title, calibreId]
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
          </button>
        </div>
      </header>

      {/* Loading overlay */}
      {isLoading && (
        <div className="reader-loading">
          <Loader2 size={32} className="reader-loading-spinner" />
          <span>Loading book...</span>
        </div>
      )}

      {/* Reader area */}
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
          epubOptions={{
            allowScriptedContent: true,
          }}
        />
      </div>

      {/* Flow Panel */}
      <FlowPanel />
    </div>
  );
}
