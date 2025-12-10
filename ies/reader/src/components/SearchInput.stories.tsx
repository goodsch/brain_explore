import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { useState } from 'react';
import { SearchInput } from './SearchInput';

const meta = {
  title: 'Components/SearchInput',
  component: SearchInput,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'SearchInput with debounce support, clear button, and loading state. Used for entity search, book search, and filtering.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    value: {
      control: 'text',
      description: 'Current search value',
    },
    placeholder: {
      control: 'text',
      description: 'Placeholder text',
    },
    size: {
      control: 'radio',
      options: ['sm', 'md', 'lg'],
      description: 'Size variant',
    },
    debounce: {
      control: { type: 'number', min: 0, max: 1000, step: 50 },
      description: 'Debounce delay in milliseconds',
    },
    loading: {
      control: 'boolean',
      description: 'Show loading spinner',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable the input',
    },
  },
  args: {
    onChange: fn(),
    onClear: fn(),
    onSubmit: fn(),
  },
} satisfies Meta<typeof SearchInput>;

export default meta;
type Story = StoryObj<typeof meta>;

// ===== Controlled Component Wrapper =====

const ControlledSearchInput = (props: React.ComponentProps<typeof SearchInput>) => {
  const [value, setValue] = useState(props.value || '');
  return (
    <SearchInput
      {...props}
      value={value}
      onChange={(newValue) => {
        setValue(newValue);
        props.onChange?.(newValue);
      }}
    />
  );
};

// ===== Default Stories =====

export const Default: Story = {
  args: {
    value: '',
    placeholder: 'Search entities...',
  },
  render: (args) => <ControlledSearchInput {...args} />,
};

export const WithValue: Story = {
  args: {
    value: 'executive function',
    placeholder: 'Search entities...',
  },
  render: (args) => <ControlledSearchInput {...args} />,
};

export const Loading: Story = {
  args: {
    value: 'ADHD',
    placeholder: 'Search entities...',
    loading: true,
  },
  render: (args) => <ControlledSearchInput {...args} />,
};

export const Disabled: Story = {
  args: {
    value: '',
    placeholder: 'Search disabled...',
    disabled: true,
  },
  render: (args) => <ControlledSearchInput {...args} />,
};

// ===== Size Variants =====

export const Small: Story = {
  args: {
    value: '',
    size: 'sm',
    placeholder: 'Search...',
  },
  render: (args) => <ControlledSearchInput {...args} />,
};

export const Medium: Story = {
  args: {
    value: '',
    size: 'md',
    placeholder: 'Search...',
  },
  render: (args) => <ControlledSearchInput {...args} />,
};

export const Large: Story = {
  args: {
    value: '',
    size: 'lg',
    placeholder: 'Search...',
  },
  render: (args) => <ControlledSearchInput {...args} />,
};

// ===== All Sizes Comparison =====

export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '300px' }}>
      <ControlledSearchInput value="" placeholder="Small search..." size="sm" onChange={() => {}} />
      <ControlledSearchInput value="" placeholder="Medium search..." size="md" onChange={() => {}} />
      <ControlledSearchInput value="" placeholder="Large search..." size="lg" onChange={() => {}} />
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

// ===== Debounce Example =====

export const WithDebounce: Story = {
  render: () => {
    const [value, setValue] = useState('');
    const [searchCount, setSearchCount] = useState(0);

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '300px' }}>
        <SearchInput
          value={value}
          onChange={(newValue) => {
            setValue(newValue);
            setSearchCount((c) => c + 1);
          }}
          placeholder="Type to search (300ms debounce)..."
          debounce={300}
        />
        <div style={{ color: 'var(--color-text-muted)', fontSize: '13px' }}>
          Search triggered: {searchCount} times
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story:
          'With 300ms debounce - onChange is called after user stops typing. Watch the counter to see debounce in action.',
      },
    },
  },
};

// ===== Real-World Examples =====

