<script>
  export let simulation;

  // Extract metadata from simulation object
  $: eventStreamName = simulation?.event_stream_name || 'Unknown';
  $: displayName = simulation?.display_name || '';
  $: module = simulation?.module || '';
  $: basedOnProcess = simulation?.based_on_process || '';
  $: basedOnScenario = simulation?.based_on_scenario || '';
  $: generated = simulation?.generated || '';
  $: generatedBy = simulation?.generated_by || '';
  $: execution = simulation?.execution || {};
  $: totalEvents = simulation?.events?.length || 0;
</script>

<div class="simulation-metadata">
  <div class="metadata-header">
    <div class="header-main">
      <h3>{displayName || eventStreamName}</h3>
      {#if displayName && eventStreamName !== displayName}
        <span class="event-stream-id">{eventStreamName}</span>
      {/if}
    </div>
    <div class="event-count">
      <span class="count-badge">{totalEvents} Events</span>
    </div>
  </div>

  <div class="metadata-details">
    {#if module}
      <div class="detail-item">
        <span class="detail-label">Module:</span>
        <span class="detail-value">{module}</span>
      </div>
    {/if}

    {#if basedOnProcess || basedOnScenario}
      <div class="detail-item">
        <span class="detail-label">Based on:</span>
        <span class="detail-value">
          {#if basedOnProcess}{basedOnProcess}{/if}
          {#if basedOnProcess && basedOnScenario}, {/if}
          {#if basedOnScenario}{basedOnScenario}{/if}
        </span>
      </div>
    {/if}

    {#if generated}
      <div class="detail-item">
        <span class="detail-label">Generated:</span>
        <span class="detail-value">
          {new Date(generated).toLocaleDateString()} {new Date(generated).toLocaleTimeString()}
          {#if generatedBy}by {generatedBy}{/if}
        </span>
      </div>
    {/if}
  </div>

  {#if execution && Object.keys(execution).length > 0}
    <div class="execution-config">
      <span class="config-label">Execution Config:</span>
      <div class="config-badges">
        {#if execution.dry_run_only}
          <span class="config-badge dry-run">Dry Run Only</span>
        {/if}
        {#if execution.clear_before_run}
          <span class="config-badge clear">Clear Before Run</span>
        {/if}
        {#if execution.stop_on_error}
          <span class="config-badge stop">Stop on Error</span>
        {:else}
          <span class="config-badge continue">Continue on Error</span>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .simulation-metadata {
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }

  .metadata-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
  }

  .header-main h3 {
    color: #ffffff;
    margin: 0 0 5px 0;
    font-size: 18px;
  }

  .event-stream-id {
    color: #94a3b8;
    font-size: 14px;
    font-family: 'Courier New', monospace;
  }

  .event-count {
    flex-shrink: 0;
  }

  .count-badge {
    background: #3b82f6;
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 600;
  }

  .metadata-details {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 15px;
  }

  .detail-item {
    display: flex;
    gap: 8px;
    font-size: 14px;
  }

  .detail-label {
    color: #94a3b8;
    font-weight: 500;
  }

  .detail-value {
    color: #e0e0e0;
  }

  .execution-config {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-top: 15px;
    border-top: 1px solid #3c3c3c;
  }

  .config-label {
    color: #94a3b8;
    font-size: 14px;
    font-weight: 500;
  }

  .config-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .config-badge {
    padding: 4px 10px;
    border-radius: 3px;
    font-size: 12px;
    font-weight: 500;
  }

  .config-badge.dry-run {
    background: rgba(251, 191, 36, 0.2);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.3);
  }

  .config-badge.clear {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
  }

  .config-badge.stop {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
  }

  .config-badge.continue {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
  }
</style>
