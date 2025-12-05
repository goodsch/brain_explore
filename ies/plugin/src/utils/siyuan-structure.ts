/**
 * SiYuan Structure Utilities
 *
 * Utilities for managing the IES notebook structure, document creation,
 * and backend integration within SiYuan.
 *
 * Key Features:
 * - Domain-agnostic notebook configuration (user-configurable preferences)
 * - Merged 9-folder structure (Daily, Seedlings, Sessions, Flow_Maps, Concepts, Insights, Favorite_Problems, Projects, Archive)
 * - Backend integration via forwardProxy (Personal Graph API, Journey API)
 * - Session document creation with ShapingBlockMeta support (block_type, session_id, thinking_mode, phase)
 * - Block attributes syncing for backend linking (be_id, be_type, status)
 * - Archive functionality for old captures
 * - Project linking for capture-to-project workflow
 */

import { fetchSyncPost, setBlockAttrs, getBlockByID, createDocWithMd, appendBlock } from 'siyuan';
import type { Block, Notebook } from 'siyuan';
import { lsNotebooks, moveDocsByID } from '../api';
import type { ShapingBlockMeta, DecisionBlockMeta } from '../types/blocks';
import { getSettingsSync } from '../stores/settings';

// === Configuration ===

/**
 * Default notebook names (domain-agnostic).
 * Users can customize via setPreferredNotebooks() or settings store.
 */
const DEFAULT_NOTEBOOK_NAMES = [
    'Personal',
    'Knowledge',
    'Notes',
    'Intelligent Exploration System',
];

/**
 * Merged 9-folder structure combining IES Architecture Package with ADHD-friendly features.
 *
 * Folder Structure:
 * - /Daily/: Quick captures (Package's 00_Inbox)
 * - /Seedlings/: Atomic ideas with 7 subcategories (Questions, Observations, Moments, Schemas, Contradictions, What_Ifs, Insights)
 * - /Sessions/: Mode-specific thinking (Learning, Articulating, Planning, Ideating, Reflecting)
 * - /Flow_Maps/: Visual maps (Package's 03_Flow_Maps)
 * - /Concepts/: Canonical concepts (Package's 04_Concepts)
 * - /Insights/: Promoted/validated insights (current)
 * - /Favorite_Problems/: ADHD anchor questions (current)
 * - /Projects/: Active work (Package's 05_Projects)
 * - /Archive/: Retired material (Package's 06_Archive)
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

/**
 * Thinking mode to folder path mapping for session documents.
 */
const MODE_FOLDER_MAP: Record<string, string> = {
    learning: 'Sessions/Learning',
    articulating: 'Sessions/Articulating',
    planning: 'Sessions/Planning',
    ideating: 'Sessions/Ideating',
    reflecting: 'Sessions/Reflecting',
};

// === Backend Configuration ===

/**
 * Default backend URL (host IP, since SiYuan runs in Docker container).
 */
const DEFAULT_BACKEND_URL = 'http://192.168.86.60:8081';

/**
 * Get the configured backend URL.
 * Checks settings store first, falls back to localStorage, then default.
 */
export function getBackendUrl(): string {
    // Primary: Settings store (workspace-persisted)
    const settings = getSettingsSync();
    if (settings?.backendUrl) {
        return settings.backendUrl;
    }

    // Fallback: localStorage (backward compatibility)
    if (typeof window !== 'undefined' && window?.localStorage) {
        try {
            const stored = window.localStorage.getItem('ies.backendUrl');
            if (stored) {
                return stored;
            }
        } catch (err) {
            console.warn('[IES] Unable to read backend URL from localStorage:', err);
        }
    }

    return DEFAULT_BACKEND_URL;
}

/**
 * Set the backend URL for API calls.
 */
export function setBackendUrl(url: string): void {
    if (typeof window === 'undefined' || !window?.localStorage) {
        return;
    }
    try {
        window.localStorage.setItem('ies.backendUrl', url);
    } catch (err) {
        console.warn('[IES] Unable to save backend URL:', err);
    }
}

// Health check caching
let cachedHealthStatus: BackendHealth | null = null;
let cachedHealthTimestamp = 0;
const HEALTH_CACHE_TTL_MS = 30000; // 30 seconds

interface BackendHealth {
    status: string;
    timestamp?: string;
}

/**
 * Check if backend is reachable.
 * Uses cached result if within TTL (30 seconds) to reduce API overhead.
 */
