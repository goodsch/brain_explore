import {
    appendBlock,
    createDocWithMd,
    getBlockByID,
    getIDsByHPath,
    lsNotebooks,
    moveDocsByID,
    setBlockAttrs,
    fetchSyncPost,
} from '../api';
import { getSettingsSync } from '../stores/settings';
import type {
    CaptureStatus,
    UserStatus,
    IdeaType,
    QuickCaptureMeta,
    SeedBlockMeta,
} from '../types/blocks';
import { SEEDLING_FOLDER_MAP } from '../types/blocks';

/**
 * IES SiYuan Folder Structure (9 top-level folders)
 *
 * Merged architecture combining:
 * - IES Architecture Package (Quick Capture system, Seedlings, Flow Maps, Projects, Archive)
 * - Current ADHD-friendly structure (Insights, Favorite Problems, Sessions)
 *
 * Two Insights folders serve different purposes:
 * - Seedlings/Insights: Raw "aha" moments (not yet validated)
 * - /Insights/: Promoted and validated insights
 */
const STRUCTURE_FOLDERS = [
    // Daily quick captures (Package's 00_Inbox)
    { path: 'Daily', title: 'Daily' },

    // Seedlings - atomic ideas (Package's 01_Seedlings)
    { path: 'Seedlings', title: 'Seedlings' },
    { path: 'Seedlings/Questions', title: 'Seedlings – Questions' },
    { path: 'Seedlings/Observations', title: 'Seedlings – Observations' },
    { path: 'Seedlings/Moments', title: 'Seedlings – Moments' },
    { path: 'Seedlings/Schemas', title: 'Seedlings – Schemas' },
    { path: 'Seedlings/Contradictions', title: 'Seedlings – Contradictions' },
    { path: 'Seedlings/What_Ifs', title: 'Seedlings – What Ifs' },
    { path: 'Seedlings/Insights', title: 'Seedlings – Insights' },

    // Sessions by thinking mode (Package's 02_Shaping)
    { path: 'Sessions', title: 'Sessions' },
    { path: 'Sessions/Learning', title: 'Learning Sessions' },
    { path: 'Sessions/Articulating', title: 'Articulating Sessions' },
    { path: 'Sessions/Planning', title: 'Planning Sessions' },
    { path: 'Sessions/Ideating', title: 'Ideating Sessions' },
    { path: 'Sessions/Reflecting', title: 'Reflecting Sessions' },

    // Flow Maps - visual maps (Package's 03_Flow_Maps)
    { path: 'Flow_Maps', title: 'Flow Maps' },

    // Concepts - canonical concepts (Package's 04_Concepts)
    { path: 'Concepts', title: 'Concepts' },

    // Promoted/validated insights (current ADHD structure)
    { path: 'Insights', title: 'Insights' },

    // ADHD anchor questions (current structure)
    { path: 'Favorite_Problems', title: 'Favorite Problems' },

    // Projects - active work (Package's 05_Projects)
    { path: 'Projects', title: 'Projects' },

    // Archive - retired material (Package's 06_Archive)
    { path: 'Archive', title: 'Archive' },
];

const NOTEBOOK_STORAGE_KEY = 'ies.structureNotebookId';
const BACKEND_URL_KEY = 'ies.backendUrl';
// SiYuan runs in Docker on 192.168.86.60, backend runs on same host
// forwardProxy makes requests FROM the container, so use host IP
const DEFAULT_BACKEND_URL = 'http://192.168.86.60:8081';
const HEALTH_CACHE_TTL_MS = 30_000;

// User-configurable notebook preferences (domain-agnostic)
// Users can customize via localStorage 'ies.preferredNotebooks' as JSON array
const DEFAULT_NOTEBOOK_NAMES = [
    'Personal',
    'Knowledge',
    'Notes',
    'Intelligent Exploration System',
];

function getPreferredNotebookNames(): string[] {
    // First try settings store (primary source of truth)
    try {
        const settings = getSettingsSync();
        if (settings.preferredNotebooks?.length > 0) {
            return settings.preferredNotebooks;
        }
    } catch {
        // Settings store not initialized yet, fall back
    }

    // Fall back to localStorage for backwards compatibility
    if (typeof window === 'undefined' || !window?.localStorage) {
        return DEFAULT_NOTEBOOK_NAMES;
    }
    try {
        const stored = window.localStorage.getItem('ies.preferredNotebooks');
        if (stored) {
            const parsed = JSON.parse(stored);
            if (Array.isArray(parsed) && parsed.length > 0) {
                return parsed;
            }
        }
    } catch {
        // Fall back to defaults on parse error
    }
    return DEFAULT_NOTEBOOK_NAMES;
}

interface NotebookInfo {
    id: string;
    name: string;
}

interface SparkResponse {
    id: string;
    title: string;
    content: string;
    resonance_signal?: string;
    energy_level: string;
    status: string;
    siyuan_block_id?: string;
}

interface InsightResponse {
    id: string;
    title: string;
    original_spark_id: string;
    status: string;
}

