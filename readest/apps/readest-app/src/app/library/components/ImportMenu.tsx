import clsx from 'clsx';
import { useEnv } from '@/context/EnvContext';
import { useTranslation } from '@/hooks/useTranslation';
import { IoFileTray, IoLibrary } from 'react-icons/io5';
import { MdRssFeed } from 'react-icons/md';

import MenuItem from '@/components/MenuItem';
import Menu from '@/components/Menu';

interface ImportMenuProps {
  setIsDropdownOpen?: (open: boolean) => void;
  onImportBooks: () => void;
  onOpenCatalogManager: () => void;
  onOpenCalibreLibrary?: () => void;
}

const ImportMenu: React.FC<ImportMenuProps> = ({
  setIsDropdownOpen,
  onImportBooks,
  onOpenCatalogManager,
  onOpenCalibreLibrary,
}) => {
  const _ = useTranslation();
  const { appService } = useEnv();

  const handleImportBooks = () => {
    onImportBooks();
    setIsDropdownOpen?.(false);
  };

  const handleOpenCatalogManager = () => {
    onOpenCatalogManager();
    setIsDropdownOpen?.(false);
  };

  const handleOpenCalibreLibrary = () => {
    onOpenCalibreLibrary?.();
    setIsDropdownOpen?.(false);
  };

  return (
    <Menu
      className={clsx(
        'dropdown-content bg-base-100 rounded-box z-[1] mt-3 w-52 p-2 shadow',
        appService?.isMobile ? 'no-triangle' : 'dropdown-center',
      )}
      onCancel={() => setIsDropdownOpen?.(false)}
    >
      <MenuItem
        label={_('From Local File')}
        Icon={<IoFileTray className='h-5 w-5' />}
        onClick={handleImportBooks}
      />
      <MenuItem
        label={_('Online Library')}
        Icon={<MdRssFeed className='h-5 w-5' />}
        onClick={handleOpenCatalogManager}
      />
      {onOpenCalibreLibrary && (
        <MenuItem
          label={_('Calibre Library')}
          Icon={<IoLibrary className='h-5 w-5' />}
          onClick={handleOpenCalibreLibrary}
        />
      )}
    </Menu>
  );
};

export default ImportMenu;