export async function checkBackendHealth(force = false): Promise<BackendHealth | null> {
    const now = Date.now();
    if (!force && cachedHealthStatus && (now - cachedHealthTimestamp < HEALTH_CACHE_TTL_MS)) {
        return cachedHealthStatus;
    }

    try {
        const health = await callBackendApi<BackendHealth>('GET', '/health');
        cachedHealthStatus = health;
        cachedHealthTimestamp = now;
        return health;
    } catch (err) {
        cachedHealthStatus = null;
        cachedHealthTimestamp = now;
        return null;
    }
}

// === Notebook Resolution ===

let cachedNotebook: any | null = null;

/**
 * Get user's preferred notebook names.
 * Checks settings store first, falls back to localStorage, then defaults.
 */
export function getPreferredNotebookNames(): string[] {
    // Primary: Settings store (workspace-persisted)
    const settings = getSettingsSync();
    if (settings?.preferredNotebooks && Array.isArray(settings.preferredNotebooks) && settings.preferredNotebooks.length > 0) {
        return settings.preferredNotebooks;
    }

    // Fallback: localStorage (backward compatibility)
    if (typeof window !== 'undefined' && window?.localStorage) {
        try {
            const stored = window.localStorage.getItem('ies.preferredNotebooks');
            if (stored) {
                const parsed = JSON.parse(stored);
                if (Array.isArray(parsed) && parsed.length > 0) {
                    return parsed;
                }
            }
        } catch (err) {
            console.warn('[IES] Unable to read preferred notebooks from localStorage:', err);
        }
    }

    return DEFAULT_NOTEBOOK_NAMES;
}

/**
 * Resolve the IES notebook by checking user preferences against open notebooks.
 * Returns the first matching open notebook, or the first available if no match.
 */
export async function resolveStructureNotebook(): Promise<any> {
    if (cachedNotebook) return cachedNotebook;

    const result = await lsNotebooks();
    const notebooks = result?.notebooks || [];

    if (notebooks.length === 0) {
        throw new Error('No notebooks found in SiYuan');
    }

    const openNotebooks = notebooks.filter((nb: any) => !nb.closed);
    if (openNotebooks.length === 0) {
        throw new Error('No open notebooks found');
    }

    // Get preferred names (supports dynamic configuration)
    const preferredNames = getPreferredNotebookNames();

    // Find first matching preferred notebook
    for (const name of preferredNames) {
        const match = openNotebooks.find((nb: any) => nb.name === name);
        if (match) {
            cachedNotebook = match;
            return match;
        }
    }

    // Fallback: Use first available open notebook
    cachedNotebook = openNotebooks[0];
    return openNotebooks[0];
}

/**
 * Ensure the IES folder structure exists in the resolved notebook.
 * Creates all folders defined in STRUCTURE_FOLDERS if they don't exist.
 */
export async function ensureNotebookStructure(): Promise<void> {
    const notebook = await resolveStructureNotebook();
    for (const folder of STRUCTURE_FOLDERS) {
        await ensureDocument(notebook.id, folder.path, folder.title);
    }
}

// === Document Management ===

/**
 * Get document ID by relative path within a notebook using SQL.
 */
export async function getDocIdByPath(notebookId: string, path: string): Promise<string | null> {
    // Use SQL to find document by path
    const hpath = '/' + path.replace(/^\/+/, '');
    const query = `SELECT id FROM blocks WHERE box = '${notebookId}' AND hpath = '${hpath}' AND type = 'd' LIMIT 1`;

    try {
        const result = await fetchSyncPost('/api/query/sql', { stmt: query });
        if (result.code === 0 && result.data && result.data.length > 0) {
            return result.data[0].id;
        }
    } catch (err) {
        console.error('[IES] Error querying document by path:', err);
    }

    return null;
}

/**
 * Ensure a document exists at the given path, creating if necessary.
 */
export async function ensureDocument(
    notebookId: string,
    path: string,
    title: string
): Promise<string> {
    const existingId = await getDocIdByPath(notebookId, path);
    if (existingId) {
        return existingId;
    }

    // Create the document
    const fullPath = `/${path}`;
    const docId = await createDocWithMd(notebookId, fullPath, `# ${title}\n\n`);
    return docId;
}

// === Backend Integration (via SiYuan forwardProxy) ===

