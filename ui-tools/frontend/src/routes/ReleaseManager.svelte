<script>
  import { onMount } from 'svelte';
  import { modules, loadModules, outputLines, activeOperation, operationStatus, currentOperationId } from '../lib/stores.js';
  import Header from '../lib/Header.svelte';
  
  // Helper to generate operation IDs
  function generateOperationId() {
    return `op-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  let selectedCategory = 'all';
  let selectedModule = null;
  let selectedStep = null;
  let releaseType = 'standard'; // 'standard', 'hotfix', or 'keep-current'
  let currentVersion = '';
  let newVersion = '';
  let releaseNotes = '';
  let searchQuery = '';
  let categories = new Set();
  
  // Environment override for version sync
  let syncTenant = '';
  let syncEnvironment = '';
  let useCustomEnvironment = false;
  
  // Step checkboxes (all enabled by default)
  let steps = {
    updateVersion: true,
    updateChangelog: true,
    createReleaseNotes: true,
    buildPackages: true,
    gitCommit: true,
    gitTag: true,
    githubRelease: true
  };
  
  // Step completion tracking
  let stepCompletion = {
    updateVersion: false,
    updateChangelog: false,
    createReleaseNotes: false,
    buildPackages: false,
    gitCommit: false,
    gitTag: false,
    githubRelease: false
  };
  
  // Step metadata
  const stepDetails = {
    updateVersion: {
      title: 'Update Version & Sync',
      description: 'Updates the solution version in Dataverse online, then syncs back to local. Uses the configured source environment for this module.',
      instructions: [
        'Reads solution unique name from Solution.xml',
        'Updates version online using pac solution online-version',
        'Syncs solution from online to local using pac solution sync',
        'Verifies Solution.xml was updated with new version'
      ],
      icon: '🔢'
    },
    updateChangelog: {
      title: 'Update CHANGELOG.md',
      description: 'Transforms the "## Unreleased" section into a versioned release section with current date.',
      instructions: [
        'Locates the "## Unreleased" section',
        'Replaces with "## [version] - YYYY-MM-DD"',
        'Preserves all changelog content'
      ],
      icon: '📝'
    },
    createReleaseNotes: {
      title: 'Create Release Notes',
      description: 'Release notes are auto-populated from CHANGELOG.md when you select a module. Review and edit them here before the GitHub release.',
      instructions: [
        'Notes are extracted from the "## Unreleased" section',
        'Auto-populated when module is selected',
        'Edit the content as needed in the textarea',
        'These notes will be included in the GitHub release'
      ],
      icon: '📋'
    },
    buildPackages: {
      title: 'Build Solution Packages',
      description: 'Compiles both managed and unmanaged solution packages using .NET SDK.',
      instructions: [
        'Runs dotnet build in Release configuration',
        'Generates managed .zip in bin/Release',
        'Generates unmanaged .zip in bin/Release'
      ],
      icon: '📦'
    },
    gitCommit: {
      title: 'Git Commit',
      description: 'Stages and commits all module changes with a release commit message, then pushes to remote.',
      instructions: [
        'Stages all files in the module folder',
        'Excludes .zip package files (not committed to source)',
        'Creates commit: "Release [module] v[version]"',
        'Pushes commit to remote repository'
      ],
      icon: '💾'
    },
    gitTag: {
      title: 'Create Git Tag',
      description: 'Creates a Git tag for this release version and pushes it to the remote repository.',
      instructions: [
        'Creates tag: module-name/vX.Y.Z.W',
        'Tags the current commit',
        'Pushes tag to remote repository'
      ],
      icon: '🏷️'
    },
    githubRelease: {
      title: 'Create GitHub Release',
      description: 'Publishes a GitHub release with release notes and package attachments.',
      instructions: [
        'Uses GitHub CLI (gh) to create release',
        'Attaches managed and unmanaged .zip files',
        'Includes changelog-based release notes',
        'Returns release URL'
      ],
      icon: '🚀'
    }
  };
  
  // Workflow state
  let validationErrors = [];
  let validationWarnings = [];
  let isValidating = false;
  let isExecuting = false;
  let executionProgress = [];
  let githubReleaseUrl = '';
  let showExecutionModal = false;
  let showCompletionModal = false;
  
  // Changelog preview state
  let showChangelogPreview = false;
  let changelogBefore = '';
  let changelogAfter = '';
  let isLoadingChangelog = false;
  
  // Build packages state
  let builtPackages = [];
  let isLoadingPackages = false;
  
  onMount(async () => {
    await loadModules();
  });
  
  // Update categories when modules change
  $: if ($modules) {
    categories = new Set($modules.map(m => m.category));
  }
  
  // Filter modules by selected category and search query
  $: filteredModules = $modules.filter(m => {
    const matchesCategory = selectedCategory === 'all' || m.category === selectedCategory;
    const matchesSearch = m.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });
  
  // Auto-load packages when buildPackages step is selected
  $: if (selectedStep === 'buildPackages' && selectedModule) {
    checkPackages();
  }
  
  async function selectModule(module) {
    selectedModule = module;
    selectedStep = null;
    validationErrors = [];
    validationWarnings = [];
    
    // Reset completion status when selecting a new module
    stepCompletion = {
      updateVersion: false,
      updateChangelog: false,
      createReleaseNotes: false,
      buildPackages: false,
      gitCommit: false,
      gitTag: false,
      githubRelease: false
    };
    
    // Set default environment from module config
    syncTenant = module.tenant || '';
    syncEnvironment = module.sourceEnvironment || '';
    useCustomEnvironment = false;
    
    // Load current version
    try {
      const response = await fetch(`http://localhost:8000/api/release/get-version?module_path=${encodeURIComponent(module.path)}`);
      const data = await response.json();
      currentVersion = data.version;
      calculateNewVersion();
      
      // Auto-load changelog
      await loadChangelog();
    } catch (error) {
      console.error('Error loading version:', error);
      currentVersion = 'Unknown';
    }
  }
  
  function calculateNewVersion() {
    if (!currentVersion || currentVersion === 'Unknown') {
      newVersion = '';
      return;
    }
    
    const parts = currentVersion.split('.').map(Number);
    if (parts.length !== 4) {
      newVersion = '';
      return;
    }
    
    if (releaseType === 'standard') {
      // Increment minor (2nd), reset build and revision to 0
      newVersion = `${parts[0]}.${parts[1] + 1}.0.0`;
    } else if (releaseType === 'hotfix') {
      // Increment build (3rd), reset revision to 0
      newVersion = `${parts[0]}.${parts[1]}.${parts[2] + 1}.0`;
    } else if (releaseType === 'keep-current') {
      // Keep the current version as-is
      newVersion = currentVersion;
    }
  }
  
  // Watch for release type changes
  $: if (releaseType) {
    calculateNewVersion();
  }
  
  async function startRelease() {
    if (!selectedModule) {
      alert('Please select a module first');
      return;
    }
    
    isValidating = true;
    validationErrors = [];
    validationWarnings = [];
    
    try {
      const response = await fetch(`http://localhost:8000/api/release/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ module_path: selectedModule.path })
      });
      
      const data = await response.json();
      validationErrors = data.errors || [];
      validationWarnings = data.warnings || [];
      
      if (validationErrors.length === 0) {
        // Proceed to execution
        executeRelease();
      }
    } catch (error) {
      console.error('Validation error:', error);
      validationErrors = [`Failed to validate: ${error.message}`];
    } finally {
      isValidating = false;
    }
  }
  
  async function loadChangelog() {
    try {
      const response = await fetch(`http://localhost:8000/api/release/extract-changelog?module_path=${encodeURIComponent(selectedModule.path)}&version=${encodeURIComponent(newVersion)}`);
      const data = await response.json();
      const content = data.content || '';
      const header = `Release Notes - ${selectedModule.displayName} ${newVersion}\n\n`;
      releaseNotes = header + content;
    } catch (error) {
      console.error('Error loading changelog:', error);
      const header = `Release Notes - ${selectedModule.displayName} ${newVersion}\n\n`;
      releaseNotes = header;
    }
  }
  
  function copyReleaseNotesToClipboard() {
    if (navigator.clipboard && releaseNotes) {
      navigator.clipboard.writeText(releaseNotes).then(() => {
        // Visual feedback could be added here
        console.log('Release notes copied to clipboard');
      }).catch(err => {
        console.error('Failed to copy to clipboard:', err);
      });
    }
  }
  
  async function previewChangelogUpdate() {
    isLoadingChangelog = true;
    try {
      const response = await fetch(`http://localhost:8000/api/release/preview-changelog`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule.path,
          new_version: newVersion
        })
      });
      const data = await response.json();
      if (data.success) {
        changelogBefore = data.before;
        changelogAfter = data.after;
        showChangelogPreview = true;
      } else {
        alert(`Failed to preview changelog: ${data.error}`);
      }
    } catch (error) {
      console.error('Error previewing changelog:', error);
      alert(`Failed to preview changelog: ${error.message}`);
    } finally {
      isLoadingChangelog = false;
    }
  }
  
  async function checkPackages() {
    if (!selectedModule) return;
    
    isLoadingPackages = true;
    try {
      const response = await fetch(`http://localhost:8000/api/release/check-packages?module_path=${encodeURIComponent(selectedModule.path)}`);
      const data = await response.json();
      if (data.success) {
        builtPackages = data.packages || [];
      } else {
        console.error('Failed to check packages:', data.error);
        builtPackages = [];
      }
    } catch (error) {
      console.error('Error checking packages:', error);
      builtPackages = [];
    } finally {
      isLoadingPackages = false;
    }
  }
  
  async function executeRelease() {
    showExecutionModal = true;
    isExecuting = true;
    executionProgress = [];
    
    const enabledSteps = Object.keys(steps).filter(key => steps[key]);
    
    try {
      const response = await fetch(`http://localhost:8000/api/release/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_path: selectedModule.path,
          module_name: selectedModule.name,
          release_type: releaseType,
          new_version: newVersion,
          release_notes: releaseNotes,
          enabled_steps: enabledSteps,
          sync_tenant: useCustomEnvironment ? syncTenant : selectedModule.tenant,
          sync_environment: useCustomEnvironment ? syncEnvironment : selectedModule.sourceEnvironment
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        executionProgress = data.steps || [];
        githubReleaseUrl = data.github_release_url || '';
        showExecutionModal = false;
        showCompletionModal = true;
      } else {
        executionProgress = data.steps || [];
        alert(`Release failed: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Execution error:', error);
      alert(`Failed to execute release: ${error.message}`);
    } finally {
      isExecuting = false;
    }
  }
  
  function closeCompletionModal() {
    showCompletionModal = false;
    // Reset for next release
    selectedModule = null;
    currentVersion = '';
    newVersion = '';
    releaseNotes = '';
    executionProgress = [];
    githubReleaseUrl = '';
  }
  
  // Helper function to check if package was modified recently (within 30 minutes)
  function isPackageRecent(pkg) {
    if (!pkg.modified_timestamp) return false;
    const now = Date.now() / 1000; // Current time in seconds
    const thirtyMinutesAgo = now - (30 * 60); // 30 minutes in seconds
    return pkg.modified_timestamp >= thirtyMinutesAgo;
  }

  async function streamResponse(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let exitCode = null;
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.type === 'output') {
                outputLines.update(prevLines => [...prevLines, data.line]);
              } else if (data.type === 'complete') {
                exitCode = data.exitCode;
                operationStatus.set(data.exitCode === 0 ? 'success' : 'error');
                outputLines.update(prevLines => [...prevLines, `\n${data.exitCode === 0 ? '✓' : '✗'} Completed with exit code: ${data.exitCode}`]);
              } else if (data.type === 'error') {
                operationStatus.set('error');
                outputLines.update(prevLines => [...prevLines, `\n✗ Error: ${data.message || 'Unknown error'}`]);
              }
            } catch (parseError) {
              console.error('Failed to parse SSE data:', line, parseError);
              outputLines.update(prevLines => [...prevLines, `\n✗ Parse error: ${line}`]);
            }
          }
        }
      }
    } catch (error) {
      operationStatus.set('error');
      outputLines.update(prevLines => [...prevLines, `\n✗ Stream error: ${error.message || error}`]);
    }
    
    return exitCode;
  }

  async function executeStep(stepKey) {
    if (!selectedModule) {
      alert('Please select a module first');
      return;
    }
    
    isExecuting = true;
    
    try {
      // Special handling for updateVersion step - use existing infrastructure
      if (stepKey === 'updateVersion') {
        const operationId = generateOperationId();
        currentOperationId.set(operationId);
        activeOperation.set(`version-update-${selectedModule.name}`);
        operationStatus.set('running');
        outputLines.set([]);
        
        const response = await fetch('/api/version', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            deployment: useCustomEnvironment ? syncTenant : selectedModule.tenant,
            category: selectedModule.category,
            module: selectedModule.name,
            version: newVersion,
            operationId: operationId
          })
        });
        
        const exitCode = await streamResponse(response);
        
        // Mark step as complete if successful
        if (exitCode === 0) {
          stepCompletion[stepKey] = true;
          // Refresh current version
          const versionData = await fetch(`http://localhost:8000/api/release/get-version?module_path=${encodeURIComponent(selectedModule.path)}`);
          const versionResult = await versionData.json();
          if (versionResult.success) {
            currentVersion = versionResult.version;
          }
        }
      } else if (stepKey === 'buildPackages') {
        // Special handling for buildPackages - use streaming
        const operationId = generateOperationId();
        currentOperationId.set(operationId);
        activeOperation.set(`build-packages-${selectedModule.name}`);
        operationStatus.set('running');
        outputLines.set([]);
        
        const response = await fetch('/api/release/build', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            module_path: selectedModule.path,
            module_name: selectedModule.name,
            version: newVersion,
            operationId: operationId
          })
        });
        
        const exitCode = await streamResponse(response);
        
        // Mark step as complete if successful
        if (exitCode === 0) {
          stepCompletion[stepKey] = true;
          // Refresh package list
          await checkPackages();
        }
      } else {
        // For other steps, use the execute-step endpoint
        const payload = {
          module_path: selectedModule.path,
          module_name: selectedModule.name,
          module_display_name: selectedModule.displayName,
          step: stepKey,
          version: newVersion,
          release_notes: releaseNotes
        };
        
        const response = await fetch('http://localhost:8000/api/release/execute-step', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (response.ok) {
          // Mark step as complete
          stepCompletion[stepKey] = true;
          
          // Auto-refresh packages after building
          if (stepKey === 'buildPackages') {
            await checkPackages();
          }
        }
        // Errors will be logged to console, user can see via completion status
      }
    } catch (error) {
      console.error('Error executing step:', error);
      alert(`Error executing step: ${error.message}`);
    } finally {
      isExecuting = false;
    }
  }
