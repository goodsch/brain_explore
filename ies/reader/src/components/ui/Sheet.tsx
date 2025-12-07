import { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import './Sheet.css';

interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  snapPoints?: string[];
  title?: string;
  children: React.ReactNode;
}

export function Sheet({
  isOpen,
  onClose,
  snapPoints = ['50%', '90%'],
  title,
  children
}: SheetProps) {
  const [currentSnap, setCurrentSnap] = useState(0);

  // Reset snap point when sheet opens
  useEffect(() => {
    if (isOpen) {
      setCurrentSnap(0);
    }
  }, [isOpen]);

  // Handle drag end to snap or close
  const handleDragEnd = useCallback(
    (_: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
      const velocity = info.velocity.y;
      const offset = info.offset.y;

      // Close if dragged down with velocity or past threshold
      if (velocity > 500 || offset > 100) {
        onClose();
        return;
      }

      // Snap to next point if dragged up with velocity
      if (velocity < -500 && currentSnap < snapPoints.length - 1) {
        setCurrentSnap(currentSnap + 1);
        return;
      }

      // Snap to previous point if dragged down with velocity
      if (velocity > 200 && currentSnap > 0) {
        setCurrentSnap(currentSnap - 1);
        return;
      }
    },
    [currentSnap, snapPoints.length, onClose]
  );

  // Prevent body scroll when sheet is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="sheet-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
          />

          {/* Sheet */}
          <motion.div
            className="sheet"
            initial={{ y: '100%' }}
            animate={{ y: `calc(100% - ${snapPoints[currentSnap]})` }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 400 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={{ top: 0.1, bottom: 0.5 }}
            onDragEnd={handleDragEnd}
            style={{ height: snapPoints[snapPoints.length - 1] }}
          >
            {/* Handle */}
            <div className="sheet-handle-container">
              <div className="sheet-handle" />
            </div>

            {/* Header */}
            {title && (
              <div className="sheet-header">
                <h3 className="sheet-title">{title}</h3>
              </div>
            )}

            {/* Content */}
            <div className="sheet-content">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
