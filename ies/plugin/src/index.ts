import {
    Plugin,
    showMessage,
    Dialog,
    openTab,
    getFrontend,
    openWindow,
    Menu
} from "siyuan";

import "@/index.scss";

import { setPluginInstance, t } from "./utils/i18n";
import { ensureNotebookStructure } from "./utils/siyuan-structure";
import { initContextTracking, destroyContextTracking, noteContext } from "./stores/contextStore";
import Dashboard from "./views/Dashboard.svelte";

export const SETTINGS_FILE = "settings.json";

const IES_SIDEBAR_TYPE = "ies-explorer-sidebar";
export const IES_TAB_TYPE = "ies-explorer-tab";

export default class IESExplorerPlugin extends Plugin {
    private dashboardApp: Dashboard;
    private docTitleMenuHandler: (e: CustomEvent) => void;
    private selectionMenuHandler: (e: CustomEvent) => void;

    async onload() {
        // Set i18n plugin instance
        setPluginInstance(this);

        // Add custom icons
        this.addIcons(`
    <symbol id="iconIESExplorer" viewBox="0 0 24 24">
        <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
    </symbol>
    <symbol id="iconForge" viewBox="0 0 24 24">
        <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
    </symbol>
    <symbol id="iconFlow" viewBox="0 0 24 24">
        <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
    </symbol>
    `);

        // Add top bar button for easy access
        this.addTopBar({
            icon: "iconIESExplorer",
            title: "IES Explorer",
            position: "right",
            callback: () => {
                this.openIESTab();
            }
        });

        // Register IES tab type
        const pluginInstance = this;
        this.addTab({
            type: IES_TAB_TYPE,
            init() {
                const element = this.element as HTMLElement;
                element.style.display = 'flex';
                element.style.flexDirection = 'column';
                element.style.height = '100%';
                // Create Dashboard in tab with plugin instance for settings persistence
                new Dashboard({
                    target: element,
                    props: {
                        plugin: pluginInstance
                    }
                });
            },
            destroy() {
                // Svelte component auto-cleanup
            }
        });
    }

    async onLayoutReady() {
        // Initialize context tracking for Flow initiation
        initContextTracking(this);

        // Register context menu items for Flow initiation
        this.registerContextMenus();

        // Create IES folder structure in the notebook
        try {
            await ensureNotebookStructure();
            console.log("[IES] Folder structure initialized");
        } catch (err) {
            console.warn("[IES] Failed to create folder structure:", err);
        }

        // Register IES sidebar dock
        this.addDock({
            config: {
                position: "RightBottom",
                size: { width: 400, height: 0 },
                icon: "iconIESExplorer",
                title: "IES Explorer",
            },
            data: {
                text: "IES Explorer"
            },
            type: IES_SIDEBAR_TYPE,
            init: (dock) => {
                this.dashboardApp = new Dashboard({
                    target: dock.element,
                    props: {
                        plugin: this
                    }
                });
            },
            destroy: () => {
                if (this.dashboardApp) {
                    this.dashboardApp.$destroy();
                }
            }
        });
    }

    async onunload() {
        // Cleanup context menus
        this.unregisterContextMenus();
        // Cleanup context tracking
        destroyContextTracking();
        console.log("IES Explorer plugin unloaded");
    }

    async uninstall() {
        console.log("IES Explorer plugin uninstalled");
        // Remove plugin data
        await this.removeData(SETTINGS_FILE);
        await this.removeData("ies-sessions.json");
    }

    /**
     * Open IES in a new tab
     */
    openIESTab() {
        const tabId = this.name + IES_TAB_TYPE;
        openTab({
            app: this.app,
            custom: {
                title: 'IES Explorer',
                icon: 'iconIESExplorer',
                id: tabId,
                data: {
                    time: Date.now()
                }
            }
        });
    }

    /**
     * Open IES in a new window
     */
    async openIESWindow() {
        const tabId = this.name + IES_TAB_TYPE;
        const tab = openTab({
            app: this.app,
            custom: {
                title: 'IES Explorer',
                icon: 'iconIESExplorer',
                id: tabId,
            }
        });

        openWindow({
            height: 700,
            width: 500,
            tab: await tab,
        });
    }

    /**
     * Register context menu items for Flow initiation
     */
    private registerContextMenus() {
        // Document title menu: "Start Flow from this note"
        this.docTitleMenuHandler = (e: CustomEvent) => {
            const menu = e.detail.menu as Menu;
            const protyle = e.detail.protyle;

            if (!protyle?.block?.rootID) return;

            menu.addItem({
                icon: 'iconFlow',
                label: 'Start Flow from this note',
                click: () => {
                    const noteId = protyle.block.rootID;
                    const noteTitle = protyle.title?.editElement?.textContent || 'Untitled';

                    // Update context store with current note
                    noteContext.setNote(noteId, noteTitle, protyle.notebookId || null);

                    // Open IES and trigger Flow
                    this.openFlowWithContext();
                }
            });
        };

        // Selection menu: "Start Flow from selection"
        this.selectionMenuHandler = (e: CustomEvent) => {
            const menu = e.detail.menu as Menu;
            const selection = window.getSelection();
            const selectedText = selection?.toString()?.trim();

            if (!selectedText) return;

            menu.addItem({
                icon: 'iconFlow',
                label: 'Start Flow from selection',
                click: () => {
                    // Selection is already tracked in contextStore via selectionchange listener
                    // Just open Flow
                    this.openFlowWithContext();
                }
            });
        };

        this.eventBus.on('click-editortitleicon', this.docTitleMenuHandler);
        this.eventBus.on('open-menu-content', this.selectionMenuHandler);

        console.log('[IES] Context menus registered');
    }

    /**
     * Unregister context menu handlers
     */
    private unregisterContextMenus() {
        if (this.docTitleMenuHandler) {
            this.eventBus.off('click-editortitleicon', this.docTitleMenuHandler);
        }
        if (this.selectionMenuHandler) {
            this.eventBus.off('open-menu-content', this.selectionMenuHandler);
        }
        console.log('[IES] Context menus unregistered');
    }

    /**
     * Open IES tab and trigger Flow mode with current context
     */
    private openFlowWithContext() {
        // Open the IES tab
        this.openIESTab();

        // Dispatch a custom event that Dashboard listens for
        // Small delay to ensure tab is ready
        setTimeout(() => {
            window.dispatchEvent(new CustomEvent('ies-start-flow-from-context'));
        }, 100);
    }
}
