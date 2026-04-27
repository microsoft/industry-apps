<script>
  export let event;
  export let index = 0;
  export let expanded = false;
  export let executionResult = null; // From full execution
  export let executionState = null; // From step-by-step execution
  export let canExecute = false;
  export let isExecuting = false;
  export let onExecute = null;

  // Extract event properties
  $: eventId = event?.event_id || index + 1;
  $: operation = (event?.operation || 'create').toLowerCase();
  $: entity = event?.entity || '';
  $: timestamp = event?.timestamp || '';
  $: performedBy = event?.performed_by || '';
  $: reasoning = event?.reasoning || '';
  $: fields = event?.fields || {};
  $: storeAs = event?.store_as || '';

  // Get combined execution status (either from full execution or step-by-step)
  $: hasExecuted = !!(executionResult || (executionState && executionState.status === 'success'));
  $: executionSuccess = executionResult?.success || executionState?.status === 'success';
  $: executionRecordId = executionResult?.record_id || executionState?.record_id;
  $: executionErrors = executionResult?.errors || executionState?.errors || [];
  $: executionStatus = executionState?.status || (executionResult ? (executionResult.success ? 'success' : 'error') : null);

  // Operation colors
  $: operationColor = {
    create: '#10b981',
    update: '#3b82f6',
    delete: '#ef4444'
  }[operation] || '#6b7280';

  // Status badge styling
  $: statusBadge = executionStatus ? {
    success: { color: '#10b981', bg: '#0f2a20', text: 'Success' },
    error: { color: '#ef4444', bg: '#3c1f1f', text: 'Failed' },
    running: { color: '#f59e0b', bg: '#3c2c1f', text: 'Running...' }
  }[executionStatus] : null;

  // Format timestamp
  function formatTimestamp(ts) {
    if (!ts) return '';
    try {
      const date = new Date(ts);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return ts;
    }
  }

  // Check if field is a lookup
  function isLookupField(fieldName) {
    return fieldName.includes('@odata.bind');
  }

  // Check if value contains template variable
  function hasTemplate(value) {
    return typeof value === 'string' && value.includes('{{') && value.includes('}}');
  }

  // Format field value for display
  function formatValue(value) {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'string' && value.length > 100) {
      return value.substring(0, 100) + '...';
    }
    return String(value);
  }

  // Toggle expand/collapse
  function toggle() {
    expanded = !expanded;
  }

  // Handle run event
  function handleRun() {
    if (onExecute && canExecute && !isExecuting) {
      onExecute();
    }
  }
</script>

