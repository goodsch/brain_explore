import { renderHook } from '@testing-library/react';
import { useReducedMotion } from './useReducedMotion';

describe('useReducedMotion', () => {
  const originalMatchMedia = window.matchMedia;

  afterEach(() => {
    window.matchMedia = originalMatchMedia;
  });

  it('should return false when user has no motion preference', () => {
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));

    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(false);
  });

  it('should return true when user prefers reduced motion', () => {
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: true,
      media: query,
      onchange: null,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));

    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(true);
  });

  it('should update when preference changes', () => {
    let listener: ((event: MediaQueryListEvent) => void) | null = null;
    
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: jest.fn((event, callback) => {
        listener = callback;
      }),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));

    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(false);

    // Simulate preference change
    if (listener) {
      listener({ matches: true } as MediaQueryListEvent);
    }

    expect(result.current).toBe(true);
  });
});
