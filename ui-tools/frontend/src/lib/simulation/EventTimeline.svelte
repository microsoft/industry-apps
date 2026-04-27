<script>
  import EventCard from './EventCard.svelte';

  export let events = [];
  export let executionResults = null;
  export let eventExecutionStates = {};
  export let onExecuteEvent = null;
  export let onResetState = null;
  export let executingEventId = null;
  export let canExecute = false;

  // State for expand/collapse all
  let expandedStates = {};

  // Initialize all as collapsed
  $: if (events && events.length > 0) {
    if (Object.keys(expandedStates).length === 0) {
      expandedStates = events.reduce((acc, event, index) => {
        acc[index] = false;
        return acc;
      }, {});
    }
  }

  // Find execution result for an event (from full execution)
  function getExecutionResult(event) {
    if (!executionResults || !executionResults.length) return null;
    return executionResults.find(result => result.event_id === event.event_id);
  }

  // Get execution state for an event (from step-by-step execution)
  function getExecutionState(event) {
    return eventExecutionStates[event.event_id] || null;
  }

  // Check if event can be executed (previous events completed)
  function canExecuteEvent(eventId) {
    if (!canExecute) return false;
    
    // Find all events before this one
    const eventIndex = events.findIndex(e => e.event_id === eventId);
    if (eventIndex === 0) return true; // First event can always run
    
    // Check if all previous events succeeded
    for (let i = 0; i < eventIndex; i++) {
      const prevEvent = events[i];
      const prevState = eventExecutionStates[prevEvent.event_id];
      if (!prevState || prevState.status !== 'success') {
        return false;
      }
    }
    
    return true;
  }

  // Expand all events
  function expandAll() {
    expandedStates = events.reduce((acc, event, index) => {
      acc[index] = true;
      return acc;
    }, {});
  }

  // Collapse all events
  function collapseAll() {
    expandedStates = events.reduce((acc, event, index) => {
      acc[index] = false;
      return acc;
    }, {});
  }

  // Run all remaining events
  async function runAllRemaining() {
    if (!onExecuteEvent || !canExecute) return;

    for (const event of events) {
      const state = eventExecutionStates[event.event_id];
      
      // Skip if already succeeded
      if (state && state.status === 'success') continue;
      
      // Check if we can execute this event
      if (!canExecuteEvent(event.event_id)) break;
      
      // Execute and wait
      await onExecuteEvent(event.event_id);
    }
  }

  // Check if all expanded or all collapsed
  $: allExpanded = Object.values(expandedStates).every(state => state === true);
  $: allCollapsed = Object.values(expandedStates).every(state => state === false);

  // Calculate progress
  $: executedCount = Object.values(eventExecutionStates).filter(s => s.status === 'success').length;
  $: hasExecutionState = Object.keys(eventExecutionStates).length > 0;
</script>

<div class="event-timeline">
  <!-- Timeline Controls -->
  <div class="timeline-controls">
    <div class="controls-left">
      <span class="timeline-title">Event Timeline</span>
      <span class="event-count">{events.length} events</span>
      {#if hasExecutionState}
        <span class="progress-badge">{executedCount} / {events.length} completed</span>
      {/if}
    </div>
    <div class="controls-right">
      {#if hasExecutionState && onResetState}
        <button 
          class="control-btn reset-btn" 
          on:click={onResetState}
          title="Reset execution state"
        >
          🔄 Reset All
        </button>
      {/if}
      {#if onExecuteEvent && canExecute}
        <button 
          class="control-btn execute-btn" 
          on:click={runAllRemaining}
          disabled={executingEventId !== null || executedCount === events.length}
          title="Run all remaining events"
        >
          ▶ Run All Remaining
        </button>
      {/if}
      <button 
        class="control-btn" 
        on:click={allExpanded ? collapseAll : expandAll}
        disabled={events.length === 0}
      >
        {allExpanded ? '▲ Collapse All' : '▼ Expand All'}
      </button>
    </div>
  </div>

  <!-- Timeline Container -->
  {#if events.length === 0}
    <div class="empty-state">
      <div class="empty-icon">📋</div>
      <p>No events in this simulation</p>
    </div>
  {:else}
    <div class="timeline-container">
      {#each events as event, index}
        <div class="timeline-item">
          <!-- Timeline Connector -->
          <div class="timeline-connector">
            <div class="timeline-dot" style="background-color: {
              {
                create: '#10b981',
                update: '#3b82f6',
                delete: '#ef4444'
              }[(event.operation || 'create').toLowerCase()] || '#6b7280'
            };"></div>
            {#if index < events.length - 1}
              <div class="timeline-line"></div>
            {/if}
          </div>

          <!-- Event Card -->
          <div class="timeline-content">
            <EventCard 
              {event} 
              {index}
              bind:expanded={expandedStates[index]}
              executionResult={getExecutionResult(event)}
              executionState={getExecutionState(event)}
              canExecute={canExecuteEvent(event.event_id)}
              isExecuting={executingEventId === event.event_id}
              onExecute={() => onExecuteEvent && onExecuteEvent(event.event_id)}
            />
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .event-timeline {
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 20px;
  }

  .timeline-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #3c3c3c;
  }

  .controls-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .timeline-title {
    color: #e0e0e0;
    font-weight: 600;
    font-size: 16px;
  }

  .event-count {
    color: #94a3b8;
    font-size: 14px;
    background: #2a2a2a;
    padding: 4px 10px;
    border-radius: 4px;
  }

  .progress-badge {
    color: #10b981;
    font-size: 14px;
    background: #0f2a20;
    padding: 4px 10px;
    border-radius: 4px;
    border: 1px solid #10b981;
    font-weight: 500;
  }

  .controls-right {
    display: flex;
    gap: 10px;
  }

  .control-btn {
    background: #2a2a2a;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    padding: 6px 14px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s ease;
  }

  .control-btn:hover:not(:disabled) {
    background: #3c3c3c;
    border-color: #4b5563;
  }

  .control-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .reset-btn {
    background: #3c1f1f;
    border-color: #ef4444;
    color: #fca5a5;
  }

  .reset-btn:hover:not(:disabled) {
    background: #4c2828;
    border-color: #f87171;
  }

  .execute-btn {
    background: #1f3c2a;
    border-color: #10b981;
    color: #6ee7b7;
  }

  .execute-btn:hover:not(:disabled) {
    background: #28523a;
    border-color: #34d399;
  }

  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #94a3b8;
  }

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  .empty-state p {
    margin: 0;
    font-size: 16px;
  }

  .timeline-container {
    position: relative;
  }

  .timeline-item {
    display: flex;
    gap: 16px;
    position: relative;
  }

  .timeline-connector {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    flex-shrink: 0;
  }

  .timeline-dot {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 3px solid #1a1a1a;
    z-index: 2;
    flex-shrink: 0;
    margin-top: 20px;
  }

  .timeline-line {
    width: 2px;
    flex-grow: 1;
    background: #3c3c3c;
    margin: 4px 0;
    min-height: 20px;
  }

  .timeline-content {
    flex-grow: 1;
    padding-bottom: 0;
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    .timeline-controls {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }

    .controls-left,
    .controls-right {
      width: 100%;
    }

    .controls-right {
      justify-content: flex-start;
    }

    .timeline-item {
      gap: 12px;
    }
  }
</style>
