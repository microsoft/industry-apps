<script>
  import { onMount } from 'svelte';
  import Header from '../lib/Header.svelte';
  import { 
    config, 
    deployments, 
    tenants, 
    outputLines, 
    operationStatus, 
    streamResponse 
  } from '../lib/stores.js';

  let selectedDeployment = '';
  let selectedEnvironment = '';
  let tableName = '';
  let fieldsText = '';
  
  // Quick entry form variables
  let quickDisplayName = '';
  let quickType = 'Text';
  let quickRequired = false;
  let quickMaxLength = '';
  let quickOptionSet = '';
  let quickOptionSetSearch = '';
  let showQuickOptionSetDropdown = false;
  let publisherPrefix = '';
  let displayNameInput;
  
  // Option sets for choice fields
  let availableOptionSets = [];
  let filteredOptionSets = [];
  
  // Tables for lookup fields
  let availableTables = [];
  let filteredTables = [];
  let quickTargetTable = '';
  let quickTargetTableSearch = '';
  let showQuickTargetTableDropdown = false;
  
  // Table selector for main form
  let tableNameSearch = '';
  let filteredTablesForMain = [];
  let showTableNameDropdown = false;
  
  // UI state
  let showQuickAdd = true;
  
  // Field counter
  $: fieldCount = countFields(fieldsText);
  
  $: availableEnvironments = getAvailableEnvironments($config, selectedDeployment);
  
  // Load publisher prefix from localStorage
  onMount(() => {
    const savedPrefix = localStorage.getItem('publisherPrefix');
    if (savedPrefix) {
      publisherPrefix = savedPrefix;
    } else {
      publisherPrefix = 'appbase_';
    }
    
    // Set default deployment
    if ($deployments && $deployments.length > 0) {
      selectedDeployment = $deployments[0];
    }
    
    // Load option sets
    loadOptionSets();
    
    // Load tables
    loadTables();
    
    // Close dropdowns when clicking outside
    const handleClickOutside = (event) => {
      const target = event.target;
      const isTableNameSearch = target.closest('.toolbar-search');
      const isQuickOptionSet = target.closest('.choice-selector');
      
      if (!isTableNameSearch) {
        showTableNameDropdown = false;
      }
      
      if (!isQuickOptionSet) {
        showQuickOptionSetDropdown = false;
        showQuickTargetTableDropdown = false;
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
  
  async function loadOptionSets() {
    try {
      const response = await fetch('/api/helpers/option-sets/scan');
      const data = await response.json();
      availableOptionSets = data.optionSets || [];
      filteredOptionSets = availableOptionSets;
    } catch (error) {
      console.error('Error loading option sets:', error);
    }
  }
  
  async function loadTables() {
    if (!selectedDeployment || !selectedEnvironment) {
      return;
    }
    
    try {
      const response = await fetch('/api/helpers/tables/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment: selectedDeployment,
          environment: selectedEnvironment
        })
      });
      const data = await response.json();
      availableTables = data.tables || [];
      filteredTables = availableTables;
    } catch (error) {
      console.error('Error loading tables:', error);
    }
  }
  
  // Reload tables when deployment or environment changes
  $: if (selectedDeployment && selectedEnvironment) {
    loadTables();
  }
  
  // Filter option sets based on search
  $: {
    if (!quickOptionSetSearch || quickOptionSetSearch.trim() === '') {
      filteredOptionSets = availableOptionSets;
    } else {
      const search = quickOptionSetSearch.toLowerCase();
      filteredOptionSets = availableOptionSets.filter(os => 
        os.schemaName.toLowerCase().includes(search) ||
        os.displayName.toLowerCase().includes(search) ||
        os.options.some(opt => opt.label.toLowerCase().includes(search))
      );
    }
  }
  
  // Filter tables based on search (for lookup dropdown)
  $: {
    if (!quickTargetTableSearch || quickTargetTableSearch.trim() === '') {
      filteredTables = availableTables;
    } else {
      const search = quickTargetTableSearch.toLowerCase();
      filteredTables = availableTables.filter(t => 
        t.logicalName.toLowerCase().includes(search) ||
        t.displayName.toLowerCase().includes(search)
      );
    }
  }
  
  // Filter tables for main table selector - ensure it updates when availableTables or tableNameSearch changes
  $: availableTables, tableNameSearch, updateFilteredTablesForMain();
  
  function updateFilteredTablesForMain() {
    if (!tableNameSearch || tableNameSearch.trim() === '') {
      filteredTablesForMain = availableTables;
    } else {
      const search = tableNameSearch.toLowerCase();
      filteredTablesForMain = availableTables.filter(t => 
        t.logicalName.toLowerCase().includes(search) ||
        t.displayName.toLowerCase().includes(search)
      );
    }
  }
  
  // Sync tableName with manual search input
  $: if (tableNameSearch) {
    tableName = tableNameSearch;
  }
  
  // Save publisher prefix to localStorage when changed
  $: if (publisherPrefix) {
    localStorage.setItem('publisherPrefix', publisherPrefix);
  }
  
  function countFields(text) {
    if (!text || !text.trim()) return 0;
    const lines = text.trim().split('\n');
    return lines.filter(line => {
      const trimmed = line.trim();
      return trimmed && !trimmed.startsWith('#');
    }).length;
  }
  
  function generateSchemaName(displayName) {
    if (!displayName || !publisherPrefix) return '';
    // Convert display name to PascalCase without spaces/underscores
    // Preserve acronyms: "HR Request" -> "appbase_HRRequest", "HR Time Off Request" -> "appbase_HRTimeOffRequest"
    const cleaned = displayName
      .replace(/[^a-z0-9\s]/gi, '') // Remove special chars, keep letters, numbers, spaces
      .split(/\s+/) // Split on whitespace
      .filter(word => word.length > 0) // Remove empty strings
      .map(word => {
        // If word is all uppercase (acronym), keep it as-is
        if (/^[A-Z]+$/.test(word)) {
          return word;
        }
        // Otherwise, capitalize first letter and lowercase the rest
        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
      })
      .join(''); // Join without spaces
    return publisherPrefix + cleaned; // PascalCase schema name
  }
  
  function toProperCase(text) {
    if (!text) return text;
    return text
      .split(' ')
      .map(word => {
        if (word.length === 0) return word;
        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
      })
      .join(' ');
  }
  
  function handleQuickDisplayNameBlur() {
    quickDisplayName = toProperCase(quickDisplayName);
  }
  
  function selectMainTable(table) {
    tableName = table.logicalName;
    tableNameSearch = table.displayName;
    showTableNameDropdown = false;
  }
  
  function selectQuickTargetTable(table) {
    quickTargetTable = table.logicalName;
    quickTargetTableSearch = table.logicalName;
    showQuickTargetTableDropdown = false;
    if (!quickDisplayName) {
      quickDisplayName = table.displayName;
    }
  }
  
  function selectQuickOptionSet(os) {
    quickOptionSet = os.schemaName;
    quickOptionSetSearch = os.displayName;
    showQuickOptionSetDropdown = false;
    if (!quickDisplayName) {
      quickDisplayName = os.displayName;
    }
  }
  
  function addQuickField() {
    if (!quickDisplayName.trim()) {
      alert('Please enter a display name');
      return;
    }
    
    if (quickType === 'Choice' && !quickOptionSet) {
      alert('Please select an option set for the choice field');
      return;
    }
    
    if (quickType === 'Lookup' && !quickTargetTable) {
      alert('Please select a target table for the lookup field');
      return;
    }
    
    const schemaName = generateSchemaName(quickDisplayName);
    const required = quickRequired ? 'true' : 'false';
    const maxLen = quickMaxLength || '';
    
    // Build field line using BUILD.md format
    let fieldLine;
    if (quickType === 'Choice') {
      // Use BUILD.md format: "Display Name: Choice (OptionSetSchemaName)"
      fieldLine = `${quickDisplayName}: Choice (${quickOptionSet})`;
    } else if (quickType === 'Lookup') {
      // Use BUILD.md format: "Display Name: Lookup (TargetTable)"
      fieldLine = `${quickDisplayName}: Lookup (${quickTargetTable})`;
    } else {
      // Use BUILD.md format: "Display Name: Type"
      fieldLine = `${quickDisplayName}: ${quickType}`;
      if (quickRequired) {
        fieldLine += ', Required';
      }
      if (maxLen) {
        fieldLine += `, Max Length: ${maxLen}`;
      }
    }
    
    // Append to textarea
    if (fieldsText.trim()) {
      fieldsText += '\n' + fieldLine;
    } else {
      fieldsText = fieldLine;
    }
    
    // Clear quick form and refocus
    quickDisplayName = '';
    quickType = 'Text';
    quickRequired = false;
    quickMaxLength = '';
    quickOptionSet = '';
    quickOptionSetSearch = '';
    quickTargetTable = '';
    quickTargetTableSearch = '';
    
    // Focus back on display name input
    setTimeout(() => {
      if (displayNameInput) {
        displayNameInput.focus();
      }
    }, 0);
  }
  
  function handleQuickEntryKeydown(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      addQuickField();
    }
  }
  
  function getAvailableEnvironments(cfg, deployment) {
    if (!cfg || !deployment || !cfg.deployments || !cfg.deployments[deployment]) {
      return [];
    }
    const dep = cfg.deployments[deployment];
    if (dep.Environments) {
      return Object.entries(dep.Environments).map(([key, env]) => ({
        key,
        name: env.Name || key
      }));
    }
    return [];
  }

  async function createFields() {
    if (!selectedDeployment || !selectedEnvironment || !tableName || !fieldsText.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    // Parse field definitions
    const lines = fieldsText.trim().split('\n');
    const fields = [];
    const warnings = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!line.trim() || line.trim().startsWith('#')) continue;
      
      let schemaName, displayName, type, required, maxLength, optionSetSchemaName, targetTableLogicalName;
      
      // Check for BUILD.md format: "Display Name: Type" or "Display Name: Type (details)"
      if (line.includes(': ') && !line.includes('|') && !line.includes('::')) {
        const colonIndex = line.indexOf(': ');
        displayName = line.substring(0, colonIndex).trim();
        let typeInfo = line.substring(colonIndex + 2).trim();
        
        // Remove any trailing bullet points or dashes
        displayName = displayName.replace(/^[-•]\s*/, '');
        
        // Extract type (handle parentheses for lookups/choices)
        optionSetSchemaName = null;
        targetTableLogicalName = null;
        if (typeInfo.includes('(')) {
          const parenIndex = typeInfo.indexOf('(');
          type = typeInfo.substring(0, parenIndex).trim();
          // Extract content from parentheses for choice/lookup fields
          const parenContent = typeInfo.substring(parenIndex + 1, typeInfo.lastIndexOf(')')).trim();
          if (type === 'Choice' && parenContent) {
            optionSetSchemaName = parenContent;
          } else if (type === 'Lookup' && parenContent) {
            targetTableLogicalName = parenContent;
          }
        } else {
          type = typeInfo;
        }
        
        // Normalize type names
        if (type === 'Yes / No' || type === 'Yes/No') {
          type = 'YesNo';
        } else if (type === 'Lookup' || type === 'Reference') {
          type = 'Lookup';
          if (!targetTableLogicalName) {
            warnings.push(`Line ${i + 1}: Lookup field "${displayName}" missing target table in parentheses - skipping`);
            continue;
          }
        } else if (type === 'Choice' || type === 'Picklist' || type === 'OptionSet') {
          type = 'Choice';
          if (!optionSetSchemaName) {
            warnings.push(`Line ${i + 1}: Choice field "${displayName}" missing option set reference in parentheses - skipping`);
            continue;
          }
        }
        
        required = false;
        maxLength = null;
        schemaName = generateSchemaName(displayName);
      }
      // Check for manual schema override with "::" notation
      else if (line.includes('::')) {
        const [schema, rest] = line.split('::').map(p => p.trim());
        schemaName = schema;
        const parts = rest.split('|').map(p => p.trim());
        displayName = parts[0] || '';
        type = parts[1] || 'Text';
        required = parts[2] === 'true' || parts[2] === 'yes';
        maxLength = parts[3] ? parseInt(parts[3]) : null;
      }
      // Check for pipe-separated format
      else if (line.includes('|')) {
        const parts = line.split('|').map(p => p.trim());
        
        // If first part looks like a schema name (contains underscore), use legacy format
        if (parts[0].includes('_')) {
          // Legacy format: schemaName|displayName|type|required|maxLength
          schemaName = parts[0];
          displayName = parts[1] || '';
          type = parts[2] || 'Text';
          required = parts[3] === 'true' || parts[3] === 'yes';
          maxLength = parts[4] ? parseInt(parts[4]) : null;
        } else {
          // New format: displayName|type|required|maxLength (auto-generate schema)
          displayName = parts[0];
          type = parts[1] || 'Text';
          required = parts[2] === 'true' || parts[2] === 'yes';
          maxLength = parts[3] ? parseInt(parts[3]) : null;
          schemaName = generateSchemaName(displayName);
        }
      }
      // Simple format: just displayName (defaults to Text)
      else {
        displayName = line.trim();
        type = 'Text';
        required = false;
        maxLength = null;
        schemaName = generateSchemaName(displayName);
      }
      
      // Validate we have required fields
      if (!schemaName || !displayName) {
        alert(`Invalid field definition on line ${i + 1}: ${line}\nMissing schema name or display name`);
        return;
      }
      
      // Apply smart defaults for maxLength
      if (!maxLength) {
        if (type === 'Text' || type === 'String') maxLength = 100;
        else if (type === 'Memo' || type === 'MultilineText') maxLength = 4000;
        else if (type === 'RichText' || type === 'HTML') maxLength = 1048576;
        else if (type === 'URL' || type === 'Url') maxLength = 200;
      }
      
      const field = {
        schemaName,
        displayName,
        type,
        required,
        maxLength
      };
      
      // Add optionSetSchemaName for choice fields
      if (type === 'Choice' && optionSetSchemaName) {
        field.optionSetSchemaName = optionSetSchemaName;
      }
      
      // Add targetTableLogicalName for lookup fields
      if (type === 'Lookup' && targetTableLogicalName) {
        field.targetTableLogicalName = targetTableLogicalName;
      }
      
      fields.push(field);
    }
    
    // Show warnings if any
    if (warnings.length > 0) {
      const warningMsg = warnings.join('\n');
      if (!confirm(`${warnings.length} field(s) will be skipped:\n\n${warningMsg}\n\nContinue with remaining fields?`)) {
        return;
      }
    }

    if (fields.length === 0) {
      alert('No valid field definitions found');
      return;
    }

    // Start operation
    outputLines.set([]);
    operationStatus.set('running');

    try {
      const response = await fetch('/api/helpers/create-fields', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deployment: selectedDeployment,
          environment: selectedEnvironment,
          tableName,
          fields
        })
      });

      await streamResponse(response);
      
      // Clear form on success
      if ($operationStatus === 'success') {
        fieldsText = '';
      }
    } catch (error) {
      outputLines.update(lines => [...lines, `\n✗ Connection error: ${error.message}`]);
      operationStatus.set('error');
    }
  }


  const exampleFields = `# Example field definitions
# BUILD.md format (recommended):
Name: Text
Position Number: Text
Full Time Equivalent: Float
Authorized Date: Date
Is Supervisory: Yes / No
Description: Memo

# Or use simple format:
Customer Full Name
Email Address|URL
Notes|Memo`;


