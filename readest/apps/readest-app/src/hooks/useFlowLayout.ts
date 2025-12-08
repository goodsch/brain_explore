import { useState, useEffect, useCallback } from 'react';

export type FlowLayoutMode = 'panel' | 'standalone';

interface FlowLayoutState {
  mode: FlowLayoutMode;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  setMode: (mode: FlowLayoutMode) => void;
}

const MOBILE_BREAKPOINT = 640;
const DESKTOP_BREAKPOINT = 1024;
const STORAGE_KEY = 'ies-flow-layout-mode';

export function useFlowLayout(): FlowLayoutState {
  const [mode, setModeState] = useState<FlowLayoutMode>('panel');
  const [dimensions, setDimensions] = useState({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
  });

  const calculateLayout = useCallback(() => {
    const width = typeof window !== 'undefined' ? window.innerWidth : 1200;
    const isMobile = width < MOBILE_BREAKPOINT;
    const isDesktop = width >= DESKTOP_BREAKPOINT;
    const isTablet = !isMobile && !isDesktop;

    setDimensions({ isMobile, isTablet, isDesktop });

    // Auto-set mode based on screen size
    if (isMobile) {
      setModeState('standalone');
    } else if (isDesktop) {
      setModeState('panel');
    } else {
      // Tablet: respect user preference
      const stored = localStorage.getItem(STORAGE_KEY) as FlowLayoutMode | null;
      setModeState(stored || 'standalone');
    }
  }, []);

  useEffect(() => {
    calculateLayout();
    window.addEventListener('resize', calculateLayout);
    return () => window.removeEventListener('resize', calculateLayout);
  }, [calculateLayout]);

  const setMode = useCallback((newMode: FlowLayoutMode) => {
    setModeState(newMode);
    localStorage.setItem(STORAGE_KEY, newMode);
  }, []);

  return {
    mode,
    ...dimensions,
    setMode,
  };
}
