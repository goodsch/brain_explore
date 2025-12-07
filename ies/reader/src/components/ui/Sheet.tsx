import { useState } from 'react';
import { motion, AnimatePresence, type PanInfo } from 'framer-motion';
import './Sheet.css';

interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  snapPoints?: string[];  // e.g., ['50%', '90%']
  children: React.ReactNode;
  title?: string;
}

export function Sheet({ isOpen, onClose, snapPoints = ['50%'], children }: SheetProps) {
  const [activeSnap] = useState(snapPoints[0]);

  const handleDragEnd = (_event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    if (info.offset.y > 100 || info.velocity.y > 500) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="sheet-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          <motion.div
            className="sheet"
            initial={{ y: '100%' }}
            animate={{ y: '0%' }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            drag="y"
            dragConstraints={{ top: 0 }}
            dragElastic={0.2}
            onDragEnd={handleDragEnd}
            style={{ height: activeSnap }} 
          >
            <div className="sheet-handle" />
            <div style={{ flex: 1, overflowY: 'auto', padding: '0 var(--ies-space-4)' }}>
                {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}