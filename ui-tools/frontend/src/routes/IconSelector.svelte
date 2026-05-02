<script>
  import { onMount } from 'svelte';
  import { modules } from '../lib/stores.js';
  import Header from '../lib/Header.svelte';
  import ModuleSelector from '../lib/ModuleSelector.svelte';
  
  // State
  let selectedModulePath = '';
  let selectedModule = null;
  let entities = [];
  let selectedEntity = null;
  
  // Icon picker state
  let iconSearchQuery = '';
  let iconResults = [];
  let selectedIcon = null;
  let iconSources = { tabler: true, material: true, lucide: true, phosphor: true };
  let isSearching = false;
  let hasSearched = false;
  
  // Progress
  let totalEntities = 0;
  let completedEntities = 0;
  
  // Apply to module state
  let isApplying = false;
  let applyResult = null;
  
  let searchDebounceTimer = null;
  
  onMount(async () => {
    await loadProgress();
  });
  
  // Handle module selection change
  async function handleModuleChange(event) {
    const { path, module } = event.detail;
    selectedModulePath = path;
    selectedModule = module;
    
    if (path) {
      await loadEntitiesForModule(path);
    } else {
      entities = [];
    }
  }
  
  // Load entities for selected module
  async function loadEntitiesForModule(modulePath) {
    try {
      const encodedModule = encodeURIComponent(modulePath);
      const response = await fetch(`/api/icon-selector/modules/${encodedModule}/entities`);
      
      if (!response.ok) {
        console.error('Failed to load entities for module:', modulePath);
        entities = [];
        return;
      }
      
      const entitiesData = await response.json();
      
      // Load icon selections to show icons next to entities
      const selectionsResponse = await fetch('/api/icon-selector/selections/all');
      let selections = {};
      if (selectionsResponse.ok) {
        selections = await selectionsResponse.json();
      }
      
      // Merge selection data into entities
      entities = entitiesData.map(entity => ({
        ...entity,
        icon_name: selections[entity.logical_name]?.icon_name,
        icon_source: selections[entity.logical_name]?.icon_source
      }));
    } catch (error) {
      console.error('Error loading entities:', error);
      entities = [];
    }
  }
  
  // Load overall progress
  async function loadProgress() {
    try {
      const response = await fetch('/api/icon-selector/progress');
      if (!response.ok) throw new Error('Failed to load progress');
      const progress = await response.json();
      totalEntities = progress.total;
      completedEntities = progress.selected;
    } catch (error) {
      console.error('Error loading progress:', error);
    }
  }
  
  // Select an entity to show icon picker
  function selectEntityForIconPicker(entity) {
    selectedEntity = entity;
    hasSearched = false;
    iconResults = [];
    selectedIcon = null;
    
    // Generate smart search query from entity display name
    const words = entity.display_name
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 3 && !['table', 'entity', 'data', 'from'].includes(w));
    
    iconSearchQuery = words.slice(0, 3).join(' ');
    
    // Auto-search
    if (iconSearchQuery) {
      searchIcons();
    }
  }
  
  // Search for icons
  async function searchIcons() {
    if (!iconSearchQuery.trim()) {
      iconResults = [];
      hasSearched = false;
      return;
    }
    
    isSearching = true;
    hasSearched = true;
    
    try {
      // Build sources array from checkboxes
      const sources = [];
      if (iconSources.tabler) sources.push('tabler');
      if (iconSources.material) sources.push('material-design');
      if (iconSources.lucide) sources.push('lucide');
      if (iconSources.phosphor) sources.push('phosphor');
      
      const response = await fetch('/api/icon-selector/icons/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: iconSearchQuery,
          sources: sources,
          limit: 100
        })
      });
      
      if (!response.ok) throw new Error('Search failed');
      
      iconResults = await response.json();
    } catch (error) {
      console.error('Error searching icons:', error);
      iconResults = [];
    } finally {
      isSearching = false;
    }
  }
  
  // Handle search input with debounce
  function handleSearchInput() {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      searchIcons();
    }, 300);
  }
  
  // Select an icon
  function selectIcon(icon) {
    selectedIcon = icon;
  }
  
  // Confirm icon selection
  async function confirmSelection() {
    if (!selectedIcon || !selectedEntity) return;
    
    try {
      const response = await fetch(`/api/icon-selector/entities/${selectedEntity.logical_name}/icon`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entity_logical_name: selectedEntity.logical_name,
          icon_name: selectedIcon.name,
          icon_source: selectedIcon.source
        })
      });
      
      if (!response.ok) throw new Error('Failed to save selection');
      
      // Update entity in list
      const entityIndex = entities.findIndex(e => e.logical_name === selectedEntity.logical_name);
      if (entityIndex !== -1) {
        entities[entityIndex].has_selection = true;
        entities[entityIndex].icon_name = selectedIcon.name;
        entities[entityIndex].icon_source = selectedIcon.source;
        entities = [...entities]; // Trigger reactivity
      }
      
      await loadProgress();
      
      // Clear selection UI but keep entity selected
      selectedIcon = null;
      iconResults = [];
      hasSearched = false;
    } catch (error) {
      console.error('Error saving selection:', error);
      alert(`Error saving selection: ${error.message}`);
    }
  }
  
  // Clear entity selection
  async function clearSelection(entity, event) {
    event.stopPropagation();
    
    if (!confirm(`Clear icon selection for ${entity.display_name}?`)) return;
    
    try {
      const response = await fetch(`/api/icon-selector/entities/${entity.logical_name}/icon`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Failed to clear selection');
      
      // Update entity in list
      const entityIndex = entities.findIndex(e => e.logical_name === entity.logical_name);
      if (entityIndex !== -1) {
        entities[entityIndex].has_selection = false;
        entities[entityIndex].icon_name = null;
        entities[entityIndex].icon_source = null;
        entities = [...entities];
      }
      
      await loadProgress();
    } catch (error) {
      console.error('Error clearing selection:', error);
      alert(`Error clearing selection: ${error.message}`);
    }
  }
  
  // Export selections
  async function exportSelections() {
    try {
      const response = await fetch('/api/icon-selector/selections/export');
      if (!response.ok) throw new Error('Export failed');
      
      const result = await response.json();
      alert(`✅ Exported ${result.count} icon selections to:\n${result.export_file}`);
    } catch (error) {
      console.error('Error exporting:', error);
      alert(`Error exporting: ${error.message}`);
    }
  }
  
  // Apply to current module
  async function applyToModule() {
    if (!selectedModulePath) {
      alert('Please select a module first');
      return;
    }
    
    if (!selectedModule) {
      alert('Module data not loaded');
      return;
    }
    
    const moduleEntities = entities.filter(e => e.has_selection).length;
    if (moduleEntities === 0) {
      alert('No icons selected for this module yet');
      return;
    }
    
    if (!confirm(`Apply ${moduleEntities} icon(s) to module:\n${selectedModulePath}\n\nThis will:\n1. Validate selections\n2. Create WebResource files\n3. Update Entity.xml files\n4. Update Solution.xml\n\nContinue?`)) {
      return;
    }
    
    isApplying = true;
    applyResult = null;
    
    try {
      const response = await fetch('/api/icon-selector/apply-to-module', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ module_path: selectedModulePath })
      });
      
      if (!response.ok) throw new Error('Apply failed');
      
      const result = await response.json();
      applyResult = result;
      
      // Log full details to console
      console.log('Apply to Module Result:', result);
      
      if (result.success) {
        // Show detailed output
        let output = `✅ Successfully applied icons to module!\n\n`;
        output += `WebResources created: ${result.webresources_created || 'N/A'}\n`;
        output += `Entity.xml updated: ${result.entities_updated || 'N/A'}\n`;
        output += `Solution.xml updated: ${result.solutions_updated || 'N/A'}\n\n`;
        
        // Show script outputs if available
        if (result.steps && result.steps.length > 0) {
          output += `\nScript Details:\n`;
          result.steps.forEach(step => {
            output += `\n${step.name}: ${step.success ? '✓ Success' : '✗ Failed'}\n`;
            if (step.output) {
              // Show last few lines of output
              const lines = step.output.trim().split('\n');
              const lastLines = lines.slice(-3).join('\n');
              output += `${lastLines}\n`;
            }
            if (!step.success && step.error) {
              output += `Error: ${step.error}\n`;
            }
          });
        }
        
        output += `\nNext steps:\n1. Review changes (git diff)\n2. Build and test the solution`;
        alert(output);
      } else {
        let errorMsg = `❌ Error applying icons:\n${result.error || 'Unknown error'}\n\n`;
        
        // Show step details
        if (result.steps && result.steps.length > 0) {
          errorMsg += `\nStep Details:\n`;
          result.steps.forEach(step => {
            errorMsg += `\n${step.name}: ${step.success ? '✓' : '✗'}\n`;
            if (step.error) {
              errorMsg += `Error: ${step.error}\n`;
            }
            if (step.output) {
              errorMsg += `Output: ${step.output.substring(0, 200)}...\n`;
            }
          });
        }
        
        errorMsg += `\nCheck browser console for full details.`;
        console.error('Apply error:', result);
        alert(errorMsg);
      }
    } catch (error) {
      console.error('Error applying to module:', error);
      alert(`Error applying to module: ${error.message}`);
    } finally {
      isApplying = false;
    }
  }
  
  // Get icon SVG URL
  function getIconSvgUrl(iconName, source) {
    return `/api/icon-selector/icons/${encodeURIComponent(iconName)}/svg?source=${source}`;
  }
  
  // Computed
  $: progressPercentage = totalEntities > 0 ? Math.round((completedEntities / totalEntities) * 100) : 0;
  $: selectedEntities = entities.filter(e => e.has_selection).length;
