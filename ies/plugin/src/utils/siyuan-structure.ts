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

const STRUCTURE_FOLDERS = [
    { path: 'Daily', title: 'Daily Log' },
    { path: 'Insights', title: 'Insights Library' },
    { path: 'Threads', title: 'Active Threads' },
    { path: 'Favorite Problems', title: 'Favorite Problems' },
    { path: 'Sessions', title: 'Sessions' },
];

const NOTEBOOK_STORAGE_KEY = 'ies.structureNotebookId';
const BACKEND_URL_KEY = 'ies.backendUrl';
const DEFAULT_BACKEND_URL = 'http://192.168.86.60:8081';

const PREFERRED_NOTEBOOK_NAMES = [
    'Personal',
    'Therapy',
    'Therapy Framework',
    'Framework Project',
    'Intelligent Exploration System',
];

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

let cachedNotebook: NotebookInfo | null = null;
let notebooksCache: NotebookInfo[] | null = null;
let lastNotebookFetch = 0;

function now(): number {
    return Date.now();
}

function getBackendUrl(): string {
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
            headers: [{ 'Content-Type': 'application/json' }],
            payload: body ? JSON.stringify(body) : undefined,
        });

        if (response?.body) {
            let data = response.body;
            if (typeof data === 'string') {
                try {
                    data = JSON.parse(data);
                } catch {
                    // Not JSON, use as-is
                }
            }
            return data as T;
        }
        return null;
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

    for (const preferred of PREFERRED_NOTEBOOK_NAMES) {
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

    const ids = await getIDsByHPath(notebookId, normalized);
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
 * Create a spark in the backend and add it to today's daily log.
 * Returns the spark ID from the backend.
 */
export async function createSparkWithBackend(
    title: string,
    content: string,
    options: {
        resonance_signal?: string;
        energy_level?: string;
        concept_ids?: string[];
    } = {}
): Promise<{ sparkId: string; blockId: string } | null> {
    if (!content || !content.trim()) {
        throw new Error('Cannot create an empty spark');
    }

    // First create the SiYuan block to get its ID
    const notebook = await resolveStructureNotebook();
    await ensureNotebookStructure();

    const dateValue = new Date();
    const relativePath = sanitizePath(getDailyLogPath(dateValue));
    const docId = await ensureDocument(notebook.id, relativePath, formatDailyTitle(dateValue));

    // Create the block in SiYuan first
    const frontmatter: Record<string, any> = {
        be_type: 'spark',
        status: 'captured',
        created: dateValue.toISOString(),
    };
    if (options.resonance_signal) {
        frontmatter.resonance = options.resonance_signal;
    }
    if (options.energy_level) {
        frontmatter.energy = options.energy_level;
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
        // Update the SiYuan block with the backend spark ID
        await setBlockAttrs(blockId, {
            'custom-be_id': spark.id,
            'custom-be_type': 'spark',
            'custom-status': 'captured',
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
