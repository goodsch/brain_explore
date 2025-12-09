import { useState, useCallback, useEffect } from 'react';
import { Reader } from './components/Reader';
import { LibraryBrowser } from './components/library';
import { graphClient, type CalibreBook } from './services/graphClient';
import { useFlowStore } from './store/flowStore';
import './App.css';

interface BookInfo {
  title: string;
  url: string;
  calibreId?: number;
}

function App() {
  const [currentBook, setCurrentBook] = useState<BookInfo | null>(null);
  const [isLoggingIn, setIsLoggingIn] = useState(true);
  const { setUserId } = useFlowStore();
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    // Initialize theme from local storage or system preference
    if (typeof localStorage !== 'undefined' && localStorage.getItem('theme')) {
      return localStorage.getItem('theme') as 'light' | 'dark';
    }
    if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return 'light';
    }
    return 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  }, []);

  // Login on app mount
  useEffect(() => {
    async function login() {
      try {
        const profile = await graphClient.login();
        setUserId(profile.user_id);
      } catch (error) {
        console.error('Login failed:', error);
        // Continue without login - user_id will be null
      } finally {
        setIsLoggingIn(false);
      }
    }
    login();
  }, [setUserId]);

  // Handle Calibre book selection
  const handleBookSelect = useCallback((book: CalibreBook) => {
    setCurrentBook({
      title: book.title,
      url: graphClient.getBookFileUrl(book.calibre_id),
      calibreId: book.calibre_id,
    });
  }, []);

  // Handle local file selection
  const handleLocalFileSelect = useCallback((file: File) => {
    const url = URL.createObjectURL(file);
    setCurrentBook({
      title: file.name.replace('.epub', ''),
      url,
    });
  }, []);

  // Return to library
  const closeBook = useCallback(() => {
    if (currentBook?.url.startsWith('blob:')) {
      URL.revokeObjectURL(currentBook.url);
    }
    setCurrentBook(null);
  }, [currentBook]);

  // Show loading while logging in
  if (isLoggingIn) {
    return (
      <div className="app">
        <div className="loading-screen">
          <div className="loading-spinner" />
          <p>Connecting...</p>
        </div>
      </div>
    );
  }

  // Show reader if a book is selected
  if (currentBook) {
    return (
      <div className="app">
        <Reader
          url={currentBook.url}
          title={currentBook.title}
          calibreId={currentBook.calibreId}
          onClose={closeBook}
        />
      </div>
    );
  }

  // Library browser
  return (
    <div className="app">
      <LibraryBrowser
        onBookSelect={handleBookSelect}
        onLocalFileSelect={handleLocalFileSelect}
        theme={theme}
        toggleTheme={toggleTheme}
      />
    </div>
  );
}

export default App;
