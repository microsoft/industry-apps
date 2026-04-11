<script>
  import { onMount } from 'svelte';
  import Header from '../lib/Header.svelte';

  let selectedModule = '';
  let selectedEntity = '';
  
  let availableModules = [];
  let layouts = []; // List of layout files {entity_name, file_path, display_name, modified_date, yaml_content}
  
  // Extraction state
  let extracting = false;
  let extractionResult = null;
  
  // Preview state
  let currentLayout = null; // Selected layout for preview
  
  // Build state
  let validating = false;
  let building = false;
  let buildingAll = false;
  let validationResult = null;
  let buildResult = null;
  let dryRunResult = null;
  let buildAllResult = null;
  
  // Quick Create state
  let addingQuickCreate = false;
  let buildingQuickCreate = false;
  let buildingAllQuickCreate = false;
  let quickCreateResult = null;
  let quickCreateBuildResult = null;
  let quickCreateBuildAllResult = null;
  
  // Load modules on mount
  onMount(() => {
    loadModules();
  });
  
  // Load existing layouts when module changes
  $: if (selectedModule) {
    loadLayouts();
  }
  
  async function loadModules() {
    try {
      const response = await fetch('/api/formbuilder/list-modules');
      const data = await response.json();
      
      if (data.success && data.modules) {
        availableModules = data.modules;
      }
    } catch (error) {
      console.error('Error loading modules:', error);
    }
  }
  
  async function extractAllEntities(overwrite = false) {
    if (!selectedModule) return;
    
    extracting = true;
    extractionResult = null;
    layouts = [];
    selectedEntity = '';
    currentLayout = null;
    
    try {
      const response = await fetch('/api/formbuilder/extract-all-entities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          overwrite: overwrite
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        extractionResult = {
          success: true,
          total: data.total_count,
          created: data.extracted.filter(e => !e.existed).length,
          skipped: data.skipped_count
        };
        
        // Load the layout files
        await loadLayouts();
      } else {
        extractionResult = { success: false, error: data.error };
      }
    } catch (error) {
      extractionResult = { success: false, error: error.message };
    } finally {
      extracting = false;
    }
  }
  
  async function loadLayouts() {
    if (!selectedModule) return;
    
    try {
      const response = await fetch(`/api/formbuilder/list-layouts?module_path=${encodeURIComponent(selectedModule)}`);
      const data = await response.json();
      
      if (data.success) {
        layouts = data.layouts;
      } else {
        layouts = [];
      }
    } catch (error) {
      console.error('Error loading layouts:', error);
      layouts = [];
    }
  }
  
  async function selectEntity(layout) {
    selectedEntity = layout.entity_name;
    
    // Clear all success/result messages when switching entities
    quickCreateResult = null;
    quickCreateBuildResult = null;
    quickCreateBuildAllResult = null;
    validationResult = null;
    buildResult = null;
    dryRunResult = null;
    buildAllResult = null;
    
    // Reload this specific entity from disk to get latest content
    try {
      const response = await fetch(`/api/formbuilder/list-layouts?module_path=${encodeURIComponent(selectedModule)}`);
      const data = await response.json();
      
      if (data.success) {
        // Find the updated layout for this entity
        const updatedLayout = data.layouts.find(l => l.entity_name === layout.entity_name);
        if (updatedLayout) {
          currentLayout = updatedLayout;
          console.log('Selected entity:', layout.entity_name);
          console.log('YAML content length:', updatedLayout.yaml_content?.length || 0);
          console.log('First 100 chars:', updatedLayout.yaml_content?.substring(0, 100));
          // Also update the layouts array to keep everything in sync
          const index = layouts.findIndex(l => l.entity_name === layout.entity_name);
          if (index !== -1) {
            layouts[index] = updatedLayout;
          }
        } else {
          currentLayout = layout; // Fallback to passed layout
        }
      } else {
        currentLayout = layout; // Fallback to passed layout
      }
    } catch (error) {
      console.error('Error reloading entity from disk:', error);
      currentLayout = layout; // Fallback to passed layout
    }
    
    // Clear previous results
    validationResult = null;
    buildResult = null;
    dryRunResult = null;
  }
  
  async function reloadFromDisk() {
    // Reload layout files from disk without regenerating them
    await loadLayouts();
    
    // Update currentLayout if one is selected
    if (currentLayout) {
      const updatedLayout = layouts.find(l => l.entity_name === currentLayout.entity_name);
      if (updatedLayout) {
        currentLayout = updatedLayout;
      }
    }
  }
  
  async function recreateEntity(layout, event) {
    event.stopPropagation(); // Prevent entity selection
    
    // Regenerate YAML file by re-extracting from entity schema (overwrites existing file)
    try {
      const response = await fetch('/api/formbuilder/extract-single-entity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          entity_name: layout.entity_name
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Reload layouts to get the updated file
        await loadLayouts();
        
        // If this was the selected entity, refresh its content
        if (currentLayout && currentLayout.entity_name === layout.entity_name) {
          const updatedLayout = layouts.find(l => l.entity_name === layout.entity_name);
          if (updatedLayout) {
            currentLayout = updatedLayout;
          }
        }
        
        // Show success message briefly
        alert(`✓ Recreated layout for ${layout.display_name}`);
      } else {
        alert(`✗ Failed to recreate layout: ${data.error}`);
      }
    } catch (error) {
      alert(`✗ Error recreating layout: ${error.message}`);
    }
  }
  
  function recreateAllLayouts() {
    // Regenerate ALL YAML files by re-extracting from entity schemas (overwrites existing files)
    extractAllEntities(true);
  }
  
  function openInVSCode() {
    if (currentLayout) {
      // Show a message with the file path
      alert(`Open this file in VS Code:\n\n${currentLayout.file_path}\n\nEdit the YAML and click the entity again to refresh the preview.`);
    }
  }
  
  async function validateYaml() {
    if (!currentLayout) return;
    
    validating = true;
    validationResult = null;
    
    try {
      const response = await fetch('/api/formbuilder/validate-yaml', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          yaml_config: currentLayout.yaml_content,
          module_path: selectedModule
        })
      });
      
      const data = await response.json();
      validationResult = data;
    } catch (error) {
      validationResult = { success: false, error: error.message };
    } finally {
      validating = false;
    }
  }
  
  async function buildForm(dryRun = false) {
    if (!currentLayout) return;
    
    building = true;
    buildResult = null;
    dryRunResult = null;
    
    try {
      const response = await fetch('/api/formbuilder/build-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: currentLayout.file_path,
          dry_run: dryRun
        })
      });
      
      const data = await response.json();
      
      if (dryRun) {
        dryRunResult = data;
      } else {
        buildResult = data;
      }
    } catch (error) {
      if (dryRun) {
        dryRunResult = { success: false, error: error.message };
      } else {
        buildResult = { success: false, error: error.message };
      }
    } finally {
      building = false;
    }
  }
  
  async function buildAllForms() {
    if (!selectedModule) return;
    
    buildingAll = true;
    buildAllResult = null;
    
    try {
      const response = await fetch('/api/formbuilder/build-all-forms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule
        })
      });
      
      const data = await response.json();
      buildAllResult = data;
    } catch (error) {
      buildAllResult = { success: false, error: error.message };
    } finally {
      buildingAll = false;
    }
  }
  
  // Quick Create Functions
  async function addQuickCreateSections() {
    if (!selectedModule) return;
    
    addingQuickCreate = true;
    quickCreateResult = null;
    
    try {
      const response = await fetch('/api/formbuilder/add-quickcreate-sections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          overwrite: false
        })
      });
      
      const data = await response.json();
      quickCreateResult = data;
      
      // Reload layouts to show updated quick_create sections
      if (data.success) {
        await loadLayouts();
        if (currentLayout) {
          // Reload current layout to show updated content
          const updatedLayout = layouts.find(l => l.entity_name === currentLayout.entity_name);
          if (updatedLayout) {
            currentLayout = updatedLayout;
          }
        }
      }
    } catch (error) {
      quickCreateResult = { success: false, error: error.message };
    } finally {
      addingQuickCreate = false;
    }
  }
  
  async function buildQuickCreateForm() {
    if (!currentLayout) return;
    
    buildingQuickCreate = true;
    quickCreateBuildResult = null;
    
    try {
      const response = await fetch('/api/formbuilder/build-quickcreate-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          entity_name: currentLayout.entity_name,
          use_single_column: true,
          force: false
        })
      });
      
      const data = await response.json();
      quickCreateBuildResult = data;
    } catch (error) {
      quickCreateBuildResult = { success: false, error: error.message };
    } finally {
      buildingQuickCreate = false;
    }
  }
  
  async function buildAllQuickCreateForms() {
    if (!selectedModule) return;
    
    buildingAllQuickCreate = true;
    quickCreateBuildAllResult = null;
    
    try {
      const response = await fetch('/api/formbuilder/build-all-quickcreate-forms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule,
          use_single_column: true,
          force: false
        })
      });
      
      const data = await response.json();
      quickCreateBuildAllResult = data;
    } catch (error) {
      quickCreateBuildAllResult = { success: false, error: error.message };
    } finally {
      buildingAllQuickCreate = false;
    }
  }
  
  function hasQuickCreateSection(layout) {
    if (!layout || !layout.yaml_content) return false;
    return layout.yaml_content.includes('quick_create:');
  }
  
  function getQuickCreateFields(layout) {
    if (!layout || !layout.yaml_content) return [];
    
    const lines = layout.yaml_content.split('\n');
    const fields = [];
    let inQuickCreate = false;
    
    for (const line of lines) {
      if (line.trim() === 'quick_create:') {
        inQuickCreate = true;
        continue;
      }
      if (inQuickCreate) {
        if (line.startsWith('  - ')) {
          fields.push(line.trim().substring(2));
        } else if (line.trim() && !line.trim().startsWith('#')) {
          // End of quick_create section
          break;
        }
      }
    }
    
    return fields;
  }
  
  function formatDate(isoDate) {
    const date = new Date(isoDate);
    return date.toLocaleString();
  }
