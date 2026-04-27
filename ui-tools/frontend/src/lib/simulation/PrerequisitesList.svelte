<script>
  export let prerequisites = { lookup_prerequisites: [], template_prerequisites: [], total_prerequisites: 0 };
  export let loading = false;

  $: hasPrerequisites = prerequisites.total_prerequisites > 0;
  $: lookupPrereqs = prerequisites.lookup_prerequisites || [];
  $: templatePrereqs = prerequisites.template_prerequisites || [];
</script>

<div class="prerequisites-container">
  <div class="prerequisites-header">
    <div class="header-title">
      <span class="icon">📋</span>
      <h3>Expected Records (Prerequisites)</h3>
      {#if hasPrerequisites}
        <span class="count-badge">{prerequisites.total_prerequisites}</span>
      {/if}
    </div>
    <p class="description">
      These records are expected to exist in Dataverse before execution. 
      Review them to ensure they exist or correct the references.
    </p>
  </div>

  {#if loading}
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Analyzing simulation...</p>
    </div>
  {:else if prerequisites.error}
    <div class="error-state">
      <p>⚠ Error analyzing prerequisites: {prerequisites.error}</p>
    </div>
  {:else if !hasPrerequisites}
    <div class="empty-state">
      <p>✓ No external prerequisites detected</p>
      <span class="sub-text">All records will be created by this simulation</span>
    </div>
  {:else}
    <div class="prerequisites-content">
      <!-- Lookup Prerequisites -->
      {#if lookupPrereqs.length > 0}
        <div class="prereq-section">
          <h4 class="section-title">
            <span class="icon">🔍</span>
            Lookup References ({lookupPrereqs.length})
          </h4>
          <p class="section-description">
            These records will be searched for using the specified criteria:
          </p>
          <div class="prereq-table">
            <table>
              <thead>
                <tr>
                  <th>Entity</th>
                  <th>Search Field</th>
                  <th>Search Value</th>
                  <th>Used In Event</th>
                </tr>
              </thead>
              <tbody>
                {#each lookupPrereqs as prereq}
                  <tr>
                    <td>
                      <code class="entity-code">{prereq.target_entity}</code>
                    </td>
                    <td>
                      <code class="field-code">{prereq.search_field}</code>
                    </td>
                    <td>
                      <span class="search-value">{prereq.search_value}</span>
                    </td>
                    <td>
                      <span class="event-ref">Event #{prereq.event_id}</span>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}

      <!-- Template Variable Prerequisites -->
      {#if templatePrereqs.length > 0}
        <div class="prereq-section">
          <h4 class="section-title">
            <span class="icon">📦</span>
            External Variables ({templatePrereqs.length})
          </h4>
          <p class="section-description">
            These template variables reference records not created in this simulation:
          </p>
          <div class="prereq-table">
            <table>
              <thead>
                <tr>
                  <th>Variable Name</th>
                  <th>Template Reference</th>
                  <th>Used In Event</th>
                </tr>
              </thead>
              <tbody>
                {#each templatePrereqs as prereq}
                  <tr>
                    <td>
                      <code class="var-code">{prereq.variable_name}</code>
                    </td>
                    <td>
                      <code class="template-code">{prereq.template_reference}</code>
                    </td>
                    <td>
                      <span class="event-ref">Event #{prereq.event_id}</span>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .prerequisites-container {
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }

  .prerequisites-header {
    margin-bottom: 20px;
  }

  .header-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
  }

  .header-title .icon {
    font-size: 20px;
  }

  .header-title h3 {
    margin: 0;
    color: #e0e0e0;
    font-size: 18px;
    font-weight: 600;
  }

  .count-badge {
    background: #3b82f6;
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
  }

  .description {
    color: #94a3b8;
    font-size: 14px;
    margin: 0;
    line-height: 1.5;
  }

  .loading-state {
    text-align: center;
    padding: 40px;
    color: #94a3b8;
  }

  .spinner {
    width: 40px;
    height: 40px;
    margin: 0 auto 15px;
    border: 3px solid #3c3c3c;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error-state {
    padding: 20px;
    background: #3c1f1f;
    border: 1px solid #ef4444;
    border-radius: 6px;
    color: #fca5a5;
  }

  .empty-state {
    text-align: center;
    padding: 40px;
    color: #10b981;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 6px;
  }

  .empty-state p {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
  }

  .sub-text {
    color: #94a3b8;
    font-size: 14px;
  }

  .prerequisites-content {
    display: flex;
    flex-direction: column;
    gap: 25px;
  }

  .prereq-section {
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 16px;
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 8px 0;
    color: #e0e0e0;
    font-size: 15px;
    font-weight: 600;
  }

  .section-title .icon {
    font-size: 16px;
  }

  .section-description {
    color: #94a3b8;
    font-size: 13px;
    margin: 0 0 15px 0;
    line-height: 1.5;
  }

  .prereq-table {
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }

  thead {
    background: #1a1a1a;
  }

  th {
    text-align: left;
    padding: 10px 12px;
    color: #94a3b8;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid #3c3c3c;
  }

  tbody tr {
    border-bottom: 1px solid #3c3c3c;
    transition: background 0.15s ease;
  }

  tbody tr:last-child {
    border-bottom: none;
  }

  tbody tr:hover {
    background: rgba(255, 255, 255, 0.03);
  }

  td {
    padding: 12px;
    color: #e0e0e0;
    vertical-align: middle;
  }

  code {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    padding: 3px 6px;
    border-radius: 3px;
  }

  .entity-code {
    background: #1f3c2a;
    color: #6ee7b7;
    border: 1px solid #10b981;
  }

  .field-code {
    background: #1f2c3c;
    color: #93c5fd;
    border: 1px solid #3b82f6;
  }

  .var-code {
    background: #3c2c1f;
    color: #fbbf24;
    border: 1px solid #f59e0b;
  }

  .template-code {
    background: #2a2a2a;
    color: #e0e0e0;
    border: 1px solid #4b5563;
  }

  .search-value {
    color: #e0e0e0;
    font-weight: 500;
  }

  .event-ref {
    display: inline-block;
    background: #2a2a2a;
    color: #94a3b8;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
  }
</style>
