/**
 * Hook to handle session resume from URL parameters
 *
 * Checks for ?ies-session={id} parameter on app load and restores
 * the exploration session from the backend.
 */

import { useEffect, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { useFlowModeStore } from '@/store/flowModeStore';

export function useSessionResume() {
  const searchParams = useSearchParams();
  const { loadSession, setFlowModeActive } = useFlowModeStore();
  const hasRestoredRef = useRef(false);

  useEffect(() => {
    // Only restore once per app load
    if (hasRestoredRef.current) return;

    const sessionId = searchParams?.get('ies-session');
    if (!sessionId) return;

    hasRestoredRef.current = true;

    // Load session and activate flow mode
    const restoreSession = async () => {
      try {
        await loadSession(sessionId);
        // Auto-open flow panel after restoration
        setFlowModeActive(true);
        console.log(`Session ${sessionId} restored successfully`);
      } catch (error) {
        console.error('Failed to restore session from URL:', error);
      }
    };

    restoreSession();
  }, [searchParams, loadSession, setFlowModeActive]);
}
