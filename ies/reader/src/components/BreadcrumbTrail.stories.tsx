import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { BreadcrumbTrail, BreadcrumbItem } from './BreadcrumbTrail';
import { EntityType } from './EntityBadge';

// Sample journey trail (most recent first)
const sampleTrail: BreadcrumbItem[] = [
  { id: '1', name: 'Working Memory', type: 'Concept' },
  { id: '2', name: 'Executive Function', type: 'Concept' },
  { id: '3', name: 'Russell Barkley', type: 'Person' },
  { id: '4', name: 'ADHD Overview', type: 'Concept' },
];

const longTrail: BreadcrumbItem[] = [
  { id: '1', name: 'Time Blindness', type: 'Concept' },
  { id: '2', name: 'Working Memory', type: 'Concept' },
  { id: '3', name: 'Cognitive Load', type: 'Theory' },
  { id: '4', name: 'Executive Function', type: 'Concept' },
  { id: '5', name: 'Self-Regulation', type: 'Theory' },
  { id: '6', name: 'Russell Barkley', type: 'Person' },
  { id: '7', name: 'ADHD Research', type: 'Thread' },
  { id: '8', name: 'Neuroscience', type: 'Concept' },
];

const meta = {
  title: 'Components/BreadcrumbTrail',
  component: BreadcrumbTrail,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'BreadcrumbTrail shows the exploration path through the knowledge graph. Features overflow handling and clickable navigation.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    trail: {
      description: 'Array of breadcrumb items (most recent first)',
    },
    maxVisible: {
      control: { type: 'number', min: 2, max: 10 },
      description: 'Maximum visible items before overflow',
    },
    showBadges: {
      control: 'boolean',
      description: 'Show entity type badges',
    },
    compact: {
      control: 'boolean',
      description: 'Compact mode',
    },
  },
  args: {
    onItemClick: fn(),
  },
  decorators: [
    (Story) => (
      <div style={{ width: '500px', padding: '16px', background: 'var(--color-bg-secondary)', borderRadius: '12px' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof BreadcrumbTrail>;

export default meta;
type Story = StoryObj<typeof meta>;

// ===== Default Stories =====

export const Default: Story = {
  args: {
    trail: sampleTrail,
  },
};

export const WithOverflow: Story = {
  args: {
    trail: longTrail,
    maxVisible: 4,
  },
};

export const NoBadges: Story = {
  args: {
    trail: sampleTrail,
    showBadges: false,
  },
};

export const Compact: Story = {
  args: {
    trail: sampleTrail,
    compact: true,
  },
};

// ===== Length Variations =====

export const SingleItem: Story = {
  args: {
    trail: [{ id: '1', name: 'Executive Function', type: 'Concept' }],
  },
};

export const TwoItems: Story = {
  args: {
    trail: [
      { id: '1', name: 'Working Memory', type: 'Concept' },
      { id: '2', name: 'Executive Function', type: 'Concept' },
    ],
  },
};

export const ManyItems: Story = {
  args: {
    trail: longTrail,
    maxVisible: 5,
  },
};

// ===== Entity Type Variations =====

export const MixedTypes: Story = {
  args: {
    trail: [
      { id: '1', name: 'Current Insight', type: 'Insight' },
      { id: '2', name: 'Working Memory', type: 'Concept' },
      { id: '3', name: 'Russell Barkley', type: 'Person' },
      { id: '4', name: 'Self-Regulation', type: 'Theory' },
      { id: '5', name: 'ADHD Exploration', type: 'Thread' },
    ],
  },
  parameters: {
    docs: {
      description: {
        story: 'Journey trail showing mixed entity types.',
      },
    },
  },
};

export const PersonalJourney: Story = {
  args: {
    trail: [
      { id: '1', name: 'Time blindness insight', type: 'Insight' },
      { id: '2', name: 'Morning struggle', type: 'Spark' },
      { id: '3', name: 'Understanding EF', type: 'Thread' },
      { id: '4', name: 'How to focus?', type: 'FavoriteProblem' },
    ],
  },
  parameters: {
    docs: {
      description: {
        story: 'Personal knowledge exploration journey.',
      },
    },
  },
};

// ===== Real-World Examples =====

export const InFlowPanel: Story = {
  render: () => (
    <div style={{ width: '100%' }}>
      <div style={{ marginBottom: '16px', color: 'var(--color-text-secondary)', fontSize: '12px', fontWeight: 500 }}>
        JOURNEY TRAIL
      </div>
      <BreadcrumbTrail
        trail={longTrail}
        maxVisible={4}
        onItemClick={(item) => console.log('Navigate to:', item.name)}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Breadcrumb trail as displayed in the Flow Panel.',
      },
    },
  },
};

export const InReader: Story = {
  render: () => (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        padding: '12px 16px',
        background: 'var(--color-bg-tertiary)',
        borderRadius: '8px',
      }}
    >
      <span style={{ color: 'var(--color-text-muted)', fontSize: '13px', flexShrink: 0 }}>
        Exploration:
      </span>
      <BreadcrumbTrail
        trail={sampleTrail}
        compact
        onItemClick={(item) => console.log('Navigate to:', item.name)}
      />
    </div>
  ),
  decorators: [
    (Story) => (
      <div style={{ width: '600px' }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    docs: {
      description: {
        story: 'Compact breadcrumb trail in the reader header.',
      },
    },
  },
};

export const WithSourceApp: Story = {
  render: () => {
    const trailWithSources: BreadcrumbItem[] = [
      { id: '1', name: 'Time Blindness', type: 'Concept', sourceApp: 'reader' },
      { id: '2', name: 'Working Memory', type: 'Concept', sourceApp: 'reader' },
      { id: '3', name: 'Executive Function', type: 'Concept', sourceApp: 'siyuan' },
      { id: '4', name: 'ADHD Research', type: 'Thread', sourceApp: 'siyuan' },
    ];

    return (
      <div>
        <div style={{ marginBottom: '8px', color: 'var(--color-text-muted)', fontSize: '12px' }}>
          Cross-app journey (reader → siyuan)
        </div>
        <BreadcrumbTrail
          trail={trailWithSources}
          onItemClick={(item) => console.log('Navigate to:', item.name, 'from', item.sourceApp)}
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Journey trail showing cross-app navigation history.',
      },
    },
  },
};

export const Clickable: Story = {
  render: () => (
    <div>
      <p style={{ color: 'var(--color-text-secondary)', fontSize: '13px', marginBottom: '12px' }}>
        Click any past item to navigate back (current item is not clickable):
      </p>
      <BreadcrumbTrail
        trail={sampleTrail}
        onItemClick={(item, index) => alert(`Navigate to: ${item.name} (index: ${index})`)}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Interactive breadcrumb trail with click handlers.',
      },
    },
  },
};

export const OverflowDemo: Story = {
  render: () => (
    <div>
      <p style={{ color: 'var(--color-text-secondary)', fontSize: '13px', marginBottom: '12px' }}>
        Click the "..." button to see overflow items:
      </p>
      <BreadcrumbTrail
        trail={longTrail}
        maxVisible={3}
        onItemClick={(item) => console.log('Navigate to:', item.name)}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Breadcrumb with overflow menu showing hidden items.',
      },
    },
  },
};

export const Empty: Story = {
  args: {
    trail: [],
  },
  parameters: {
    docs: {
      description: {
        story: 'Empty trail returns null (nothing rendered).',
      },
    },
  },
};

// ===== Interactive =====

export const Interactive: Story = {
  args: {
    trail: longTrail,
    maxVisible: 5,
    showBadges: true,
    compact: false,
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive example - use the controls to customize the breadcrumb trail.',
      },
    },
  },
};
