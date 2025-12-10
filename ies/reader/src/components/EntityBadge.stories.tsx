import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { EntityBadge, EntityType } from './EntityBadge';

const meta = {
  title: 'Components/EntityBadge',
  component: EntityBadge,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'EntityBadge displays entity type with visual identifier (color + icon). Used in entity labels, search results, entity cards, and breadcrumbs.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    entityType: {
      control: 'select',
      options: [
        'Concept',
        'Person',
        'Theory',
        'Framework',
        'Assessment',
        'Spark',
        'Insight',
        'Thread',
        'FavoriteProblem',
        'Reframe',
        'Pattern',
        'DynamicPattern',
        'StoryInsight',
        'SchemaBreak',
      ] as EntityType[],
      description: 'The entity type to display',
    },
    size: {
      control: 'radio',
      options: ['sm', 'md', 'lg'],
      description: 'Size variant',
    },
    interactive: {
      control: 'boolean',
      description: 'Whether the badge is clickable',
    },
    muted: {
      control: 'boolean',
      description: 'Muted/inactive state',
    },
    onClick: {
      action: 'clicked',
      description: 'Click handler (only when interactive)',
    },
  },
  args: {
    onClick: fn(),
  },
} satisfies Meta<typeof EntityBadge>;

export default meta;
type Story = StoryObj<typeof meta>;

// ===== Default Stories =====

export const Default: Story = {
  args: {
    entityType: 'Concept',
  },
};

export const Interactive: Story = {
  args: {
    entityType: 'Concept',
    interactive: true,
  },
};

export const Muted: Story = {
  args: {
    entityType: 'Concept',
    muted: true,
  },
};

// ===== Size Variants =====

export const Small: Story = {
  args: {
    entityType: 'Concept',
    size: 'sm',
  },
};

export const Medium: Story = {
  args: {
    entityType: 'Concept',
    size: 'md',
  },
};

export const Large: Story = {
  args: {
    entityType: 'Concept',
    size: 'lg',
  },
};

// ===== All Sizes Comparison =====

export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
      <EntityBadge entityType="Concept" size="sm" />
      <EntityBadge entityType="Concept" size="md" />
      <EntityBadge entityType="Concept" size="lg" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Comparison of all three size variants: sm (18px), md (24px), lg (32px).',
      },
    },
  },
};

// ===== Domain Entity Types =====

export const DomainEntities: Story = {
  render: () => (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
      <EntityBadge entityType="Concept" />
      <EntityBadge entityType="Person" />
      <EntityBadge entityType="Theory" />
      <EntityBadge entityType="Framework" />
      <EntityBadge entityType="Assessment" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Domain knowledge entity types from ingested books.',
      },
    },
  },
};

// ===== Personal Entity Types =====

export const PersonalEntities: Story = {
  render: () => (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
      <EntityBadge entityType="Spark" />
      <EntityBadge entityType="Insight" />
      <EntityBadge entityType="Thread" />
      <EntityBadge entityType="FavoriteProblem" />
      <EntityBadge entityType="Reframe" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Personal knowledge entity types for ADHD-friendly capture.',
      },
    },
  },
};

// ===== Pattern Entity Types =====

export const PatternEntities: Story = {
  render: () => (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
      <EntityBadge entityType="Pattern" />
      <EntityBadge entityType="DynamicPattern" />
      <EntityBadge entityType="StoryInsight" />
      <EntityBadge entityType="SchemaBreak" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Pattern-related entity types for advanced analysis.',
      },
    },
  },
};

// ===== All 14 Entity Types =====