</script>

<div class="field-creator">
  <Header title="📋 Field Creator" description="Mass create fields on Dataverse tables">
    <button class="btn btn-primary" on:click={createFields} disabled={$operationStatus === 'running'}>
      {$operationStatus === 'running' ? '⏳ Creating...' : '▶ Create Fields'}
    </button>
  </Header>

  <!-- Toolbar -->
  <div class="toolbar">
    <div class="toolbar-row">
      <select class="toolbar-select" bind:value={selectedDeployment}>
        <option value="">Deployment</option>
        {#each $deployments as deployment}
          <option value={deployment}>{deployment}</option>
        {/each}
      </select>

      <select class="toolbar-select" bind:value={selectedEnvironment} disabled={!selectedDeployment}>
        <option value="">Environment</option>
        {#each availableEnvironments as env}
          <option value={env.key}>{env.name}</option>
        {/each}
      </select>

      <input 
        type="text" 
        class="toolbar-input"
        bind:value={publisherPrefix}
        placeholder="Publisher Prefix (e.g., appbase_)"
        pattern="[a-z0-9]+_"
      />

      <div class="toolbar-search-container">
        <input 
          type="text" 
          class="toolbar-input toolbar-search"
          bind:value={tableNameSearch}
          on:focus={() => showTableNameDropdown = true}
          on:blur={() => setTimeout(() => { showTableNameDropdown = false; }, 200)}
          placeholder="🔍 Search table..."
        />
        {#if showTableNameDropdown}
          <div class="toolbar-dropdown">
            {#if filteredTablesForMain.length === 0}
              <div class="no-results">No tables found</div>
            {:else}
              {#each filteredTablesForMain.slice(0, 8) as table}
                <div 
                  class="dropdown-item" 
                  class:selected={tableName === table.logicalName}
                  role="button"
                  tabindex="0"
                  on:click={() => selectMainTable(table)}
                  on:keydown={(e) => { 
                    if (e.key === 'Enter' || e.key === ' ') { 
                      selectMainTable(table);
                    } 
                  }}
                >
                  <div class="item-name">{table.displayName}</div>
                  <div class="item-schema">{table.logicalName}</div>
                </div>
              {/each}
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <div class="content">
    <!-- Main Content -->
      <div class="main-container">
        <!-- Left Column: Quick Add -->
        <div class="left-column">
          <!-- Collapsible Quick Add -->
          <div class="form-section collapsible">
            <button 
              class="section-header-collapsible" 
              type="button"
              on:click={() => showQuickAdd = !showQuickAdd}
            >
              <h3>⚡ Quick Add Field</h3>
              <span class="collapse-icon">{showQuickAdd ? '▼' : '▶'}</span>
            </button>
            
            {#if showQuickAdd}
              <div class="quick-entry-content">
                <div class="quick-entry-grid">
                  <div class="form-group quick-field">
                    <label for="quickDisplayName">Display Name</label>
                    <input 
                      type="text" 
                      id="quickDisplayName" 
                      bind:value={quickDisplayName}
                      bind:this={displayNameInput}
                      on:keydown={handleQuickEntryKeydown}
                      on:blur={handleQuickDisplayNameBlur}
                      placeholder="e.g., Customer Full Name"
                    />
                    {#if quickDisplayName}
                      <p class="help-text schema-preview">→ {generateSchemaName(quickDisplayName)}</p>
                    {/if}
                  </div>

                  <div class="form-group">
                    <label for="quickType">Type</label>
                    <select id="quickType" bind:value={quickType}>
                      <option value="Text">Text</option>
                      <option value="Memo">Memo (Multiline)</option>
                      <option value="RichText">Rich Text</option>
                      <option value="URL">URL</option>
                      <option value="Integer">Integer</option>
                      <option value="Float">Float</option>
                      <option value="Currency">Currency</option>
                      <option value="Date">Date</option>
                      <option value="DateTime">Date & Time</option>
                      <option value="YesNo">Yes/No</option>
                      <option value="Choice">Choice</option>
                      <option value="Lookup">Lookup</option>
                    </select>
                  </div>
                  
                  {#if quickType === 'Choice'}
                    <div class="form-group choice-selector">
                      <label for="quickOptionSetSearch">Option Set</label>
                      <input 
                        type="text" 
                        id="quickOptionSetSearch"
                        bind:value={quickOptionSetSearch}
                        on:focus={() => showQuickOptionSetDropdown = true}
                        placeholder="Search option sets..."
                      />
                      {#if showQuickOptionSetDropdown}
                        <div class="option-set-dropdown">
                          {#if filteredOptionSets.length === 0}
                            <div class="no-results">No option sets found</div>
                          {:else}
                            {#each filteredOptionSets.slice(0, 10) as os}
                              <div 
                                class="option-set-item" 
                                class:selected={quickOptionSet === os.schemaName}
                                role="button"
                                tabindex="0"
                                on:click={() => selectQuickOptionSet(os)}
                                on:keydown={(e) => { 
                                  if (e.key === 'Enter' || e.key === ' ') { 
                                    selectQuickOptionSet(os);
                                  } 
                                }}
                              >
                                <div class="os-name">{os.displayName}</div>
                                <div class="os-schema">{os.schemaName}</div>
                                <div class="os-options">{os.options.length} options</div>
                              </div>
                            {/each}
                          {/if}
                        </div>
                      {/if}
                    </div>
                  {/if}
                  
                  {#if quickType === 'Lookup'}
                    <div class="form-group choice-selector">
                      <label for="quickTargetTableSearch">Target Table</label>
                      <input 
                        type="text" 
                        id="quickTargetTableSearch"
                        bind:value={quickTargetTableSearch}
                        on:focus={() => showQuickTargetTableDropdown = true}
                        placeholder="Search tables..."
                      />
                      {#if showQuickTargetTableDropdown}
                        <div class="option-set-dropdown">
                          {#if filteredTables.length === 0}
                            <div class="no-results">No tables found</div>
                          {:else}
                            {#each filteredTables.slice(0, 15) as table}
                              <div 
                                class="option-set-item" 
                                class:selected={quickTargetTable === table.logicalName}
                                role="button"
                                tabindex="0"
                                on:click={() => selectQuickTargetTable(table)}
                                on:keydown={(e) => { 
                                  if (e.key === 'Enter' || e.key === ' ') { 
                                    selectQuickTargetTable(table);
                                  } 
                                }}
                              >
                                <div class="os-name">{table.displayName}</div>
                                <div class="os-schema">{table.logicalName}</div>
                                <div class="os-options">{table.primaryIdAttribute}</div>
                              </div>
                            {/each}
                          {/if}
                        </div>
                      {/if}
                    </div>
                  {/if}

                  <div class="form-group quick-checkbox">
                    <label>
                      <input type="checkbox" bind:checked={quickRequired} />
                      Required
                    </label>
                  </div>

                  {#if quickType === 'Text' || quickType === 'Memo' || quickType === 'URL' || quickType === 'RichText'}
                    <div class="form-group">
                      <label for="quickMaxLength">Max Length</label>
                      <input 
                        type="number" 
                        id="quickMaxLength" 
                        bind:value={quickMaxLength}
                        placeholder="Auto"
                      />
                    </div>
                  {/if}

                  <div class="form-group quick-button">
                    <button type="button" class="btn btn-add" on:click={addQuickField}>
                      ➕ Add
                    </button>
                  </div>
                </div>
                
                <p class="help-text">Press Enter in Display Name to quickly add • Schema name auto-generated from Display Name</p>
              </div>
            {/if}
          </div>
        </div>

        <!-- Middle Column: Field Definitions -->
        <div class="middle-column">
          <div class="form-section">
            <div class="section-header">
              <h3>Field Definitions</h3>
              {#if fieldCount > 0}
                <span class="field-count">✓ {fieldCount} field{fieldCount !== 1 ? 's' : ''} ready</span>
              {/if}
            </div>
            
            <div class="form-group">
              <label for="fieldsText">Fields (one per line)</label>
              <textarea 
                id="fieldsText"
                bind:value={fieldsText}
                placeholder={exampleFields}
              ></textarea>
              <p class="help-text">
                📋 <strong>Copy/paste from BUILD.md:</strong> Bullet points auto-removed • Format: <code>- Name: Type</code> or <code>Display Name: Type</code> • Choice fields: <code>- Name: Choice (OptionSetSchemaName)</code> • Lookup fields: <code>- Name: Lookup (TargetTable)</code> • Use <code>#</code> for comments
              </p>
            </div>
          </div>
        </div>

        <!-- Right Column: Help -->
        <div class="right-column">
          <div class="help-section">
            <h3>ℹ️ How to Use</h3>
            <ol class="help-list">
              <li>Select your deployment, environment, and publisher prefix at the top of the page</li>
              <li>Enter the table logical name (this changes table-by-table)</li>
              <li><strong>Copy/paste from BUILD.md</strong> or use Quick Add form</li>
              <li>Review and edit field definitions as needed</li>
              <li>For Choice fields, ensure the referenced option set exists in Choice Creator first</li>
              <li>Click "Create Fields" and monitor progress</li>
            </ol>
            <div class="info-box success">
              <strong>💡 Tip:</strong> The BUILD.md format (<code>- Name: Type</code>) works great for copy/paste from your documentation! Select your deployment and environment at the top of the page before creating fields.
            </div>
          </div>

          <div class="help-section">
            <h3>⚠️ Important Notes</h3>
            <ul class="help-list">
              <li>Schema names auto-generated with your prefix</li>
              <li>Schema names cannot be changed after creation</li>
              <li>Review all fields before clicking Create</li>
              <li>Choice fields reference global option sets created in Choice Creator</li>
              <li>Lookup fields create N:1 relationships with RemoveLink cascade delete</li>
              <li>Smart defaults for max lengths applied automatically</li>
              <li>Always test in a development environment first</li>
            </ul>
          </div>

          <div class="help-section">
            <h3>📋 Supported Field Types</h3>
            <div class="type-grid">
              <div>
                <strong>Text Types:</strong>
                <ul class="type-list-compact">
                  <li>Text - Single line (100)</li>
                  <li>Memo - Multiline (4000)</li>
                  <li>RichText - HTML (1MB)</li>
                  <li>URL - Web link (200)</li>
                </ul>
              </div>
              <div>
                <strong>Number Types:</strong>
                <ul class="type-list-compact">
                  <li>Integer - Whole number</li>
                  <li>Float - Decimal</li>
                  <li>Currency - Money</li>
                </ul>
              </div>
              <div>
                <strong>Other Types:</strong>
                <ul class="type-list-compact">
                  <li>Date - Date only</li>
                  <li>DateTime - Date & time</li>
                  <li>YesNo - Boolean</li>
                  <li>Choice - References option set</li>
                  <li>Lookup - References table</li>
                </ul>
              </div>
            </div>
            <div class="info-box">
              <strong>✨ Choice Fields:</strong> Use format <code>Display Name: Choice (OptionSetSchemaName)</code> in BUILD.md or select from dropdown in Quick Add. Option set must exist first.
            </div>
            <div class="info-box">
              <strong>🔗 Lookup Fields:</strong> Use format <code>Display Name: Lookup (TargetTable)</code> in BUILD.md or select from dropdown in Quick Add. Creates N:1 relationship with RemoveLink cascade delete. Self-referential lookups supported.
            </div>
          </div>
        </div>
      </div>
  </div>
</div>

<style>
  .field-creator {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  /* Toolbar */
  .toolbar {
    background: #252526;
    border-radius: 8px;
    padding: 16px;
    margin: 0 2rem 1.25rem 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    border: 1px solid #3c3c3c;
    position: relative;
  }

  .toolbar-row {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .toolbar-select {
    padding: 10px 16px;
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    font-size: 14px;
    font-family: inherit;
    min-width: 180px;
    cursor: pointer;
  }

  .toolbar-select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .toolbar-select:focus {
    outline: none;
    border-color: #0078d4;
    background: #252526;
  }

  .toolbar-input {
    padding: 10px 16px;
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    font-size: 14px;
    font-family: inherit;
    min-width: 200px;
  }

  .toolbar-input:focus {
    outline: none;
    border-color: #0078d4;
    background: #252526;
  }

  .toolbar-input.toolbar-search {
    flex: 1;
    min-width: 250px;
  }

  .toolbar-search-container {
    position: relative;
    flex: 1;
    min-width: 250px;
  }

  .toolbar-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    margin-top: 8px;
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    max-height: 400px;
    overflow-y: auto;
    z-index: 1000;
  }

  .dropdown-item {
    padding: 12px 16px;
    cursor: pointer;
    border-bottom: 1px solid #2d2d30;
    transition: background 0.15s;
  }

  .dropdown-item:hover,
  .dropdown-item.selected {
    background: #2d2d30;
  }

  .dropdown-item:last-child {
    border-bottom: none;
  }

  .item-name {
    font-size: 14px;
    color: #e0e0e0;
    font-weight: 500;
    margin-bottom: 4px;
  }

  .item-schema {
    font-size: 12px;
    color: #858585;
    font-family: 'Courier New', monospace;
  }

  .no-results {
    padding: 16px;
    text-align: center;
    color: #858585;
    font-size: 14px;
  }

  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .main-container {
    flex: 1;
    overflow-y: auto;
    padding: 1.25rem 2rem;
    display: grid;
    grid-template-columns: 380px 1fr 400px;
    gap: 1.5rem;
    align-items: start;
  }

  .left-column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .middle-column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-height: 0;
    height: calc(100vh - 280px);
  }

  .middle-column .form-section {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
  }

  .middle-column .form-section .section-header {
    flex-shrink: 0;
  }

  .middle-column .form-section .form-group {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
  }

  .middle-column .form-section .form-group label {
    flex-shrink: 0;
  }

  .middle-column .form-section .form-group textarea {
    flex: 1;
    min-height: 400px;
    resize: none;
  }

  .middle-column .form-section .form-group .help-text {
    flex-shrink: 0;
  }

  .right-column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    position: sticky;
    top: 1.25rem;
  }

  .form-section {
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 1rem;
  }

  .help-section {
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 1rem;
  }

  .form-section h3,
  .help-section h3 {
    margin: 0 0 0.75rem 0;
    font-size: 1.1rem;
    color: #ffffff;
    font-weight: 600;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .form-group {
    margin-bottom: 0.85rem;
  }

  .form-group:last-child {
    margin-bottom: 0;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.35rem;
    font-weight: 600;
    color: #cccccc;
    font-size: 13px;
  }

  .form-group input[type="text"],
  .form-group input[type="number"],
  .form-group select,
  .form-group textarea {
    width: 100%;
    padding: 0.5rem 0.65rem;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
    background: #1e1e1e;
    color: #e0e0e0;
    transition: border-color 0.2s, background 0.2s;
  }

  .form-group input[type="text"]:focus,
  .form-group input[type="number"]:focus,
  .form-group select:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #0078d4;
    background: #252526;
  }

  .form-group input[type="number"] {
    appearance: textfield;
    -moz-appearance: textfield;
  }

  .form-group input[type="number"]::-webkit-inner-spin-button,
  .form-group input[type="number"]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  .form-group textarea {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    resize: vertical;
  }

  .form-group select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .help-text {
    font-size: 12px;
    color: #808080;
    margin: 0.35rem 0 0 0;
  }

  .help-text code {
    background: #1e1e1e;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Courier New', monospace;
    color: #4fc3f7;
    font-size: 11px;
  }



  .type-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    color: #cccccc;
    font-size: 13px;
  }

  .type-grid strong {
    color: #4fc3f7;
    display: block;
    margin-bottom: 0.35rem;
  }

  .type-list-compact {
    margin: 0;
    padding-left: 1.25rem;
    list-style-type: disc;
  }

  .type-list-compact li {
    margin-bottom: 0.25rem;
    color: #cccccc;
  }

  @media (max-width: 768px) {
    .type-grid {
      grid-template-columns: 1fr;
      gap: 1rem;
    }
  }

  /* Info Box Styles */
  .info-box {
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 0.75rem;
    margin-top: 0.75rem;
    color: #cccccc;
    font-size: 13px;
    line-height: 1.5;
  }

  .info-box h4 {
    margin: 0 0 0.75rem 0;
    font-size: 14px;
    color: #4fc3f7;
    font-weight: 600;
  }

  .info-box.success {
    border-left: 4px solid #28a745;
  }

  .info-box.warning {
    border-left: 4px solid #f44336;
  }

  .info-box strong {
    color: #ffffff;
  }

  .info-box code {
    background: #252526;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Courier New', monospace;
    color: #4fc3f7;
    font-size: 11px;
  }

  .info-box ul, .info-box p {
    margin: 0.5rem 0;
  }

  .info-box ul {
    padding-left: 1.25rem;
  }

  .info-box li {
    margin-bottom: 0.25rem;
  }

  .help-list {
    margin: 0.35rem 0;
    padding-left: 1.5rem;
    color: #cccccc;
    font-size: 13px;
    line-height: 1.6;
  }

  .help-list li {
    margin-bottom: 0.5rem;
  }

  .help-list strong {
    color: #ffffff;
  }



  @media (max-width: 1400px) {
    .main-container {
      grid-template-columns: 1fr 400px;
    }
    
    .left-column,
    .middle-column {
      grid-column: 1;
    }
    
    .middle-column {
      grid-row: 2;
    }
    
    .right-column {
      grid-column: 2;
      grid-row: 1 / 3;
    }
  }

  @media (max-width: 1000px) {
    .main-container {
      grid-template-columns: 1fr;
      padding: 1.5rem;
    }
    
    .left-column,
    .middle-column,
    .right-column {
      grid-column: 1;
    }
    
    .right-column {
      position: static;
      grid-row: auto;
    }
  }



  .collapsible {
    cursor: pointer;
  }

  .section-header-collapsible {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 0;
    background: transparent;
    border: none;
    cursor: pointer;
    user-select: none;
    text-align: left;
    color: inherit;
  }

  .section-header-collapsible:hover {
    opacity: 0.8;
  }

  .section-header-collapsible h3 {
    margin: 0;
  }

  .collapse-icon {
    color: #0078d4;
    font-size: 12px;
    transition: transform 0.2s;
  }

  .quick-entry-content {
    padding-top: 0.75rem;
  }

  .quick-entry-grid {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .quick-field {
    min-width: 0;
  }

  .quick-checkbox {
    display: flex;
    align-items: center;
    padding: 0.65rem 0.75rem;
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    transition: background 0.2s, border-color 0.2s;
  }

  .quick-checkbox:hover {
    background: #252526;
    border-color: #4c4c4c;
  }

  .quick-checkbox label {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin: 0;
    cursor: pointer;
    user-select: none;
    width: 100%;
    color: #cccccc;
    font-weight: 500;
    font-size: 13px;
  }

  .quick-checkbox input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    appearance: none;
    -webkit-appearance: none;
    background: #1e1e1e;
    border: 2px solid #4c4c4c;
    border-radius: 3px;
    position: relative;
    transition: all 0.2s;
    flex-shrink: 0;
  }

  .quick-checkbox input[type="checkbox"]:hover {
    border-color: #6c6c6c;
    background: #252526;
  }

  .quick-checkbox input[type="checkbox"]:focus {
    outline: none;
    border-color: #0078d4;
    box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.2);
  }

  .quick-checkbox input[type="checkbox"]:checked {
    background: #0078d4;
    border-color: #0078d4;
  }

  .quick-checkbox input[type="checkbox"]:checked::after {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 12px;
    font-weight: bold;
  }

  .quick-button {
    padding-top: 0;
  }

  .btn-add {
    width: 100%;
    padding: 0.5rem 1rem;
    background: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 14px;
  }

  .btn-add:hover {
    background: #218838;
  }

  .btn-add:active {
    background: #1e7e34;
  }

  .schema-preview {
    color: #4fc3f7 !important;
    font-family: 'Consolas', 'Courier New', monospace;
    margin-top: 0.25rem !important;
  }
  
  .choice-selector {
    grid-column: span 2;
    position: relative;
  }
  
  .option-set-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    min-width: 400px;
    max-width: 600px;
    max-height: 300px;
    overflow-y: auto;
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    margin-top: 0.25rem;
    z-index: 1000;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  }
  
  .option-set-item {
    padding: 0.75rem;
    cursor: pointer;
    border-bottom: 1px solid #2d2d30;
    transition: background 0.2s;
  }
  
  .option-set-item:hover {
    background: #2d2d30;
  }
  
  .option-set-item.selected {
    background: #0078d4;
  }
  
  .option-set-item:last-child {
    border-bottom: none;
  }
  
  .os-name {
    font-weight: 600;
    color: #e0e0e0;
    margin-bottom: 0.25rem;
  }
  
  .os-schema {
    font-size: 12px;
    color: #4fc3f7;
    font-family: 'Consolas', 'Courier New', monospace;
    margin-bottom: 0.25rem;
  }
  
  .os-options {
    font-size: 11px;
    color: #888;
  }
  
  .no-results {
    padding: 1rem;
    text-align: center;
    color: #888;
    font-style: italic;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .section-header h3 {
    margin: 0;
  }

  .field-count {
    color: #28a745;
    font-weight: 600;
    font-size: 14px;
  }

</style>