<div class="event-card" class:expanded>
  <!-- Card Header (always visible) -->
  <div class="card-header">
    <div class="header-clickable" on:click={toggle} on:keydown={(e) => e.key === 'Enter' && toggle()} role="button" tabindex="0">
      <div class="header-main">
        <div class="event-id-operation">
          <span class="event-id">#{eventId}</span>
          <span class="operation-badge" style="background-color: {operationColor};">
            {operation.toUpperCase()}
          </span>
          <span class="entity-name">{entity}</span>
        </div>
        
        <!-- Status Badge -->
        {#if statusBadge}
          <div class="execution-status-badge" style="background-color: {statusBadge.bg}; border-color: {statusBadge.color}; color: {statusBadge.color};">
            {statusBadge.text}
            {#if executionRecordId}
              <span class="record-id-inline">{executionRecordId.substring(0, 8)}...</span>
            {/if}
          </div>
        {/if}
    </div>

    <div class="header-meta">
      {#if timestamp}
        <span class="timestamp">⏱ {formatTimestamp(timestamp)}</span>
      {/if}
      {#if performedBy}
        <span class="performed-by">👤 {performedBy}</span>
      {/if}
    </div>

    <div class="expand-icon">
      {expanded ? '▼' : '▶'}
    </div>
    </div>

    <!-- Run Button (separate from clickable area) -->
    {#if onExecute}
      <button 
        class="run-btn" 
        on:click|stopPropagation={handleRun}
        disabled={!canExecute || isExecuting || executionStatus === 'success'}
        title={!canExecute ? 'Complete previous events first' : isExecuting ? 'Running...' : executionStatus === 'success' ? 'Already executed' : 'Run this event'}
      >
        {#if isExecuting}
          ⏳ Running...
        {:else if executionStatus === 'success'}
          ✓ Completed
        {:else}
          ▶ Run This Event
        {/if}
      </button>
    {/if}
  </div>

  <!-- Reasoning Section (always visible) -->
  {#if reasoning}
    <div class="reasoning-section-visible">
      <div class="reasoning-content">{reasoning}</div>
    </div>
  {/if}

  <!-- Card Body (expandable fields and details) -->
  {#if expanded}
    <div class="card-body">
      <!-- Fields Section -->
      {#if Object.keys(fields).length > 0}
        <div class="fields-section">
          <div class="section-header">
            <span class="section-icon">📝</span>
            <span class="section-title">Fields ({Object.keys(fields).length})</span>
          </div>
          <div class="fields-grid">
            {#each Object.entries(fields) as [fieldName, fieldValue]}
              <div class="field-row" class:lookup={isLookupField(fieldName)} class:template={hasTemplate(fieldValue)}>
                <div class="field-name">
                  {#if isLookupField(fieldName)}
                    <span class="field-icon">🔗</span>
                  {/if}
                  {#if hasTemplate(fieldValue)}
                    <span class="field-icon template-icon">🔀</span>
                  {/if}
                  {fieldName}
                </div>
                <div class="field-value" title={String(fieldValue)}>
                  {formatValue(fieldValue)}
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Store As Section -->
      {#if storeAs}
        <div class="store-as-section">
          <span class="store-icon">📌</span>
          <span class="store-label">Stored as:</span>
          <code class="store-variable">{storeAs}</code>
        </div>
      {/if}

      <!-- Execution Errors -->
      {#if executionResult && executionResult.errors && executionResult.errors.length > 0}
        <div class="errors-section">
          <div class="section-header error">
            <span class="section-icon">⚠</span>
            <span class="section-title">Errors</span>
          </div>
          <ul class="error-list">
            {#each executionResult.errors as error}
              <li>{error}</li>
            {/each}
          </ul>
        </div>
      {/if}

      <!-- Execution Duration -->
      {#if executionResult && executionResult.duration_seconds !== undefined}
        <div class="execution-duration">
          Duration: {executionResult.duration_seconds.toFixed(3)}s
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .event-card {
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
  }

  .event-card:hover {
    border-color: #4b5563;
  }

  .card-header {
    padding: 16px;
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .header-clickable {
    cursor: pointer;
    user-select: none;
  }

  .header-clickable:hover {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 4px;
    margin: -4px;
    padding: 4px;
  }

  .header-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .event-id-operation {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .event-id {
    color: #94a3b8;
    font-weight: 600;
    font-size: 14px;
    min-width: 30px;
  }

  .operation-badge {
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
  }

  .entity-name {
    color: #e0e0e0;
    font-size: 14px;
    font-family: 'Courier New', monospace;
  }

  .execution-status-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid;
  }

  .record-id-inline {
    font-family: 'Courier New', monospace;
    font-size: 11px;
    opacity: 0.8;
  }

  .run-btn {
    width: 100%;
    padding: 10px 16px;
    background: #1f3c2a;
    color: #6ee7b7;
    border: 1px solid #10b981;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    transition: all 0.2s ease;
  }

  .run-btn:hover:not(:disabled) {
    background: #28523a;
    border-color: #34d399;
  }

  .run-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: #2a2a2a;
    color: #94a3b8;
    border-color: #3c3c3c;
  }

  .header-meta {
    display: flex;
    gap: 20px;
    font-size: 13px;
    color: #94a3b8;
  }

  .timestamp, .performed-by {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .expand-icon {
    position: absolute;
    right: 16px;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
    font-size: 12px;
    transition: transform 0.2s ease;
  }

  /* Reasoning section that's always visible */
  .reasoning-section-visible {
    padding: 16px;
    border-top: 1px solid #3c3c3c;
  }

  .reasoning-section-visible .reasoning-content {
    color: #cbd5e1;
    font-size: 14px;
    line-height: 1.6;
    padding: 12px;
    background: #1a1a1a;
    border-radius: 4px;
    border-left: 3px solid #3b82f6;
    white-space: pre-wrap;
  }

  .card-body {
    padding: 0 16px 16px 16px;
    border-top: 1px solid #3c3c3c;
    animation: slideDown 0.2s ease;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      max-height: 0;
    }
    to {
      opacity: 1;
      max-height: 2000px;
    }
  }

  .fields-section,
  .store-as-section,
  .errors-section {
    margin-top: 16px;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 10px;
    font-weight: 600;
    color: #e0e0e0;
    font-size: 13px;
  }

  .section-header.error {
    color: #f87171;
  }

  .section-icon {
    font-size: 14px;
  }

  .reasoning-content {
    color: #cbd5e1;
    font-size: 14px;
    line-height: 1.6;
    padding: 12px;
    background: #1a1a1a;
    border-radius: 4px;
    border-left: 3px solid #3b82f6;
  }

  .fields-grid {
    display: grid;
    gap: 8px;
  }

  .field-row {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 12px;
    padding: 8px;
    background: #1a1a1a;
    border-radius: 4px;
    font-size: 13px;
    align-items: start;
  }

  .field-row.lookup {
    border-left: 3px solid #06b6d4;
  }

  .field-row.template {
    border-left: 3px solid #a78bfa;
  }

  .field-name {
    color: #94a3b8;
    font-weight: 500;
    font-family: 'Courier New', monospace;
    word-break: break-word;
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .field-icon {
    font-size: 12px;
  }

  .template-icon {
    filter: hue-rotate(270deg);
  }

  .field-value {
    color: #e0e0e0;
    word-break: break-word;
    font-family: 'Courier New', monospace;
  }

  .store-as-section {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    background: rgba(168, 139, 250, 0.1);
    border: 1px solid rgba(168, 139, 250, 0.2);
    border-radius: 4px;
    font-size: 13px;
  }

  .store-icon {
    font-size: 14px;
  }

  .store-label {
    color: #94a3b8;
  }

  .store-variable {
    color: #a78bfa;
    font-weight: 600;
    background: rgba(168, 139, 250, 0.2);
    padding: 2px 6px;
    border-radius: 3px;
  }

  .error-list {
    margin: 0;
    padding-left: 20px;
    color: #f87171;
    font-size: 13px;
  }

  .error-list li {
    margin: 6px 0;
  }

  .execution-duration {
    text-align: right;
    color: #94a3b8;
    font-size: 12px;
    margin-top: 8px;
    font-style: italic;
  }
</style>