export const AllEntityTypes: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div>
        <h4 style={{ color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
          Domain Entities
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          <EntityBadge entityType="Concept" />
          <EntityBadge entityType="Person" />
          <EntityBadge entityType="Theory" />
          <EntityBadge entityType="Framework" />
          <EntityBadge entityType="Assessment" />
        </div>
      </div>
      <div>
        <h4 style={{ color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
          Personal Entities
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          <EntityBadge entityType="Spark" />
          <EntityBadge entityType="Insight" />
          <EntityBadge entityType="Thread" />
          <EntityBadge entityType="FavoriteProblem" />
          <EntityBadge entityType="Reframe" />
        </div>
      </div>
      <div>
        <h4 style={{ color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
          Patterns
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          <EntityBadge entityType="Pattern" />
          <EntityBadge entityType="DynamicPattern" />
          <EntityBadge entityType="StoryInsight" />
          <EntityBadge entityType="SchemaBreak" />
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Complete showcase of all 14 entity types organized by category.',
      },
    },
  },
};

// ===== States =====

export const AllStates: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ color: 'var(--color-text-secondary)', width: '80px' }}>Default</span>
        <EntityBadge entityType="Concept" />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ color: 'var(--color-text-secondary)', width: '80px' }}>Interactive</span>
        <EntityBadge entityType="Concept" interactive onClick={() => alert('Clicked!')} />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ color: 'var(--color-text-secondary)', width: '80px' }}>Muted</span>
        <EntityBadge entityType="Concept" muted />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Comparison of default, interactive, and muted states.',
      },
    },
  },
};

// ===== Interactive Example =====

export const FilterByType: Story = {
  render: () => (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
      <EntityBadge
        entityType="Concept"
        interactive
        onClick={() => console.log('Filter by Concept')}
      />
      <EntityBadge
        entityType="Person"
        interactive
        onClick={() => console.log('Filter by Person')}
      />
      <EntityBadge
        entityType="Theory"
        interactive
        muted
        onClick={() => console.log('Filter by Theory')}
      />
      <EntityBadge
        entityType="Framework"
        interactive
        muted
        onClick={() => console.log('Filter by Framework')}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          'Example of using EntityBadges as filter toggles. Active filters are full opacity, inactive are muted.',
      },
    },
  },
};

// ===== Accessibility =====

export const AccessibilityDemo: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <p style={{ color: 'var(--color-text-secondary)' }}>
        Try navigating with Tab and activating with Enter/Space:
      </p>
      <div style={{ display: 'flex', gap: '8px' }}>
        <EntityBadge
          entityType="Concept"
          interactive
          onClick={() => alert('Concept clicked!')}
        />
        <EntityBadge
          entityType="Person"
          interactive
          onClick={() => alert('Person clicked!')}
        />
        <EntityBadge
          entityType="Theory"
          interactive
          onClick={() => alert('Theory clicked!')}
        />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          'Interactive badges are fully keyboard accessible. Tab to focus, Enter/Space to activate.',
      },
    },
  },
};

// ===== Real-World Examples =====

export const InSearchResults: Story = {
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        maxWidth: '400px',
      }}
    >
      {[
        { type: 'Concept', name: 'Executive Function' },
        { type: 'Person', name: 'Russell Barkley' },
        { type: 'Theory', name: 'Self-Regulation Theory' },
        { type: 'Framework', name: 'ADHD Coaching Model' },
      ].map((item, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '8px 12px',
            background: 'var(--color-bg-secondary)',
            borderRadius: '8px',
          }}
        >
          <EntityBadge entityType={item.type as EntityType} size="sm" />
          <span style={{ color: 'var(--color-text-primary)' }}>{item.name}</span>
        </div>
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'EntityBadges used in a search results list to indicate entity types.',
      },
    },
  },
};

export const InBreadcrumb: Story = {
  render: () => (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '12px 16px',
        background: 'var(--color-bg-secondary)',
        borderRadius: '8px',
      }}
    >
      <EntityBadge entityType="Concept" size="sm" interactive />
      <span style={{ color: 'var(--color-text-muted)' }}>/</span>
      <EntityBadge entityType="Person" size="sm" interactive />
      <span style={{ color: 'var(--color-text-muted)' }}>/</span>
      <EntityBadge entityType="Theory" size="sm" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'EntityBadges used in a breadcrumb trail showing exploration path.',
      },
    },
  },
};