export const EntitySearch: Story = {
  render: () => {
    const [value, setValue] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSearch = (searchValue: string) => {
      setValue(searchValue);
      if (searchValue) {
        setLoading(true);
        setTimeout(() => setLoading(false), 500);
      }
    };

    return (
      <div style={{ width: '350px' }}>
        <SearchInput
          value={value}
          onChange={handleSearch}
          placeholder="Search entities..."
          debounce={300}
          loading={loading}
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story:
          'Entity search with debounce and loading state. Shows spinner while "searching".',
      },
    },
  },
};

export const BookSearch: Story = {
  render: () => {
    const [value, setValue] = useState('');

    return (
      <div
        style={{
          padding: '16px',
          background: 'var(--color-bg-secondary)',
          borderRadius: '12px',
          width: '400px',
        }}
      >
        <div style={{ marginBottom: '12px', color: 'var(--color-text-secondary)' }}>
          Calibre Library
        </div>
        <SearchInput
          value={value}
          onChange={setValue}
          placeholder="Search books by title or author..."
          size="lg"
        />
        {value && (
          <div
            style={{
              marginTop: '12px',
              padding: '8px',
              background: 'var(--color-bg-tertiary)',
              borderRadius: '8px',
              color: 'var(--color-text-muted)',
              fontSize: '13px',
            }}
          >
            Searching for: "{value}"
          </div>
        )}
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Book search in the Calibre library dialog.',
      },
    },
  },
};

export const FilterEntities: Story = {
  render: () => {
    const [value, setValue] = useState('');
    const entities = [
      { name: 'Executive Function', type: 'Concept' },
      { name: 'Russell Barkley', type: 'Person' },
      { name: 'Self-Regulation Theory', type: 'Theory' },
      { name: 'ADHD Coaching Model', type: 'Framework' },
      { name: 'Working Memory', type: 'Concept' },
      { name: 'Attention Control', type: 'Concept' },
    ];

    const filteredEntities = entities.filter((e) =>
      e.name.toLowerCase().includes(value.toLowerCase())
    );

    return (
      <div style={{ width: '350px' }}>
        <SearchInput
          value={value}
          onChange={setValue}
          placeholder="Filter entities..."
          size="sm"
        />
        <div
          style={{
            marginTop: '12px',
            display: 'flex',
            flexDirection: 'column',
            gap: '4px',
          }}
        >
          {filteredEntities.map((entity, i) => (
            <div
              key={i}
              style={{
                padding: '8px 12px',
                background: 'var(--color-bg-secondary)',
                borderRadius: '6px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <span style={{ color: 'var(--color-text-primary)' }}>{entity.name}</span>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '12px' }}>
                {entity.type}
              </span>
            </div>
          ))}
          {filteredEntities.length === 0 && (
            <div
              style={{
                padding: '16px',
                textAlign: 'center',
                color: 'var(--color-text-muted)',
              }}
            >
              No entities found
            </div>
          )}
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Using SearchInput to filter a list of entities in real-time.',
      },
    },
  },
};

export const WithSubmit: Story = {
  render: () => {
    const [value, setValue] = useState('');
    const [submitted, setSubmitted] = useState('');

    return (
      <div style={{ width: '300px' }}>
        <SearchInput
          value={value}
          onChange={setValue}
          onSubmit={(v) => setSubmitted(v)}
          placeholder="Press Enter to search..."
        />
        {submitted && (
          <div
            style={{
              marginTop: '12px',
              padding: '8px',
              background: 'var(--color-bg-tertiary)',
              borderRadius: '8px',
              color: 'var(--color-text-secondary)',
              fontSize: '13px',
            }}
          >
            Submitted: "{submitted}"
          </div>
        )}
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'SearchInput with Enter key submission handler.',
      },
    },
  },
};

// ===== Keyboard Navigation =====

export const KeyboardDemo: Story = {
  render: () => (
    <div style={{ width: '300px' }}>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: '12px', fontSize: '13px' }}>
        Keyboard shortcuts:
        <br />• <strong>Escape</strong>: Clear input
        <br />• <strong>Enter</strong>: Submit search
      </p>
      <ControlledSearchInput
        value=""
        placeholder="Try keyboard shortcuts..."
        onChange={() => {}}
        onSubmit={(v) => alert(`Submitted: ${v}`)}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Demonstrates keyboard navigation: Escape to clear, Enter to submit.',
      },
    },
  },
};
