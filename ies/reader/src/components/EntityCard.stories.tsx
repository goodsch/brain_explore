import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { EntityCard, Entity } from './EntityCard';
import { EntityType } from './EntityBadge';

// Sample entities for stories
const sampleEntities: Entity[] = [
  {
    id: '1',
    name: 'Executive Function',
    type: 'Concept',
    description:
      'Executive functions are a set of cognitive processes that include working memory, flexible thinking, and self-control. These skills help people manage time, pay attention, switch focus, plan and organize, and remember details.',
    connectionCount: 15,
    sourceCount: 8,
    lastVisited: new Date(Date.now() - 3600000), // 1 hour ago
  },
  {
    id: '2',
    name: 'Russell Barkley',
    type: 'Person',
    description:
      'Russell A. Barkley is an American clinical psychologist who has focused his career on ADHD. He is a clinical professor of psychiatry at Virginia Commonwealth University Medical Center.',
    connectionCount: 23,
    sourceCount: 12,
    lastVisited: new Date(Date.now() - 86400000), // 1 day ago
  },
  {
    id: '3',
    name: 'Self-Regulation Theory',
    type: 'Theory',
    description:
      'Self-regulation is the ability to monitor and manage your energy states, emotions, thoughts, and behaviors in ways that are acceptable and produce positive results.',
    connectionCount: 8,
    sourceCount: 5,
  },
  {
    id: '4',
    name: 'ADHD Coaching Model',
    type: 'Framework',
    description: 'A structured approach to helping individuals with ADHD develop strategies and skills.',
    connectionCount: 4,
    sourceCount: 2,
  },
];

const meta = {
  title: 'Components/EntityCard',
  component: EntityCard,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'EntityCard displays entity information in a card format with expandable details. Used in search results, related entities, and entity lists.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    entity: {
      description: 'Entity data to display',
    },
    expanded: {
      control: 'boolean',
      description: 'Whether the card is expanded',
    },
    selected: {
      control: 'boolean',
      description: 'Whether the card is selected',
    },
    compact: {
      control: 'boolean',
      description: 'Compact mode (smaller padding, single line)',
    },
  },
  args: {
    onClick: fn(),
    onViewDetails: fn(),
    onViewSources: fn(),
  },
  decorators: [
    (Story) => (
      <div style={{ width: '400px' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof EntityCard>;

export default meta;
type Story = StoryObj<typeof meta>;

// ===== Default Stories =====

export const Default: Story = {
  args: {
    entity: sampleEntities[0],
  },
};

export const WithActions: Story = {
  args: {
    entity: sampleEntities[0],
    onViewDetails: fn(),
    onViewSources: fn(),
  },
};

export const Selected: Story = {
  args: {
    entity: sampleEntities[0],
    selected: true,
  },
};

export const Expanded: Story = {
  args: {
    entity: sampleEntities[0],
    expanded: true,
  },
};

export const Compact: Story = {
  args: {
    entity: sampleEntities[0],
    compact: true,
  },
};

// ===== Entity Types =====

export const ConceptCard: Story = {
  args: {
    entity: sampleEntities[0],
  },
};

export const PersonCard: Story = {
  args: {
    entity: sampleEntities[1],
  },
};

export const TheoryCard: Story = {
  args: {
    entity: sampleEntities[2],
  },
};

export const FrameworkCard: Story = {
  args: {
    entity: sampleEntities[3],
  },
};

// ===== All Entity Types =====

export const AllEntityTypes: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {[
        { id: '1', name: 'Working Memory', type: 'Concept' as EntityType, description: 'The cognitive system responsible for temporarily holding information available for processing.', connectionCount: 12, sourceCount: 6 },
        { id: '2', name: 'Edward Hallowell', type: 'Person' as EntityType, description: 'American psychiatrist specializing in ADHD and author of numerous books on the subject.', connectionCount: 8, sourceCount: 4 },
        { id: '3', name: 'Interest-Based Nervous System', type: 'Theory' as EntityType, description: 'ADHD is driven by interest rather than importance or consequences.', connectionCount: 5, sourceCount: 3 },
        { id: '4', name: 'Pomodoro Technique', type: 'Framework' as EntityType, description: 'Time management method using 25-minute focused work intervals.', connectionCount: 3, sourceCount: 2 },
        { id: '5', name: 'WAIS-IV', type: 'Assessment' as EntityType, description: 'Wechsler Adult Intelligence Scale, commonly used in ADHD evaluations.', connectionCount: 2, sourceCount: 1 },
      ].map((entity) => (
        <EntityCard key={entity.id} entity={entity} />
      ))}
    </div>
  ),
  decorators: [
    (Story) => (
      <div style={{ width: '450px' }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    docs: {
      description: {
        story: 'Cards for different domain entity types.',
      },
    },
  },
};

// ===== Personal Entity Types =====

export const PersonalEntityTypes: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {[
        { id: '1', name: 'Morning routine struggle', type: 'Spark' as EntityType, description: 'Noticed I always fail at morning routines - could be an EF issue?', connectionCount: 2 },
        { id: '2', name: 'Time blindness pattern', type: 'Insight' as EntityType, description: 'My time estimation is consistently 3x off - need external cues', connectionCount: 5, sourceCount: 2 },
        { id: '3', name: 'Understanding EF', type: 'Thread' as EntityType, description: 'Exploration of executive function and its impact on daily life', connectionCount: 8 },
        { id: '4', name: 'How to maintain focus?', type: 'FavoriteProblem' as EntityType, description: 'My ongoing question about sustained attention and focus strategies', connectionCount: 12, sourceCount: 4 },
      ].map((entity) => (
        <EntityCard key={entity.id} entity={entity} compact />
      ))}
    </div>
  ),
  decorators: [
    (Story) => (
      <div style={{ width: '400px' }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    docs: {
      description: {
        story: 'Personal knowledge entity types (Spark, Insight, Thread, FavoriteProblem) in compact mode.',
      },
    },
  },
};

// ===== States =====

export const AllStates: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div>
        <h4 style={{ color: 'var(--color-text-muted)', marginBottom: '8px', fontSize: '12px' }}>
          Default
        </h4>
        <EntityCard entity={sampleEntities[0]} />
      </div>
      <div>
        <h4 style={{ color: 'var(--color-text-muted)', marginBottom: '8px', fontSize: '12px' }}>
          Selected
        </h4>
        <EntityCard entity={sampleEntities[0]} selected />
      </div>
      <div>
        <h4 style={{ color: 'var(--color-text-muted)', marginBottom: '8px', fontSize: '12px' }}>
          Compact
        </h4>
        <EntityCard entity={sampleEntities[0]} compact />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Comparison of default, selected, and compact states.',
      },
    },
  },
};