/**
 * Generic function to call backend APIs via SiYuan's forwardProxy.
 * Handles GET, POST, PUT, DELETE methods.
 */
export async function callBackendApi<T = any>(
    method: string,
    endpoint: string,
    body?: any
): Promise<T | null> {
    const backendUrl = getBackendUrl();
    const url = `${backendUrl}${endpoint}`;

    const payload: any = {
        url: url,
        method: method.toUpperCase(),
        timeout: 30000,
        contentType: 'application/json',
        headers: [],
    };

    if (body) {
        payload.payload = body;
    }

    const response = await fetchSyncPost('/api/network/forwardProxy', payload);

    if (response.code !== 0) {
        console.error('[IES] Proxy error:', response.msg);
        return null;
    }

    const proxyData = response.data;
    if (!proxyData) {
        console.error('[IES] Proxy returned empty data');
        return null;
    }

    if (proxyData.status < 200 || proxyData.status >= 300) {
        console.error('[IES] Backend error:', proxyData.status, proxyData.body);
        return null;
    }

    const result = typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    return result as T;
}

// === Date/Path Utilities ===

function pad2(n: number): string {
    return String(n).padStart(2, '0');
}

function getDailyLogPath(date: Date): string {
    return `Daily/${date.getFullYear()}/${pad2(date.getMonth() + 1)}`;
}

