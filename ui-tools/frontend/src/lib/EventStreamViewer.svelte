<script>
  export let result = null;
</script>

{#if result}
  <div class="event-stream-viewer">
    <div class="summary">
      <h3>
        {#if result.success}
          ✓ Dry Run Successful
        {:else}
          ✗ Dry Run Failed
        {/if}
      </h3>
      <div class="summary-stats">
        <span>Total Events: {result.total_events}</span>
        <span>Valid: {result.valid_events}</span>
        {#if result.errors && result.errors.length > 0}
          <span class="error-count">Errors: {result.errors.length}</span>
        {/if}
        {#if result.warnings && result.warnings.length > 0}
          <span class="warning-count">Warnings: {result.warnings.length}</span>
        {/if}
      </div>
    </div>

    {#if result.errors && result.errors.length > 0}
      <div class="errors-section">
        <h4>Errors</h4>
        <ul>
          {#each result.errors as error}
            <li>{error}</li>
          {/each}
        </ul>
      </div>
    {/if}

    {#if result.warnings && result.warnings.length > 0}
      <div class="warnings-section">
        <h4>Warnings</h4>
        <ul>
          {#each result.warnings as warning}
            <li>{warning}</li>
          {/each}
        </ul>
      </div>
    {/if}

    {#if result.event_results && result.event_results.length > 0}
      <div class="events-timeline">
        <h4>Event Stream</h4>
        
        {#each result.event_results as event, index}
          <div class="event-card {event.success ? 'success' : 'error'}">
            <div class="event-header">
              <div class="event-id">
                <span class="event-number">#{event.event_id}</span>
                <span class="event-operation">{event.operation.toUpperCase()}</span>
              </div>
              <div class="event-entity">{event.entity}</div>
              <div class="event-status">
                {#if event.success}
                  <span class="status-icon success">✓</span>
                {:else}
                  <span class="status-icon error">✗</span>
                {/if}
              </div>
            </div>

            {#if event.errors && event.errors.length > 0}
              <div class="event-errors">
                <strong>Errors:</strong>
                <ul>
                  {#each event.errors as error}
                    <li>{error}</li>
                  {/each}
                </ul>
              </div>
            {/if}

            {#if event.warnings && event.warnings.length > 0}
              <div class="event-warnings">
                <strong>Warnings:</strong>
                <ul>
                  {#each event.warnings as warning}
                    <li>{warning}</li>
                  {/each}
                </ul>
              </div>
            {/if}

            {#if event.resolved_fields && Object.keys(event.resolved_fields).length > 0}
              <div class="event-fields">
                <strong>Fields:</strong>
                <table>
                  <tbody>
                    {#each Object.entries(event.resolved_fields) as [field, value]}
                      <tr>
                        <td class="field-name">{field}</td>
                        <td class="field-value">
                          {#if typeof value === 'object'}
                            {JSON.stringify(value)}
                          {:else}
                            {value}
                          {/if}
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            {/if}

            {#if index < result.event_results.length - 1}
              <div class="event-connector"></div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </div>
{/if}

<style>
  .event-stream-viewer {
    margin: 20px 0;
    padding: 20px;
    background: #fafafa;
    border-radius: 8px;
  }

  .summary {
    margin-bottom: 20px;
    padding: 15px;
    background: white;
    border-radius: 6px;
    border-left: 4px solid #107c10;
  }

  .summary h3 {
    margin: 0 0 10px 0;
    color: #107c10;
  }

  .summary-stats {
    display: flex;
    gap: 20px;
    font-size: 14px;
    color: #666;
  }

  .summary-stats span {
    padding: 4px 8px;
    background: #f0f0f0;
    border-radius: 4px;
  }

  .error-count {
    background: #fde7e9 !important;
    color: #d83b01 !important;
  }

  .warning-count {
    background: #fff4ce !important;
    color: #8a6d3b !important;
  }

  .errors-section,
  .warnings-section {
    margin: 15px 0;
    padding: 15px;
    border-radius: 6px;
  }

  .errors-section {
    background: #fde7e9;
    border-left: 4px solid #d83b01;
    color: #d83b01;
  }

  .warnings-section {
    background: #fff4ce;
    border-left: 4px solid #f59f00;
    color: #8a6d3b;
  }

  .errors-section h4,
  .warnings-section h4 {
    margin: 0 0 10px 0;
  }

  .errors-section ul,
  .warnings-section ul {
    margin: 0;
    padding-left: 20px;
  }

  .events-timeline {
    margin-top: 20px;
  }

  .events-timeline h4 {
    margin-bottom: 15px;
    color: #333;
  }

  .event-card {
    position: relative;
    margin: 10px 0;
    padding: 15px;
    background: white;
    border-radius: 6px;
    border-left: 4px solid #107c10;
    transition: box-shadow 0.2s;
  }

  .event-card:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .event-card.error {
    border-left-color: #d83b01;
  }

  .event-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }

  .event-id {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .event-number {
    font-weight: bold;
    font-size: 16px;
    color: #333;
  }

  .event-operation {
    padding: 3px 8px;
    background: #0078d4;
    color: white;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
  }

  .event-entity {
    font-family: 'Courier New', monospace;
    font-size: 14px;
    color: #666;
  }

  .status-icon {
    font-size: 18px;
    font-weight: bold;
  }

  .status-icon.success {
    color: #107c10;
  }

  .status-icon.error {
    color: #d83b01;
  }

  .event-errors,
  .event-warnings {
    margin: 10px 0;
    padding: 10px;
    border-radius: 4px;
    font-size: 13px;
  }

  .event-errors {
    background: #fde7e9;
    color: #d83b01;
  }

  .event-warnings {
    background: #fff4ce;
    color: #8a6d3b;
  }

  .event-errors ul,
  .event-warnings ul {
    margin: 5px 0 0 0;
    padding-left: 20px;
  }

  .event-fields {
    margin-top: 10px;
    font-size: 13px;
  }

  .event-fields strong {
    display: block;
    margin-bottom: 8px;
    color: #666;
  }

  .event-fields table {
    width: 100%;
    border-collapse: collapse;
  }

  .field-name {
    padding: 6px 10px;
    background: #f8f8f8;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #333;
    width: 30%;
    border-bottom: 1px solid #eee;
  }

  .field-value {
    padding: 6px 10px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #666;
    border-bottom: 1px solid #eee;
    word-break: break-all;
  }

  .event-connector {
    position: absolute;
    bottom: -20px;
    left: 20px;
    width: 2px;
    height: 20px;
    background: #ddd;
  }
</style>
