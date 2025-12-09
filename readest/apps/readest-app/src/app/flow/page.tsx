'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import clsx from 'clsx';
import { LuArrowLeft, LuMessageCircle, LuCompass, LuMessageCircleQuestion } from 'react-icons/lu';

import { useFlowModeStore } from '@/store/flowModeStore';
import QuestionSelector from '@/app/reader/components/flowpanel/QuestionSelector';
import EntitySection from '@/app/reader/components/flowpanel/EntitySection';
import EvidenceSection from '@/app/reader/components/flowpanel/EvidenceSection';
import JourneyBreadcrumb from '@/app/reader/components/flowpanel/JourneyBreadcrumb';

type FlowTab = 'questions' | 'explore' | 'chat';

export default function FlowPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<FlowTab>('explore');

  const {
    questions,
    currentQuestionId,
    currentEntity,
    evidence,
    isLoadingEntity,
    isLoadingEvidence,
    isLoadingQuestions,
    addQuestion,
    setCurrentQuestionId,
  } = useFlowModeStore();

  const handleBack = () => {
    router.back();
  };

  const handleCreateQuestion = (text: string) => {
    const newQuestion = {
      id: `q-${Date.now()}`,
      text,
      source: 'reader' as const,
      status: 'active' as const,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    addQuestion(newQuestion);
    setCurrentQuestionId(newQuestion.id);
  };

  return (
    <div className="flex flex-col h-screen bg-base-100">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-base-300 bg-base-100/80 backdrop-blur-sm">
        <button onClick={handleBack} className="p-2 -ml-2 hover:bg-base-200 rounded-lg">
          <LuArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="font-semibold">Flow</h1>
        <div className="w-9" /> {/* Spacer for centering */}
      </header>

      {/* Question Selector */}
      <div className="px-4 py-3 border-b border-base-300">
        <QuestionSelector
          questions={questions}
          currentQuestionId={currentQuestionId}
          onSelect={setCurrentQuestionId}
          onCreate={handleCreateQuestion}
          isLoading={isLoadingQuestions}
        />
      </div>

      {/* Journey Breadcrumb */}
      <div className="px-4 py-2 border-b border-base-300">
        <JourneyBreadcrumb />
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {activeTab === 'questions' && (
          <QuestionsTab />
        )}

        {activeTab === 'explore' && (
          <div className="space-y-4">
            {isLoadingEntity ? (
              <div className="flex items-center justify-center py-12">
                <span className="loading loading-spinner loading-md text-primary" />
              </div>
            ) : currentEntity ? (
              <>
                <EntitySection entity={currentEntity} />
                <EvidenceSection evidence={evidence} isLoading={isLoadingEvidence} />
              </>
            ) : (
              <div className="text-center py-12 text-base-content/50">
                <LuCompass className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Select a question to start exploring</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'chat' && (
          <ChatTab />
        )}
      </div>

      {/* Bottom Tab Bar */}
      <nav className="flex border-t border-base-300 bg-base-100">
        <TabButton
          icon={<LuMessageCircleQuestion className="w-5 h-5" />}
          label="Questions"
          isActive={activeTab === 'questions'}
          onClick={() => setActiveTab('questions')}
        />
        <TabButton
          icon={<LuCompass className="w-5 h-5" />}
          label="Explore"
          isActive={activeTab === 'explore'}
          onClick={() => setActiveTab('explore')}
        />
        <TabButton
          icon={<LuMessageCircle className="w-5 h-5" />}
          label="Chat"
          isActive={activeTab === 'chat'}
          onClick={() => setActiveTab('chat')}
        />
      </nav>
    </div>
  );
}

// Tab Button Component
function TabButton({
  icon,
  label,
  isActive,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'flex-1 flex flex-col items-center gap-1 py-3 transition-colors',
        isActive ? 'text-primary' : 'text-base-content/50 hover:text-base-content'
      )}
    >
      {icon}
      <span className="text-xs">{label}</span>
    </button>
  );
}

// Questions Tab (placeholder)
function QuestionsTab() {
  const { questions, currentQuestionId, setCurrentQuestionId } = useFlowModeStore();

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">My Questions</h2>
      {questions.length === 0 ? (
        <p className="text-base-content/50 text-sm">
          No questions yet. Use the selector above to create one.
        </p>
      ) : (
        <div className="space-y-2">
          {questions.map((q) => (
            <button
              key={q.id}
              onClick={() => setCurrentQuestionId(q.id)}
              className={clsx(
                'w-full text-left p-3 rounded-lg border transition-colors',
                q.id === currentQuestionId
                  ? 'border-primary bg-primary/10'
                  : 'border-base-300 hover:bg-base-200'
              )}
            >
              <p className="font-medium">{q.text}</p>
              <p className="text-xs text-base-content/50 mt-1">
                {q.source === 'siyuan' ? '🔗 From SiYuan' : '📝 Created here'}
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Chat Tab (placeholder)
function ChatTab() {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 flex items-center justify-center text-base-content/50">
        <div className="text-center">
          <LuMessageCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>AI thinking partner coming soon</p>
        </div>
      </div>
      <div className="mt-auto">
        <input
          type="text"
          placeholder="Ask the AI..."
          className="w-full px-4 py-3 bg-base-200 rounded-lg"
          disabled
        />
      </div>
    </div>
  );
}
