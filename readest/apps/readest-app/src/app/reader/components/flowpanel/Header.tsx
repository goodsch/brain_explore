import React from 'react';
import clsx from 'clsx';
import { RiPushpinFill, RiPushpinLine, RiCloseLine } from 'react-icons/ri';
import { LuSparkles } from 'react-icons/lu';

import { useTranslation } from '@/hooks/useTranslation';
import { useResponsiveSize } from '@/hooks/useResponsiveSize';

interface FlowPanelHeaderProps {
  isPinned: boolean;
  handleClose: () => void;
  handleTogglePin: () => void;
}

const FlowPanelHeader: React.FC<FlowPanelHeaderProps> = ({
  isPinned,
  handleClose,
  handleTogglePin,
}) => {
  const _ = useTranslation();
  const iconSize = useResponsiveSize(18);

  return (
    <div className='border-base-300 flex items-center justify-between border-b px-4 py-3'>
      <div className='flex items-center gap-2'>
        <LuSparkles size={iconSize} className='text-primary' />
        <h2 className='text-base font-semibold'>{_('Flow Mode')}</h2>
      </div>
      <div className='flex items-center gap-1'>
        <button
          className={clsx(
            'sidebar-pin-btn btn btn-ghost btn-sm',
            'hidden sm:inline-flex',
            isPinned && 'btn-active',
          )}
          onClick={handleTogglePin}
          aria-label={isPinned ? _('Unpin panel') : _('Pin panel')}
          title={isPinned ? _('Unpin panel') : _('Pin panel')}
        >
          {isPinned ? <RiPushpinFill size={iconSize} /> : <RiPushpinLine size={iconSize} />}
        </button>
        <button
          className='btn btn-ghost btn-sm'
          onClick={handleClose}
          aria-label={_('Close Flow Mode')}
          title={_('Close Flow Mode')}
        >
          <RiCloseLine size={iconSize} />
        </button>
      </div>
    </div>
  );
};

export default FlowPanelHeader;
