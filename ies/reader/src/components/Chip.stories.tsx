import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { Chip } from './Chip';

/**
 * Chip component from IES Design System v2.
 *
 * Interactive pill-shaped component for selections, filters, and tags.
 * Supports selection states, removal, and optional icons.
 */
const meta = {
  title: 'Components/Chip',
  component: Chip,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'selected'],
      description: 'Visual style variant',
    },
    size: {
      control: 'select',
      options: ['sm', 'md'],
      description: 'Chip size',
    },
    selected: {
      control: 'boolean',
      description: 'Selected state',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable chip interaction',
    },
  },
  args: {
    onClick: fn(),
    onRemove: fn(),
  },
} satisfies Meta<typeof Chip>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default variant - Standard chip
 */
export const Default: Story = {
  args: {
    variant: 'default',
    children: 'Default Chip',
    onClick: fn(),
  },
};

/**
 * Selected state - Active chip
 */
export const Selected: Story = {
  args: {
    selected: true,
    children: 'Selected Chip',
    onClick: fn(),
  },
};

/**
 * With remove button - Dismissible chip
 */
export const WithRemove: Story = {
  args: {
    children: 'Removable Chip',
    onRemove: fn(),
  },
};

/**
 * With leading icon - Icon + label
 */
export const WithLeadingIcon: Story = {
  args: {
    children: 'Icon Chip',
    leadingIcon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" />
        <circle cx="8" cy="8" r="2" fill="currentColor" />
      </svg>
    ),
    onClick: fn(),
  },
};

/**
 * Small size chip
 */
export const Small: Story = {
  args: {
    size: 'sm',
    children: 'Small Chip',
    onClick: fn(),
  },
};

/**
 * Medium size chip (default)
 */
export const Medium: Story = {
  args: {
    size: 'md',
    children: 'Medium Chip',
    onClick: fn(),
  },
};

/**
 * Disabled state - Non-interactive
 */
export const Disabled: Story = {
  args: {
    disabled: true,
    children: 'Disabled Chip',
    onClick: fn(),
  },
};

/**
 * Disabled with remove button - Remove button hidden
 */
export const DisabledWithRemove: Story = {
  args: {
    disabled: true,
    children: 'Disabled Chip',
    onRemove: fn(),
  },
};

/**
 * Interactive states showcase
 */
export const InteractiveStates: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
      <Chip onClick={fn()}>Default</Chip>
      <Chip selected onClick={fn()}>Selected</Chip>
      <Chip onClick={fn()} onRemove={fn()}>With Remove</Chip>
      <Chip disabled onClick={fn()}>Disabled</Chip>
    </div>
  ),
};

/**
 * All sizes showcase
 */
export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
      <Chip size="sm" onClick={fn()}>Small</Chip>
      <Chip size="md" onClick={fn()}>Medium</Chip>
    </div>
  ),
};

/**
 * Filter chips example - Multi-select interface
 */
