'use client';

import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';

interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  snapPoints?: string[]; // Currently ignored, keeping for future compatibility
}

export function Sheet({ isOpen, onClose, title, children }: SheetProps) {
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

  return createPortal(
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[999] bg-black/50" // High z-index to ensure it's on top
          onClick={onClose}
        >
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: '0%' }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-0 left-0 right-0 z-[1000] flex max-h-[90vh] flex-col rounded-t-xl bg-base-100 shadow-xl"
            onClick={(e) => e.stopPropagation()} // Prevent click from closing sheet
          >
            {/* Handle for visual affordance */}
            <div className="mx-auto mt-3 h-1.5 w-12 rounded-full bg-base-300" />

            {/* Header */}
            {title && (
              <div className="border-b border-base-200 px-4 py-3 text-center text-lg font-semibold">
                {title}
              </div>
            )}

            {/* Content */}
            <div className="flex-1 overflow-y-auto px-4 pb-8 pt-4">
              {children}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body
  );
}
