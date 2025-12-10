import type { Meta, StoryObj } from '@storybook/react';
import { Badge } from './Badge';

/**
 * Badge component from IES Design System v2.
 *
 * Static pill-shaped indicator for entity types, semantic states, and labels.
 * Non-interactive display component with multiple variants.
 */
const meta = {
  title: 'Components/Badge',
  component: Badge,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: [
        'default',
        'success',
        'warning',
        'error',
        'info',
        'concept',
        'person',
        'theory',
        'framework',
        'assessment',
        'spark',
        'insight',
        'thread',
      ],
      description: 'Visual style variant',
    },
    size: {
      control: 'select',
      options: ['sm', 'md'],
      description: 'Badge size',
    },
  },
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default variant - Standard label
 */
export const Default: Story = {
  args: {
    variant: 'default',
    children: 'Default',
  },
};

/**
 * Success variant - Positive state
 */
export const Success: Story = {
  args: {
    variant: 'success',
    children: 'Success',
  },
};

/**
 * Warning variant - Caution state
 */
export const Warning: Story = {
  args: {
    variant: 'warning',
    children: 'Warning',
  },
};

/**
 * Error variant - Error state
 */
export const Error: Story = {
  args: {
    variant: 'error',
    children: 'Error',
  },
};

/**
 * Info variant - Informational state
 */
export const Info: Story = {
  args: {
    variant: 'info',
    children: 'Info',
  },
};

/**
 * Concept entity type
 */
export const Concept: Story = {
  args: {
    variant: 'concept',
    children: 'Concept',
  },
};

/**
 * Person entity type
 */
export const Person: Story = {
  args: {
    variant: 'person',
    children: 'Person',
  },
};

/**
 * Theory entity type
 */
export const Theory: Story = {
  args: {
    variant: 'theory',
    children: 'Theory',
  },
};

/**
 * Framework entity type
 */
export const Framework: Story = {
  args: {
    variant: 'framework',
    children: 'Framework',
  },
};

/**
 * Assessment entity type
 */
export const Assessment: Story = {
  args: {
    variant: 'assessment',
    children: 'Assessment',
  },
};

/**
 * Spark entity type
 */
export const Spark: Story = {
  args: {
    variant: 'spark',
    children: 'Spark',
  },
};

/**
 * Insight entity type
 */
export const Insight: Story = {
  args: {
    variant: 'insight',
    children: 'Insight',
  },
};

/**
 * Thread entity type
 */
export const Thread: Story = {
  args: {
    variant: 'thread',
    children: 'Thread',
  },
};

/**
 * Small size badge
 */
export const Small: Story = {
  args: {
    size: 'sm',
    variant: 'concept',
    children: 'Small Badge',
  },
};

/**
 * Medium size badge (default)
 */
export const Medium: Story = {
  args: {
    size: 'md',
    variant: 'concept',
    children: 'Medium Badge',
  },
};

/**
 * All semantic variants showcase
 */
export const AllSemanticVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
      <Badge variant="default">Default</Badge>
      <Badge variant="success">Success</Badge>
      <Badge variant="warning">Warning</Badge>
      <Badge variant="error">Error</Badge>
      <Badge variant="info">Info</Badge>
    </div>
  ),
};

/**
 * All entity type variants showcase
 */
export const AllEntityTypes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
      <Badge variant="concept">Concept</Badge>
      <Badge variant="person">Person</Badge>
      <Badge variant="theory">Theory</Badge>
      <Badge variant="framework">Framework</Badge>
      <Badge variant="assessment">Assessment</Badge>
      <Badge variant="spark">Spark</Badge>
      <Badge variant="insight">Insight</Badge>
      <Badge variant="thread">Thread</Badge>
    </div>
  ),
};

/**
 * All sizes showcase
 */
export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
      <Badge size="sm" variant="concept">Small</Badge>
      <Badge size="md" variant="concept">Medium</Badge>
    </div>
  ),
};

/**
 * Real-world usage example with entity labels
 */
export const EntityLabels: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div>
        <h3 style={{ marginBottom: '0.5rem', fontSize: '1rem', color: 'var(--color-text-primary)' }}>
          ADHD Executive Function
        </h3>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <Badge variant="concept" size="sm">Executive Function</Badge>
          <Badge variant="theory" size="sm">Dual-Process Theory</Badge>
          <Badge variant="assessment" size="sm">WAIS-IV</Badge>
        </div>
      </div>
      <div>
        <h3 style={{ marginBottom: '0.5rem', fontSize: '1rem', color: 'var(--color-text-primary)' }}>
          Personal Insights
        </h3>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <Badge variant="spark" size="sm">Energy Management</Badge>
          <Badge variant="insight" size="sm">Context Switching</Badge>
          <Badge variant="thread" size="sm">Task Initiation</Badge>
        </div>
      </div>
    </div>
  ),
};
