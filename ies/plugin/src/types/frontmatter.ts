import { dump, load } from 'js-yaml';

export type BeType =
  | 'spark'
  | 'insight'
  | 'thread'
  | 'favorite_problem'
  | 'session';

export type EntityStatus = 'captured' | 'exploring' | 'anchored';

export type ResonanceSignal =
  | 'curious'
  | 'excited'
  | 'surprised'
  | 'moved'
  | 'disturbed'
  | 'unclear'
  | 'connected'
  | 'validated';

export type EnergyLevel = 'low' | 'medium' | 'high';

export interface BrainExploreFrontmatter {
  be_type: BeType;
  be_id: string;
  status: EntityStatus;
  resonance?: ResonanceSignal;
  energy?: EnergyLevel;
  concept_ids?: string[];
  thread_id?: string;
  created: string;
  promoted_from?: string;
}

const FRONTMATTER_REGEX = /^---\s*\r?\n([\s\S]*?)\r?\n---/;

const BE_TYPES: readonly BeType[] = [
  'spark',
  'insight',
  'thread',
  'favorite_problem',
  'session',
] as const;

const ENTITY_STATUSES: readonly EntityStatus[] = ['captured', 'exploring', 'anchored'] as const;

const RESONANCE_SIGNALS: readonly ResonanceSignal[] = [
  'curious',
  'excited',
  'surprised',
  'moved',
  'disturbed',
  'unclear',
  'connected',
  'validated',
] as const;

const ENERGY_LEVELS: readonly EnergyLevel[] = ['low', 'medium', 'high'] as const;

const isStringArray = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every((item) => typeof item === 'string');

const isBeType = (value: unknown): value is BeType =>
  typeof value === 'string' && (BE_TYPES as readonly string[]).includes(value);

const isEntityStatus = (value: unknown): value is EntityStatus =>
  typeof value === 'string' && (ENTITY_STATUSES as readonly string[]).includes(value);

const isResonanceSignal = (value: unknown): value is ResonanceSignal =>
  typeof value === 'string' && (RESONANCE_SIGNALS as readonly string[]).includes(value);

const isEnergyLevel = (value: unknown): value is EnergyLevel =>
  typeof value === 'string' && (ENERGY_LEVELS as readonly string[]).includes(value);

const isBrainExploreFrontmatter = (value: unknown): value is BrainExploreFrontmatter => {
  if (!value || typeof value !== 'object') {
    return false;
  }

  const fm = value as Record<string, unknown>;

  if (!isBeType(fm.be_type) || typeof fm.be_id !== 'string' || !isEntityStatus(fm.status)) {
    return false;
  }

  if (typeof fm.created !== 'string') {
    return false;
  }

  if (
    fm.resonance !== undefined &&
    fm.resonance !== null &&
    !isResonanceSignal(fm.resonance)
  ) {
    return false;
  }

  if (fm.energy !== undefined && fm.energy !== null && !isEnergyLevel(fm.energy)) {
    return false;
  }

  if (fm.concept_ids !== undefined && fm.concept_ids !== null && !isStringArray(fm.concept_ids)) {
    return false;
  }

  if (fm.thread_id !== undefined && fm.thread_id !== null && typeof fm.thread_id !== 'string') {
    return false;
  }

  if (
    fm.promoted_from !== undefined &&
    fm.promoted_from !== null &&
    typeof fm.promoted_from !== 'string'
  ) {
    return false;
  }

  return true;
};

export const parseFrontmatter = (content: string): BrainExploreFrontmatter | null => {
  const match = content.match(FRONTMATTER_REGEX);
  if (!match) {
    return null;
  }

  try {
    const data = load(match[1]);
    return isBrainExploreFrontmatter(data) ? data : null;
  } catch (error) {
    console.warn('Failed to parse frontmatter', error);
    return null;
  }
};

export const serializeFrontmatter = (fm: BrainExploreFrontmatter): string => {
  const yamlContent = dump(fm, { lineWidth: 80, noRefs: true }).trimEnd();
  return `---\n${yamlContent}\n---\n`;
};