export interface BackendHealth {
    ok: boolean;
    status?: string;
    message?: string;
    backendUrl: string;
    checkedAt: number;
}

let cachedNotebook: NotebookInfo | null = null;
let notebooksCache: NotebookInfo[] | null = null;
let lastNotebookFetch = 0;
let cachedHealthStatus: BackendHealth | null = null;
let lastHealthCheck = 0;

function now(): number {
    return Date.now();
}

function getBackendUrl(): string {
    // First try settings store (primary source of truth)
    try {
        const settings = getSettingsSync();
        if (settings.backendUrl) {
            return settings.backendUrl;
        }
    } catch {
        // Settings store not initialized yet, fall back
    }

    // Fall back to localStorage for backwards compatibility
    if (typeof window === 'undefined' || !window?.localStorage) {
        return DEFAULT_BACKEND_URL;
    }
    try {
        return window.localStorage.getItem(BACKEND_URL_KEY) || DEFAULT_BACKEND_URL;
    } catch {
        return DEFAULT_BACKEND_URL;
    }
}

async function callBackendApi<T>(
    method: 'GET' | 'POST',
    endpoint: string,
    body?: Record<string, any>
): Promise<T | null> {
    const backendUrl = getBackendUrl();
    const url = `${backendUrl}${endpoint}`;

    try {
        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url,
            method,
            timeout: 30000,
            contentType: 'application/json',
            headers: [],
            payload: body ? JSON.stringify(body) : undefined,
        });

        // SiYuan forwardProxy returns { code: 0, data: { status: 200, body: "..." } }
        if (response?.code !== 0) {
            console.warn(`[IES] Proxy error (${endpoint}):`, response?.msg);
            return null;
        }

        const proxyData = response?.data;
        if (!proxyData || proxyData.status !== 200) {
            console.warn(`[IES] Backend error (${endpoint}):`, proxyData?.status);
            return null;
        }

        let data = proxyData.body;
        if (typeof data === 'string') {
            try {
                data = JSON.parse(data);
            } catch {
                // Not JSON, use as-is
            }
        }
        return data as T;
    } catch (err) {
        console.warn(`[IES] Backend API call failed (${endpoint}):`, err);
        return null;
    }
}

async function fetchOpenNotebooks(): Promise<NotebookInfo[]> {
    if (notebooksCache && now() - lastNotebookFetch < 30_000) {
        return notebooksCache;
    }

    const response = await lsNotebooks();
    const notebooks = (response?.notebooks || [])
        .filter((notebook: any) => !notebook.closed)
        .map((notebook: any) => ({ id: notebook.id, name: notebook.name }));

    notebooksCache = notebooks;
    lastNotebookFetch = now();
    return notebooks;
}

function readStoredNotebookId(): string | null {
    if (typeof window === 'undefined' || !window?.localStorage) {
        return null;
    }
    try {
        return window.localStorage.getItem(NOTEBOOK_STORAGE_KEY);
    } catch (err) {
        console.warn('[IES] Unable to read stored notebook id:', err);
        return null;
    }
}

function rememberNotebookId(id: string) {
    if (typeof window === 'undefined' || !window?.localStorage) {
        return;
    }
    try {
        window.localStorage.setItem(NOTEBOOK_STORAGE_KEY, id);
    } catch (err) {
        console.warn('[IES] Unable to persist notebook id:', err);
    }
}

async function resolveStructureNotebook(): Promise<NotebookInfo> {
    if (cachedNotebook) {
        return cachedNotebook;
    }

    const notebooks = await fetchOpenNotebooks();
    if (!notebooks.length) {
        throw new Error('No open notebooks available in SiYuan');
    }

    const storedId = readStoredNotebookId();
    if (storedId) {
        const stored = notebooks.find(nb => nb.id === storedId);
        if (stored) {
            cachedNotebook = stored;
            return stored;
        }
    }

    for (const preferred of getPreferredNotebookNames()) {
        const match = notebooks.find(nb => nb.name === preferred);
        if (match) {
            cachedNotebook = match;
            rememberNotebookId(match.id);
            return match;
        }
    }

    cachedNotebook = notebooks[0];
    rememberNotebookId(cachedNotebook.id);
    return cachedNotebook;
}

function sanitizePath(path: string): string {
    return path
        .replace(/^\/+/, '')
        .replace(/\.md$/i, '')
        .trim();
}

async function getDocIdByPath(notebookId: string, relativePath: string): Promise<string | null> {
    const normalized = sanitizePath(relativePath);
    if (!normalized) {
        return null;
    }

    // SiYuan's getIDsByHPath expects paths with leading slash
    const hpath = '/' + normalized;
    const ids = await getIDsByHPath(notebookId, hpath);
    if (!ids || !ids.length) {
        return null;
    }
    return ids[ids.length - 1];
}

async function ensureDocument(notebookId: string, relativePath: string, titleOverride?: string): Promise<string> {
    const normalized = sanitizePath(relativePath);
    if (!normalized) {
        throw new Error('Cannot create document without path');
    }

    const existingId = await getDocIdByPath(notebookId, normalized);
    if (existingId) {
        return existingId;
    }

    const segments = normalized.split('/');
    const docTitle = titleOverride || segments[segments.length - 1] || 'Untitled';
    const markdown = `# ${docTitle}\n\n`;
    const docId = await createDocWithMd(notebookId, normalized, markdown);
    return docId;
}

