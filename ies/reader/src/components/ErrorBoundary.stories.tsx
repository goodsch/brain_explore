import type { Meta, StoryObj } from '@storybook/react';
import { ErrorBoundary } from './ErrorBoundary';
import { Button } from './Button';
import { useState } from 'react';

/**
 * ErrorBoundary component from IES Design System v2.
 *
 * Catches React component errors and displays a graceful fallback UI.
 * Provides error details and a reset mechanism.
 */
const meta = {
  title: 'Components/ErrorBoundary',
  component: ErrorBoundary,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
  argTypes: {
    fallbackMessage: {
      control: 'text',
      description: 'Custom error message to display',
    },
  },
} satisfies Meta<typeof ErrorBoundary>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Component that throws an error when button is clicked
 */
const ThrowErrorComponent = ({ shouldThrow = false }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error thrown by component');
  }
  return <div style={{ padding: '2rem', color: 'var(--text-primary)' }}>No error - click the button to trigger an error</div>;
};

/**
 * Interactive component to demonstrate error boundary
 */
const InteractiveErrorDemo = () => {
  const [shouldError, setShouldError] = useState(false);
  const [resetKey, setResetKey] = useState(0);

  const handleReset = () => {
    setShouldError(false);
    setResetKey((prev) => prev + 1);
  };

  return (
    <div style={{ padding: '2rem', minHeight: '100vh' }}>
      <ErrorBoundary key={resetKey} onReset={handleReset}>
        <div style={{ textAlign: 'center', color: 'var(--text-primary)' }}>
          <h2>Error Boundary Test</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            Click the button below to simulate a component error
          </p>
          <Button onClick={() => setShouldError(true)}>
            Trigger Error
          </Button>
          <ThrowErrorComponent shouldThrow={shouldError} />
        </div>
      </ErrorBoundary>
    </div>
  );
};

/**
 * Default error boundary with standard error
 */
export const Default: Story = {
  render: () => <InteractiveErrorDemo />,
};

/**
 * Custom error message
 */
export const CustomMessage: Story = {
  render: () => {
    const [shouldError, setShouldError] = useState(false);
    const [resetKey, setResetKey] = useState(0);

    const handleReset = () => {
      setShouldError(false);
      setResetKey((prev) => prev + 1);
    };

    return (
      <div style={{ padding: '2rem', minHeight: '100vh' }}>
        <ErrorBoundary
          key={resetKey}
          fallbackMessage="The reader encountered a problem"
          onReset={handleReset}
        >
          <div style={{ textAlign: 'center', color: 'var(--text-primary)' }}>
            <h2>Custom Error Message Test</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
              This demonstrates a custom error message
            </p>
            <Button onClick={() => setShouldError(true)}>
              Trigger Error
            </Button>
            <ThrowErrorComponent shouldThrow={shouldError} />
          </div>
        </ErrorBoundary>
      </div>
    );
  },
};

/**
 * Error boundary in error state (for visual testing)
 */
export const ErrorState: Story = {
  render: () => (
    <div style={{ minHeight: '100vh' }}>
      <ErrorBoundary>
        <ThrowErrorComponent shouldThrow={true} />
      </ErrorBoundary>
    </div>
  ),
};

/**
 * Multiple nested boundaries
 */
export const NestedBoundaries: Story = {
  render: () => {
    const [outerError, setOuterError] = useState(false);
    const [innerError, setInnerError] = useState(false);
    const [resetKey, setResetKey] = useState(0);

    return (
      <div style={{ padding: '2rem', minHeight: '100vh' }}>
        <ErrorBoundary key={resetKey} fallbackMessage="Outer boundary caught an error">
          <div style={{ padding: '2rem', background: 'var(--bg-secondary)', borderRadius: '8px', color: 'var(--text-primary)' }}>
            <h3>Outer Boundary</h3>
            <p style={{ color: 'var(--text-secondary)' }}>This is protected by the outer error boundary</p>
            <Button onClick={() => setOuterError(true)} style={{ marginRight: '1rem' }}>
              Trigger Outer Error
            </Button>

            <div style={{ marginTop: '2rem' }}>
              <ErrorBoundary fallbackMessage="Inner boundary caught an error">
                <div style={{ padding: '1.5rem', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                  <h4>Inner Boundary</h4>
                  <p style={{ color: 'var(--text-secondary)' }}>This is protected by the inner error boundary</p>
                  <Button onClick={() => setInnerError(true)}>
                    Trigger Inner Error
                  </Button>
                  <ThrowErrorComponent shouldThrow={innerError} />
                </div>
              </ErrorBoundary>
            </div>

            <ThrowErrorComponent shouldThrow={outerError} />
          </div>
        </ErrorBoundary>
      </div>
    );
  },
};