function formatDailyTitle(date: Date): string {
    return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`;
}

function sanitizePath(path: string): string {
    return path.replace(/[/\\?%*:|"<>]/g, '-');
}

/**
 * Serialize frontmatter object to YAML format.
 * Properly handles arrays, objects, dates, nested structures.
 */
function serializeFrontmatter(obj: Record<string, any>): string {
    const lines: string[] = [];

    for (const [key, value] of Object.entries(obj)) {
        if (value === null || value === undefined) {
            continue; // Skip null/undefined values
        }

        if (Array.isArray(value)) {
            if (value.length === 0) {
                lines.push(`${key}: []`);
            } else {
                lines.push(`${key}:`);
                for (const item of value) {
                    if (typeof item === 'object' && item !== null && !Array.isArray(item)) {
                        // Nested object in array
                        lines.push(`  - ${JSON.stringify(item)}`);
                    } else {
                        lines.push(`  - ${item}`);
                    }
                }
            }
        } else if (typeof value === 'object' && !(value instanceof Date)) {
            // Nested object (not Date)
            lines.push(`${key}:`);
            for (const [subKey, subValue] of Object.entries(value)) {
                if (subValue !== null && subValue !== undefined) {
                    lines.push(`  ${subKey}: ${subValue}`);
                }
            }
        } else if (value instanceof Date) {
            lines.push(`${key}: ${value.toISOString()}`);
        } else if (typeof value === 'string' && value.includes('\n')) {
            // Multi-line string (block scalar)
            lines.push(`${key}: |`);
            const subLines = value.split('\n');
            for (const subLine of subLines) {
                lines.push(`  ${subLine}`);
            }
        } else {
            lines.push(`${key}: ${value}`);
        }
    }

    return lines.join('\n');
}

// === Personal Graph Integration ===

interface SparkOptions {
    content: string;
    title?: string;
    resonance_signal?: string;
    energy_level?: string;
    source_entity?: string;
    capture_status?: string;
    capture_channel?: string;
    capture_source?: string;
}

interface SparkResponse {
    id: string;
    user_id: string;
    title: string;
    content: string;
    created_at: string;
}

interface InsightResponse {
    id: string;
    user_id: string;
    title: string;
    content: string;
    created_at: string;
}

interface ProjectInfo {
    id: string;
    title: string;
    created_at: string;
    status?: string;
}

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
    thinking_mode?: string; // Phase 4: Add thinking_mode for ShapingBlockMeta
    phase?: string; // Phase 4: Add phase tracking for ShapingBlockMeta
}

/**
 * Create a spark in the backend and a corresponding block in SiYuan Daily log.
 * Returns spark ID from backend and block ID from SiYuan for bidirectional linking.
 */
export async function createSparkWithBackend(options: SparkOptions): Promise<{ sparkId: string; blockId: string } | null> {
    if (!options.content || !options.content.trim()) {
        throw new Error('Content is required to create a spark');
    }

    // Create spark in backend
    const spark = await callBackendApi<SparkResponse>('POST', '/personal/sparks', {
        content: options.content,
        title: options.title,
        resonance_signal: options.resonance_signal,
        energy_level: options.energy_level,
        source_entity: options.source_entity,
    });

    if (!spark || !spark.id) {
        console.error('[IES] Failed to create spark in backend');
        return null;
    }

    // Create a daily log entry in SiYuan
    const notebook = await resolveStructureNotebook();
    await ensureNotebookStructure();

    const dateValue = new Date();
    const relativePath = sanitizePath(getDailyLogPath(dateValue));
    const docId = await ensureDocument(notebook.id, relativePath, formatDailyTitle(dateValue));

    // Build frontmatter with capture metadata
    const frontmatter: Record<string, any> = {
        be_type: 'spark',
        be_id: spark.id,
        status: 'captured',
        created: spark.created_at,
    };
    if (options.resonance_signal) {
        frontmatter.resonance_signal = options.resonance_signal;
    }
    if (options.energy_level) {
        frontmatter.energy_level = options.energy_level;
    }
    if (options.capture_status) {
        frontmatter.capture_status = options.capture_status;
    }
    if (options.capture_channel) {
        frontmatter.capture_channel = options.capture_channel;
    }
    if (options.capture_source) {
        frontmatter.capture_source = options.capture_source;
    }

    const fm = serializeFrontmatter(frontmatter);
    const yamlBlock = fm ? `---\n${fm}\n---\n` : '';
    const title = options.title || 'Spark';
    const entry = `${yamlBlock}## ${title}\n\n${options.content.trim()}\n\n`;

    const blockId = await appendBlock('markdown', entry, docId);

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
 * Archive a capture by moving it to the Archive folder.
 * Adds archived_at timestamp and archive_reason to metadata.
 */
export async function archiveCapture(
    blockId: string,
    archiveReason: string = 'User archived'
): Promise<void> {
    if (!blockId) {
        throw new Error('Block ID is required');
    }

    const block = await getBlockByID(blockId);
    if (!block) {
        throw new Error('Unable to locate the block');
    }

    // Get the document block
    const docBlock = block.type === 'd' ? block : await getBlockByID(block.root_id);
    if (!docBlock) {
        throw new Error('Unable to resolve the parent document');
    }

    const notebookId = docBlock.box;
    await ensureNotebookStructure();

    // Ensure Archive folder exists
    await ensureDocument(notebookId, 'Archive', 'Archive');
    const archiveId = await getDocIdByPath(notebookId, 'Archive');
    if (!archiveId) {
        throw new Error('Archive folder is missing');
    }

    // Move document to Archive
    await moveDocsByID([docBlock.id], archiveId);

    // Update block attributes with archive metadata
    const now = new Date().toISOString();
    await setBlockAttrs(docBlock.id, {
        'custom-status': 'archived',
        'custom-archived_at': now,
        'custom-archive_reason': archiveReason,
        'custom-last_touched_at': now,
    });
}

/**
 * Get list of projects in the Projects folder.
 * Returns project documents with their metadata.
 */
export async function getProjects(): Promise<ProjectInfo[]> {
    const notebook = await resolveStructureNotebook();
    await ensureNotebookStructure();

    const projectsFolderId = await getDocIdByPath(notebook.id, 'Projects');
    if (!projectsFolderId) {
        return [];
    }

    // Use SQL to get all documents in Projects folder
    const query = `
        SELECT id, content, created, ial
        FROM blocks
        WHERE box = '${notebook.id}'
        AND hpath LIKE '/Projects/%'
        AND type = 'd'
        ORDER BY created DESC
    `;

    try {
        const result = await fetchSyncPost('/api/query/sql', { stmt: query });
        if (result.code !== 0 || !result.data) {
            return [];
        }

        return result.data.map((row: any) => {
            const title = row.content?.replace(/^#\s*/, '') || 'Untitled Project';
            const attrs = JSON.parse(row.ial || '{}');

            return {
                id: row.id,
                title: title,
                created_at: row.created || new Date().toISOString(),
                status: attrs['custom-status'] || attrs['custom-project_status'] || 'active',
            };
        });
    } catch (err) {
        console.error('[IES] Error fetching projects:', err);
        return [];
    }
}

/**
 * Link a capture to a project by adding project_id to its metadata.
 */
export async function linkCaptureToProject(
    captureBlockId: string,
    projectId: string
): Promise<void> {
    if (!captureBlockId || !projectId) {
        throw new Error('Both capture block ID and project ID are required');
    }

    const block = await getBlockByID(captureBlockId);
    if (!block) {
        throw new Error('Unable to locate the capture');
    }

    const now = new Date().toISOString();
    await setBlockAttrs(captureBlockId, {
        'custom-project_id': projectId,
        'custom-last_touched_at': now,
    });
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
        thinking_mode,
        phase,
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
    if (thinking_mode) {
        frontmatter.thinking_mode = thinking_mode;
    }
    if (phase) {
        frontmatter.phase = phase;
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
        const attrs: Record<string, string> = {
            'custom-be_type': 'session',
            'custom-be_id': sessionId,
            'custom-mode': mode,
            'custom-status': 'completed',
        };
        if (thinking_mode) {
            attrs['custom-thinking_mode'] = thinking_mode;
        }
        if (phase) {
            attrs['custom-phase'] = phase;
        }
        await setBlockAttrs(docId, attrs);

        return docId;
    } catch (err) {
        console.error('[IES] Failed to create session document:', err);
        return null;
    }
}

/**
 * Options for creating a concept document.
 */
export interface ConceptDocumentOptions {
    conceptId: string;
    name: string;
    conceptType: string;
    description: string;
    aliases?: string[];
    relationships?: Array<{
        targetName: string;
        relationshipType: string;
        evidence?: string;
    }>;
    sourceSessionId?: string;
    sourceQuotes?: string[];
    userId: string;
}

/**
 * Create a concept document in the /Concepts/ folder.
 * This formalizes insights from thinking sessions into persistent knowledge graph nodes.
 */
export async function createConceptDocument(options: ConceptDocumentOptions): Promise<string | null> {
    const {
        conceptId,
        name,
        conceptType,
        description,
        aliases = [],
        relationships = [],
        sourceSessionId,
        sourceQuotes = [],
        userId,
    } = options;

    const notebook = await resolveStructureNotebook();
    await ensureNotebookStructure();

    // Create document path in Concepts folder
    const safeTitle = name.substring(0, 50).replace(/[/\\?%*:|"<>]/g, '-').trim();
    const docPath = `Concepts/${safeTitle}`;

    // Build frontmatter
    const frontmatter: Record<string, any> = {
        be_type: 'concept',
        be_id: conceptId,
        concept_type: conceptType,
        name: name,
        status: 'anchored',
        created: new Date().toISOString(),
        created_by: userId,
    };
    if (aliases.length > 0) {
        frontmatter.aliases = aliases;
    }
    if (sourceSessionId) {
        frontmatter.source_session_id = sourceSessionId;
    }

    const fm = serializeFrontmatter(frontmatter);

    // Build document content
    let content = `---\n${fm}\n---\n\n`;
    content += `# ${name}\n\n`;
    content += `**Type:** ${conceptType.charAt(0).toUpperCase() + conceptType.slice(1)}\n\n`;

    // Description section
    content += `## Definition\n\n${description}\n\n`;

    // Aliases section
    if (aliases.length > 0) {
        content += `## Also Known As\n\n`;
        content += aliases.map(a => `- ${a}`).join('\n') + '\n\n';
    }

    // Relationships section
    if (relationships.length > 0) {
        content += `## Relationships\n\n`;
        for (const rel of relationships) {
            const relType = rel.relationshipType.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            content += `- **${relType}** → [[${rel.targetName}]]`;
            if (rel.evidence) {
                content += `\n  - *${rel.evidence}*`;
            }
            content += '\n';
        }
        content += '\n';
    }

    // Source quotes section
    if (sourceQuotes.length > 0) {
        content += `## Supporting Evidence\n\n`;
        for (const quote of sourceQuotes) {
            content += `> ${quote}\n\n`;
        }
    }

    // Source session link
    if (sourceSessionId) {
        content += `## Origin\n\n`;
        content += `This concept was extracted from session \`${sourceSessionId}\`.\n\n`;
    }

    try {
        const docId = await createDocWithMd(notebook.id, docPath, content);

        // Set block attributes for backend linking
        await setBlockAttrs(docId, {
            'custom-be_type': 'concept',
            'custom-be_id': conceptId,
            'custom-concept_type': conceptType,
            'custom-status': 'anchored',
        });

        return docId;
    } catch (err) {
        console.error('[IES] Failed to create concept document:', err);
        return null;
    }
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

export { lsNotebooks };
