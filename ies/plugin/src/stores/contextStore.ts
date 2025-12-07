/**
 * Context Store
 * Tracks the currently open note in SiYuan for context-aware Flow initiation
 */

import { writable, derived } from 'svelte/store';
import type { Plugin } from 'siyuan';

export interface NoteContext {
    noteId: string | null;
    noteTitle: string | null;
    notebookId: string | null;
    blockIds: string[];
    selectedText: string | null;
    updatedAt: number | null;
}

// Initial state - no note open
const initialContext: NoteContext = {
    noteId: null,
    noteTitle: null,
    notebookId: null,
    blockIds: [],
    selectedText: null,
    updatedAt: null
};

// Create the store
function createContextStore() {
    const { subscribe, set, update } = writable<NoteContext>(initialContext);

    return {
        subscribe,

        /**
         * Set the current note context (called from EventBus listener)
         */
        setNote: (noteId: string, noteTitle: string | null, notebookId: string | null) => {
            update(ctx => ({
                ...ctx,
                noteId,
                noteTitle,
                notebookId,
                blockIds: [],
                selectedText: null,
                updatedAt: Date.now()
            }));
        },

        /**
         * Update selected text (called from selection listener)
         */
        setSelection: (text: string | null, blockIds: string[] = []) => {
            update(ctx => ({
                ...ctx,
                selectedText: text,
                blockIds,
                updatedAt: Date.now()
            }));
        },

        /**
         * Clear the context (when note is closed)
         */
        clear: () => {
            set(initialContext);
        },

        /**
         * Get spark source for Flow initiation
         */
        getSparkSource: () => {
            let current: NoteContext = initialContext;
            subscribe(ctx => { current = ctx; })();

            if (!current.noteId) return null;

            if (current.selectedText) {
                return {
                    type: 'selection' as const,
                    noteId: current.noteId,
                    noteTitle: current.noteTitle,
                    text: current.selectedText,
                    blockIds: current.blockIds
                };
            }

            return {
                type: 'note' as const,
                noteId: current.noteId,
                noteTitle: current.noteTitle
            };
        }
    };
}

// Export the singleton store
export const noteContext = createContextStore();

// Derived stores for convenience
export const hasNoteOpen = derived(noteContext, $ctx => $ctx.noteId !== null);
export const hasSelection = derived(noteContext, $ctx => $ctx.selectedText !== null && $ctx.selectedText.length > 0);
export const currentNoteTitle = derived(noteContext, $ctx => $ctx.noteTitle || 'Untitled');

// Plugin reference for EventBus registration
let _plugin: Plugin | null = null;
let _selectionHandler: (() => void) | null = null;

/**
 * Initialize context tracking by registering EventBus listeners
 * Call this in plugin onLayoutReady()
 */
export function initContextTracking(plugin: Plugin): void {
    _plugin = plugin;

    // Listen for protyle load events (when a note is opened)
    plugin.eventBus.on('loaded-protyle', (event: CustomEvent) => {
        const protyle = event.detail?.protyle;
        if (!protyle) return;

        const noteId = protyle.block?.rootID || null;
        const noteTitle = protyle.title?.editElement?.textContent || null;
        const notebookId = protyle.notebookId || null;

        if (noteId) {
            noteContext.setNote(noteId, noteTitle, notebookId);
            console.log('[IES Context] Note opened:', noteTitle || noteId);
        }
    });

    // Track selection changes in the document
    _selectionHandler = () => {
        const selection = window.getSelection();
        if (selection && selection.toString().trim()) {
            // Get the selected block IDs if available
            const blockIds: string[] = [];
            const range = selection.getRangeAt(0);
            const container = range.commonAncestorContainer;

            // Find parent block element
            let blockElement = container.nodeType === Node.ELEMENT_NODE
                ? container as Element
                : container.parentElement;

            while (blockElement && !blockElement.hasAttribute('data-node-id')) {
                blockElement = blockElement.parentElement;
            }

            if (blockElement) {
                const blockId = blockElement.getAttribute('data-node-id');
                if (blockId) blockIds.push(blockId);
            }

            noteContext.setSelection(selection.toString(), blockIds);
        }
    };

    document.addEventListener('selectionchange', _selectionHandler);

    console.log('[IES Context] Context tracking initialized');
}

/**
 * Cleanup context tracking (call in plugin onunload)
 */
export function destroyContextTracking(): void {
    if (_selectionHandler) {
        document.removeEventListener('selectionchange', _selectionHandler);
        _selectionHandler = null;
    }
    noteContext.clear();
    _plugin = null;
    console.log('[IES Context] Context tracking destroyed');
}

/**
 * Get the current note ID for use in non-reactive contexts
 */
export function getCurrentNoteId(): string | null {
    let noteId: string | null = null;
    noteContext.subscribe(ctx => { noteId = ctx.noteId; })();
    return noteId;
}

/**
 * Get selected block IDs for use in non-reactive contexts
 */
export function getSelectedBlockIds(): string[] {
    let blockIds: string[] = [];
    noteContext.subscribe(ctx => { blockIds = ctx.blockIds; })();
    return blockIds;
}
