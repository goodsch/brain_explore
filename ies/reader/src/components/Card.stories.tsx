import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { Card } from './Card';
import { Button } from './Button';

/**
 * Card component from IES Design System v2.
 *
 * Container component for organizing related content with multiple variants,
 * optional header/footer, and clickable states. Follows the glassmorphic design language.
 */
const meta = {
  title: 'Components/Card',
  component: Card,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'elevated', 'outlined', 'glass'],
      description: 'Visual style variant',
    },
    padding: {
      control: 'select',
      options: ['none', 'sm', 'md', 'lg'],
      description: 'Content padding size',
    },
    clickable: {
      control: 'boolean',
      description: 'Enable clickable/interactive state',
    },
    title: {
      control: 'text',
      description: 'Card title (simple header)',
    },
  },
  decorators: [
    (Story) => (
      <div style={{ minWidth: '400px', maxWidth: '600px' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default variant - Standard card appearance
 */
export const Default: Story = {
  args: {
    children: (
      <div>
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          This is a default card with standard styling. It uses the secondary background
          color and subtle borders for clean separation.
        </p>
      </div>
    ),
  },
};

/**
 * Elevated variant - Card with shadow for depth
 */
export const Elevated: Story = {
  args: {
    variant: 'elevated',
    children: (
      <div>
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          This elevated card includes a shadow to create depth and hierarchy. Hover to see
          the enhanced shadow effect.
        </p>
      </div>
    ),
  },
};

/**
 * Outlined variant - Transparent card with border
 */
export const Outlined: Story = {
  args: {
    variant: 'outlined',
    children: (
      <div>
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          This outlined card has a transparent background with a visible border, perfect
          for subtle content separation.
        </p>
      </div>
    ),
  },
};

/**
 * Glass variant - Glassmorphism effect with backdrop blur
 */
export const Glass: Story = {
  args: {
    variant: 'glass',
    children: (
      <div>
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          This glass card features the signature glassmorphic design with backdrop blur,
          creating a frosted glass effect.
        </p>
      </div>
    ),
  },
};

/**
 * Card with title - Simple header with title text
 */
export const WithTitle: Story = {
  args: {
    title: 'Card Title',
    children: (
      <div>
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          This card includes a title in the header section, providing clear context for
          the content below.
        </p>
      </div>
    ),
  },
};

/**
 * Card with title and actions - Header with title and action buttons
 */
export const WithTitleAndActions: Story = {
  args: {
    title: 'Entity: Cognitive Load Theory',
    actions: (
      <>
        <Button variant="ghost" size="sm">
          Edit
        </Button>
        <Button variant="ghost" size="sm">
          Share
        </Button>
      </>
    ),
    children: (
      <div>
        <p style={{ margin: '0 0 1rem 0', color: 'var(--color-text-primary)' }}>
          Cognitive Load Theory describes how the human cognitive architecture processes
          and stores information in working memory.
        </p>
        <div
          style={{
            display: 'flex',
            gap: '0.5rem',
            flexWrap: 'wrap',
          }}
        >
          <span
            style={{
              padding: '0.25rem 0.75rem',
              background: 'var(--color-entity-theory-bg)',
              color: 'var(--color-entity-theory)',
              borderRadius: 'var(--radius-full)',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            Theory
          </span>
          <span
            style={{
              padding: '0.25rem 0.75rem',
              background: 'var(--color-entity-concept-bg)',
              color: 'var(--color-entity-concept)',
              borderRadius: 'var(--radius-full)',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            Learning
          </span>
        </div>
      </div>
    ),
  },
};

/**
 * Card with footer - Content with footer section
 */
export const WithFooter: Story = {
  args: {
    title: 'Research Paper',
    footer: 'Last updated: December 9, 2025 • 5 min read',
    children: (
      <div>
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          This card includes a footer section for metadata, timestamps, or additional
          information about the content.
        </p>
      </div>
    ),
  },
};

/**
 * Card with custom header - Complex header with custom content
 */
export const WithCustomHeader: Story = {
  args: {
    header: (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          width: '100%',
        }}
      >
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: 'var(--radius-md)',
            background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.5rem',
          }}
        >
          📚
        </div>
        <div style={{ flex: 1 }}>
          <h3
            style={{
              margin: 0,
              color: 'var(--color-text-primary)',
              fontSize: 'var(--font-size-lg)',
              fontWeight: 'var(--font-weight-semibold)',
            }}
          >
            Thinking, Fast and Slow
          </h3>
          <p
            style={{
              margin: '0.25rem 0 0 0',
              color: 'var(--color-text-muted)',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            by Daniel Kahneman
          </p>
        </div>
      </div>
    ),
    children: (
      <div>
        <p style={{ margin: '0 0 1rem 0', color: 'var(--color-text-primary)' }}>
          This card demonstrates a custom header with an icon, title, and subtitle,
          perfect for displaying book information or complex metadata.
        </p>
        <Button variant="primary" size="sm">
          Continue Reading
        </Button>
      </div>
    ),
  },
};

/**
 * Clickable card - Interactive card with click handler
 */
export const Clickable: Story = {
  args: {
    variant: 'outlined',
    clickable: true,
    title: 'Clickable Card',
    onClick: fn(),
    children: (
      <div>
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          This card is clickable and will trigger an action when clicked. Hover to see
          the interactive state, and use keyboard navigation (Tab + Enter) for
          accessibility.
        </p>
      </div>
    ),
  },
};

/**
 * Padding variants - Different padding sizes
 */
export const PaddingVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', minWidth: '400px' }}>
      <Card padding="none" title="No Padding">
        <div style={{ padding: 'var(--space-4)', background: 'rgba(139, 92, 246, 0.1)' }}>
          Content with no padding from card (background shows edge)
        </div>
      </Card>

      <Card padding="sm" title="Small Padding">
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          Content with small padding (12px)
        </p>
      </Card>

      <Card padding="md" title="Medium Padding">
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          Content with medium padding (16px) - default
        </p>
      </Card>

      <Card padding="lg" title="Large Padding">
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          Content with large padding (24px)
        </p>
      </Card>
    </div>
  ),
};

/**
 * All variants showcase - Side-by-side comparison
 */
export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(2, 1fr)' }}>
      <Card variant="default" title="Default">
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>Standard card</p>
      </Card>

      <Card variant="elevated" title="Elevated">
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>Card with shadow</p>
      </Card>

      <Card variant="outlined" title="Outlined">
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          Transparent with border
        </p>
      </Card>

      <Card variant="glass" title="Glass">
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>
          Glassmorphic effect
        </p>
      </Card>
    </div>
  ),
};

/**
 * Entity card example - Real-world usage with entity data
 */
export const EntityCardExample: Story = {
  args: {
    variant: 'elevated',
    clickable: true,
    onClick: fn(),
    title: 'Growth Mindset',
    actions: (
      <span
        style={{
          padding: '0.25rem 0.75rem',
          background: 'var(--color-entity-concept-bg)',
          color: 'var(--color-entity-concept)',
          borderRadius: 'var(--radius-full)',
          fontSize: 'var(--font-size-xs)',
          fontWeight: 'var(--font-weight-medium)',
        }}
      >
        Concept
      </span>
    ),
    footer: 'Mentioned in 12 books • Last visited 2 hours ago',
    children: (
      <div>
        <p style={{ margin: '0 0 1rem 0', color: 'var(--color-text-primary)' }}>
          The belief that abilities and intelligence can be developed through dedication,
          effort, and learning from mistakes.
        </p>
        <div
          style={{
            display: 'flex',
            gap: '0.5rem',
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-text-muted)',
          }}
        >
          <span>Related: Fixed Mindset, Self-Efficacy, Neuroplasticity</span>
        </div>
      </div>
    ),
  },
};

/**
 * Question card example - Real-world usage with question data
 */
export const QuestionCardExample: Story = {
  args: {
    variant: 'glass',
    clickable: true,
    onClick: fn(),
    header: (
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', width: '100%' }}>
        <span
          style={{
            padding: '0.25rem 0.75rem',
            background: 'var(--color-question-dimensional-bg)',
            color: 'var(--color-question-dimensional)',
            borderRadius: 'var(--radius-full)',
            fontSize: 'var(--font-size-xs)',
            fontWeight: 'var(--font-weight-medium)',
          }}
        >
          Dimensional
        </span>
        <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)' }}>
          Active exploration
        </span>
      </div>
    ),
    children: (
      <div>
        <p
          style={{
            margin: 0,
            color: 'var(--color-text-primary)',
            fontSize: 'var(--font-size-lg)',
            fontWeight: 'var(--font-weight-medium)',
            lineHeight: 'var(--font-line-height-snug)',
          }}
        >
          What spectrum does attention exist on between diffuse and focused modes?
        </p>
      </div>
    ),
    footer: '3 relevant passages found • 2 related questions',
  },
};