</script>

<div class="page-container">
  <Header title="Form Builder" subtitle="Generate forms from entity schemas with AI-assisted YAML layouts" />
  
  <div class="content">
    <!-- Module Selection -->
    <div class="card">
      <div class="module-header">
        <div class="form-group">
          <label>Module</label>
          <select bind:value={selectedModule}>
            <option value="">Select Module</option>
            {#each availableModules as module}
              <option value={module.path}>{module.display_name}</option>
            {/each}
          </select>
        </div>
        
        {#if selectedModule}
          <div class="button-group">
            <button 
              class="btn btn-secondary" 
              on:click={reloadFromDisk}
              disabled={extracting || buildingAll}
              title="Reload layout files from disk without modifying them"
            >
              ↻ Reload from Disk
            </button>
            <button 
              class="btn btn-warning" 
              on:click={recreateAllLayouts}
              disabled={extracting || buildingAll}
              title="Regenerate ALL layout files from entity schemas (overwrites existing files)"
            >
              {extracting ? '⏳ Recreating...' : '🔄 Recreate All Layouts'}
            </button>
            <button 
              class="btn btn-primary" 
              on:click={buildAllForms}
              disabled={extracting || buildingAll || layouts.length === 0}
              title="Build forms for all entities in this module"
            >
              {buildingAll ? '⏳ Building...' : '🔨 Build All Forms'}
            </button>
          </div>
          <div class="button-group quickcreate-buttons">
            <button 
              class="btn btn-info" 
              on:click={addQuickCreateSections}
              disabled={extracting || addingQuickCreate || layouts.length === 0}
              title="Add quick_create sections to all entity YAML files with smart defaults"
            >
              {addingQuickCreate ? '⏳ Adding...' : '➕ Add Quick Create Sections'}
            </button>
            <button 
              class="btn btn-success" 
              on:click={buildAllQuickCreateForms}
              disabled={extracting || buildingAllQuickCreate || layouts.length === 0}
              title="Build Quick Create forms for all entities with quick_create sections"
            >
              {buildingAllQuickCreate ? '⏳ Building...' : '⚡ Build All Quick Create Forms'}
            </button>
          </div>
        {/if}
      </div>
      
      {#if quickCreateResult}
        <div class="extraction-summary">
          {#if quickCreateResult.success}
            <div class="alert alert-success">
              ✓ Quick Create sections added: {quickCreateResult.updated} entities updated, {quickCreateResult.skipped} skipped
            </div>
          {:else}
            <div class="alert alert-error">
              ✗ Failed to add Quick Create sections: {quickCreateResult.error}
            </div>
          {/if}
        </div>
      {/if}
      
      {#if quickCreateBuildAllResult}
        <div class="extraction-summary">
          {#if quickCreateBuildAllResult.success}
            <div class="alert alert-success">
              ✓ Quick Create forms built: {quickCreateBuildAllResult.success_count} created, {quickCreateBuildAllResult.skipped_count} skipped, {quickCreateBuildAllResult.error_count} errors
            </div>
          {:else}
            <div class="alert alert-error">
              ✗ Failed to build Quick Create forms: {quickCreateBuildAllResult.error}
            </div>
          {/if}
        </div>
      {/if}
      
      {#if extractionResult}
        <div class="extraction-summary">
          {#if extractionResult.success}
            <div class="alert alert-success">
              ✓ Extraction complete: {extractionResult.created} layouts created, {extractionResult.skipped} already existed ({extractionResult.total} total entities)
            </div>
          {:else}
            <div class="alert alert-error">
              ✗ Extraction failed: {extractionResult.error}
            </div>
          {/if}
        </div>
      {/if}
      
      {#if buildAllResult}
        <div class="extraction-summary">
          {#if buildAllResult.success}
            <div class="alert alert-success">
              <strong>✓ Build All Complete!</strong>
              <p>{buildAllResult.success_count} forms built successfully, {buildAllResult.error_count} errors ({buildAllResult.total} total)</p>
              {#if buildAllResult.results && buildAllResult.results.length > 0}
                <details>
                  <summary>View Details</summary>
                  <ul class="result-list">
                    {#each buildAllResult.results as result}
                      <li class:success={result.success} class:error={!result.success}>
                        {#if result.success}
                          ✓ <strong>{result.entity}</strong>: {result.stats.tabs} tabs, {result.stats.sections} sections, {result.stats.fields} fields
                        {:else}
                          ✗ <strong>{result.entity}</strong>: {result.error}
                        {/if}
                      </li>
                    {/each}
                  </ul>
                </details>
              {/if}
            </div>
          {:else}
            <div class="alert alert-error">
              ✗ Build All failed: {buildAllResult.error}
            </div>
          {/if}
        </div>
      {/if}
    </div>
    
    {#if selectedModule && !extracting}
      <!-- Two-column layout: Entity List | Preview + Build -->
      <div class="workspace">
        <!-- Left: Entity List -->
        <div class="entity-list-panel">
          <h3>Entities ({layouts.length})</h3>
          
          {#if layouts.length === 0}
            <div class="empty-state">
              <p>No layout files found.</p>
              <p class="help-text">Select a different module or check that entities have custom fields.</p>
            </div>
          {:else}
            <div class="entity-list">
              {#each layouts as layout}
                <div 
                  class="entity-item {selectedEntity === layout.entity_name ? 'selected' : ''}"
                  on:click={() => selectEntity(layout)}
                >
                  <div class="entity-info">
                    <div class="entity-name">{layout.display_name}</div>
                    <div class="entity-meta">{layout.entity_name}</div>
                    <div class="entity-date">{formatDate(layout.modified_date)}</div>
                  </div>
                  <button 
                    class="recreate-btn" 
                    on:click={(e) => recreateEntity(layout, e)}
                    title="Recreate layout file from entity schema (overwrites file)"
                  >
                    🔄
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </div>
        
        <!-- Right: Preview + Build -->
        <div class="preview-panel">
          {#if !currentLayout}
            <div class="empty-state">
              <h3>Select an Entity</h3>
              <p>Click an entity from the list on the left to preview its layout and build the form.</p>
            </div>
          {:else}
            <div class="preview-content">
              <!-- Entity Header -->
              <div class="entity-header">
                <div>
                  <h3>{currentLayout.display_name}</h3>
                  <p class="file-path">{currentLayout.file_path}</p>
                </div>
                <button class="btn btn-secondary" on:click={openInVSCode}>
                  📝 Open in VS Code
                </button>
              </div>
              
              <!-- Actions -->
              <div class="actions-section">
                <h4>🔨 Build Main Form</h4>
                <p class="help-text">Validate and build the form from the saved YAML file</p>
                
                <div class="button-group">
                  <button 
                    class="btn btn-secondary" 
                    on:click={validateYaml}
                    disabled={validating}
                  >
                    {validating ? 'Validating...' : '✓ Validate YAML'}
                  </button>
                  
                  <button 
                    class="btn btn-secondary" 
                    on:click={() => buildForm(true)}
                    disabled={building}
                  >
                    👁️ Preview (Dry Run)
                  </button>
                  
                  <button 
                    class="btn btn-primary" 
                    on:click={() => buildForm(false)}
                    disabled={building}
                  >
                    {building ? 'Building...' : '🔨 Build Form'}
                  </button>
                </div>
                
                <!-- Results -->
                {#if validationResult}
                  <div class="alert {validationResult.valid ? 'alert-success' : 'alert-error'}">
                    <strong>{validationResult.valid ? '✓ Valid YAML' : '✗ Invalid YAML'}</strong>
                    
                    {#if validationResult.errors && validationResult.errors.length > 0}
                      <ul class="error-list">
                        {#each validationResult.errors as error}
                          <li>❌ {error}</li>
                        {/each}
                      </ul>
                    {/if}
                    
                    {#if validationResult.warnings && validationResult.warnings.length > 0}
                      <ul class="warning-list">
                        {#each validationResult.warnings as warning}
                          <li>⚠️ {warning}</li>
                        {/each}
                      </ul>
                    {/if}
                  </div>
                {/if}
                
                {#if dryRunResult}
                  <div class="alert alert-info">
                    <strong>📋 Preview of Operations</strong>
                    {#if dryRunResult.success}
                      <p>{dryRunResult.operations.length} operations will be performed:</p>
                      <ul class="operation-list">
                        {#each dryRunResult.operations as op}
                          <li>
                            {#if op.type === 'add_tab'}
                              ➕ Add tab: <strong>{op.tab_label}</strong>
                            {:else if op.type === 'add_section'}
                              ➕ Add section: <strong>{op.section_label}</strong> ({op.columns} column{op.columns > 1 ? 's' : ''})
                            {:else if op.type === 'add_fields'}
                              ➕ Add {op.field_count} fields to <strong>{op.section_label}</strong>
                            {/if}
                          </li>
                        {/each}
                      </ul>
                    {:else}
                      <p class="error-text">❌ {dryRunResult.error}</p>
                    {/if}
                  </div>
                {/if}
                
                {#if buildResult}
                  <div class="alert {buildResult.success ? 'alert-success' : 'alert-error'}">
                    {#if buildResult.success}
                      <strong>✓ Form Built Successfully!</strong>
                      <p>{buildResult.message}</p>
                      {#if buildResult.stats}
                        <p class="stats">
                          Added: {buildResult.stats.tabs_added} tabs, 
                          {buildResult.stats.sections_added} sections, 
                          {buildResult.stats.fields_added} fields
                        </p>
                      {/if}
                      <p class="file-path">Form updated: {buildResult.form_path}</p>
                      <p class="next-steps">
                        Next: Run <code>pac solution sync --packagetype Both</code> to sync changes
                      </p>
                    {:else}
                      <strong>✗ Build Failed</strong>
                      <p class="error-text">{buildResult.error}</p>
                    {/if}
                  </div>
                {/if}
              </div>
              
              <!-- Quick Create -->
              <div class="actions-section quickcreate-section">
                <h4>⚡ Quick Create Form</h4>
                <p class="help-text">Generate a simplified Quick Create form with 3-5 key fields</p>
                
                {#if !hasQuickCreateSection(currentLayout)}
                  <div class="quickcreate-info">
                    <p>No quick_create section in YAML</p>
                    <p class="help-text">Add one with smart defaults using the button below</p>
                  </div>
                  
                  <div class="button-group">
                    <button 
                      class="btn btn-info" 
                      on:click={addQuickCreateSections}
                      disabled={addingQuickCreate}
                      title="Add quick_create section to this entity's YAML"
                    >
                      {addingQuickCreate ? 'Adding...' : '➕ Add Quick Create Section'}
                    </button>
                  </div>
                {:else}
                  <div class="quickcreate-info">
                    <p><strong>✓ Quick Create Configured</strong></p>
                    <p class="field-list-preview">
                      Fields ({getQuickCreateFields(currentLayout).length}): 
                      {getQuickCreateFields(currentLayout).join(', ')}
                    </p>
                  </div>
                  
                  <div class="button-group">
                    <button 
                      class="btn btn-success" 
                      on:click={buildQuickCreateForm}
                      disabled={buildingQuickCreate}
                    >
                      {buildingQuickCreate ? 'Building...' : '⚡ Build Quick Create Form'}
                    </button>
                  </div>
                  
                  {#if quickCreateBuildResult}
                    <div class="alert {quickCreateBuildResult.success ? 'alert-success' : 'alert-error'}">
                      {#if quickCreateBuildResult.success}
                        <strong>✓ Quick Create Form Created!</strong>
                        <p>Form GUID: <code>{quickCreateBuildResult.form_guid}</code></p>
                        <p>Fields: {quickCreateBuildResult.field_count} ({quickCreateBuildResult.fields.join(', ')})</p>
                        <p class="file-path">Created:</p>
                        <ul>
                          <li>{quickCreateBuildResult.unmanaged_file}</li>
                          <li>{quickCreateBuildResult.managed_file}</li>
                        </ul>
                        <p class="next-steps">
                          Next: Run <code>pac solution sync --packagetype Both</code> to sync changes
                        </p>
                      {:else}
                        <strong>✗ Quick Create Build Failed</strong>
                        <p class="error-text">{quickCreateBuildResult.error}</p>
                      {/if}
                    </div>
                  {/if}
                {/if}
              </div>
              
              <!-- YAML Preview -->
              <div class="yaml-preview-section">
                <div class="section-header">
                  <h4>Layout YAML (Read-Only)</h4>
                  <p class="help-text">Edit this file in VS Code, then click the entity again to refresh</p>
                </div>
                {#key currentLayout.entity_name}
                  <textarea 
                    class="yaml-preview" 
                    readonly
                  >{currentLayout.yaml_content || ''}</textarea>
                {/key}
              </div>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .page-container {
    padding: 20px;
    max-width: 1600px;
    margin: 0 auto;
  }
  
  .content {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .card {
    background: #0d0d0d;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 24px;
  }
  
  .module-header {
    display: flex;
    gap: 16px;
    align-items: flex-end;
  }
  
  .module-header .form-group {
    flex: 1;
  }
  
  .extraction-summary {
    margin-top: 16px;
  }
  
  .workspace {
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 20px;
  }
  
  .entity-list-panel {
    background: #0d0d0d;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 16px;
    height: calc(100vh - 340px);
    max-height: 700px;
    display: flex;
    flex-direction: column;
  }
  
  .entity-list-panel h3 {
    margin: 0 0 16px 0;
    color: #e0e0e0;
    font-size: 16px;
    font-weight: 600;
  }
  
  .entity-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .entity-item {
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 12px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    min-width: 0;
  }
  
  .entity-item:hover {
    border-color: #0078d4;
    background: #1e1e1e;
  }
  
  .entity-item.selected {
    background: rgba(0, 120, 212, 0.1);
    border-color: #0078d4;
  }
  
  .entity-info {
    flex: 1;
    min-width: 0;
    overflow: hidden;
  }
  
  .entity-name {
    color: #e0e0e0;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .entity-meta {
    color: #a0a0a0;
    font-size: 12px;
    font-family: 'Courier New', monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .entity-date {
    color: #808080;
    font-size: 11px;
    margin-top: 4px;
  }
  
  .recreate-btn {
    background: #3c3c3c;
    border: none;
    border-radius: 4px;
    color: #e0e0e0;
    padding: 6px 10px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
    flex-shrink: 0;
  }
  
  .recreate-btn:hover {
    background: #ffb900;
    color: #000;
  }
  
  .preview-panel {
    background: #0d0d0d;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 24px;
    height: calc(100vh - 340px);
    max-height: 700px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #a0a0a0;
    text-align: center;
  }
  
  .empty-state h3 {
    color: #e0e0e0;
    margin-bottom: 8px;
  }
  
  .preview-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
    height: 100%;
    overflow-y: auto;
  }
  
  .entity-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding-bottom: 16px;
    border-bottom: 1px solid #3c3c3c;
    flex-shrink: 0;
  }
  
  .entity-header h3 {
    margin: 0;
    color: #e0e0e0;
    font-size: 20px;
  }
  
  .yaml-preview-section {
    display: flex;
    flex-direction: column;
    gap: 12px;
    flex: 1;
    min-height: 400px;
  }
  
  .section-header h4 {
    margin: 0 0 4px 0;
    color: #e0e0e0;
    font-size: 16px;
    font-weight: 600;
  }
  
  .yaml-preview {
    width: 100%;
    height: 100%;
    min-height: 400px;
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    padding: 12px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    resize: none;
    overflow-y: auto;
  }
  
  .actions-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
    flex-shrink: 0;
    padding-top: 16px;
    border-top: 1px solid #3c3c3c;
  }
  
  .actions-section h4 {
    margin: 0;
    color: #e0e0e0;
    font-size: 16px;
    font-weight: 600;
  }
  
  .quickcreate-section {
    background: rgba(16, 110, 190, 0.05);
    border: 1px solid rgba(0, 120, 212, 0.2);
    border-radius: 4px;
    padding: 16px;
    margin-top: 8px;
  }
  
  .quickcreate-buttons {
    margin-top: 8px;
  }
  
  .quickcreate-info {
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 12px;
  }
  
  .quickcreate-info p {
    margin: 4px 0;
    color: #c0c0c0;
  }
  
  .quickcreate-info strong {
    color: #4ec9b0;
  }
  
  .field-list-preview {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 13px;
    color: #9cdcfe;
  }
  
  .btn-info {
    background: #0e639c;
    color: white;
  }
  
  .btn-info:hover:not(:disabled) {
    background: #1177bb;
  }
  
  .btn-success {
    background: #107c10;
    color: white;
  }
  
  .btn-success:hover:not(:disabled) {
    background: #0e6a0e;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .form-group label {
    color: #b0b0b0;
    font-size: 14px;
    font-weight: 500;
  }
  
  select {
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    padding: 8px 12px;
    font-size: 14px;
    font-family: inherit;
  }
  
  select:focus {
    outline: none;
    border-color: #0078d4;
  }
  
  .btn {
    padding: 10px 20px;
    border-radius: 4px;
    border: none;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-primary {
    background: #0078d4;
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    background: #106ebe;
  }
  
  .btn-secondary {
    background: #3c3c3c;
    color: #e0e0e0;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background: #4c4c4c;
  }
  
  .btn-warning {
    background: #ffb900;
    color: #000;
  }
  
  .btn-warning:hover:not(:disabled) {
    background: #ffc933;
  }
  
  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .button-group {
    display: flex;
    gap: 12px;
  }
  
  .alert {
    padding: 16px;
    border-radius: 4px;
  }
  
  .alert-success {
    background: rgba(0, 120, 212, 0.1);
    border: 1px solid #0078d4;
    color: #4db8ff;
  }
  
  .alert-error {
    background: rgba(232, 17, 35, 0.1);
    border: 1px solid #e81123;
    color: #ff6b7a;
  }
  
  .alert-info {
    background: rgba(255, 185, 0, 0.1);
    border: 1px solid #ffb900;
    color: #ffd666;
  }
  
  .alert strong {
    display: block;
    margin-bottom: 8px;
    font-size: 15px;
  }
  
  .error-list, .warning-list, .operation-list, .result-list {
    margin: 12px 0 0 0;
    padding-left: 20px;
  }
  
  .error-list li, .warning-list li, .operation-list li, .result-list li {
    margin: 6px 0;
    font-size: 14px;
  }
  
  .result-list li.success {
    color: #4ec9b0;
  }
  
  .result-list li.error {
    color: #f48771;
  }
  
  details {
    margin-top: 12px;
    cursor: pointer;
  }
  
  details summary {
    color: #0078d4;
    font-weight: 500;
  }
  
  details summary:hover {
    text-decoration: underline;
  }
  
  .help-text {
    color: #a0a0a0;
    font-size: 14px;
    margin: 0;
    line-height: 1.5;
  }
  
  .file-path {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #a0a0a0;
    margin: 8px 0;
  }
  
  .stats {
    font-size: 14px;
    margin: 8px 0;
  }
  
  .next-steps {
    margin: 12px 0 0 0;
    font-size: 14px;
  }
  
  code {
    background: #1a1a1a;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
  }
</style>