</script>

<div class="icon-selector">
  <Header 
    title="Icon Selector" 
    subtitle=""
  />

  <div class="container">
    <!-- Compact Top Bar: Module + Progress + Export -->
    <div class="top-bar">
      <div class="module-selector-compact">
        <ModuleSelector 
          bind:value={selectedModulePath}
          on:change={handleModuleChange}
          placeholder="-- Select a module --"
          showLabel={false}
        />
      </div>
      
      <div class="progress-compact">
        <div class="progress-bar">
          <div class="progress-fill" style="width: {progressPercentage}%"></div>
        </div>
        <span class="progress-text">{completedEntities} / {totalEntities}</span>
      </div>
      
      {#if completedEntities > 0}
        <button class="export-btn-compact" on:click={exportSelections}>
          📦 Export
        </button>
      {/if}
      
      {#if selectedModulePath && selectedEntities > 0}
        <button 
          class="apply-btn-compact" 
          on:click={applyToModule}
          disabled={isApplying}
        >
          {isApplying ? '⏳ Applying...' : '⚙️ Apply to Module'}
        </button>
      {/if}
    </div>

    <!-- Two Column Layout: Entities + Icon Picker -->
    {#if selectedModulePath}
      {#if entities.length > 0}
        <div class="two-column-layout">
          <!-- Left Column: Entity List -->
          <div class="entities-column">
            <h3>Entities ({entities.length})</h3>
            <div class="entities-list">
              {#each entities as entity}
                <button 
                  class="entity-card" 
                  class:has-selection={entity.has_selection}
                  class:selected={selectedEntity && selectedEntity.logical_name === entity.logical_name}
                  on:click={() => selectEntityForIconPicker(entity)}
                >
                  <div class="entity-header">
                    {#if entity.has_selection && entity.icon_name && entity.icon_source}
                      <img 
                        src={getIconSvgUrl(entity.icon_name, entity.icon_source)} 
                        alt={entity.icon_name}
                        class="entity-icon"
                      />
                    {:else if entity.has_selection}
                      <span class="check-mark">✓</span>
                    {/if}
                    <h4>{entity.display_name}</h4>
                  </div>
                  <p class="entity-logical-name">{entity.logical_name}</p>
                </button>
              {/each}
            </div>
          </div>
          
          <!-- Right Column: Icon Picker -->
          <div class="icon-picker-column">
            {#if selectedEntity}
              <div class="picker-header">
                <div>
                  <h3>Select Icon</h3>
                  <p class="entity-name">{selectedEntity.display_name}</p>
                </div>
                {#if selectedEntity.has_selection}
                  <button class="btn-clear" on:click={(e) => clearSelection(selectedEntity, e)}>
                    🗑️ Clear Selection
                  </button>
                {/if}
              </div>
              
              <div class="search-section">
                <div class="search-bar">
                  <input
                    type="text"
                    bind:value={iconSearchQuery}
                    on:input={handleSearchInput}
                    on:focus={(e) => e.target.select()}
                    placeholder="Search icons (e.g., calendar, money, user)..."
                    class="search-input"
                  />
                  <button class="search-btn" on:click={searchIcons} disabled={isSearching}>
                    {isSearching ? '⏳' : '🔍'} Search
                  </button>
                </div>
                
                <div class="source-filters">
                  <label>
                    <input type="checkbox" bind:checked={iconSources.tabler} on:change={searchIcons} />
                    Tabler (5,039)
                  </label>
                  <label>
                    <input type="checkbox" bind:checked={iconSources.material} on:change={searchIcons} />
                    Material Design (7,447)
                  </label>
                  <label>
                    <input type="checkbox" bind:checked={iconSources.lucide} on:change={searchIcons} />
                    Lucide (1,703)
                  </label>
                  <label>
                    <input type="checkbox" bind:checked={iconSources.phosphor} on:change={searchIcons} />
                    Phosphor (1,512)
                  </label>
                </div>
              </div>
              
              {#if isSearching}
                <div class="loading-state">
                  <p>Searching icons...</p>
                </div>
              {:else if iconResults.length > 0}
                <div class="icons-grid">
                  {#each iconResults as icon}
                    <button
                      class="icon-card"
                      class:selected={selectedIcon && selectedIcon.name === icon.name && selectedIcon.source === icon.source}
                      on:click={() => selectIcon(icon)}
                    >
                      <div class="icon-preview">
                        <img src={getIconSvgUrl(icon.name, icon.source)} alt={icon.name} />
                      </div>
                      <div class="icon-info">
                        <p class="icon-name">{icon.display_name}</p>
                        <p class="icon-source">{icon.source}</p>
                      </div>
                    </button>
                  {/each}
                </div>
                
                {#if selectedIcon}
                  <div class="selection-footer">
                    <div class="selected-icon-info">
                      <div class="selected-icon-preview">
                        <img src={getIconSvgUrl(selectedIcon.name, selectedIcon.source)} alt={selectedIcon.name} />
                      </div>
                      <div>
                        <p class="selected-icon-name">{selectedIcon.display_name}</p>
                        <p class="selected-icon-source">{selectedIcon.source}</p>
                      </div>
                    </div>
                    <button class="btn-confirm" on:click={confirmSelection}>
                      ✓ Confirm Selection
                    </button>
                  </div>
                {/if}
              {:else if hasSearched}
                <div class="empty-state">
                  <p>No icons found for "{iconSearchQuery}"</p>
                  <p class="hint">Try different keywords or enable more sources</p>
                </div>
              {:else}
                <div class="empty-state">
                  <p>👈 Select an entity to search for icons</p>
                </div>
              {/if}
            {:else}
              <div class="empty-state">
                <p>👈 Select an entity to start</p>
              </div>
            {/if}
          </div>
        </div>
      {:else}
        <div class="empty-state">
          <p>No entities found in this module</p>
        </div>
      {/if}
    {:else}
      <div class="empty-state">
        <p>👆 Select a module to view its entities</p>
      </div>
    {/if}
  </div>
</div>

<style>
  .icon-selector {
    padding: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .container {
    max-width: 100%;
    margin: 0;
    padding: 1rem 2rem;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  /* Compact Top Bar */
  .top-bar {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #1e293b;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
  }

  .module-selector-compact {
    flex: 0 0 300px;
  }

  .progress-compact {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .progress-bar {
    flex: 1;
    height: 24px;
    background: #0f172a;
    border-radius: 12px;
    overflow: hidden;
    position: relative;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    transition: width 0.3s ease;
  }

  .progress-text {
    color: #cbd5e1;
    font-weight: 600;
    font-size: 13px;
    white-space: nowrap;
    min-width: 80px;
  }

  .export-btn-compact {
    background: #10b981;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .export-btn-compact:hover {
    background: #059669;
  }

  .apply-btn-compact {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .apply-btn-compact:hover:not(:disabled) {
    background: #2563eb;
  }

  .apply-btn-compact:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Two Column Layout */
  .two-column-layout {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 1rem;
    flex: 1;
    min-height: 0;
  }

  /* Left Column: Entities */
  .entities-column {
    display: flex;
    flex-direction: column;
    background: #1e293b;
    border-radius: 8px;
    padding: 1rem;
    overflow: hidden;
  }

  .entities-column h3 {
    margin: 0 0 0.75rem 0;
    color: #e0e0e0;
    font-size: 14px;
    font-weight: 600;
  }

  .entities-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    overflow-y: auto;
    padding-right: 0.5rem;
    flex: 1;
    min-height: 0;
  }

  .entity-card {
    background: #0f172a;
    border: 2px solid #334155;
    border-radius: 8px;
    padding: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    width: 100%;
  }

  .entity-card:hover {
    border-color: #3b82f6;
    transform: translateX(4px);
  }

  .entity-card.selected {
    border-color: #3b82f6;
    background: rgba(59, 130, 246, 0.1);
  }

  .entity-card.has-selection {
    border-left: 4px solid #10b981;
  }

  .entity-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .check-mark {
    color: #10b981;
    font-size: 16px;
    font-weight: bold;
    flex-shrink: 0;
  }

  .entity-icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    filter: brightness(0) invert(1);
  }

  .entity-card h4 {
    margin: 0;
    color: #f1f5f9;
    font-size: 14px;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .entity-logical-name {
    margin: 0;
    color: #64748b;
    font-size: 11px;
    font-family: 'Consolas', 'Monaco', monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* Right Column: Icon Picker */
  .icon-picker-column {
    display: flex;
    flex-direction: column;
    background: #1e293b;
    border-radius: 8px;
    padding: 1rem;
    overflow: hidden;
  }

  .picker-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
  }

  .picker-header h3 {
    margin: 0;
    color: #f1f5f9;
    font-size: 16px;
    font-weight: 600;
  }

  .picker-header .entity-name {
    margin: 0.25rem 0 0 0;
    color: #94a3b8;
    font-size: 13px;
  }

  .btn-clear {
    background: #ef4444;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-clear:hover {
    background: #dc2626;
  }

  /* Empty State */
  .empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: #64748b;
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #1e293b;
    border-radius: 8px;
  }

  .empty-state p {
    margin: 0.5rem 0;
  }

  .empty-state .hint {
    font-size: 14px;
    color: #475569;
  }

  /* Search Section */
  .search-section {
    margin-bottom: 1rem;
  }

  .search-bar {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .search-input {
    flex: 1;
    background: #0f172a;
    border: 2px solid #334155;
    color: #f1f5f9;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    font-size: 13px;
  }

  .search-input:focus {
    outline: none;
    border-color: #3b82f6;
  }

  .search-btn {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
  }

  .search-btn:hover:not(:disabled) {
    background: #2563eb;
  }

  .search-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .source-filters {
    display: flex;
    gap: 1.5rem;
  }

  .source-filters label {
    color: #94a3b8;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }

  .source-filters input[type="checkbox"] {
    cursor: pointer;
  }

  /* Loading State */
  .loading-state {
    text-align: center;
    padding: 3rem;
    color: #64748b;
  }

  /* Icons Grid */
  .icons-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 130px));
    gap: 0.75rem;
    overflow-y: auto;
    padding: 0.5rem;
    flex: 1;
    min-height: 0;
    justify-content: start;
    align-content: start;
  }

  .icon-card {
    background: #1e293b;
    border: 2px solid #334155;
    border-radius: 8px;
    padding: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .icon-card:hover {
    border-color: #3b82f6;
    transform: translateY(-2px);
  }

  .icon-card.selected {
    border-color: #10b981;
    background: rgba(16, 185, 129, 0.1);
  }

  .icon-preview {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .icon-preview img {
    width: 100%;
    height: 100%;
    filter: brightness(0) invert(1);
  }

  .icon-info {
    text-align: center;
    width: 100%;
  }

  .icon-name {
    color: #cbd5e1;
    font-size: 11px;
    margin: 0;
    word-break: break-word;
    font-weight: 500;
  }

  .icon-source {
    color: #64748b;
    font-size: 10px;
    margin: 0;
  }

  /* Selection Footer */
  .selection-footer {
    border-top: 2px solid #334155;
    padding-top: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .selected-icon-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .selected-icon-preview {
    width: 48px;
    height: 48px;
    background: #1e293b;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .selected-icon-preview img {
    width: 32px;
    height: 32px;
    filter: brightness(0) invert(1);
  }

  .selected-icon-name {
    margin: 0;
    color: #f1f5f9;
    font-weight: 600;
    font-size: 14px;
  }

  .selected-icon-source {
    margin: 0.25rem 0 0 0;
    color: #64748b;
    font-size: 12px;
  }

  .btn-confirm {
    background: #10b981;
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
  }

  .btn-confirm:hover {
    background: #059669;
    transform: translateY(-1px);
  }
</style>
