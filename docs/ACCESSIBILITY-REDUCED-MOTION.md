# Accessibility: Reduced Motion Support

## Overview

Both IES Reader and SiYuan Plugin now have comprehensive support for the `prefers-reduced-motion` media query, respecting users' OS-level accessibility preferences.

## Implementation Details

### IES Reader

**Files Added:**
- `/ies/reader/src/styles/motion.css` - Complete motion system with reduced motion overrides
- `/ies/reader/src/hooks/useReducedMotion.ts` - React hook for detecting motion preferences
- `/ies/reader/src/hooks/useReducedMotion.test.ts` - Unit tests for the hook
- `/ies/reader/src/hooks/index.ts` - Export barrel for all hooks

**Files Modified:**
- `/ies/reader/src/index.css` - Added import for motion.css

**Features:**
1. **CSS Media Query Override**: All animations and transitions are reduced to 0.01ms when `prefers-reduced-motion: reduce`
2. **Scroll Behavior**: Smooth scrolling disabled, instant scrolling used instead
3. **React Hook**: `useReducedMotion()` provides programmatic access to user preference
4. **Graceful Degradation**: Loading spinners still function but with minimal duration

**Usage Example:**
```tsx
import { useReducedMotion } from '@/hooks';

function MyComponent() {
  const prefersReducedMotion = useReducedMotion();
  
  const duration = prefersReducedMotion ? 0 : 300;
  
  return (
    <div className={prefersReducedMotion ? '' : 'animate-fade-in'}>
      Content
    </div>
  );
}
```

### SiYuan Plugin

**Files Modified:**
- `/.worktrees/siyuan/ies/plugin/src/styles/design-system/animations.css` - Added scroll-behavior override

**Existing Support:**
The SiYuan plugin already had comprehensive reduced motion support via its design system:
- All animations reduced to 0.01ms
- All transitions reduced to 0.01ms
- Animation iteration counts limited to 1

**Enhancement:**
Added `scroll-behavior: auto !important;` to ensure smooth scrolling is also disabled when users prefer reduced motion.

## What Gets Disabled

When a user has `prefers-reduced-motion: reduce` enabled:

1. **All CSS Animations**: Keyframe animations run for only 0.01ms (effectively instant)
2. **All CSS Transitions**: Property transitions happen instantly
3. **Smooth Scrolling**: Disabled in favor of instant scroll jumps
4. **Spinner Animations**: Still visible but rotate with minimal animation

## Why This Matters

Users may enable reduced motion for several reasons:
- **Vestibular disorders**: Motion can cause dizziness, nausea, or disorientation
- **Attention disorders**: Excessive motion can be distracting
- **Epilepsy**: Some animations can trigger seizures
- **Personal preference**: Some users simply prefer less motion

According to accessibility guidelines (WCAG 2.1), respecting this preference is essential for inclusive design.

## Testing

### Manual Testing

**macOS:**
1. System Preferences → Accessibility → Display
2. Enable "Reduce motion"
3. Reload the application

**Windows:**
1. Settings → Ease of Access → Display
2. Enable "Show animations in Windows"
3. Reload the application

**Linux (GNOME):**
```bash
gsettings set org.gnome.desktop.interface enable-animations false
```

### Browser DevTools Testing

**Chrome/Edge:**
1. Open DevTools (F12)
2. Click three dots → More tools → Rendering
3. Find "Emulate CSS media feature prefers-reduced-motion"
4. Select "reduce"

**Firefox:**
1. Open DevTools (F12)
2. Click three dots → Settings
3. Find "Accessibility" section
4. Check "Enable accessibility features"
5. Reload page and use accessibility inspector

### Automated Testing

Run the test suite for `useReducedMotion`:
```bash
cd ies/reader
pnpm test useReducedMotion.test.ts
```

## Resources

- [MDN: prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
- [WCAG 2.1 Success Criterion 2.3.3](https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html)
- [A11y Project: prefers-reduced-motion](https://www.a11yproject.com/posts/design-reduced-motion-sensitivities/)

## Future Enhancements

- Add user preference override in settings (allow users to enable animations even if OS says reduce)
- Create utility function for conditional animation delays in JS
- Add telemetry to understand how many users have reduced motion enabled
- Consider adding "reduced motion" toggle in app settings for users who can't change OS settings
