import type { Meta, StoryObj } from '@storybook/react';
import { ProgressRing } from './ProgressRing';

const meta = {
  title: 'Components/ProgressRing',
  component: ProgressRing,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'ProgressRing is an SVG circular progress indicator. Used for loading states, completion tracking, and progress visualization.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    value: {
      control: { type: 'range', min: 0, max: 100, step: 1 },
      description: 'Progress value (0-100)',
    },
    size: {
      control: 'radio',
      options: ['sm', 'md', 'lg', 'xl'],
      description: 'Size variant',
    },
    variant: {
      control: 'select',
      options: ['default', 'success', 'warning', 'error', 'info'],
      description: 'Color variant',
    },
    showLabel: {
      control: 'boolean',
      description: 'Show percentage label in center',
    },
    label: {
      control: 'text',
      description: 'Custom label (overrides percentage)',
    },
    strokeWidth: {
      control: { type: 'number', min: 1, max: 10 },
      description: 'Custom stroke width in pixels',
    },
  },
} satisfies Meta<typeof ProgressRing>;

export default meta;
type Story = StoryObj<typeof meta>;

// ===== Default Stories =====

export const Default: Story = {
  args: {
    value: 65,
  },
};

export const WithLabel: Story = {
  args: {
    value: 75,
    showLabel: true,
  },
};

export const CustomLabel: Story = {
  args: {
    value: 100,
    showLabel: true,
    label: '✓',
  },
};

// ===== Progress Values =====

export const Empty: Story = {
  args: {
    value: 0,
    showLabel: true,
  },
};

export const Quarter: Story = {
  args: {
    value: 25,
    showLabel: true,
  },
};

export const Half: Story = {
  args: {
    value: 50,
    showLabel: true,
  },
};

export const ThreeQuarters: Story = {
  args: {
    value: 75,
    showLabel: true,
  },
};

export const Complete: Story = {
  args: {
    value: 100,
    showLabel: true,
    variant: 'success',
  },
};

// ===== Size Variants =====

export const Small: Story = {
  args: {
    value: 60,
    size: 'sm',
  },
};

export const Medium: Story = {
  args: {
    value: 60,
    size: 'md',
  },
};

export const Large: Story = {
  args: {
    value: 60,
    size: 'lg',
    showLabel: true,
  },
};

export const ExtraLarge: Story = {
  args: {
    value: 60,
    size: 'xl',
    showLabel: true,
  },
};

// ===== All Sizes Comparison =====

export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
      <ProgressRing value={65} size="sm" />
      <ProgressRing value={65} size="md" />
      <ProgressRing value={65} size="lg" showLabel />
      <ProgressRing value={65} size="xl" showLabel />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Comparison of all four size variants: sm (24px), md (40px), lg (64px), xl (96px).',
      },
    },
  },
};

// ===== Color Variants =====

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
      <div style={{ textAlign: 'center' }}>
        <ProgressRing value={75} variant="default" size="lg" showLabel />
        <div style={{ marginTop: '8px', color: 'var(--color-text-muted)', fontSize: '12px' }}>
          Default
        </div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <ProgressRing value={75} variant="success" size="lg" showLabel />
        <div style={{ marginTop: '8px', color: 'var(--color-text-muted)', fontSize: '12px' }}>
          Success
        </div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <ProgressRing value={75} variant="warning" size="lg" showLabel />
        <div style={{ marginTop: '8px', color: 'var(--color-text-muted)', fontSize: '12px' }}>
          Warning
        </div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <ProgressRing value={75} variant="error" size="lg" showLabel />
        <div style={{ marginTop: '8px', color: 'var(--color-text-muted)', fontSize: '12px' }}>
          Error
        </div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <ProgressRing value={75} variant="info" size="lg" showLabel />
        <div style={{ marginTop: '8px', color: 'var(--color-text-muted)', fontSize: '12px' }}>
          Info
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All semantic color variants for different progress contexts.',
      },
    },
  },
};

// ===== Progress Steps =====

export const ProgressSteps: Story = {
  render: () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
      {[0, 25, 50, 75, 100].map((value) => (
        <ProgressRing
          key={value}
          value={value}
          size="md"
          variant={value === 100 ? 'success' : 'default'}
        />
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Progress ring at different completion stages.',
      },
    },
  },
};

// ===== Real-World Examples =====

export const LoadingState: Story = {
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '12px',
        padding: '24px',
        background: 'var(--color-bg-secondary)',
        borderRadius: '12px',
      }}
    >
      <ProgressRing value={45} size="lg" showLabel variant="info" />
      <div style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
        Processing entities...
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Progress ring used to show entity processing progress.',
      },
    },
  },
};

export const QuestionCoverage: Story = {
  render: () => (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        padding: '16px',
        background: 'var(--color-bg-secondary)',
        borderRadius: '12px',
      }}
    >
      <ProgressRing value={56} size="lg" showLabel />
      <div>
        <div style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>
          Question Coverage
        </div>
        <div style={{ color: 'var(--color-text-muted)', fontSize: '13px' }}>
          5 of 9 question types used
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Progress ring showing thinking session question coverage.',
      },
    },
  },
};

export const MultipleMetrics: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '32px' }}>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <ProgressRing value={87} size="lg" showLabel variant="success" />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: '12px' }}>
          Entities Found
        </span>
      </div>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <ProgressRing value={62} size="lg" showLabel variant="info" />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: '12px' }}>
          Relationships
        </span>
      </div>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <ProgressRing value={34} size="lg" showLabel variant="warning" />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: '12px' }}>
          Enrichment
        </span>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Multiple progress rings showing different ingestion metrics.',
      },
    },
  },
};

export const CompletionStates: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '24px' }}>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <ProgressRing value={100} size="lg" showLabel label="✓" variant="success" />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: '12px' }}>
          Complete
        </span>
      </div>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <ProgressRing value={100} size="lg" showLabel label="!" variant="warning" />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: '12px' }}>
          With Warnings
        </span>
      </div>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <ProgressRing value={100} size="lg" showLabel label="✗" variant="error" />
        <span style={{ color: 'var(--color-text-secondary)', fontSize: '12px' }}>
          Failed
        </span>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Custom labels for different completion states.',
      },
    },
  },
};

// ===== Interactive Example =====

export const Interactive: Story = {
  args: {
    value: 50,
    size: 'xl',
    showLabel: true,
    variant: 'info',
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive example - use the controls to adjust all properties.',
      },
    },
  },
};