function pad2(value: number): string {
    return value.toString().padStart(2, '0');
}

function formatDailyTitle(date: Date): string {
    return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`;
}

function isPlainObject(value: unknown): value is Record<string, any> {
    return Object.prototype.toString.call(value) === '[object Object]';
}

function formatYamlValue(value: any, indent: number): string {
    const prefix = '  '.repeat(indent);

    if (value === null || value === undefined) {
        return 'null';
    }

    if (Array.isArray(value)) {
        if (!value.length) {
            return '[]';
        }
        return value
            .map(item => `${prefix}- ${formatYamlValue(item, indent + 1).trimStart()}`)
            .join('\n');
    }

    if (value instanceof Date) {
        return value.toISOString();
    }

    if (isPlainObject(value)) {
        const entries = Object.entries(value);
        if (!entries.length) {
            return '{}';
        }
        return entries
            .map(([key, val]) => {
                const serialized = formatYamlValue(val, indent + 1);
                const needsBlock = Array.isArray(val) || isPlainObject(val);
                if (needsBlock && serialized.includes('\n')) {
                    return `${prefix}${key}:\n${serialized}`;
                }
                return `${prefix}${key}: ${serialized}`;
            })
            .join('\n');
    }

    if (typeof value === 'string') {
        const safeValue = value.replace(/"/g, '\\"');
        return `"${safeValue}"`;
    }

    return String(value);
}

function serializeFrontmatter(data: Record<string, any>): string {
    const entries = Object.entries(data || {});
    if (!entries.length) {
        return '';
    }
    return entries
        .map(([key, value]) => {
            const formatted = formatYamlValue(value, 0);
            if (formatted.includes('\n')) {
                return `${key}:\n${formatted}`;
            }
            return `${key}: ${formatted}`;
        })
        .join('\n');
}

export async function ensureNotebookStructure(): Promise<void> {
    const notebook = await resolveStructureNotebook();
    for (const folder of STRUCTURE_FOLDERS) {
        try {
            await ensureDocument(notebook.id, folder.path, folder.title);
        } catch (err) {
            console.warn(`[IES] Failed to ensure folder ${folder.path}:`, err);
        }
    }
}

export function getDailyLogPath(date: Date): string {
    const target = date instanceof Date ? date : new Date(date);
    const formatted = formatDailyTitle(target);
    return `/Daily/${formatted}.md`;
}

/**
 * Options for creating a spark with backend integration.
 * Combines ADHD metadata with the new block schema fields.
 */
export interface CreateSparkOptions {
    // ADHD metadata (existing)
    resonance_signal?: string;
    energy_level?: string;
    concept_ids?: string[];
    // New block schema fields (from QuickCaptureMeta)
    capture_channel?: string;
    capture_source?: string;
    capture_status?: string;
    capture_time?: string;
    // AI-populated fields
    auto_summary?: string;
    auto_labels?: string[];
    linked_concepts?: string[];
    // Optional book metadata (from Readest captures)
    book_title?: string;
    book_author?: string;
    location?: string;
    highlight_id?: string;
    entities?: string[];
}

/**
 * Create a spark in the backend and add it to today's daily log.
 * Returns the spark ID from the backend.
 *
 * Supports both the original ADHD metadata (resonance_signal, energy_level)
 * and the new block schema fields (capture_channel, capture_source, capture_status).
 */
export async function createSparkWithBackend(
    title: string,
    content: string,
    options: CreateSparkOptions = {}
): Promise<{ sparkId: string; blockId: string } | null> {
    if (!content || !content.trim()) {
        throw new Error('Cannot create an empty spark');
    }

    // First create the SiYuan block to get its ID
    const notebook = await resolveStructureNotebook();
    await ensureNotebookStructure();

    const dateValue = new Date();
    const captureTime = options.capture_time || dateValue.toISOString();
    const relativePath = sanitizePath(getDailyLogPath(dateValue));
    const docId = await ensureDocument(notebook.id, relativePath, formatDailyTitle(dateValue));

    // Create the block in SiYuan first with full schema metadata
    const frontmatter: Record<string, any> = {
        be_type: 'spark',
        status: 'captured',
        created: captureTime,
        // New block schema fields
        quick_capture: true,
        capture_status: options.capture_status || 'raw',
    };

    // Add optional ADHD metadata
    if (options.resonance_signal) {
        frontmatter.resonance = options.resonance_signal;
    }
    if (options.energy_level) {
        frontmatter.energy = options.energy_level;
    }

    // Add optional capture source metadata
    if (options.capture_channel) {
        frontmatter.capture_channel = options.capture_channel;
    }
    if (options.capture_source) {
        frontmatter.capture_source = options.capture_source;
    }

    // Add AI-populated fields if present
    if (options.auto_summary) {
        frontmatter.auto_summary = options.auto_summary;
    }
    if (options.auto_labels?.length) {
        frontmatter.auto_labels = options.auto_labels;
    }
    if (options.linked_concepts?.length) {
        frontmatter.linked_concepts = options.linked_concepts;
    }

    // Add book metadata if present (from Readest captures)
    if (options.book_title) {
        frontmatter.book_title = options.book_title;
    }
    if (options.book_author) {
        frontmatter.book_author = options.book_author;
    }
    if (options.location) {
        frontmatter.location = options.location;
    }
    if (options.highlight_id) {
        frontmatter.highlight_id = options.highlight_id;
    }
    if (options.entities?.length) {
        frontmatter.entities = options.entities;
    }

    const fm = serializeFrontmatter(frontmatter);
    const yamlBlock = fm ? `---\n${fm}\n---\n` : '';
    const entry = `${yamlBlock}## ${title}\n\n${content.trim()}\n\n`;

    // Append to daily log and get the block ID
    const appendResult = await appendBlock('markdown', entry, docId);
    const blockId = appendResult?.[0]?.doOperations?.[0]?.id || '';

    // Now create the spark in the backend with the SiYuan block ID
    const sparkData = {
        title,
        content,
        resonance_signal: options.resonance_signal || null,
        energy_level: options.energy_level || 'medium',
        concept_ids: options.concept_ids || [],
        siyuan_block_id: blockId || null,
    };

    const spark = await callBackendApi<SparkResponse>('POST', '/personal/sparks', sparkData);

    if (spark?.id && blockId) {
        // Update the SiYuan block with the backend spark ID and capture status
        await setBlockAttrs(blockId, {
            'custom-be_id': spark.id,
            'custom-be_type': 'spark',
            'custom-status': 'captured',
            'custom-capture_status': options.capture_status || 'raw',
            ...(options.capture_channel && { 'custom-capture_channel': options.capture_channel }),
            ...(options.capture_source && { 'custom-capture_source': options.capture_source }),
        });
    }

    return spark ? { sparkId: spark.id, blockId } : null;
}

