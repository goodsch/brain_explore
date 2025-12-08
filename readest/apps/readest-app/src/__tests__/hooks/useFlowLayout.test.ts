import { describe, it, expect, afterEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useFlowLayout } from '../../hooks/useFlowLayout';

describe('useFlowLayout', () => {
  const originalInnerWidth = window.innerWidth;

  afterEach(() => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    });
  });

  it('returns standalone mode for mobile width (<640px)', () => {
    Object.defineProperty(window, 'innerWidth', { value: 500, writable: true });
    const { result } = renderHook(() => useFlowLayout());
    expect(result.current.mode).toBe('standalone');
    expect(result.current.isMobile).toBe(true);
  });

  it('returns panel mode for desktop width (>1024px)', () => {
    Object.defineProperty(window, 'innerWidth', { value: 1200, writable: true });
    const { result } = renderHook(() => useFlowLayout());
    expect(result.current.mode).toBe('panel');
    expect(result.current.isMobile).toBe(false);
  });

  it('returns tablet mode for medium width (640-1024px)', () => {
    Object.defineProperty(window, 'innerWidth', { value: 800, writable: true });
    const { result } = renderHook(() => useFlowLayout());
    expect(result.current.isTablet).toBe(true);
  });
});
