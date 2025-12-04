import clsx from 'clsx';
import React, { useCallback, useEffect } from 'react';

import { useReaderStore } from '@/store/readerStore';
import { useSidebarStore } from '@/store/sidebarStore';
import { useFlowModeStore } from '@/store/flowModeStore';
import { useTranslation } from '@/hooks/useTranslation';
import { useThemeStore } from '@/store/themeStore';
import { useEnv } from '@/context/EnvContext';
import { DragKey, useDrag } from '@/hooks/useDrag';
import { Overlay } from '@/components/Overlay';
import useShortcuts from '@/hooks/useShortcuts';

import FlowPanelHeader from './Header';
import EntitySection from './EntitySection';
import RelationshipsSection from './RelationshipsSection';
import SourcesSection from './SourcesSection';
import QuestionsSection from './QuestionsSection';
import ReframesSection from './ReframesSection';
import { EntityTypeFilter } from '../EntityTypeFilter';

const MIN_FLOW_PANEL_WIDTH = 0.2;
const MAX_FLOW_PANEL_WIDTH = 0.5;

const FlowPanel: React.FC = () => {
  const _ = useTranslation();
  const { updateAppTheme, safeAreaInsets } = useThemeStore();
  const { appService } = useEnv();
  const { sideBarBookKey } = useSidebarStore();
  const { getViewSettings } = useReaderStore();

  const {
    flowPanelWidth,
    isFlowModeActive,
    isFlowPanelPinned,
    currentEntity,
    relationships,
    bookSources,
    thinkingPartnerQuestions,
    isLoadingEntity,
    getFlowPanelWidth,
    setFlowPanelWidth,
    setFlowModeActive,
    toggleFlowPanelPin,
  } = useFlowModeStore();

  const handleHideFlowPanel = useCallback(() => {
    if (!isFlowPanelPinned) {
      setFlowModeActive(false);
    }
  }, [isFlowPanelPinned, setFlowModeActive]);

  useShortcuts({ onEscape: handleHideFlowPanel }, [handleHideFlowPanel]);

  useEffect(() => {
    if (isFlowModeActive) {
      updateAppTheme('base-200');
    } else {
      updateAppTheme('base-100');
    }
  }, [isFlowModeActive, updateAppTheme]);

  const handleFlowPanelResize = (newWidth: string) => {
    setFlowPanelWidth(newWidth);
  };

  const handleTogglePin = () => {
    toggleFlowPanelPin();
  };

  const handleClickOverlay = () => {
    setFlowModeActive(false);
  };

  const onDragMove = (data: { clientX: number }) => {
    const widthFraction = 1 - data.clientX / window.innerWidth;
    const newWidth = Math.max(MIN_FLOW_PANEL_WIDTH, Math.min(MAX_FLOW_PANEL_WIDTH, widthFraction));
    handleFlowPanelResize(`${Math.round(newWidth * 10000) / 100}%`);
  };

  const onDragKeyDown = (data: { key: DragKey; step: number }) => {
    const currentWidth = parseFloat(getFlowPanelWidth()) / 100;
    let newWidth = currentWidth;

    if (data.key === 'ArrowLeft') {
      newWidth = Math.max(MIN_FLOW_PANEL_WIDTH, currentWidth + data.step);
    } else if (data.key === 'ArrowRight') {
      newWidth = Math.min(MAX_FLOW_PANEL_WIDTH, currentWidth - data.step);
    }
    handleFlowPanelResize(`${Math.round(newWidth * 10000) / 100}%`);
  };

  const { handleDragStart, handleDragKeyDown } = useDrag(onDragMove, onDragKeyDown);

  if (!sideBarBookKey) return null;
  const viewSettings = getViewSettings(sideBarBookKey);

  return isFlowModeActive ? (
    <>
      {!isFlowPanelPinned && (
        <Overlay
          className={clsx('z-[45]', viewSettings?.isEink ? '' : 'bg-black/20')}
          onDismiss={handleClickOverlay}
        />
      )}
      <div
        className={clsx(
          'flow-panel-container right-0 flex min-w-72 select-none flex-col',
          'full-height font-sans text-base font-normal sm:text-sm',
          viewSettings?.isEink ? 'bg-base-100' : 'bg-base-200',
          appService?.hasRoundedWindow && 'rounded-window-top-right rounded-window-bottom-right',
          isFlowPanelPinned ? 'z-20' : 'z-[45] shadow-2xl',
          !isFlowPanelPinned && viewSettings?.isEink && 'border-base-content border-s',
        )}
        role='complementary'
        aria-label={_('Flow Mode Panel')}
        style={{
          width: flowPanelWidth,
          maxWidth: `${MAX_FLOW_PANEL_WIDTH * 100}%`,
          position: isFlowPanelPinned ? 'relative' : 'absolute',
          paddingTop: `${safeAreaInsets?.top || 0}px`,
        }}
      >
        <style jsx>{`
          @media (max-width: 640px) {
            .flow-panel-container {
              width: 100%;
              min-width: 100%;
            }
          }
        `}</style>
        <div
          className={clsx(
            'drag-bar absolute -left-2 top-0 h-full w-0.5 cursor-col-resize bg-transparent p-2',
          )}
          role='slider'
          tabIndex={0}
          aria-label={_('Resize Flow Panel')}
          aria-orientation='horizontal'
          aria-valuenow={parseFloat(flowPanelWidth)}
          onMouseDown={handleDragStart}
          onTouchStart={handleDragStart}
          onKeyDown={handleDragKeyDown}
        />

        <div className='flex-shrink-0'>
          <FlowPanelHeader
            isPinned={isFlowPanelPinned}
            handleClose={() => setFlowModeActive(false)}
            handleTogglePin={handleTogglePin}
          />
        </div>

        <div className='flex-grow overflow-y-auto px-4 py-2'>
          {/* Entity Overlay Filter - Always visible at top */}
          <div className='mb-4'>
            <EntityTypeFilter />
          </div>

          {isLoadingEntity ? (
            <div className='flex h-32 items-center justify-center'>
              <span className='loading loading-spinner loading-md'></span>
            </div>
          ) : currentEntity ? (
            <div className='space-y-4'>
              <EntitySection entity={currentEntity} />
              <RelationshipsSection relationships={relationships} />
              <SourcesSection sources={bookSources} />
              <QuestionsSection questions={thinkingPartnerQuestions} />
              {currentEntity?.id && <ReframesSection conceptId={currentEntity.id} />}
            </div>
          ) : (
            <div className='flex h-full flex-col items-center justify-center text-center'>
              <p className='text-base-content/60 mb-2 text-lg font-medium'>
                {_('Select text to explore')}
              </p>
              <p className='text-base-content/40 text-sm'>
                {_('Highlight a concept or term to see its connections in the knowledge graph')}
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  ) : null;
};

export default FlowPanel;