/**
 * Legacy function for backwards compatibility.
 * Creates a daily entry without backend integration.
 */
export async function createDailyEntry(content: string, frontmatter: Record<string, any>): Promise<void> {
    if (!content || !content.trim()) {
        throw new Error('Cannot create an empty daily entry');
    }

    const notebook = await resolveStructureNotebook();
    await ensureNotebookStructure();

    const dateValue = frontmatter?.date ? new Date(frontmatter.date) : new Date();
    const relativePath = sanitizePath(getDailyLogPath(dateValue));
    const docId = await ensureDocument(notebook.id, relativePath, formatDailyTitle(dateValue));

    const fm = serializeFrontmatter(frontmatter || {});
    const yamlBlock = fm ? `---\n${fm}\n---\n` : '';
    const entry = `${yamlBlock}${content.trim()}\n\n`;

    await appendBlock('markdown', entry, docId);
}

/**
 * Promote a spark to an insight in both SiYuan and the backend.
 */
export async function promoteToInsight(sparkId: string, options: {
    backendSparkId?: string;
    insightTitle?: string;
} = {}): Promise<InsightResponse | null> {
    if (!sparkId) {
        throw new Error('Spark id is required');
    }

    const block = await getBlockByID(sparkId);
    if (!block) {
        throw new Error('Unable to locate the requested spark');
    }

    const docBlock = block.type === 'd' ? block : await getBlockByID(block.root_id);
    if (!docBlock) {
        throw new Error('Unable to resolve the parent document');
    }

    // Get the backend spark ID from block attributes if not provided
    let beSparkId = options.backendSparkId;
    if (!beSparkId) {
        const attrs = block['ial'] || {};
        beSparkId = attrs['custom-be_id'];
    }

    // Promote in backend first (if we have a backend spark ID)
    let insight: InsightResponse | null = null;
    if (beSparkId) {
        insight = await callBackendApi<InsightResponse>(
            'POST',
            `/personal/sparks/${beSparkId}/promote`,
            { insight_title: options.insightTitle }
        );
    }

    // Move the SiYuan document to Insights folder
    const notebookId = docBlock.box;
    await ensureDocument(notebookId, 'Insights', 'Insights');
    const insightsId = await getDocIdByPath(notebookId, 'Insights');
    if (!insightsId) {
        throw new Error('Insights folder is missing');
    }

    await moveDocsByID([docBlock.id], insightsId);

    // Update SiYuan block attributes
    const attrs: Record<string, string> = {
        'custom-status': 'anchored',
        'custom-be_type': 'insight',
        'custom-updated': new Date().toISOString(),
    };
    if (insight?.id) {
        attrs['custom-be_id'] = insight.id;
    }
    await setBlockAttrs(docBlock.id, attrs);

    return insight;
}

/**
 * Get personal graph statistics from the backend.
 */
export async function getPersonalStats(): Promise<{
    total_sparks: number;
    total_insights: number;
    sparks_by_status: Record<string, number>;
} | null> {
    return callBackendApi('GET', '/personal/stats');
}

