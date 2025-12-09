import { CalibreBook } from '../../services/graphClient';

interface Props {
  onBookSelect: (book: CalibreBook) => void;
  onLocalFileSelect: (file: File) => void;
}

export function LibraryBrowser({ onBookSelect: _onBookSelect, onLocalFileSelect }: Props) {
  return (
    <div className="library-container">
      <h1>Library</h1>
      <input
        type="file"
        accept=".epub"
        onChange={(e) => e.target.files?.[0] && onLocalFileSelect(e.target.files[0])}
      />
      {/* Mock book list could go here */}
    </div>
  );
}
