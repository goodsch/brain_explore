import { useState, useCallback, useRef } from 'react';
import { ReactReader } from 'react-reader';
import type { Rendition } from 'epubjs';
import { FlowPanel } from './flow/FlowPanel';
import { useFlowStore } from '../store/flowStore';
import { useEntityLookup } from '../hooks/useEntityLookup';
import { graphClient } from '../services/graphClient';
import './Reader.css';

interface ReaderProps {
  url: string;
  title?: string;
  onClose?: () => void;
}

export function Reader({ url, title = 'Book', onClose }: ReaderProps) {
  const [location, setLocation] = useState<string | number>(0);
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
      startJourney(title);
    },
    [lookupEntity, startJourney, title]
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
      startJourney(title);
    }
    setFlowPanelOpen(!isFlowPanelOpen);
  }, [isFlowPanelOpen, setFlowPanelOpen, startJourney, endJourney, title, userId, setSyncStatus]);

  return (
    <div className="reader-container">
      {/* Toolbar */}
      <div className="reader-toolbar">
        {onClose && (
          <button className="back-button" onClick={onClose} title="Back to library">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
            </svg>
          </button>
        )}
        <h1 className="reader-title">{title}</h1>
        <button
          className={`flow-toggle ${isFlowPanelOpen ? 'active' : ''}`}
          onClick={toggleFlowPanel}
          title="Toggle Flow Mode"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
          </svg>
          <span>Flow</span>
        </button>
      </div>

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