export const FilterChips: Story = {
  render: () => {
    const [selectedFilters, setSelectedFilters] = React.useState<string[]>(['concept', 'theory']);

    const filters = [
      { id: 'concept', label: 'Concept' },
      { id: 'person', label: 'Person' },
      { id: 'theory', label: 'Theory' },
      { id: 'framework', label: 'Framework' },
      { id: 'spark', label: 'Spark' },
    ];

    const toggleFilter = (filterId: string) => {
      setSelectedFilters((prev) =>
        prev.includes(filterId)
          ? prev.filter((id) => id !== filterId)
          : [...prev, filterId]
      );
    };

    return (
      <div>
        <h3 style={{ marginBottom: '0.75rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
          Filter by Entity Type
        </h3>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {filters.map((filter) => (
            <Chip
              key={filter.id}
              size="sm"
              selected={selectedFilters.includes(filter.id)}
              onClick={() => toggleFilter(filter.id)}
            >
              {filter.label}
            </Chip>
          ))}
        </div>
      </div>
    );
  },
};

/**
 * Tag chips example - Removable tags
 */
export const TagChips: Story = {
  render: () => {
    const [tags, setTags] = React.useState([
      'Executive Function',
      'Working Memory',
      'Task Switching',
      'ADHD',
    ]);

    const removeTag = (index: number) => {
      setTags((prev) => prev.filter((_, i) => i !== index));
    };

    return (
      <div>
        <h3 style={{ marginBottom: '0.75rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
          Active Tags
        </h3>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {tags.map((tag, index) => (
            <Chip
              key={tag}
              size="sm"
              onRemove={() => removeTag(index)}
            >
              {tag}
            </Chip>
          ))}
        </div>
      </div>
    );
  },
};

/**
 * Icon chips example - Chips with leading icons
 */
export const IconChips: Story = {
  render: () => {
    const ConceptIcon = () => (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" />
        <circle cx="8" cy="8" r="2" fill="currentColor" />
      </svg>
    );

    const PersonIcon = () => (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="8" cy="6" r="3" stroke="currentColor" strokeWidth="1.5" />
        <path d="M3 14C3 11.2386 5.23858 9 8 9C10.7614 9 13 11.2386 13 14" stroke="currentColor" strokeWidth="1.5" />
      </svg>
    );

    return (
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        <Chip leadingIcon={<ConceptIcon />} onClick={fn()}>Concept</Chip>
        <Chip leadingIcon={<PersonIcon />} onClick={fn()}>Person</Chip>
        <Chip leadingIcon={<ConceptIcon />} selected onClick={fn()}>Selected</Chip>
      </div>
    );
  },
};

/**
 * Complex example - Filter + selected + removable
 */
export const ComplexExample: Story = {
  render: () => {
    const [selectedTags, setSelectedTags] = React.useState(['concept', 'theory']);
    const [appliedFilters, setAppliedFilters] = React.useState(['concept']);

    const availableTags = [
      { id: 'concept', label: 'Concept' },
      { id: 'person', label: 'Person' },
      { id: 'theory', label: 'Theory' },
      { id: 'framework', label: 'Framework' },
    ];

    const toggleTag = (tagId: string) => {
      setSelectedTags((prev) =>
        prev.includes(tagId)
          ? prev.filter((id) => id !== tagId)
          : [...prev, tagId]
      );
    };

    const applyFilters = () => {
      setAppliedFilters([...selectedTags]);
    };

    const removeFilter = (filterId: string) => {
      setAppliedFilters((prev) => prev.filter((id) => id !== filterId));
      setSelectedTags((prev) => prev.filter((id) => id !== filterId));
    };

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', minWidth: '400px' }}>
        <div>
          <h3 style={{ marginBottom: '0.75rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
            Select Filters
          </h3>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
            {availableTags.map((tag) => (
              <Chip
                key={tag.id}
                size="sm"
                selected={selectedTags.includes(tag.id)}
                onClick={() => toggleTag(tag.id)}
              >
                {tag.label}
              </Chip>
            ))}
          </div>
          <button
            onClick={applyFilters}
            style={{
              padding: '0.5rem 1rem',
              fontSize: '0.875rem',
              background: 'rgba(139, 92, 246, 0.2)',
              color: '#8b5cf6',
              border: '1px solid rgba(139, 92, 246, 0.4)',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            Apply Filters
          </button>
        </div>

        <div>
          <h3 style={{ marginBottom: '0.75rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
            Active Filters
          </h3>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {appliedFilters.length > 0 ? (
              appliedFilters.map((filterId) => {
                const tag = availableTags.find((t) => t.id === filterId);
                return tag ? (
                  <Chip
                    key={filterId}
                    size="sm"
                    selected
                    onRemove={() => removeFilter(filterId)}
                  >
                    {tag.label}
                  </Chip>
                ) : null;
              })
            ) : (
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
                No filters applied
              </span>
            )}
          </div>
        </div>
      </div>
    );
  },
};