</script>

<div class="release-manager">
  <Header 
    title="🚀 Release Manager"
    subtitle="Create and publish module releases"
    icon="🚀"
  >
    {#if selectedModule}
      <div class="header-module-info">
        <span class="header-module-name">{selectedModule.name}</span>
        <span class="header-module-category">{selectedModule.category}</span>
        <span class="header-module-env" title="Source Environment">
          📍 {selectedModule.tenant} / {selectedModule.sourceEnvironment}
        </span>
      </div>
    {/if}
  </Header>
  
  <!-- Filter Toolbar -->
  <div class="filter-toolbar">
    <div class="search-box">
      <input type="text" placeholder="🔍 Search modules..." bind:value={searchQuery} />
    </div>
    
    <div class="category-filter">
      <button 
        class="category-chip {selectedCategory === 'all' ? 'active' : ''}"
        on:click={() => selectedCategory = 'all'}>
        All
      </button>
      {#each Array.from(categories).sort() as category}
        <button 
          class="category-chip {selectedCategory === category ? 'active' : ''}"
          on:click={() => selectedCategory = category}>
          {category}
        </button>
      {/each}
    </div>
  </div>
  
  <div class="content-grid">
    <!-- Left Panel: Module Cards -->
    <div class="left-panel">
      <div class="module-cards">
        {#if filteredModules.length === 0}
          <div class="empty-state-small">
            <p>No modules found</p>
          </div>
        {:else}
          {#each filteredModules as module}
            <div 
              class="module-card {selectedModule?.name === module.name ? 'selected' : ''}" 
              role="button" 
              tabindex="0" 
              on:click={() => selectModule(module)} 
              on:keypress={(e) => e.key === 'Enter' && selectModule(module)}
            >
              <div class="module-name">{module.name}</div>
              <div class="module-version">{module.version || '1.0.0.0'}</div>
            </div>
          {/each}
        {/if}
      </div>
    </div>
    
    <!-- Middle Panel: Configuration -->
    <div class="middle-panel">
      {#if !selectedModule}
        <div class="empty-state">
          <div class="empty-icon">🚀</div>
          <p>Select a module from the left panel to begin</p>
        </div>
      {:else}
        <div class="config-layout">
          <!-- Release Type -->
          <div class="release-type-section">
            <h4>Release Type</h4>
            <div class="radio-group-compact">
              <label class="radio-option-compact">
                <input type="radio" bind:group={releaseType} value="standard" />
                <span class="radio-content">
                  <strong>Standard</strong>
                  <small>Increment Minor (2nd)</small>
                </span>
              </label>
              <label class="radio-option-compact">
                <input type="radio" bind:group={releaseType} value="hotfix" />
                <span class="radio-content">
                  <strong>Hotfix</strong>
                  <small>Increment Build (3rd)</small>
                </span>
              </label>
              <label class="radio-option-compact">
                <input type="radio" bind:group={releaseType} value="keep-current" />
                <span class="radio-content">
                  <strong>Keep Current</strong>
                  <small>Use existing version</small>
                </span>
              </label>
            </div>
          </div>
          
          <!-- Version Display -->
          <div class="version-section">
            <h4>Version</h4>
            <div class="version-display-compact">
              <div class="version-box">
                <span class="version-label">Current</span>
                <span class="version-number">{currentVersion}</span>
              </div>
              <div class="version-arrow">→</div>
              <div class="version-box">
                <span class="version-label">New</span>
                <span class="version-number {releaseType}">{newVersion}</span>
              </div>
            </div>
          </div>
          
          <!-- Scrollable Steps and Notes Area -->
          <div class="scrollable-config">
            <!-- Steps -->
            <div class="steps-section">
              <h4>Release Steps</h4>
              <div class="step-list">
                {#each Object.entries(stepDetails) as [key, detail]}
                  <div 
                    class="step-item {selectedStep === key ? 'selected' : ''} {stepCompletion[key] ? 'completed' : ''}">
                    <div 
                      class="step-content" 
                      role="button"
                      tabindex="0"
                      on:click={() => selectedStep = key}
                      on:keypress={(e) => e.key === 'Enter' && (selectedStep = key)}>
                      <span class="step-icon">{detail.icon}</span>
                      <div class="step-text">
                        <span class="step-title">{detail.title}</span>
                        {#if key === 'updateVersion' && selectedModule}
                          <span class="step-env">
                            {useCustomEnvironment ? syncTenant : selectedModule.tenant} / {useCustomEnvironment ? syncEnvironment : selectedModule.sourceEnvironment}
                          </span>
                        {/if}
                      </div>
                      {#if stepCompletion[key]}
                        <span class="step-complete-badge">✓</span>
                      {/if}
                    </div>
                  </div>
                {/each}
              </div>
            </div>
            
            <!-- Validation Messages -->
            {#if validationErrors.length > 0}
              <div class="validation-errors">
                <h4>❌ Errors</h4>
                <ul>
                  {#each validationErrors as error}
                    <li>{error}</li>
                  {/each}
                </ul>
              </div>
            {/if}
            
            {#if validationWarnings.length > 0}
              <div class="validation-warnings">
                <h4>⚠️ Warnings</h4>
                <ul>
                  {#each validationWarnings as warning}
                    <li>{warning}</li>
                  {/each}
                </ul>
              </div>
            {/if}
          </div>
        </div>
      {/if}
    </div>
    
    <!-- Detail Panel: Step Details -->
    <div class="detail-panel">
      {#if !selectedModule}
        <div class="empty-state">
          <div class="empty-icon">📋</div>
          <p>Select a module to view step details</p>
        </div>
      {:else if !selectedStep}
        <div class="empty-state">
          <div class="empty-icon">👈</div>
          <p>Click a step to view details</p>
        </div>
      {:else}
        <div class="step-detail-content">
          <div class="step-detail-header">
            <span class="step-detail-icon">{stepDetails[selectedStep].icon}</span>
            <h3>{stepDetails[selectedStep].title}</h3>
            <button 
              class="btn-complete-header {stepCompletion[selectedStep] ? 'completed' : ''}"
              on:click={() => stepCompletion[selectedStep] = !stepCompletion[selectedStep]}
              title={stepCompletion[selectedStep] ? 'Marked as complete' : 'Mark as complete'}>
              ✓
            </button>
          </div>
          
          <p class="step-description">{stepDetails[selectedStep].description}</p>
          
          {#if selectedStep === 'updateVersion'}
            <!-- Environment Configuration for Update Version -->
            <div class="step-config-section">
              <h4>Environment Configuration</h4>
              <div class="env-info-box">
                <div class="env-info-row">
                  <span class="env-label">Tenant:</span>
                  <span class="env-value">{useCustomEnvironment ? syncTenant : selectedModule.tenant}</span>
                </div>
                <div class="env-info-row">
                  <span class="env-label">Environment:</span>
                  <span class="env-value">{useCustomEnvironment ? syncEnvironment : selectedModule.sourceEnvironment}</span>
                </div>
              </div>
              
              <label class="env-override-toggle">
                <input type="checkbox" bind:checked={useCustomEnvironment} />
                <span>Override environment (advanced)</span>
              </label>
              
              {#if useCustomEnvironment}
                <div class="env-override-fields">
                  <div class="form-field">
                    <label>
                      <span class="field-label">Tenant</span>
                      <input type="text" bind:value={syncTenant} placeholder="Enter tenant name" />
                    </label>
                  </div>
                  <div class="form-field">
                    <label>
                      <span class="field-label">Environment</span>
                      <input type="text" bind:value={syncEnvironment} placeholder="Enter environment name" />
                    </label>
                  </div>
                </div>
              {/if}
            </div>
          {/if}
          
          {#if selectedStep === 'updateChangelog'}
            <!-- Changelog Preview Actions -->
            <div class="step-config-section">
              <h4>Changelog Preview</h4>
              <button 
                class="btn btn-primary btn-block"
                on:click={previewChangelogUpdate}
                disabled={isLoadingChangelog || !newVersion}>
                {isLoadingChangelog ? '⏳ Loading...' : '👁️ Preview Changes (Before/After)'}
              </button>
              <small class="hint-text">Preview how Unreleased will transform to v{newVersion || '...'}</small>
            </div>
          {/if}
          
          {#if selectedStep === 'createReleaseNotes'}
            <!-- Release Notes Editor -->
            <div class="step-config-section">
              <h4>Release Notes</h4>
              <div class="release-notes-actions">
                <button 
                  class="btn btn-secondary btn-sm"
                  on:click={loadChangelog}
                  disabled={!selectedModule || !newVersion}>
                  🔄 Refresh from CHANGELOG.md
                </button>
                <button 
                  class="btn btn-secondary btn-sm"
                  on:click={copyReleaseNotesToClipboard}
                  disabled={!releaseNotes}>
                  📋 Copy to Clipboard
                </button>
              </div>
              <small class="hint-text">Populated from "## [{newVersion || '...'}]" section in CHANGELOG.md</small>
              <textarea 
                bind:value={releaseNotes} 
                class="release-notes-textarea"
                rows="10" 
                placeholder="Release notes will be auto-populated from CHANGELOG.md when you select a module..."
              ></textarea>
              <small class="hint-text">Edit as needed - these notes will be included in the GitHub release</small>
            </div>
          {/if}
          
          {#if selectedStep === 'buildPackages'}
            <!-- Built Packages Display -->
            <div class="step-config-section">
              <h4>Built Packages</h4>
              <button 
                class="btn btn-secondary btn-sm"
                on:click={checkPackages}
                disabled={isLoadingPackages}>
                {isLoadingPackages ? '⏳ Loading...' : '🔍 Check for Packages'}
              </button>
              <small class="hint-text">Scan bin/Release folder for package files</small>
              
              {#if builtPackages.length > 0}
                <div class="packages-list">
                  {#each builtPackages as pkg}
                    <div class="package-item">
                      <div class="package-name">📦 {pkg.name}</div>
                      <div class="package-meta">
                        <span class="package-size">{pkg.size_mb} MB</span>
                        <span class="package-date {isPackageRecent(pkg) ? 'recent' : 'old'}">Modified: {pkg.modified}</span>
                      </div>
                    </div>
                  {/each}
                </div>
              {:else if !isLoadingPackages}
                <div class="empty-packages">
                  <small>No packages found. Run the build step to create them.</small>
                </div>
              {/if}
            </div>
          {/if}
          
          {#if selectedStep === 'githubRelease'}
            <!-- GitHub Release Preview -->
            <div class="step-config-section">
              <h4>Release Preview</h4>
              {#if selectedModule && newVersion}
                <div class="release-preview">
                  <div class="preview-row">
                    <span class="preview-label">Tag:</span>
                    <span class="preview-value preview-tag">{selectedModule.name}/v{newVersion}</span>
                  </div>
                  <div class="preview-row">
                    <span class="preview-label">Title:</span>
                    <span class="preview-value preview-title">
                      {selectedModule.displayName || (selectedModule.name.charAt(0).toUpperCase() + selectedModule.name.slice(1))} {newVersion}
                    </span>
                  </div>
                </div>
                <small class="hint-text">The GitHub release will be created with this tag and title</small>
                
                <!-- Collapsible Release Notes Preview -->
                {#if releaseNotes}
                  <details class="release-notes-collapsible">
                    <summary>Release Notes Preview</summary>
                    <div class="release-notes-preview-content">
                      {releaseNotes}
                    </div>
                  </details>
                {/if}
              {:else}
                <small class="hint-text">Select a module and version to see preview</small>
              {/if}
            </div>
          {/if}
          
          <div class="step-instructions">
            <h4>What this step does:</h4>
            <ul>
              {#each stepDetails[selectedStep].instructions as instruction}
                <li>{instruction}</li>
              {/each}
            </ul>
          </div>
          
          {#if selectedStep !== 'createReleaseNotes'}
            <div class="step-actions">
              <button 
                class="btn btn-primary btn-block"
                on:click={() => executeStep(selectedStep)}
                disabled={isExecuting}>
                {isExecuting ? 'Running...' : `▶ Run This Step`}
              </button>
              <small class="step-hint">Run automation for this step</small>
            </div>
          {:else}
            <div class="step-info-box">
              <small>💡 This step is for reviewing and editing release notes. The notes are auto-populated when you select a module and can be refreshed using the button above.</small>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- Execution Modal -->
{#if showExecutionModal}
  <div class="modal-overlay">
    <div class="modal-content execution-modal">
      <h2>Executing Release: {selectedModule?.name} v{newVersion}</h2>
      
      <div class="progress-list">
        {#each executionProgress as step}
          <div class="progress-item {step.status}">
            <span class="progress-icon">
              {#if step.status === 'pending'}⏳{/if}
              {#if step.status === 'running'}🔄{/if}
              {#if step.status === 'success'}✓{/if}
              {#if step.status === 'error'}✗{/if}
            </span>
            <span class="progress-label">{step.label}</span>
            {#if step.message}
              <div class="progress-message">{step.message}</div>
            {/if}
          </div>
        {/each}
      </div>
    </div>
  </div>
{/if}

<!-- Completion Modal -->
{#if showCompletionModal}
  <div class="modal-overlay">
    <div class="modal-content completion-modal">
      <h2>✅ Release Complete!</h2>
      
      <div class="completion-info">
        <p class="success-message">
          Successfully released <strong>{selectedModule?.name} v{newVersion}</strong>
        </p>
        
        {#if githubReleaseUrl}
          <div class="github-link">
            <a href={githubReleaseUrl} target="_blank" rel="noopener noreferrer">
              View GitHub Release →
            </a>
          </div>
        {/if}
      </div>
      
      <div class="execution-summary">
        <h3>Summary</h3>
        <div class="progress-list">
          {#each executionProgress as step}
            <div class="progress-item {step.status}">
              <span class="progress-icon">
                {#if step.status === 'success'}✓{/if}
                {#if step.status === 'error'}✗{/if}
              </span>
              <span class="progress-label">{step.label}</span>
            </div>
          {/each}
        </div>
      </div>
      
      <div class="modal-actions">
        <button class="btn btn-primary" on:click={closeCompletionModal}>
          Close
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Changelog Preview Modal -->
{#if showChangelogPreview}
  <div class="modal-overlay" 
       role="button" 
       tabindex="0"
       on:click={(e) => e.target === e.currentTarget && (showChangelogPreview = false)}
       on:keydown={(e) => e.key === 'Escape' && (showChangelogPreview = false)}>
    <div class="modal-content changelog-preview-modal" 
         role="dialog"
         aria-modal="true">
      <div class="modal-header">
        <h2>📝 CHANGELOG.md {changelogAfter ? 'Preview' : 'Current Content'}</h2>
        <button class="modal-close" on:click={() => showChangelogPreview = false}>✕</button>
      </div>
      
      <div class="changelog-preview-content">
        {#if changelogAfter}
          <!-- Side by side comparison -->
          <div class="preview-grid">
            <div class="preview-column">
              <h3>Before (Current)</h3>
              <pre class="changelog-text">{changelogBefore}</pre>
            </div>
            <div class="preview-column">
              <h3>After (Transform)</h3>
              <pre class="changelog-text">{changelogAfter}</pre>
            </div>
          </div>
        {:else}
          <!-- Single view -->
          <pre class="changelog-text">{changelogBefore}</pre>
        {/if}
      </div>
      
      <div class="modal-actions">
        <button class="btn btn-secondary" on:click={() => showChangelogPreview = false}>
          Close
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .release-manager {
    padding: 0;
    max-width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  /* Header Module Info */
  .header-module-info {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 0.75rem;
    margin-right: 1rem;
  }
  
  .header-module-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #e2e8f0;
  }
  
  .header-module-category {
    font-size: 0.75rem;
    color: #94a3b8;
    padding: 0.125rem 0.5rem;
    background: rgba(148, 163, 184, 0.1);
    border-radius: 0.25rem;
  }
  
  .header-module-env {
    font-size: 0.75rem;
    color: #60a5fa;
    padding: 0.125rem 0.5rem;
    background: rgba(96, 165, 250, 0.1);
    border-radius: 0.25rem;
    border: 1px solid rgba(96, 165, 250, 0.2);
  }
  
  .filter-toolbar {
    display: flex;
    gap: 1rem;
    align-items: center;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 0 1rem 1rem 1rem;
  }
  
  .content-grid {
    display: grid;
    grid-template-columns: 280px 1fr 1fr;
    gap: 1rem;
    flex: 1;
    overflow: hidden;
    margin: 0 1rem 1rem 1rem;
  }
  
  /* Left Panel - Module Cards */
  .left-panel {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 0.5rem;
    padding: 1rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }
  
  .search-box {
    flex: 0 0 250px;
  }
  
  .search-box input {
    width: 100%;
    padding: 0.625rem 0.875rem;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-family: inherit;
    background: #0f172a;
    color: #e2e8f0;
  }
  
  .search-box input::placeholder {
    color: #64748b;
  }
  
  .search-box input:focus {
    outline: none;
    border-color: #60a5fa;
    background: #1e293b;
  }
  
  .category-filter {
    flex: 1;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  
  .category-chip {
    padding: 0.375rem 0.875rem;
    border: 1px solid #334155;
    border-radius: 1rem;
    background: #0f172a;
    cursor: pointer;
    font-size: 0.75rem;
    font-family: inherit;
    transition: all 0.2s;
    color: #94a3b8;
    white-space: nowrap;
  }
  
  .category-chip:hover {
    border-color: #60a5fa;
    background: #1e293b;
    color: #e2e8f0;
  }
  
  .category-chip.active {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border-color: #60a5fa;
  }
  
  .module-cards {
    display: flex;
    flex-direction: column;
    gap: 0.625rem;
    overflow-y: auto;
    flex: 1;
    padding-right: 0.5rem;
  }
  
  .module-card {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    padding: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .module-card:hover {
    background: #1e293b;
    border-color: #60a5fa;
    transform: translateY(-1px);
  }
  
  .module-card.selected {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-color: #60a5fa;
    box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2);
  }
  
  .module-name {
    color: #f1f5f9;
    font-weight: 600;
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
  }
  
  .module-version {
    color: #94a3b8;
    font-size: 0.75rem;
    font-family: 'Courier New', monospace;
  }
  
  .empty-state-small {
    padding: 2rem 1rem;
    text-align: center;
    color: #64748b;
    font-size: 0.875rem;
  }
  
  /* Middle Panel - Configuration */
  .middle-panel {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 0.5rem;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .middle-panel h4 {
    color: #e2e8f0;
    margin: 0 0 0.375rem 0;
    font-size: 0.875rem;
    font-weight: 600;
  }
  
  .config-layout {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    height: 100%;
    overflow: hidden;
  }
  
  .scrollable-config {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding-right: 0.5rem;
  }
  
  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #64748b;
    text-align: center;
  }
  
  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }
  
  .version-display-compact {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.625rem;
    background: rgba(59, 130, 246, 0.1);
    border-radius: 0.375rem;
  }
  
  .version-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    flex: 1;
  }
  
  .version-label {
    color: #94a3b8;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .version-number {
    color: #e2e8f0;
    font-size: 1.25rem;
    font-weight: 700;
    font-family: 'Courier New', monospace;
  }
  
  .version-number.standard {
    color: #4ade80;
  }
  
  .version-number.hotfix {
    color: #fb923c;
  }
  
  .version-number.keep-current {
    color: #60a5fa;
  }
  
  .version-arrow {
    color: #60a5fa;
    font-size: 1.5rem;
  }
  
  .radio-group-compact {
    display: flex;
    gap: 0.5rem;
  }
  
  .radio-option-compact {
    flex: 1;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.75rem;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .radio-option-compact:hover {
    background: #1e293b;
    border-color: #60a5fa;
  }
  
  .radio-option-compact input {
    margin-top: 0.125rem;
  }
  
  .radio-content {
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
  }
  
  .radio-content strong {
    color: #e2e8f0;
    font-size: 0.875rem;
  }
  
  .radio-content small {
    color: #94a3b8;
    font-size: 0.75rem;
  }
  
  .step-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .step-item {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    padding: 0.625rem;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    background: #0f172a;
    transition: all 0.2s;
  }
  
  .step-item.selected {
    border-color: #60a5fa;
    background: #1e293b;
  }
  
  .step-item.completed {
    border-color: #4ade80;
    background: rgba(34, 197, 94, 0.1);
  }
  
  .step-item.completed .step-title {
    color: #4ade80;
  }
  
  .step-content {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 0.25rem;
  }
  
  .step-content:hover {
    background: rgba(96, 165, 250, 0.1);
  }
  
  .step-icon {
    font-size: 1.125rem;
  }
  
  .step-text {
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
    flex: 1;
  }
  
  .step-title {
    color: #e2e8f0;
    font-size: 0.875rem;
  }
  
  .step-env {
    color: #60a5fa;
    font-size: 0.6875rem;
    font-weight: 500;
  }
  
  .step-complete-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: #4ade80;
    color: #0f172a;
    border-radius: 50%;
    font-size: 0.875rem;
    font-weight: 700;
    flex-shrink: 0;
  }
  
  textarea {
    width: 100%;
    padding: 0.75rem;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    color: #e2e8f0;
    font-family: inherit;
    font-size: 0.875rem;
    resize: vertical;
  }
  
  textarea:focus {
    outline: none;
    border-color: #60a5fa;
  }
  
  .release-notes-actions {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }
  
  .release-notes-textarea {
    min-height: 180px;
    font-family: 'Courier New', Consolas, monospace;
    line-height: 1.6;
  }
  
  .validation-errors,
  .validation-warnings {
    padding: 0.75rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
  }
  
  .validation-errors {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid #dc2626;
  }
  
  .validation-warnings {
    background: rgba(251, 191, 36, 0.1);
    border: 1px solid #f59e0b;
  }
  
  .validation-errors h4 {
    color: #fca5a5;
    margin: 0 0 0.5rem 0;
  }
  
  .validation-warnings h4 {
    color: #fcd34d;
    margin: 0 0 0.5rem 0;
  }
  
  .validation-errors ul,
  .validation-warnings ul {
    margin: 0;
    padding-left: 1.25rem;
    font-size: 0.875rem;
  }
  
  .validation-errors li {
    color: #fca5a5;
  }
  
  .validation-warnings li {
    color: #fcd34d;
  }
  
  .btn {
    padding: 0.75rem 1.5rem;
    border-radius: 0.375rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    font-size: 0.875rem;
  }
  
  .btn-primary {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }
  
  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .btn-secondary {
    background: #334155;
    color: #e2e8f0;
    border: 1px solid #475569;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background: #475569;
    border-color: #64748b;
  }
  
  .btn-success {
    background: rgba(34, 197, 94, 0.2);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.4);
  }
  
  .btn-success:hover:not(:disabled) {
    background: rgba(34, 197, 94, 0.3);
    border-color: rgba(34, 197, 94, 0.6);
  }
  
  .btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
  }
  
  .btn-large {
    padding: 0.75rem 1.5rem;
    font-size: 0.9375rem;
  }
  
  /* Modals */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  /* Detail Panel - Step Details */
  .detail-panel {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 0.5rem;
    padding: 1rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }
  
  .step-detail-content {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }
  
  .step-detail-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #334155;
  }
  
  .step-detail-icon {
    font-size: 2rem;
  }
  
  .step-detail-header h3 {
    color: #e2e8f0;
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    flex: 1;
  }
  
  .btn-complete-header {
    background: transparent;
    border: 2px solid #475569;
    color: #94a3b8;
    border-radius: 50%;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 1rem;
    font-weight: bold;
    transition: all 0.2s ease;
    margin-left: auto;
  }
  
  .btn-complete-header:hover {
    background: #1e293b;
    border-color: #64748b;
    color: #cbd5e1;
  }
  
  .btn-complete-header.completed {
    background: #059669;
    border-color: #10b981;
    color: white;
  }
  
  .btn-complete-header.completed:hover {
    background: #047857;
    border-color: #059669;
  }
  
  .step-description {
    color: #cbd5e1;
    font-size: 0.875rem;
    line-height: 1.5;
    margin: 0;
  }
  
  .step-instructions {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    padding: 0.875rem;
  }
  
  .step-config-section {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    padding: 0.875rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .step-config-section h4 {
    color: #e2e8f0;
    margin: 0;
    font-size: 0.8125rem;
    font-weight: 600;
  }
  
  .env-info-box {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 0.25rem;
    padding: 0.625rem;
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
  }
  
  .env-info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .env-label {
    color: #94a3b8;
    font-size: 0.75rem;
  }
  
  .env-value {
    color: #60a5fa;
    font-size: 0.75rem;
    font-weight: 600;
  }
  
  .env-override-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-size: 0.75rem;
    color: #94a3b8;
  }
  
  .env-override-toggle input[type="checkbox"] {
    cursor: pointer;
  }
  
  .env-override-fields {
    display: flex;
    flex-direction: column;
    gap: 0.625rem;
    padding-top: 0.5rem;
    border-top: 1px solid #334155;
  }
  
  .form-field {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .form-field label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .form-field .field-label {
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .form-field input[type="text"] {
    padding: 0.5rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 0.25rem;
    color: #e2e8f0;
    font-size: 0.75rem;
    font-family: inherit;
  }
  
  .form-field input[type="text"]:focus {
    outline: none;
    border-color: #60a5fa;
  }
  
  .step-instructions h4 {
    color: #e2e8f0;
    margin: 0 0 0.625rem 0;
    font-size: 0.8125rem;
    font-weight: 600;
  }
  
  .step-instructions ul {
    margin: 0;
    padding-left: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
  }
  
  .step-instructions li {
    color: #94a3b8;
    font-size: 0.8125rem;
    line-height: 1.4;
  }
  
  .hint-text {
    color: #64748b;
    font-size: 0.75rem;
    margin-top: 0.25rem;
  }
  
  .step-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: auto;
    padding-top: 1rem;
    border-top: 1px solid #334155;
  }
  
  .btn-block {
    width: 100%;
  }
  
  .step-hint {
    color: #64748b;
    font-size: 0.75rem;
    text-align: center;
  }
  
  .step-info-box {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 0.375rem;
    padding: 0.75rem;
    margin-top: auto;
  }
  
  .step-info-box small {
    color: #93c5fd;
    font-size: 0.75rem;
    line-height: 1.5;
  }
  
  .packages-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 0.75rem;
  }
  
  .package-item {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    padding: 0.75rem;
  }
  
  .package-name {
    color: #e2e8f0;
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 0.375rem;
    font-family: 'Courier New', monospace;
  }
  
  .package-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.75rem;
  }
  
  .package-size {
    color: #60a5fa;
    font-weight: 500;
  }
  
  .package-date {
    color: #94a3b8;
  }
  
  .package-date.recent {
    color: #4ade80;
    font-weight: 600;
  }
  
  .package-date.old {
    color: #fb923c;
  }
  
  .empty-packages {
    margin-top: 0.75rem;
    padding: 0.75rem;
    background: rgba(148, 163, 184, 0.1);
    border-radius: 0.375rem;
    text-align: center;
  }
  
  .empty-packages small {
    color: #94a3b8;
  }
  
  .release-preview {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    padding: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }
  
  .preview-row {
    display: flex;
    gap: 0.75rem;
    align-items: baseline;
  }
  
  .preview-label {
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 500;
    min-width: 45px;
  }
  
  .preview-value {
    color: #e2e8f0;
    font-size: 0.875rem;
    font-family: 'Courier New', monospace;
  }
  
  .preview-tag {
    color: #fbbf24;
  }
  
  .preview-title {
    color: #60a5fa;
    font-weight: 600;
  }
  
  .release-notes-collapsible {
    margin-top: 1rem;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    padding: 0.75rem;
  }
  
  .release-notes-collapsible summary {
    color: #60a5fa;
    font-size: 0.8125rem;
    font-weight: 600;
    cursor: pointer;
    user-select: none;
    list-style-position: outside;
    padding-left: 0.25rem;
  }
  
  .release-notes-collapsible summary:hover {
    color: #93c5fd;
  }
  
  .release-notes-preview-content {
    margin-top: 0.75rem;
    padding: 0.75rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 0.25rem;
    color: #e2e8f0;
    font-size: 0.8125rem;
    line-height: 1.6;
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 300px;
    overflow-y: auto;
    font-family: 'Courier New', Consolas, monospace;
  }
  
  .release-notes-preview-content::-webkit-scrollbar {
    width: 6px;
  }
  
  .release-notes-preview-content::-webkit-scrollbar-track {
    background: #0f172a;
  }
  
  .release-notes-preview-content::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 3px;
  }
  
  .release-notes-preview-content::-webkit-scrollbar-thumb:hover {
    background: #475569;
  }
  
  .modal-content {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 0.5rem;
    padding: 1.5rem;
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
  }
  
  .modal-content h2 {
    color: #e2e8f0;
    margin: 0 0 1.5rem 0;
  }
  
  .modal-content h3 {
    color: #e2e8f0;
    margin: 1.5rem 0 1rem 0;
    font-size: 1rem;
  }
  
  .progress-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .progress-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 0.375rem;
  }
  
  .progress-item.success {
    border-color: #10b981;
  }
  
  .progress-item.error {
    border-color: #dc2626;
  }
  
  .progress-item.running {
    border-color: #60a5fa;
  }
  
  .progress-icon {
    font-size: 1.25rem;
  }
  
  .progress-label {
    color: #e2e8f0;
    flex: 1;
    font-size: 0.875rem;
  }
  
  .progress-message {
    color: #94a3b8;
    font-size: 0.75rem;
    margin-top: 0.5rem;
    padding-left: 2.25rem;
  }
  
  .completion-info {
    text-align: center;
    padding: 1.5rem;
    background: rgba(16, 185, 129, 0.1);
    border-radius: 0.5rem;
    margin-bottom: 1.5rem;
  }
  
  .success-message {
    color: #e2e8f0;
    font-size: 1.125rem;
    margin-bottom: 1rem;
  }
  
  .github-link a {
    color: #60a5fa;
    text-decoration: none;
    font-weight: 600;
  }
  
  .github-link a:hover {
    text-decoration: underline;
  }
  
  .modal-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1.5rem;
  }
  
  /* Changelog Preview Modal */
  .changelog-preview-modal {
    max-width: 90vw;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #334155;
  }
  
  .modal-header h2 {
    margin: 0;
    font-size: 1.25rem;
  }
  
  .modal-close {
    background: none;
    border: none;
    color: #94a3b8;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    line-height: 1;
  }
  
  .modal-close:hover {
    color: #e2e8f0;
  }
  
  .changelog-preview-content {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  
  .preview-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    flex: 1;
    overflow: hidden;
  }
  
  .preview-column {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    padding: 0.75rem;
  }
  
  .preview-column h3 {
    color: #94a3b8;
    font-size: 0.875rem;
    margin: 0 0 0.75rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #334155;
  }
  
  .changelog-text {
    flex: 1;
    overflow: auto;
    margin: 0;
    padding: 0.75rem;
    background: #020617;
    border: 1px solid #1e293b;
    border-radius: 0.25rem;
    color: #cbd5e1;
    font-family: 'Courier New', monospace;
    font-size: 0.8125rem;
    line-height: 1.6;
    white-space: pre-wrap;
  }
</style>