/**
 * Complex layout example - Card with rich content
 */
export const ComplexLayoutExample: Story = {
  args: {
    variant: 'elevated',
    padding: 'lg',
    title: 'Reading Session Summary',
    actions: (
      <Button variant="ghost" size="sm">
        View Details
      </Button>
    ),
    footer: (
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Session started 45 minutes ago</span>
        <Button variant="primary" size="sm">
          Resume
        </Button>
      </div>
    ),
    children: (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '1rem',
            padding: '1rem',
            background: 'var(--color-bg-tertiary)',
            borderRadius: 'var(--radius-md)',
          }}
        >
          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                fontSize: 'var(--font-size-2xl)',
                fontWeight: 'var(--font-weight-semibold)',
                color: 'var(--color-text-primary)',
              }}
            >
              23
            </div>
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)' }}>
              Pages Read
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                fontSize: 'var(--font-size-2xl)',
                fontWeight: 'var(--font-weight-semibold)',
                color: 'var(--color-text-primary)',
              }}
            >
              8
            </div>
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)' }}>
              Entities
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                fontSize: 'var(--font-size-2xl)',
                fontWeight: 'var(--font-weight-semibold)',
                color: 'var(--color-text-primary)',
              }}
            >
              5
            </div>
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)' }}>
              Questions
            </div>
          </div>
        </div>

        <div>
          <h4
            style={{
              margin: '0 0 0.5rem 0',
              fontSize: 'var(--font-size-base)',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--color-text-primary)',
            }}
          >
            Recent Entities
          </h4>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {['Cognitive Load', 'Schema Theory', 'Working Memory', 'Mental Models'].map(
              (entity) => (
                <span
                  key={entity}
                  style={{
                    padding: '0.375rem 0.75rem',
                    background: 'var(--color-entity-concept-bg)',
                    color: 'var(--color-entity-concept)',
                    borderRadius: 'var(--radius-full)',
                    fontSize: 'var(--font-size-sm)',
                  }}
                >
                  {entity}
                </span>
              )
            )}
          </div>
        </div>
      </div>
    ),
  },
};
