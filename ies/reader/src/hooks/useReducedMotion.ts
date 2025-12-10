import { useState, useEffect } from 'react';

/**
 * Hook to detect user's motion preference
 * Returns true if user prefers reduced motion
 *
 * @example
 * const prefersReducedMotion = useReducedMotion();
 *
 * // Use in animations
 * const duration = prefersReducedMotion ? 0 : 300;
 *
 * // Or conditionally apply animation classes
 * <div className={prefersReducedMotion ? '' : 'animate-fade-in'}>
 */
export function useReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(
    () => {
      // SSR-safe initial value
      if (typeof window === 'undefined') return false;

      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      return mediaQuery.matches;
    }
  );

  useEffect(() => {
    // Create media query
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    // Update state when preference changes
    const handleChange = (event: MediaQueryListEvent | MediaQueryList) => {
      setPrefersReducedMotion(event.matches);
    };

    // Set initial value
    handleChange(mediaQuery);

    // Listen for changes (modern browsers)
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
    // Fallback for older browsers
    else if (mediaQuery.addListener) {
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  return prefersReducedMotion;
}
