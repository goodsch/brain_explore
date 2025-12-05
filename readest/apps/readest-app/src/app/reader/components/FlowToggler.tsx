import React from 'react';
import { LuSparkles } from 'react-icons/lu';

import { useEnv } from '@/context/EnvContext';
import { useReaderStore } from '@/store/readerStore';
import { useSidebarStore } from '@/store/sidebarStore';
import { useFlowModeStore } from '@/store/flowModeStore';
import { useTranslation } from '@/hooks/useTranslation';
import { useResponsiveSize } from '@/hooks/useResponsiveSize';
import { saveJourneyToStorage, getGraphClient } from '@/services/flow';
import Button from '@/components/Button';

interface FlowTogglerProps {
  bookKey: string;
}

const FlowToggler: React.FC<FlowTogglerProps> = ({ bookKey }) => {
  const _ = useTranslation();
  const { appService } = useEnv();
  const { setHoveredBookKey } = useReaderStore();
  const { sideBarBookKey, setSideBarBookKey } = useSidebarStore();
  const { isFlowModeActive, toggleFlowMode, startJourney, endJourney } = useFlowModeStore();
  const iconSize16 = useResponsiveSize(16);

  const handleToggleFlowMode = async () => {
    if (appService?.isMobile) {
      setHoveredBookKey('');
    }

    // Set sidebar book key to current book
    if (sideBarBookKey !== bookKey) {
      setSideBarBookKey(bookKey);
    }

    // Toggle flow mode
    if (isFlowModeActive) {
      // Ending flow mode - complete the journey
      const journey = endJourney();
      if (journey && journey.path.length > 0) {
        // Save journey to local storage first (offline-safe)
        saveJourneyToStorage(journey);
        console.log('Flow journey saved locally:', journey.id);

        // Attempt to save to backend (non-blocking)
        try {
          const client = getGraphClient();
          await client.saveJourney(journey);
          console.log('Flow journey synced to backend:', journey.id);
        } catch (error) {
          console.log('Backend sync deferred (offline mode):', error);
          // Journey is already saved locally, will sync when online
        }
      }
    } else {
      // Starting flow mode - begin a new journey
      startJourney('default-user', {
        type: 'book',
        reference: bookKey.split('-')[0] || bookKey,
      });
    }

    toggleFlowMode();
  };

  return (
    <Button
      icon={
        <LuSparkles
          size={iconSize16}
          className={isFlowModeActive ? 'text-primary' : 'text-base-content'}
        />
      }
      onClick={handleToggleFlowMode}
      label={_('Flow Mode')}
    />
  );
};

export default FlowToggler;
