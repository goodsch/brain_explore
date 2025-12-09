import React from 'react';
import { useFlowStore } from '../../store/flowStore';

export function FlowPanel() {
  const { isFlowPanelOpen } = useFlowStore();
  if (!isFlowPanelOpen) return null;
  
  return (
    <div className="flow-panel" style={{ width: '30%', borderLeft: '1px solid #ccc' }}>
      <h2>Flow Panel</h2>
    </div>
  );
}