// ===== Real-World Examples =====

export const SearchResults: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ color: 'var(--color-text-muted)', fontSize: '13px', marginBottom: '4px' }}>
        4 results for "ADHD"
      </div>
      {sampleEntities.map((entity) => (
        <EntityCard
          key={entity.id}
          entity={entity}
          onClick={() => console.log('Clicked:', entity.name)}
          onViewDetails={() => console.log('View details:', entity.name)}
          onViewSources={() => console.log('View sources:', entity.name)}
        />
      ))}
    </div>
  ),
  decorators: [
    (Story) => (
      <div style={{ width: '450px' }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    docs: {
      description: {
        story: 'Entity cards displayed as search results with click handlers.',
      },
    },
  },
};

export const RelatedEntities: Story = {
  render: () => (
    <div
      style={{
        padding: '16px',
        background: 'var(--color-bg-primary)',
        borderRadius: '12px',
      }}
    >
      <div
        style={{
          color: 'var(--color-text-secondary)',
          fontSize: '14px',
          fontWeight: 500,
          marginBottom: '12px',
        }}
      >
        Related Concepts
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {sampleEntities.slice(0, 3).map((entity) => (
          <EntityCard
            key={entity.id}
            entity={entity}
            compact
            onClick={() => console.log('Navigate to:', entity.name)}
          />
        ))}
      </div>
    </div>
  ),
  decorators: [
    (Story) => (
      <div style={{ width: '350px' }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    docs: {
      description: {
        story: 'Compact cards showing related entities in a panel.',
      },
    },
  },
};

export const EntityDetail: Story = {
  render: () => {
    const entity = sampleEntities[0];
    return (
      <div
        style={{
          padding: '20px',
          background: 'var(--color-bg-primary)',
          borderRadius: '16px',
        }}
      >
        <EntityCard
          entity={entity}
          expanded
          selected
          onViewDetails={() => console.log('View full details')}
          onViewSources={() => console.log('View sources')}
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Selected and expanded card showing entity details.',
      },
    },
  },
};

export const NoDescription: Story = {
  args: {
    entity: {
      id: '5',
      name: 'Unnamed Pattern',
      type: 'Pattern',
      connectionCount: 2,
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Entity card without description.',
      },
    },
  },
};

export const MinimalEntity: Story = {
  args: {
    entity: {
      id: '6',
      name: 'Quick Note',
      type: 'Spark',
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Minimal entity card with only name and type.',
      },
    },
  },
};

// ===== Interactive =====

export const Interactive: Story = {
  args: {
    entity: sampleEntities[0],
    onViewDetails: fn(),
    onViewSources: fn(),
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive example - use the controls to customize the card.',
      },
    },
  },
};
