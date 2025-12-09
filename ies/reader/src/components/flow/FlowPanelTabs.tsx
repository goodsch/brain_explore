/**
 * FlowPanelTabs - Tab navigation for Flow panel
 *
 * Switches between "Explore" mode (entity/question exploration) and
 * "Timeline" mode (journey history visualization).
 */

import './flow-panel-tabs.css';

interface FlowPanelTabsProps {
  activeTab: 'explore' | 'timeline';
  onTabChange: (tab: 'explore' | 'timeline') => void;
}

export function FlowPanelTabs({ activeTab, onTabChange }: FlowPanelTabsProps) {
  return (
    <div className="flow-panel-tabs">
      <button
        className={`flow-panel-tabs__tab ${activeTab === 'explore' ? 'active' : ''}`}
        onClick={() => onTabChange('explore')}
      >
        Explore
      </button>
      <button
        className={`flow-panel-tabs__tab ${activeTab === 'timeline' ? 'active' : ''}`}
        onClick={() => onTabChange('timeline')}
      >
        Timeline
      </button>
    </div>
  );
}
