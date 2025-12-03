import {
    Plugin,
    showMessage,
    Dialog,
    openTab,
    getFrontend,
    openWindow
} from "siyuan";

import "@/index.scss";

import { setPluginInstance, t } from "./utils/i18n";
import Dashboard from "./views/Dashboard.svelte";

export const SETTINGS_FILE = "settings.json";

const IES_SIDEBAR_TYPE = "ies-explorer-sidebar";
export const IES_TAB_TYPE = "ies-explorer-tab";

export default class IESExplorerPlugin extends Plugin {
    private dashboardApp: Dashboard;

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

        // Register IES tab type
        const pluginInstance = this;
        this.addTab({
            type: IES_TAB_TYPE,
            init() {
                const element = this.element as HTMLElement;
                element.style.display = 'flex';
                element.style.flexDirection = 'column';
                element.style.height = '100%';
                // Create Dashboard in tab
                new Dashboard({
                    target: element
                });
            },
            destroy() {
                // Svelte component auto-cleanup
            }
        });
    }

    async onLayoutReady() {
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
                    target: dock.element
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
}
