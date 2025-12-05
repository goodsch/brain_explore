import { ViewSettings } from '@/types/book';

export type EntityOverlay = {
  name: string;
  type: string; // Concept, Person, Theory, Assessment
  mentionCount: number;
};

export type TransformContext = {
  bookKey: string;
  viewSettings: ViewSettings;
  userLocale: string;
  primaryLanguage?: string;
  width?: number;
  height?: number;
  content: string;
  transformers: string[];
  reversePunctuationTransform?: boolean;
  // New: entity overlay data
  entityOverlay?: {
    enabled: boolean;
    entities: EntityOverlay[];
    visibleTypes: string[];
  };
};

export type Transformer = {
  name: string;
  transform: (ctx: TransformContext) => Promise<string>;
};
