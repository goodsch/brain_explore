import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import './ErrorBoundary.css';

interface Props {
  children: ReactNode;
  fallbackMessage?: string;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * ErrorBoundary - Catches React component errors and displays graceful fallback UI
 *
 * Usage:
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error details to console for debugging
    console.error('[ErrorBoundary] Component error caught:', error);
    console.error('[ErrorBoundary] Component stack:', errorInfo.componentStack);

    this.setState({
      error,
      errorInfo,
    });

    // TODO: Send error to logging service (e.g., Sentry)
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });

    // Call optional reset handler from props
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-boundary__content">
            <div className="error-boundary__icon">
              <AlertCircle size={48} />
            </div>

            <h2 className="error-boundary__title">
              {this.props.fallbackMessage || 'Something went wrong'}
            </h2>

            <p className="error-boundary__description">
              The application encountered an unexpected error.
              This has been logged for investigation.
            </p>

            {this.state.error && (
              <details className="error-boundary__details">
                <summary>Error Details</summary>
                <div className="error-boundary__error-text">
                  <strong>Error:</strong> {this.state.error.toString()}
                </div>
                {this.state.errorInfo && (
                  <div className="error-boundary__stack">
                    <strong>Component Stack:</strong>
                    <pre>{this.state.errorInfo.componentStack}</pre>
                  </div>
                )}
              </details>
            )}

            <button
              onClick={this.handleReset}
              className="error-boundary__reset-btn"
            >
              <RefreshCw size={18} />
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Convenience hook for throwing errors that will be caught by ErrorBoundary
 * Useful for functional components
 */
export function useErrorHandler() {
  const [, setState] = React.useState();

  return React.useCallback((error: Error) => {
    setState(() => {
      throw error;
    });
  }, []);
}
