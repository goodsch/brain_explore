import React, { useState } from 'react';
import { useFlowModeStore } from '@/store/flowModeStore';
import { getSyncService, AppSource } from '@/services/flow/syncService';

const ResumeSection: React.FC = () => {
  const { sessionId, currentSession } = useFlowModeStore();
  const [resumeData, setResumeData] = useState<{
    deepLink?: string;
    instructions?: string;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showCopied, setShowCopied] = useState(false);

  if (!sessionId || !currentSession) {
    return null;
  }

  const handleGetResumeLink = async () => {
    setIsLoading(true);
    try {
      const syncService = getSyncService();
      const data = await syncService.getResumeData(sessionId, AppSource.SIYUAN);
      setResumeData(data);
    } catch (error) {
      console.error('Failed to get resume data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenDeepLink = () => {
    if (resumeData?.deepLink) {
      window.location.href = resumeData.deepLink;
    }
  };

  const handleCopyLink = async () => {
    if (resumeData?.deepLink) {
      try {
        await navigator.clipboard.writeText(resumeData.deepLink);
        setShowCopied(true);
        setTimeout(() => setShowCopied(false), 2000);
      } catch (error) {
        console.error('Failed to copy link:', error);
      }
    }
  };

  return (
    <div className='rounded-lg bg-base-300 p-3'>
      <h3 className='mb-2 text-sm font-semibold text-base-content/80'>Cross-App Continuity</h3>

      {!resumeData ? (
        <button
          onClick={handleGetResumeLink}
          disabled={isLoading}
          className='btn btn-primary btn-sm w-full'
        >
          {isLoading ? (
            <span className='loading loading-spinner loading-xs'></span>
          ) : (
            'Resume in SiYuan'
          )}
        </button>
      ) : (
        <div className='space-y-2'>
          {resumeData.instructions && (
            <p className='text-xs text-base-content/60'>{resumeData.instructions}</p>
          )}
          {resumeData.deepLink && (
            <div className='space-y-1'>
              <button onClick={handleOpenDeepLink} className='btn btn-primary btn-sm w-full'>
                Open in SiYuan
              </button>
              <button onClick={handleCopyLink} className='btn btn-ghost btn-sm w-full'>
                {showCopied ? 'Copied!' : 'Copy Deep Link'}
              </button>
              <details className='mt-2'>
                <summary className='cursor-pointer text-xs text-base-content/60'>
                  View deep link
                </summary>
                <code className='mt-1 block break-all rounded bg-base-100 p-2 text-xs'>
                  {resumeData.deepLink}
                </code>
              </details>
            </div>
          )}
        </div>
      )}

      <div className='mt-2 text-xs text-base-content/50'>
        Session: {sessionId.slice(0, 8)}...
      </div>
    </div>
  );
};

export default ResumeSection;