/**
 * Record a visit to a spark (updates visit count for recency-based navigation).
 */
export async function visitSpark(sparkId: string): Promise<boolean> {
    const result = await callBackendApi<{ success: boolean }>('POST', `/personal/sparks/${sparkId}/visit`);
    return result?.success || false;
}

// Thinking mode to folder path mapping
const MODE_FOLDER_MAP: Record<string, string> = {
    learning: 'Sessions/Learning',
    articulating: 'Sessions/Articulating',
    planning: 'Sessions/Planning',
    ideating: 'Sessions/Ideating',
    reflecting: 'Sessions/Reflecting',
};

interface QuestionResponseEntry {
    question: string;
    questionClass: string;
    userResponse: string;
    followUpQuestion?: string;
    timestamp: number;
}

interface SessionDocumentOptions {
    sessionId: string;
    mode: string;
    topic: string;
    templateId?: string;
    templateName?: string;
    sectionResponses?: Record<string, string>;
    transcript: Array<{ role: string; content: string }>;
    entitiesExtracted?: number;
    graphMappingExecuted?: boolean;
    questionClassesUsed?: string[];
    questionResponseHistory?: QuestionResponseEntry[];
}

/**
 * Create a session document in SiYuan for a completed ForgeMode session.
 * Stores the full session with metadata, section responses, and transcript.
 */
