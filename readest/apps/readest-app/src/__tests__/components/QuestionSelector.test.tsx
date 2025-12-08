// src/__tests__/components/QuestionSelector.test.tsx
import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import QuestionSelector from '../../app/reader/components/flowpanel/QuestionSelector';

const mockQuestions = [
  {
    id: 'q1',
    text: 'How does ADHD affect time perception?',
    source: 'reader' as const,
    status: 'active' as const,
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
  },
  {
    id: 'q2',
    text: 'Why do I procrastinate?',
    source: 'siyuan' as const,
    status: 'active' as const,
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
  },
];

describe('QuestionSelector', () => {
  afterEach(() => {
    cleanup();
  });

  it('displays current question text when collapsed', () => {
    render(
      <QuestionSelector
        questions={mockQuestions}
        currentQuestionId="q1"
        onSelect={vi.fn()}
        onCreate={vi.fn()}
        isLoading={false}
      />
    );

    expect(screen.getByText(/How does ADHD affect time perception/)).toBeDefined();
  });

  it('shows placeholder when no question selected', () => {
    render(
      <QuestionSelector
        questions={mockQuestions}
        currentQuestionId={null}
        onSelect={vi.fn()}
        onCreate={vi.fn()}
        isLoading={false}
      />
    );

    expect(screen.getByText(/Select a question/)).toBeDefined();
  });

  it('expands dropdown on click', () => {
    const { container } = render(
      <QuestionSelector
        questions={mockQuestions}
        currentQuestionId={null}
        onSelect={vi.fn()}
        onCreate={vi.fn()}
        isLoading={false}
      />
    );

    const mainButton = container.querySelector('button');
    expect(mainButton).toBeDefined();
    fireEvent.click(mainButton!);
    expect(screen.getByText('Why do I procrastinate?')).toBeDefined();
  });

  it('calls onSelect when question clicked', () => {
    const onSelect = vi.fn();
    const { container } = render(
      <QuestionSelector
        questions={mockQuestions}
        currentQuestionId={null}
        onSelect={onSelect}
        onCreate={vi.fn()}
        isLoading={false}
      />
    );

    const mainButton = container.querySelector('button');
    fireEvent.click(mainButton!);
    fireEvent.click(screen.getByText('Why do I procrastinate?'));
    expect(onSelect).toHaveBeenCalledWith('q2');
  });
});
