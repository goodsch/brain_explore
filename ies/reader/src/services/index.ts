// Services barrel export
export { graphClient, type CalibreBook } from './graphClient';
export {
  questionApi,
  QuestionApiClient,
  type Question,
  type QuestionCreate,
  type QuestionUpdate,
  type AnswerBlock,
  type AnswerBlockCreate,
} from './questionApi';
export {
  contextApi,
  ContextApiClient,
  type Context,
  type ContextCreate,
  type ContextUpdate,
  type ContextType,
  type ContextStatus,
} from './contextApi';
export {
  syncApi,
  SyncApiClient,
  type ExplorationSession,
  type SessionCreateRequest,
  type SessionUpdateRequest,
  type ResumeData,
  type JourneyStep,
  type ReadingPosition,
  type AppSource,
  type SessionStatus,
} from './syncApi';
export {
  extractionApi,
  ExtractionApiClient,
  type ExtractionRunRequest,
  type ExtractionRunResponse,
  type ExtractionResult,
  type ExtractionProfile,
  type ExtractionProfileCreate,
} from './extractionApi';
export {
  sessionStateApi,
  SessionStateApiClient,
  type SessionState,
  type SessionStateUpdate,
  type SessionStateHistory,
  type HeartbeatResponse,
  type SessionStateHistoryResponse,
  type ReadingPosition as SessionReadingPosition,
} from './sessionStateApi';