export async function createSessionDocument(options: SessionDocumentOptions): Promise<string | null> {
    const {
        sessionId,
        mode,
        topic,
        templateId,
        templateName,
        sectionResponses,
        transcript,
        entitiesExtracted,
        graphMappingExecuted,
        questionClassesUsed,
        questionResponseHistory,
    } = options;

    const notebook = await resolveStructureNotebook();
    await ensureNotebookStructure();

    // Determine folder based on mode
    const folderPath = MODE_FOLDER_MAP[mode] || 'Sessions';

    // Create document path with timestamp
    const dateValue = new Date();
    const dateStr = formatDailyTitle(dateValue);
    const timeStr = `${pad2(dateValue.getHours())}${pad2(dateValue.getMinutes())}`;
    const safeTitle = topic.substring(0, 50).replace(/[/\\?%*:|"<>]/g, '-').trim();
    const docPath = `${folderPath}/${dateStr}-${timeStr}-${safeTitle}`;

    // Build frontmatter
    const frontmatter: Record<string, any> = {
        be_type: 'session',
        be_id: sessionId,
        mode: mode,
        topic: topic,
        status: 'completed',
        created: dateValue.toISOString(),
    };
    if (templateId) {
        frontmatter.template_id = templateId;
        frontmatter.template_name = templateName || templateId;
    }
    if (entitiesExtracted !== undefined) {
        frontmatter.entities_extracted = entitiesExtracted;
    }
    if (graphMappingExecuted !== undefined) {
        frontmatter.graph_mapping_executed = graphMappingExecuted;
    }
    if (questionClassesUsed && questionClassesUsed.length > 0) {
        frontmatter.question_classes_used = questionClassesUsed;
    }
    if (questionResponseHistory && questionResponseHistory.length > 0) {
        frontmatter.thinking_dialogues_count = questionResponseHistory.length;
    }

    const fm = serializeFrontmatter(frontmatter);

    // Build document content
    let content = `---\n${fm}\n---\n\n`;
    content += `# ${topic}\n\n`;
    content += `**Mode:** ${mode.charAt(0).toUpperCase() + mode.slice(1)}`;
    if (templateName) {
        content += ` (${templateName})`;
    }
    content += `\n**Date:** ${dateStr}\n\n`;

    // Add section responses if template-driven
    if (sectionResponses && Object.keys(sectionResponses).length > 0) {
        content += `## Section Responses\n\n`;
        for (const [sectionId, response] of Object.entries(sectionResponses)) {
            const formattedId = sectionId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            content += `### ${formattedId}\n\n${response}\n\n`;
        }
    }

    // Add thinking dialogues (question-response exchanges)
    if (questionResponseHistory && questionResponseHistory.length > 0) {
        const classLabels: Record<string, string> = {
            schema_probe: '🏗️ Structure',
            boundary: '🔲 Boundary',
            dimensional: '📐 Dimensional',
            causal: '⚡ Causal',
            counterfactual: '🔮 What-If',
            anchor: '⚓ Anchor',
            perspective_shift: '👁️ Perspective',
            meta_cognitive: '🧠 Meta',
            reflective_synthesis: '🔗 Synthesis',
        };
        content += `## Thinking Dialogues\n\n`;
        content += `*${questionResponseHistory.length} thinking partner exchange${questionResponseHistory.length > 1 ? 's' : ''} during this session:*\n\n`;

        for (let i = 0; i < questionResponseHistory.length; i++) {
            const qr = questionResponseHistory[i];
            const classLabel = classLabels[qr.questionClass] || qr.questionClass.replace(/_/g, ' ');

            if (qr.userResponse === '[skipped]') {
                content += `### Dialogue ${i + 1} (${classLabel}) — *Skipped*\n\n`;
                content += `> ${qr.question}\n\n`;
            } else {
                content += `### Dialogue ${i + 1} (${classLabel})\n\n`;
                content += `> ${qr.question}\n\n`;
                content += `**Response:** ${qr.userResponse}\n\n`;
                if (qr.followUpQuestion) {
                    content += `*Follow-up generated:* ${qr.followUpQuestion}\n\n`;
                }
            }
            content += `---\n\n`;
        }
    }

    // Add conversation transcript
    content += `## Conversation\n\n`;
    for (const msg of transcript) {
        const speaker = msg.role === 'user' ? '**You:**' : '**AI:**';
        content += `${speaker}\n\n${msg.content}\n\n---\n\n`;
    }

    // Extraction summary
    const hasResults = entitiesExtracted !== undefined ||
        graphMappingExecuted ||
        (questionClassesUsed && questionClassesUsed.length > 0) ||
        (questionResponseHistory && questionResponseHistory.length > 0);

    if (hasResults) {
        content += `## Session Results\n\n`;
        if (entitiesExtracted !== undefined) {
            content += `- Entities extracted: ${entitiesExtracted}\n`;
        }
        if (graphMappingExecuted) {
            content += `- Graph mapping executed: ✓\n`;
        }
        if (questionResponseHistory && questionResponseHistory.length > 0) {
            const answered = questionResponseHistory.filter(qr => qr.userResponse !== '[skipped]').length;
            const skipped = questionResponseHistory.length - answered;
            content += `- Thinking dialogues: ${answered} answered`;
            if (skipped > 0) {
                content += `, ${skipped} skipped`;
            }
            content += `\n`;
        }
        if (questionClassesUsed && questionClassesUsed.length > 0) {
            // Format question classes with human-readable labels
            const classLabels: Record<string, string> = {
                schema_probe: 'Structure',
                boundary: 'Boundary',
                dimensional: 'Dimensional',
                causal: 'Causal',
                counterfactual: 'What-If',
                anchor: 'Anchor',
                perspective_shift: 'Perspective',
                meta_cognitive: 'Meta',
                reflective_synthesis: 'Synthesis',
            };
            const formattedClasses = questionClassesUsed
                .map(qc => classLabels[qc] || qc.replace(/_/g, ' '))
                .join(', ');
            content += `- Question types used: ${formattedClasses}\n`;
        }
    }

    try {
        const docId = await createDocWithMd(notebook.id, docPath, content);

        // Set block attributes for backend linking
        await setBlockAttrs(docId, {
            'custom-be_type': 'session',
            'custom-be_id': sessionId,
            'custom-mode': mode,
            'custom-status': 'completed',
        });

        return docId;
    } catch (err) {
        console.error('[IES] Failed to create session document:', err);
        return null;
    }
}

/**
 * Set user's preferred notebook names for structure creation.
 * Enables domain-agnostic usage (user can set to match their domain).
 */
export function setPreferredNotebooks(names: string[]): void {
    if (typeof window === 'undefined' || !window?.localStorage) {
        return;
    }
    try {
        if (Array.isArray(names) && names.length > 0) {
            window.localStorage.setItem('ies.preferredNotebooks', JSON.stringify(names));
            // Clear cached notebook to force re-resolution
            cachedNotebook = null;
        }
    } catch (err) {
        console.warn('[IES] Unable to save preferred notebooks:', err);
    }
}

/**
 * Get the current list of preferred notebook names.
 */
export function getPreferredNotebooks(): string[] {
    return getPreferredNotebookNames();
}

/**
 * Set the backend URL for API calls.
 */
export function setBackendUrl(url: string): void {
    if (typeof window === 'undefined' || !window?.localStorage) {
        return;
    }
    try {
        window.localStorage.setItem(BACKEND_URL_KEY, url);
    } catch (err) {
        console.warn('[IES] Unable to save backend URL:', err);
    }
}

/**
 * Get the current backend URL.
 */
export function getConfiguredBackendUrl(): string {
    return getBackendUrl();
}

export async function checkBackendHealth(options: { force?: boolean } = {}): Promise<BackendHealth> {
    const backendUrl = getBackendUrl();
    const timestamp = now();

    if (
        !options.force &&
        cachedHealthStatus &&
        timestamp - lastHealthCheck < HEALTH_CACHE_TTL_MS &&
        cachedHealthStatus.backendUrl === backendUrl
    ) {
        return cachedHealthStatus;
    }

    const setCache = (health: BackendHealth): BackendHealth => {
        cachedHealthStatus = health;
        lastHealthCheck = timestamp;
        return health;
    };

    const response = await callBackendApi<any>('GET', '/health');
    if (!response) {
        return setCache({
            ok: false,
            status: 'unreachable',
            message: 'No response from backend',
            backendUrl,
            checkedAt: timestamp,
        });
    }

    const ok = Boolean(response?.status === 'ok' || response?.status === 'healthy' || response?.ok === true);
    const message = typeof response === 'string' ? response : response?.message;

    return setCache({
        ok,
        status: typeof response === 'object' ? response?.status : undefined,
        message: ok ? message || 'Backend reachable' : message || 'Backend reported unhealthy status',
        backendUrl,
        checkedAt: timestamp,
    });
}

// === Block Metadata Helpers ===

/**
 * Sets block metadata in both YAML frontmatter format and SiYuan attributes.
 * Returns YAML string for insertion at top of block content.
 * Sets custom-* attributes for SQL querying.
 */
export async function setBlockMeta(
    blockId: string,
    meta: Record<string, any>
): Promise<string> {
    if (!blockId) {
        throw new Error('setBlockMeta requires a blockId');
    }

    // Build YAML frontmatter string
    const yaml = serializeFrontmatter(meta);
    const attrs: Record<string, string> = {};

    // Mirror all meta keys into SiYuan custom-* attrs for querying
    for (const [key, value] of Object.entries(meta)) {
        if (value === undefined) continue;
        const attrKey = `custom-${key}`;
        if (value === null) {
            attrs[attrKey] = '';
            continue;
        }
        if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
            attrs[attrKey] = String(value);
            continue;
        }
        // Arrays / objects → JSON string for lossless round-trip
        attrs[attrKey] = JSON.stringify(value);
    }

    await setBlockAttrs(blockId, attrs);
    return yaml;
}

/**
 * Updates capture_status (AI processing state) and sets last_touched_at timestamp.
 */
export async function updateCaptureStatus(
    blockId: string,
    newStatus: CaptureStatus
): Promise<void> {
    const now = new Date().toISOString();
    await setBlockAttrs(blockId, {
        'custom-capture_status': newStatus,
        'custom-last_touched_at': now,
    });
}

/**
 * Updates user engagement status and increments exploration visits.
 */
export async function updateUserStatus(
    blockId: string,
    newStatus: UserStatus,
    currentVisits: number = 0
): Promise<void> {
    const now = new Date().toISOString();
    await setBlockAttrs(blockId, {
        'custom-status': newStatus,
        'custom-exploration_visits': String(currentVisits + 1),
        'custom-last_touched_at': now,
    });
}

/**
 * Creates a Quick Capture block in the Daily folder with proper metadata.
 * Returns the block ID.
 */
export async function createQuickCapture(
    content: string,
    options: {
        capture_channel?: QuickCaptureMeta['capture_channel'];
        capture_source?: QuickCaptureMeta['capture_source'];
        resonance_signal?: string;
        energy_level?: string;
        book_title?: string;
        book_author?: string;
        location?: string;
    } = {}
): Promise<string | null> {
    if (!content || !content.trim()) {
        throw new Error('Cannot create an empty quick capture');
    }

    const notebook = await resolveStructureNotebook();
    await ensureNotebookStructure();

    const dateValue = new Date();
    const relativePath = sanitizePath(getDailyLogPath(dateValue));
    const docId = await ensureDocument(notebook.id, relativePath, formatDailyTitle(dateValue));

    // Build Quick Capture metadata
    const meta: Partial<QuickCaptureMeta> = {
        quick_capture: true,
        capture_channel: options.capture_channel || 'other',
        capture_source: options.capture_source || 'manual',
        capture_time: dateValue.toISOString(),
        capture_status: 'raw',
        status: 'captured',
    };

    if (options.resonance_signal) {
        meta.resonance_signal = options.resonance_signal as any;
    }
    if (options.energy_level) {
        meta.energy_level = options.energy_level as any;
    }
    if (options.book_title) {
        meta.book_title = options.book_title;
    }
    if (options.book_author) {
        meta.book_author = options.book_author;
    }
    if (options.location) {
        meta.location = options.location;
    }

    const fm = serializeFrontmatter(meta);
    const yamlBlock = fm ? `---\n${fm}\n---\n` : '';
    const entry = `${yamlBlock}${content.trim()}\n\n`;

    // Append to daily log and get the block ID
    const appendResult = await appendBlock('markdown', entry, docId);
    const blockId = appendResult?.[0]?.doOperations?.[0]?.id || '';

    if (blockId) {
        // Set SiYuan attributes for SQL querying
        const attrs: Record<string, string> = {
            'custom-quick_capture': 'true',
            'custom-capture_status': 'raw',
            'custom-status': 'captured',
            'custom-capture_time': meta.capture_time!,
            'custom-capture_channel': meta.capture_channel!,
            'custom-capture_source': meta.capture_source!,
        };
        if (options.resonance_signal) {
            attrs['custom-resonance_signal'] = options.resonance_signal;
        }
        if (options.energy_level) {
            attrs['custom-energy_level'] = options.energy_level;
        }
        await setBlockAttrs(blockId, attrs);
    }

    return blockId || null;
}

/**
 * Creates a Seedling from a processed Quick Capture.
 * Moves content to appropriate Seedlings subfolder based on idea_type.
 */
export async function createSeedling(
    title: string,
    content: string,
    ideaType: IdeaType,
    options: {
        sourceBlockId?: string;
        domain?: string;
        clarity?: SeedBlockMeta['clarity'];
        confidence?: SeedBlockMeta['confidence'];
        resonance_signal?: string;
        energy_level?: string;
        related_concepts?: string[];
        tags?: string[];
    } = {}
): Promise<string | null> {
    if (!content || !content.trim()) {
        throw new Error('Cannot create an empty seedling');
    }

    const notebook = await resolveStructureNotebook();
    await ensureNotebookStructure();

    // Determine folder based on idea type
    const folderPath = SEEDLING_FOLDER_MAP[ideaType] || 'Seedlings';

    // Create document path with timestamp
    const dateValue = new Date();
    const dateStr = formatDailyTitle(dateValue);
    const timeStr = `${pad2(dateValue.getHours())}${pad2(dateValue.getMinutes())}`;
    const safeTitle = title.substring(0, 50).replace(/[/\\?%*:|"<>]/g, '-').trim();
    const docPath = `${folderPath}/${dateStr}-${timeStr}-${safeTitle}`;

    // Build Seedling metadata
    const meta: Partial<SeedBlockMeta> = {
        block_type: 'seed',
        idea_type: ideaType,
        status: 'captured',
        created_at: dateValue.toISOString(),
        last_touched_at: dateValue.toISOString(),
    };

    if (options.sourceBlockId) {
        meta.source_capture_id = options.sourceBlockId;
    }
    if (options.domain) {
        meta.domain = options.domain;
    }
    if (options.clarity) {
        meta.clarity = options.clarity;
    }
    if (options.confidence) {
        meta.confidence = options.confidence;
    }
    if (options.resonance_signal) {
        meta.resonance_signal = options.resonance_signal as any;
    }
    if (options.energy_level) {
        meta.energy_level = options.energy_level as any;
    }
    if (options.related_concepts?.length) {
        meta.related_concepts = options.related_concepts;
    }
    if (options.tags?.length) {
        meta.tags = options.tags;
    }

    const fm = serializeFrontmatter(meta);

    // Build document content
    let docContent = `---\n${fm}\n---\n\n`;
    docContent += `# ${title}\n\n`;
    docContent += content.trim();
    docContent += '\n';

    try {
        const docId = await createDocWithMd(notebook.id, docPath, docContent);

        // Set SiYuan attributes for SQL querying
        const attrs: Record<string, string> = {
            'custom-block_type': 'seed',
            'custom-idea_type': ideaType,
            'custom-status': 'captured',
            'custom-created_at': meta.created_at!,
        };
        if (options.sourceBlockId) {
            attrs['custom-source_capture_id'] = options.sourceBlockId;
        }
        if (options.domain) {
            attrs['custom-domain'] = options.domain;
        }
        if (options.resonance_signal) {
            attrs['custom-resonance_signal'] = options.resonance_signal;
        }
        if (options.energy_level) {
            attrs['custom-energy_level'] = options.energy_level;
        }
        await setBlockAttrs(docId, attrs);

        // If this came from a Quick Capture, update its status
        if (options.sourceBlockId) {
            await updateCaptureStatus(options.sourceBlockId, 'processed');
        }

        return docId;
    } catch (err) {
        console.error('[IES] Failed to create seedling:', err);
        return null;
    }
}

/**
 * Promotes a seedling from Seedlings/Insights to /Insights/ folder.
 * Updates status to 'anchored'.
 */
export async function promoteSeedlingToInsight(
    seedlingBlockId: string,
    options: {
        backendSparkId?: string;
        insightTitle?: string;
    } = {}
): Promise<string | null> {
    if (!seedlingBlockId) {
        throw new Error('Seedling block ID is required');
    }

    const block = await getBlockByID(seedlingBlockId);
    if (!block) {
        throw new Error('Unable to locate the seedling');
    }

    // Get the document block (seedlings are documents)
    const docBlock = block.type === 'd' ? block : await getBlockByID(block.root_id);
    if (!docBlock) {
        throw new Error('Unable to resolve the parent document');
    }

    const notebookId = docBlock.box;

    // Ensure Insights folder exists
    await ensureDocument(notebookId, 'Insights', 'Insights');
    const insightsId = await getDocIdByPath(notebookId, 'Insights');
    if (!insightsId) {
        throw new Error('Insights folder is missing');
    }

    // Move the document to Insights folder
    await moveDocsByID([docBlock.id], insightsId);

    // Update SiYuan block attributes
    const now = new Date().toISOString();
    const attrs: Record<string, string> = {
        'custom-status': 'anchored',
        'custom-last_touched_at': now,
    };

    // If we have a backend spark ID, sync with backend
    let beSparkId = options.backendSparkId;
    if (!beSparkId) {
        const blockAttrs = block['ial'] || {};
        beSparkId = blockAttrs['custom-be_id'];
    }

    if (beSparkId) {
        // Promote in backend
        const insight = await callBackendApi<InsightResponse>(
            'POST',
            `/personal/sparks/${beSparkId}/promote`,
            { insight_title: options.insightTitle }
        );
        if (insight?.id) {
            attrs['custom-be_id'] = insight.id;
            attrs['custom-be_type'] = 'insight';
        }
    }

    await setBlockAttrs(docBlock.id, attrs);

    return docBlock.id;
}
