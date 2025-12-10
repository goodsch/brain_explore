import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { Input } from './Input';

// Simple icon components for demonstration
const SearchIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="100%"
    height="100%"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.35-4.35" />
  </svg>
);

const MailIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="100%"
    height="100%"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect width="20" height="16" x="2" y="4" rx="2" />
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
  </svg>
);

const CheckIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="100%"
    height="100%"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const LockIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="100%"
    height="100%"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
  </svg>
);

/**
 * Input component from IES Design System v2.
 *
 * Form input element with multiple variants, sizes, and accessibility features.
 * Follows the glassmorphic design language.
 */
const meta = {
  title: 'Components/Input',
  component: Input,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'error', 'success'],
      description: 'Visual style variant',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Input size',
    },
    type: {
      control: 'select',
      options: ['text', 'email', 'password', 'search', 'tel', 'url', 'number'],
      description: 'Input type',
    },
    label: {
      control: 'text',
      description: 'Label text',
    },
    helperText: {
      control: 'text',
      description: 'Helper text below input',
    },
    errorMessage: {
      control: 'text',
      description: 'Error message (sets variant to error)',
    },
    placeholder: {
      control: 'text',
      description: 'Placeholder text',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable input interaction',
    },
    fullWidth: {
      control: 'boolean',
      description: 'Take full width of container',
    },
  },
  args: {
    onChange: fn(),
    onFocus: fn(),
    onBlur: fn(),
  },
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default variant - Standard input field
 */
export const Default: Story = {
  args: {
    placeholder: 'Enter text...',
  },
};

/**
 * With label - Input with descriptive label
 */
export const WithLabel: Story = {
  args: {
    label: 'Username',
    placeholder: 'Enter your username',
  },
};

/**
 * With helper text - Input with helpful guidance
 */
export const WithHelperText: Story = {
  args: {
    label: 'Email',
    type: 'email',
    placeholder: 'you@example.com',
    helperText: 'We will never share your email with anyone else.',
  },
};

/**
 * Error state - Input with validation error
 */
export const ErrorState: Story = {
  args: {
    label: 'Email',
    type: 'email',
    placeholder: 'you@example.com',
    errorMessage: 'Please enter a valid email address.',
    defaultValue: 'invalid-email',
  },
};

/**
 * Success variant - Input showing successful validation
 */
export const SuccessVariant: Story = {
  args: {
    label: 'Email',
    type: 'email',
    variant: 'success',
    placeholder: 'you@example.com',
    helperText: 'Email is valid!',
    defaultValue: 'user@example.com',
    rightIcon: <CheckIcon />,
  },
};

/**
 * Small size input
 */
export const Small: Story = {
  args: {
    size: 'sm',
    placeholder: 'Small input',
  },
};

/**
 * Medium size input (default)
 */
export const Medium: Story = {
  args: {
    size: 'md',
    placeholder: 'Medium input',
  },
};

/**
 * Large size input
 */
export const Large: Story = {
  args: {
    size: 'lg',
    placeholder: 'Large input',
  },
};

/**
 * With left icon - Search input
 */
export const WithLeftIcon: Story = {
  args: {
    placeholder: 'Search...',
    type: 'search',
    leftIcon: <SearchIcon />,
  },
};

/**
 * With right icon - Email input
 */
export const WithRightIcon: Story = {
  args: {
    label: 'Email',
    type: 'email',
    placeholder: 'you@example.com',
    rightIcon: <MailIcon />,
  },
};

/**
 * With both icons
 */
export const WithBothIcons: Story = {
  args: {
    placeholder: 'Search entities...',
    type: 'search',
    leftIcon: <SearchIcon />,
    rightIcon: <CheckIcon />,
  },
};

/**
 * Password input
 */
export const PasswordInput: Story = {
  args: {
    label: 'Password',
    type: 'password',
    placeholder: 'Enter your password',
    helperText: 'Minimum 8 characters',
    leftIcon: <LockIcon />,
  },
};

/**
 * Disabled state
 */
export const Disabled: Story = {
  args: {
    label: 'Disabled Input',
    placeholder: 'Cannot edit',
    disabled: true,
    defaultValue: 'Disabled value',
  },
};

/**
 * Full width - Input taking full container width
 */
export const FullWidth: Story = {
  args: {
    label: 'Full Width Input',
    placeholder: 'This input takes full width',
    fullWidth: true,
  },
  decorators: [
    (Story) => (
      <div style={{ width: '400px' }}>
        <Story />
      </div>
    ),
  ],
};

/**
 * All sizes showcase
 */
export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '300px' }}>
      <Input size="sm" placeholder="Small input" />
      <Input size="md" placeholder="Medium input" />
      <Input size="lg" placeholder="Large input" />
    </div>
  ),
};

/**
 * All variants showcase
 */
export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '300px' }}>
      <Input
        label="Default Variant"
        placeholder="Enter text..."
        helperText="This is a default input"
      />
      <Input
        label="Success Variant"
        variant="success"
        placeholder="Valid input"
        defaultValue="valid@example.com"
        helperText="Email is valid!"
        rightIcon={<CheckIcon />}
      />
      <Input
        label="Error Variant"
        placeholder="Invalid input"
        defaultValue="invalid-email"
        errorMessage="Please enter a valid email address"
      />
    </div>
  ),
};

/**
 * Form example - Complete form with multiple inputs
 */
export const FormExample: Story = {
  render: () => (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        console.log('Form submitted');
      }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '400px' }}
    >
      <Input
        label="Full Name"
        placeholder="John Doe"
        helperText="Enter your first and last name"
        fullWidth
      />
      <Input
        label="Email"
        type="email"
        placeholder="you@example.com"
        leftIcon={<MailIcon />}
        fullWidth
      />
      <Input
        label="Password"
        type="password"
        placeholder="Minimum 8 characters"
        helperText="Use a strong password with letters, numbers, and symbols"
        leftIcon={<LockIcon />}
        fullWidth
      />
      <Input
        label="Search"
        type="search"
        placeholder="Search..."
        leftIcon={<SearchIcon />}
        fullWidth
      />
    </form>
  ),
};
