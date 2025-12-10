import type { Meta, StoryObj } from '@storybook/react';
import { QuestionClassBadge, QuestionClass } from './QuestionClassBadge';

const meta = {
  title: 'Components/QuestionClassBadge',
  component: QuestionClassBadge,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'QuestionClassBadge displays question class with visual identifier (color + icon). Used in thinking sessions, question displays, and ForgeMode UI.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    questionClass: {
      control: 'select',
      options: [
        'schema-probe',
        'boundary',
        'dimensional',
        'causal',
        'counterfactual',
        'anchor',
        'perspective-shift',
        'meta-cognitive',
        'reflective-synthesis',
      ] as QuestionClass[],
      description: 'The question class to display',
    },
    size: {
      control: 'radio',
      options: ['sm', 'md', 'lg'],
      description: 'Size variant',
    },
    iconOnly: {
      control: 'boolean',
      description: 'Show only icon (no label)',
    },
  },
} satisfies Meta<typeof QuestionClassBadge>;

export default meta;
type Story = StoryObj<typeof meta>;

// ===== Default Stories =====

export const Default: Story = {
  args: {
    questionClass: 'schema-probe',
  },
};

export const IconOnly: Story = {
  args: {
    questionClass: 'schema-probe',
    iconOnly: true,
  },
};

// ===== Size Variants =====

export const Small: Story = {
  args: {
    questionClass: 'causal',
    size: 'sm',
  },
};

export const Medium: Story = {
  args: {
    questionClass: 'causal',
    size: 'md',
  },
};

export const Large: Story = {
  args: {
    questionClass: 'causal',
    size: 'lg',
  },
};

// ===== All Sizes Comparison =====

export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
      <QuestionClassBadge questionClass="causal" size="sm" />
      <QuestionClassBadge questionClass="causal" size="md" />
      <QuestionClassBadge questionClass="causal" size="lg" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Comparison of all three size variants.',
      },
    },
  },
};

// ===== All Question Classes =====

export const AllQuestionClasses: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div>
        <h4 style={{ color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
          Discovery Questions
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          <QuestionClassBadge questionClass="schema-probe" />
          <QuestionClassBadge questionClass="boundary" />
          <QuestionClassBadge questionClass="dimensional" />
        </div>
      </div>
      <div>
        <h4 style={{ color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
          Dialogue Questions
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          <QuestionClassBadge questionClass="causal" />
          <QuestionClassBadge questionClass="counterfactual" />
          <QuestionClassBadge questionClass="anchor" />
        </div>
      </div>
      <div>
        <h4 style={{ color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
          Flow & Meta Questions
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          <QuestionClassBadge questionClass="perspective-shift" />
          <QuestionClassBadge questionClass="meta-cognitive" />
          <QuestionClassBadge questionClass="reflective-synthesis" />
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All 9 question classes organized by thinking mode.',
      },
    },
  },
};

// ===== Icon Only Grid =====

export const IconOnlyGrid: Story = {
  render: () => (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
      <QuestionClassBadge questionClass="schema-probe" iconOnly />
      <QuestionClassBadge questionClass="boundary" iconOnly />
      <QuestionClassBadge questionClass="dimensional" iconOnly />
      <QuestionClassBadge questionClass="causal" iconOnly />
      <QuestionClassBadge questionClass="counterfactual" iconOnly />
      <QuestionClassBadge questionClass="anchor" iconOnly />
      <QuestionClassBadge questionClass="perspective-shift" iconOnly />
      <QuestionClassBadge questionClass="meta-cognitive" iconOnly />
      <QuestionClassBadge questionClass="reflective-synthesis" iconOnly />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Icon-only variant for compact displays.',
      },
    },
  },
};

// ===== Real-World Examples =====

export const InQuestionDisplay: Story = {
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        maxWidth: '500px',
      }}
    >
      {[
        {
          class: 'schema-probe' as QuestionClass,
          question: 'What are the main categories of executive function?',
        },
        {
          class: 'causal' as QuestionClass,
          question: 'What mechanisms enable working memory to function?',
        },
        {
          class: 'anchor' as QuestionClass,
          question: 'Can you give a specific example of inhibitory control failure?',
        },
      ].map((item, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            gap: '12px',
            padding: '12px 16px',
            background: 'var(--color-bg-secondary)',
            borderRadius: '8px',
          }}
        >
          <QuestionClassBadge questionClass={item.class} size="sm" />
          <span style={{ color: 'var(--color-text-primary)', flex: 1 }}>
            {item.question}
          </span>
        </div>
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Question class badges used to label thinking partner questions.',
      },
    },
  },
};

export const CognitiveTracking: Story = {
  render: () => (
    <div
      style={{
        padding: '16px',
        background: 'var(--color-bg-secondary)',
        borderRadius: '12px',
        maxWidth: '400px',
      }}
    >
      <div style={{ marginBottom: '12px', color: 'var(--color-text-secondary)' }}>
        Questions used in this session:
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        <QuestionClassBadge questionClass="schema-probe" size="sm" />
        <QuestionClassBadge questionClass="causal" size="sm" />
        <QuestionClassBadge questionClass="anchor" size="sm" />
        <QuestionClassBadge questionClass="meta-cognitive" size="sm" />
        <QuestionClassBadge questionClass="reflective-synthesis" size="sm" />
      </div>
      <div
        style={{
          marginTop: '16px',
          fontSize: '12px',
          color: 'var(--color-text-muted)',
        }}
      >
        5 of 9 question types covered
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Tracking which question classes have been used in a thinking session.',
      },
    },
  },
};

export const QuestionClassReference: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {[
        { class: 'schema-probe', desc: 'Surfaces hidden structure (lists, buckets, taxonomies)' },
        { class: 'boundary', desc: 'Clarifies edges/limits to avoid scope creep' },
        { class: 'dimensional', desc: 'Introduces spectra/coordinates for precise positioning' },
        { class: 'causal', desc: 'Pushes for mechanisms, prerequisites, sequences' },
        { class: 'counterfactual', desc: '"What if" deviations to expose assumptions' },
        { class: 'anchor', desc: 'Grounds abstractions in concrete instances' },
        { class: 'perspective-shift', desc: 'Forces viewpoint changes (roles, time, system level)' },
        { class: 'meta-cognitive', desc: 'Checks thinking patterns directly' },
        { class: 'reflective-synthesis', desc: 'Integration statements tying threads together' },
      ].map((item, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '8px 12px',
            background: 'var(--color-bg-secondary)',
            borderRadius: '6px',
          }}
        >
          <QuestionClassBadge questionClass={item.class as QuestionClass} size="sm" />
          <span
            style={{
              color: 'var(--color-text-secondary)',
              fontSize: '13px',
              flex: 1,
            }}
          >
            {item.desc}
          </span>
        </div>
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Reference guide showing all question classes with their cognitive functions.',
      },
    },
  },
};
