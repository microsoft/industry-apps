<script>
  import { onMount } from 'svelte';
  import Header from '../lib/Header.svelte';
  import { config, deployments } from '../lib/stores.js';

  // Settings (persisted)
  let selectedDeployment = '';
  let selectedEnvironment = '';
  let publisherPrefix = '';
  let selectedSolution = '';

  // Data
  let solutions = [];
  let optionSets = [];
  let pendingOptionSets = [];
  let loading = false;

  // UI state
  let activeTab = 'create'; // 'search', 'create', 'browse'
  let showReviewModal = false;

  // Search tab
  let searchQuery = '';
  let searchResults = [];
  let searchMode = 'name'; // 'name' or 'values'

  // Create tab
  let createStep = 1; // 1: Basic Info, 2: Define Options, 3: Check Duplicates, 4: Create
  let displayName = '';
  let schemaName = '';
  let description = '';
  let options = [{ label: '', value: '' }];
  let duplicateMatches = [];
  let creationResult = null;
  
  // Live suggestions while creating
  let liveSuggestions = [];
  let suggestionSearchTimeout = null;

  // Browse tab
  let browseFilter = '';

  $: availableEnvironments = getAvailableEnvironments($config, selectedDeployment);
  $: sortedSolutions = solutions.slice().sort((a, b) => {
    const nameA = a.displayName.replace(/^App Base - /i, '');
    const nameB = b.displayName.replace(/^App Base - /i, '');
    return nameA.localeCompare(nameB);
  });
  $: allOptionSets = [...optionSets, ...pendingOptionSets];
  $: filteredOptionSets = allOptionSets.filter(os =>
    os.displayName.toLowerCase().includes(browseFilter.toLowerCase()) ||
    os.schemaName.toLowerCase().includes(browseFilter.toLowerCase()) ||
    os.category.toLowerCase().includes(browseFilter.toLowerCase())
  );

  // Watch for display name changes to auto-generate schema name
  $: if (displayName && createStep === 1) {
    autoGenerateSchemaName();
  }

  onMount(() => {
    console.log('[ChoiceCreator] Component mounted');
    // Load saved settings
    selectedDeployment = localStorage.getItem('choiceCreator_deployment') || '';
    selectedEnvironment = localStorage.getItem('choiceCreator_environment') || '';
    publisherPrefix = localStorage.getItem('publisherPrefix') || 'appbase_';
    selectedSolution = localStorage.getItem('choiceCreator_solution') || '';

    console.log('[ChoiceCreator] Loaded settings:', { selectedDeployment, selectedEnvironment, publisherPrefix, selectedSolution });

    // Load solutions and pending option sets on mount
    loadSolutions();
    loadPendingOptionSets();
  });

  function getAvailableEnvironments(config, deploymentName) {
    if (!config || !deploymentName) return [];
    const deployment = config.deployments?.[deploymentName];
    if (!deployment) return [];
    return Object.keys(deployment.Environments || {});
  }

  async function loadSolutions() {
    console.log('[ChoiceCreator] Loading solutions...');
    loading = true;
    try {
      const response = await fetch('/api/helpers/solutions/list');
      console.log('[ChoiceCreator] Solutions response:', response.status);
      const data = await response.json();
      console.log('[ChoiceCreator] Solutions data:', data);
      solutions = data.solutions || [];
      console.log('[ChoiceCreator] Loaded', solutions.length, 'solutions');
    } catch (error) {
      console.error('Error loading solutions:', error);
    }
    loading = false;
  }

  async function loadOptionSets() {
    console.log('[ChoiceCreator] Loading option sets...');
    loading = true;
    try {
      const response = await fetch('/api/helpers/option-sets/scan');
      console.log('[ChoiceCreator] Option sets response:', response.status);
      const data = await response.json();
      console.log('[ChoiceCreator] Option sets data:', data);
      optionSets = data.optionSets || [];
      console.log('[ChoiceCreator] Loaded', optionSets.length, 'option sets');
      
      // Load pending option sets from backend (auto-cleans synced items)
      await loadPendingOptionSets();
      
    } catch (error) {
      console.error('Error loading option sets:', error);
    }
    loading = false;
  }
  
  async function loadPendingOptionSets() {
    try {
      const response = await fetch('/api/helpers/option-sets/pending');
      const data = await response.json();
      pendingOptionSets = data.pending || [];
      console.log('[ChoiceCreator] Loaded', pendingOptionSets.length, 'pending option sets from backend');
    } catch (error) {
      console.error('Error loading pending option sets:', error);
      pendingOptionSets = [];
    }
  }
  
  async function savePendingOptionSet(optionSet) {
    try {
      const response = await fetch('/api/helpers/option-sets/pending', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(optionSet)
      });
      const data = await response.json();
      
      if (data.success) {
        // Reload to get updated list
        await loadPendingOptionSets();
        console.log('[ChoiceCreator] Saved pending option set:', optionSet.schemaName);
      } else {
        console.error('[ChoiceCreator] Failed to save pending:', data.error);
      }
    } catch (error) {
      console.error('Error saving pending option set:', error);
    }
  }
  
  async function clearAllPending() {
    if (confirm(`Clear ${pendingOptionSets.length} pending option set(s)? This cannot be undone.`)) {
      try {
        const response = await fetch('/api/helpers/option-sets/pending', {
          method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
          pendingOptionSets = [];
          console.log('[ChoiceCreator] Cleared all pending option sets');
        }
      } catch (error) {
        console.error('Error clearing pending option sets:', error);
      }
    }
  }

  async function searchOptionSets() {
    console.log('[ChoiceCreator] Searching for:', searchQuery, 'mode:', searchMode);
    if (!searchQuery.trim()) {
      searchResults = [];
      return;
    }

    loading = true;
    try {
      const requestBody = {
        displayName: searchMode === 'name' ? searchQuery : null,
        optionLabels: searchMode === 'values' 
          ? searchQuery.split(',').map(v => v.trim()).filter(v => v.length > 0)
          : null
      };
      
      console.log('[ChoiceCreator] Search request body:', requestBody);
      
      const response = await fetch('/api/helpers/option-sets/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      console.log('[ChoiceCreator] Search response:', response.status);
      const data = await response.json();
      console.log('[ChoiceCreator] Search results:', data);
      searchResults = data.matches || [];
      console.log('[ChoiceCreator] Found', searchResults.length, 'matches');
    } catch (error) {
      console.error('Error searching option sets:', error);
      searchResults = [];
    }
    loading = false;
  }

  function autoGenerateSchemaName() {
    if (!displayName) {
      schemaName = '';
      return;
    }
    
    // Remove special characters and convert to lowercase
    let generated = displayName
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, '');
    
    // Add prefix if not already there
    if (!generated.startsWith(publisherPrefix)) {
      generated = publisherPrefix + generated;
    }
    
    schemaName = generated;
  }

  function addOption() {
    options = [...options, { label: '', value: '' }];
  }

  function removeOption(index) {
    options = options.filter((_, i) => i !== index);
  }

  function moveOption(index, direction) {
    if (direction === 'up' && index > 0) {
      [options[index], options[index - 1]] = [options[index - 1], options[index]];
      options = [...options];
    } else if (direction === 'down' && index < options.length - 1) {
      [options[index], options[index + 1]] = [options[index + 1], options[index]];
      options = [...options];
    }
  }
  
  let labelInputs = [];
  
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
  
  function handleDisplayNameBlur() {
    displayName = toProperCase(displayName);
  }
  
  function handleLabelBlur(index) {
    options[index].label = toProperCase(options[index].label);
    options = [...options];
  }
  
  function handleValueBlur(index) {
    // If this is the last row and it has a label, add a new row
    if (index === options.length - 1 && options[index].label.trim()) {
      addOption();
      // Focus the label input of the new row after a tick
      setTimeout(() => {
        const newRowIndex = options.length - 1;
        if (labelInputs[newRowIndex]) {
          labelInputs[newRowIndex].focus();
        }
      }, 0);
    }
  }

  async function checkForDuplicates() {
    loading = true;
    try {
      const optionLabels = options
        .map(o => o.label.trim())
        .filter(label => label !== '');

      const response = await fetch('/api/helpers/option-sets/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          displayName: displayName,
          optionLabels: optionLabels
        })
      });
      const data = await response.json();
      duplicateMatches = data.matches || [];
      showReviewModal = true;
    } catch (error) {
      console.error('Error checking for duplicates:', error);
      duplicateMatches = [];
    }
    loading = false;
  }

  async function createOptionSet() {
    if (!selectedSolution) {
      alert('Please select a target solution');
      return;
    }
    
    if (!selectedDeployment || !selectedEnvironment) {
      alert('Please select deployment and environment');
      return;
    }

    loading = true;
    creationResult = null;

    try {
      const validOptions = options
        .filter(o => o.label.trim() !== '')
        .map(o => ({
          label: o.label.trim(),
          value: o.value.trim() || null
        }));

      const response = await fetch('/api/helpers/option-sets/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          schemaName: schemaName,
          displayName: displayName,
          description: description,
          options: validOptions,
          targetSolution: selectedSolution,
          deployment: selectedDeployment,
          environment: selectedEnvironment
        })
      });

      const data = await response.json();
      
      if (data.success) {
        creationResult = { success: true, ...data };
        createStep = 4;
        showReviewModal = false;
        
        // Save to pending cache on backend
        await savePendingOptionSet({
          schemaName: data.schemaName,
          displayName: data.displayName,
          description: data.description,
          category: data.category,
          module: data.module,
          path: data.path,
          options: data.options,
          deployment: data.deployment,
          environment: data.environment
        });
        
        // Reload option sets to show in browse (will now include pending)
        if (activeTab === 'browse') {
          await loadOptionSets();
        }
      } else {
        creationResult = { success: false, error: data.error };
        createStep = 4;
        showReviewModal = false;
      }
    } catch (error) {
      console.error('Error creating option set:', error);
      creationResult = { success: false, error: error.message };
      createStep = 4;
      showReviewModal = false;
    }
    loading = false;
  }

  function resetCreateForm() {
    createStep = 1;
    displayName = '';
    schemaName = '';
    description = '';
    options = [{ label: '', value: '' }];
    duplicateMatches = [];
    creationResult = null;
    liveSuggestions = [];
    showReviewModal = false;
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      alert(`Copied "${text}" to clipboard!`);
    });
  }
  
  function isMatchingValue(optionLabel) {
    if (searchMode !== 'values' || !searchQuery) return false;
    const searchTerms = searchQuery.split(',').map(v => v.trim().toLowerCase()).filter(v => v.length > 0);
    const label = optionLabel.toLowerCase();
    return searchTerms.some(term => label.includes(term) || term.includes(label));
  }
  
  function isOptionMatchingForSuggestion(suggestionOptionLabel) {
    // Check if any of the user's entered options match this suggestion option (word-level, not substring)
    const suggestionWords = suggestionOptionLabel.toLowerCase().split(/\s+/);
    
    return options.some(userOption => {
      if (!userOption.label.trim()) return false;
      const userWords = userOption.label.toLowerCase().split(/\s+/);
      
      // Check if any words match exactly
      return suggestionWords.some(sw => userWords.some(uw => sw === uw));
    });
  }

  function saveSettings() {
    localStorage.setItem('choiceCreator_deployment', selectedDeployment);
    localStorage.setItem('choiceCreator_environment', selectedEnvironment);
    localStorage.setItem('publisherPrefix', publisherPrefix);
    localStorage.setItem('choiceCreator_solution', selectedSolution);
  }

  $: {
    // Auto-save settings when they change
    if (selectedDeployment) saveSettings();
    if (selectedEnvironment) saveSettings();
    if (publisherPrefix) saveSettings();
    if (selectedSolution) saveSettings();
  }

  // Load option sets when browse tab is activated
  $: if (activeTab === 'browse' && optionSets.length === 0) {
    console.log('[ChoiceCreator] Browse tab activated, loading option sets...');
    loadOptionSets();
  }
  
  // Clear live suggestions when leaving create tab
  $: if (activeTab !== 'create') {
    liveSuggestions = [];
  }
  
  // Don't clear suggestions on step 3 anymore - keep them for when user goes back

  // Group option sets by category/module for browse view
  $: groupedOptionSets = filteredOptionSets.reduce((acc, os) => {
    const key = `${os.category}/${os.module}`;
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(os);
    return acc;
  }, {});
  
  $: console.log('[ChoiceCreator] activeTab:', activeTab, 'optionSets.length:', optionSets.length);
  
  // Re-search when search mode changes (if there's already a query)
  $: if (searchMode && searchQuery.trim()) {
    searchOptionSets();
  }
  
  // Live suggestions: Search as user types in create mode
  $: if (activeTab === 'create' && (displayName || options.some(o => o.label))) {
    performLiveSearch();
  }
  
  async function performLiveSearch() {
    // Clear existing timeout
    if (suggestionSearchTimeout) {
      clearTimeout(suggestionSearchTimeout);
    }
    
    // Debounce: wait 500ms after user stops typing
    suggestionSearchTimeout = setTimeout(async () => {
      const hasDisplayName = displayName && displayName.trim().length > 2;
      const optionLabels = options
        .map(o => o.label.trim())
        .filter(label => label.length > 0);
      const hasOptions = optionLabels.length > 0;
      
      // Only search if we have either a display name or option labels
      if (!hasDisplayName && !hasOptions) {
        liveSuggestions = [];
        return;
      }
      
      try {
        const response = await fetch('/api/helpers/option-sets/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            displayName: hasDisplayName ? displayName : null,
            optionLabels: hasOptions ? optionLabels : null
          })
        });
        const data = await response.json();
        let suggestions = data.matches || [];
        
        // Calculate match counts and sort by similarity
        suggestions = suggestions.map(suggestion => {
          const matchCount = calculateMatchCount(suggestion);
          return {
            ...suggestion,
            matchCount,
            matchPercentage: suggestion.options.length > 0 ? Math.round((matchCount / suggestion.options.length) * 100) : 0,
            totalOptions: suggestion.options.length
          };
        });
        
        // Sort by match count (descending), then by match percentage
        suggestions.sort((a, b) => {
          if (b.matchCount !== a.matchCount) {
            return b.matchCount - a.matchCount;
          }
          return b.matchPercentage - a.matchPercentage;
        });
        
        liveSuggestions = suggestions;
        console.log('[ChoiceCreator] Live suggestions:', liveSuggestions.length, 'sorted by match quality');
      } catch (error) {
        console.error('Error fetching live suggestions:', error);
        liveSuggestions = [];
      }
    }, 500);
  }
  
  function calculateMatchCount(suggestion) {
    // Count how many of the user's option labels match the suggestion's options
    const userLabels = options
      .map(o => o.label.trim().toLowerCase())
      .filter(label => label.length > 0);
    
    if (userLabels.length === 0) return 0;
    
    let matchCount = 0;
    
    for (const userLabel of userLabels) {
      const userWords = userLabel.split(/\s+/);
      
      // Check if this user label matches any suggestion option
      const hasMatch = suggestion.options.some(suggestionOption => {
        const suggestionLabel = suggestionOption.label.toLowerCase();
        const suggestionWords = suggestionLabel.split(/\s+/);
        
        // Exact match
        if (suggestionLabel === userLabel) return true;
        
        // Word-level match (at least one word matches)
        return suggestionWords.some(sw => userWords.includes(sw));
      });
      
      if (hasMatch) matchCount++;
    }
    
    return matchCount;
  }
</script>

<div class="choice-creator">
  <Header title="Choice Creator" subtitle="Create and discover global option sets">
    {#if activeTab === 'create' && createStep <= 2}
      <button class="btn btn-primary" on:click={checkForDuplicates} disabled={!displayName || !schemaName || !selectedDeployment || !selectedEnvironment || !selectedSolution || options.filter(o => o.label.trim()).length === 0}>
        Review & Create →
      </button>
    {/if}
  </Header>

  <!-- Settings Bar -->
  <div class="settings-bar">
    <div class="settings-group">
      <label>Deployment</label>
      <select bind:value={selectedDeployment}>
        <option value="">Select Deployment</option>
        {#each $deployments as deployment}
          <option value={deployment}>{deployment}</option>
        {/each}
      </select>
    </div>

    <div class="settings-group">
      <label>Environment</label>
      <select bind:value={selectedEnvironment} disabled={!selectedDeployment}>
        <option value="">Select Environment</option>
        {#each availableEnvironments as env}
          <option value={env}>{env}</option>
        {/each}
      </select>
    </div>

    <div class="settings-group">
      <label>Publisher Prefix</label>
      <input type="text" bind:value={publisherPrefix} placeholder="appbase_" />
    </div>

    <div class="settings-group">
      <label>Solution</label>
      <select bind:value={selectedSolution}>
        <option value="">Select Solution</option>
        {#each sortedSolutions as solution}
          <option value={solution.uniqueName}>
            {solution.displayName.replace(/^App Base - /i, '')}
          </option>
        {/each}
      </select>
    </div>

    {#if selectedSolution}
      <div class="settings-info">
        Creating in: <strong>{solutions.find(s => s.uniqueName === selectedSolution)?.path || selectedSolution}</strong>
      </div>
    {/if}
    
    {#if pendingOptionSets.length > 0}
      <div class="settings-info pending-info">
        <span>⏳ {pendingOptionSets.length} pending sync</span>
        <button class="clear-pending-btn" on:click={clearAllPending} title="Clear all pending">✕</button>
      </div>
    {/if}
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <button 
      class="tab" 
      class:active={activeTab === 'create'}
      on:click={() => activeTab = 'create'}
    >
      ➕ Create New
    </button>
    <button 
      class="tab" 
      class:active={activeTab === 'search'}
      on:click={() => activeTab = 'search'}
    >
      🔍 Search Existing
    </button>
    <button 
      class="tab" 
      class:active={activeTab === 'browse'}
      on:click={() => activeTab = 'browse'}
    >
      📚 Browse All
    </button>
  </div>

  <!-- Tab Content -->
  <div class="tab-content">
    <!-- Search Tab -->
    {#if activeTab === 'search'}
      <div class="search-tab">
        <div class="search-mode">
          <label>Search by:</label>
          <div class="radio-group">
            <label class="radio-option">
              <input type="radio" bind:group={searchMode} value="name" />
              <span>Option Set Name</span>
            </label>
            <label class="radio-option">
              <input type="radio" bind:group={searchMode} value="values" />
              <span>Choice Values</span>
            </label>
          </div>
        </div>
        
        <div class="search-box">
          <input 
            type="text" 
            bind:value={searchQuery} 
            placeholder={searchMode === 'name' ? 'Search by option set name...' : 'Search by choice values (comma-separated, e.g., Low, Medium, High)...'}
            on:input={searchOptionSets}
          />
          <button on:click={searchOptionSets} disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {#if searchResults.length > 0}
          <div class="results">
            {#each searchResults as result}
              <div class="option-set-card">
                <div class="card-header">
                  <div>
                    <h3>{result.displayName}</h3>
                    <p class="schema-name">{result.schemaName}</p>
                  </div>
                  <span class="badge">{result.category}/{result.module}</span>
                </div>
                <div class="card-body">
                  <div class="options-preview">
                    {#each result.options.slice(0, 5) as option}
                      <span class="option-chip" class:matching={isMatchingValue(option.label)}>{option.label}</span>
                    {/each}
                    {#if result.options.length > 5}
                      <span class="option-chip more">+{result.options.length - 5} more</span>
                    {/if}
                  </div>
                  {#if result.matchReasons && result.matchReasons.length > 0}
                    <div class="match-reasons">
                      <strong>Match:</strong> {result.matchReasons.join(', ')}
                    </div>
                  {/if}
                </div>
                <div class="card-footer">
                  <button class="btn-secondary" on:click={() => copyToClipboard(result.schemaName)}>
                    📋 Copy Schema Name
                  </button>
                </div>
              </div>
            {/each}
          </div>
        {:else if searchQuery && !loading}
          <p class="empty-state">
            No option sets found with {searchMode === 'name' ? 'matching name' : 'matching choice values'}. 
            {#if searchMode === 'values'}Try different values or search by name.{:else}Try creating a new one!{/if}
          </p>
        {:else if !searchQuery}
          <p class="empty-state">
            {#if searchMode === 'name'}
              Enter an option set name to search (e.g., "priority", "status")
            {:else}
              Enter choice values to search, separated by commas (e.g., "In Progress, Complete" or "Low, Medium, High")
            {/if}
          </p>
        {/if}
      </div>
    {/if}

    <!-- Create Tab -->
    {#if activeTab === 'create'}
      <div class="create-tab">
        <div class="create-layout" class:three-column={createStep <= 2}>
          {#if createStep <= 3}
            <!-- Left: Step 1 Basic Info -->
            <div class="step-column">
              <div class="form-section">
                <h3>Step 1: Basic Information</h3>
                <div class="form-group">
                  <label>Display Name *</label>
                  <input type="text" bind:value={displayName} on:blur={handleDisplayNameBlur} placeholder="e.g., Request Status" />
                </div>
                <div class="form-group">
                  <label>Schema Name *</label>
                  <input type="text" bind:value={schemaName} placeholder="e.g., appbase_requeststatus" />
                  <small>Will be auto-generated from display name</small>
                </div>
                <div class="form-group">
                  <label>Description (optional)</label>
                  <textarea bind:value={description} placeholder="Describe the purpose of this choice field..." rows="3"></textarea>
                </div>
              </div>
            </div>

            <!-- Middle: Step 2 Define Options -->
            <div class="step-column step-options">
              <div class="form-section">
                <h3>Step 2: Define Options</h3>
                <div class="options-table">
                  <div class="table-header">
                    <span>Label</span>
                    <span>Value (optional)</span>
                    <span>Actions</span>
                  </div>
                  {#each options as option, index}
                    <div class="table-row">
                      <input type="text" bind:value={option.label} bind:this={labelInputs[index]} on:blur={() => handleLabelBlur(index)} placeholder="Enter label" />
                      <input type="text" bind:value={option.value} placeholder="Auto-generated" on:blur={() => handleValueBlur(index)} />
                      <div class="row-actions">
                        <button on:click={() => moveOption(index, 'up')} disabled={index === 0} title="Move up">
                          ↑
                        </button>
                        <button on:click={() => moveOption(index, 'down')} disabled={index === options.length - 1} title="Move down">
                          ↓
                        </button>
                        <button on:click={() => removeOption(index)} disabled={options.length === 1} title="Remove">
                          ✕
                        </button>
                      </div>
                    </div>
                  {/each}
                </div>
                <button class="btn-secondary" on:click={addOption}>+ Add Option</button>
              </div>
            </div>
          {:else if createStep === 4}
            <div class="create-form">
              <!-- Step 4: Creation Result -->
              <div class="form-section">
                {#if creationResult?.success}
                  <div class="success-message">
                    <h3>✓ Option Set Created Successfully!</h3>
                    <p><strong>Display Name:</strong> {displayName}</p>
                    <p><strong>Schema Name:</strong> {schemaName}</p>
                    <p><strong>Environment:</strong> {creationResult.deployment} / {creationResult.environment}</p>
                    <p><strong>Solution:</strong> {creationResult.category}/{creationResult.module}</p>
                    <p><strong>Options:</strong> {creationResult.optionCount}</p>
                    <div class="pending-notice">
                      ⏳ This option set is <strong>pending sync</strong>. Run a solution sync to import it into your local repository.
                    </div>
                    <button class="btn-secondary" on:click={() => copyToClipboard(schemaName)}>
                      📋 Copy Schema Name
                    </button>
                  </div>
                {:else}
                  <div class="error-message">
                    <h3>✗ Error Creating Option Set</h3>
                    <p>{creationResult?.error || 'Unknown error'}</p>
                  </div>
                {/if}
                <div class="button-group">
                  <button class="btn-primary" on:click={resetCreateForm}>Create Another</button>
                  <button class="btn-secondary" on:click={() => activeTab = 'browse'}>Browse All</button>
                </div>
              </div>
            </div>
          {/if}
          
          <!-- Right: Live Suggestions -->
          {#if createStep <= 2 && liveSuggestions.length > 0}
            <!-- Live Suggestions Panel -->
            <div class="suggestions-panel">
              <div class="panel-header">
                <h4>💡 Similar Option Sets Found</h4>
                <span class="badge">{liveSuggestions.length}</span>
              </div>
              <p class="panel-hint">These existing option sets might match what you're creating. Consider reusing one!</p>
              <div class="suggestions-list">
                {#each liveSuggestions.slice(0, 5) as suggestion}
                  <div class="suggestion-card">
                    <div class="suggestion-header">
                      <strong>{suggestion.displayName}</strong>
                      <button class="btn-sm" on:click={() => copyToClipboard(suggestion.schemaName)} title="Copy schema name">
                        📋
                      </button>
                    </div>
                    <p class="schema-name-small">{suggestion.schemaName}</p>
                    <div class="options-preview-small">
                      {#each suggestion.options.slice(0, 4) as option}
                        <span class="option-chip-tiny" class:matching={isOptionMatchingForSuggestion(option.label)}>{option.label}</span>
                      {/each}
                      {#if suggestion.options.length > 4}
                        <span class="option-chip-tiny more">+{suggestion.options.length - 4}</span>
                      {/if}
                    </div>
                    {#if suggestion.matchCount > 0}
                      <div class="match-quality">
                        <span class="match-badge">{suggestion.matchPercentage}% match</span>
                        <span class="match-detail">({suggestion.matchCount}/{suggestion.totalOptions} values)</span>
                      </div>
                    {/if}
                    {#if suggestion.matchReasons && suggestion.matchReasons.length > 0}
                      <div class="match-hint">
                        {suggestion.matchReasons.slice(0, 2).join(', ')}
                      </div>
                    {/if}
                    <div class="suggestion-location">
                      📁 {suggestion.category}/{suggestion.module}
                    </div>
                  </div>
                {/each}
                {#if liveSuggestions.length > 5}
                  <p class="more-suggestions">+{liveSuggestions.length - 5} more similar option sets</p>
                {/if}
              </div>
            </div>
          {/if}
        </div>
      </div>
    {/if}

    <!-- Browse Tab -->
    {#if activeTab === 'browse'}
      <div class="browse-tab">
        <div class="browse-header">
          <input 
            type="text" 
            bind:value={browseFilter} 
            placeholder="Filter by name, category, or module..."
          />
          <button class="btn-secondary" on:click={loadOptionSets}>
            🔄 Refresh
          </button>
        </div>

        {#if loading}
          <p class="loading">Loading option sets...</p>
        {:else if Object.keys(groupedOptionSets).length > 0}
          <div class="browse-tree">
            {#each Object.entries(groupedOptionSets) as [path, optionSetsGroup]}
              <details class="tree-node" open={browseFilter !== ''}>
                <summary>
                  <strong>{path}</strong>
                  <span class="count">({optionSetsGroup.length})</span>
                </summary>
                <div class="tree-children">
                  {#each optionSetsGroup as optionSet}
                    <div class="option-set-item" class:pending-item={optionSet.isPending}>
                      <div class="item-header">
                        <h4>
                          {optionSet.displayName}
                          {#if optionSet.isPending}
                            <span class="pending-badge">⏳ Pending Sync</span>
                          {/if}
                        </h4>
                        <button class="btn-sm" on:click={() => copyToClipboard(optionSet.schemaName)}>
                          📋 Copy
                        </button>
                      </div>
                      <p class="schema-name">{optionSet.schemaName}</p>
                      <div class="options-preview">
                        {#each optionSet.options.slice(0, 8) as option}
                          <span class="option-chip-sm">{option.label}</span>
                        {/each}
                        {#if optionSet.options.length > 8}
                          <span class="option-chip-sm more">+{optionSet.options.length - 8}</span>
                        {/if}
                      </div>
                    </div>
                  {/each}
                </div>
              </details>
            {/each}
          </div>
        {:else}
          <p class="empty-state">No option sets found. Create your first one!</p>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Review Modal -->
  {#if showReviewModal}
    <div class="modal-overlay" on:click={() => showReviewModal = false} on:keydown={(e) => e.key === 'Escape' && (showReviewModal = false)} role="button" tabindex="0">
      <div class="modal-content" on:click|stopPropagation role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="modal-header">
          <h3 id="modal-title">⚠️ Final Review</h3>
          <button class="modal-close" on:click={() => showReviewModal = false}>✕</button>
        </div>
        
        <div class="modal-body">
          {#if duplicateMatches.length > 0}
            <p class="modal-warning">Found {duplicateMatches.length} similar option set{duplicateMatches.length > 1 ? 's' : ''}. Consider reusing one of these:</p>
            <div class="modal-suggestions">
              {#each duplicateMatches as match}
                <div class="modal-suggestion-card">
                  <div class="suggestion-header">
                    <strong>{match.displayName}</strong>
                    <button class="btn-sm" on:click={() => copyToClipboard(match.schemaName)} title="Copy schema name">
                      📋
                    </button>
                  </div>
                  <p class="schema-name-small">{match.schemaName}</p>
                  <div class="options-preview-small">
                    {#each match.options.slice(0, 6) as option}
                      <span class="option-chip-tiny">{option.label}</span>
                    {/each}
                    {#if match.options.length > 6}
                      <span class="option-chip-tiny more">+{match.options.length - 6}</span>
                    {/if}
                  </div>
                  {#if match.matchReasons && match.matchReasons.length > 0}
                    <div class="match-hint">
                      {match.matchReasons.join(', ')}
                    </div>
                  {/if}
                  <div class="suggestion-location">
                    📁 {match.category}/{match.module}
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <div class="modal-success">
              <div class="success-icon">✓</div>
              <p class="success-text">No similar option sets found!</p>
              <p class="success-detail">You're good to create a new one.</p>
            </div>
          {/if}
        </div>

        <div class="modal-footer">
          <button class="btn-primary" on:click={createOptionSet} disabled={loading || !selectedSolution}>
            {loading ? 'Creating...' : '✓ Create Option Set'}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .choice-creator {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  .settings-bar {
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 2rem;
    display: flex;
    gap: 1rem;
    align-items: flex-end;
    flex-wrap: wrap;
  }

  .settings-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 180px;
  }

  .settings-group label {
    font-size: 0.85rem;
    color: #999;
    font-weight: 500;
  }

  .settings-group select,
  .settings-group input {
    padding: 0.5rem;
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    font-family: inherit;
  }

  .settings-info {
    color: #60a5fa;
    font-size: 0.9rem;
    padding: 0.5rem;
    flex: 1;
    text-align: right;
  }

  .pending-info {
    background: #f59e0b22;
    border: 1px solid #f59e0b;
    border-radius: 4px;
    padding: 0.5rem 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    justify-content: space-between;
    color: #fbbf24;
    min-width: 180px;
    flex: none;
  }

  .clear-pending-btn {
    background: transparent;
    border: none;
    color: #fbbf24;
    cursor: pointer;
    padding: 0.25rem;
    font-size: 1rem;
    opacity: 0.7;
    transition: opacity 0.2s;
  }

  .clear-pending-btn:hover {
    opacity: 1;
  }

  .pending-badge {
    display: inline-block;
    background: #f59e0b;
    color: #000;
    padding: 0.15rem 0.5rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
    margin-left: 0.5rem;
    vertical-align: middle;
  }

  .pending-item {
    border-left: 3px solid #f59e0b;
    background: #f59e0b11;
  }

  .tabs {
    display: flex;
    gap: 0.5rem;
    border-bottom: 2px solid #3c3c3c;
    margin-bottom: 2rem;
  }

  .tab {
    padding: 0.75rem 1.5rem;
    background: transparent;
    border: none;
    color: #999;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
  }

  .tab:hover {
    color: #e0e0e0;
  }

  .tab.active {
    color: #60a5fa;
    border-bottom-color: #60a5fa;
  }

  .tab-content {
    min-height: 400px;
  }

  .search-mode {
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .search-mode label {
    color: #999;
    font-weight: 500;
    font-size: 0.9rem;
  }

  .radio-group {
    display: flex;
    gap: 1.5rem;
  }

  .radio-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    color: #e0e0e0;
    font-weight: 400;
  }

  .radio-option input[type="radio"] {
    cursor: pointer;
    width: 16px;
    height: 16px;
  }

  .radio-option:hover {
    color: #60a5fa;
  }

  .search-box {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .search-box input {
    flex: 1;
    padding: 0.75rem;
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    font-size: 1rem;
  }

  .search-box button {
    padding: 0.75rem 2rem;
  }

  .results {
    display: grid;
    gap: 1rem;
  }

  .option-set-card {
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    overflow: hidden;
  }

  .card-header {
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid #3c3c3c;
  }

  .card-header h3 {
    margin: 0;
    font-size: 1.1rem;
    color: #e0e0e0;
  }

  .schema-name {
    margin: 0.25rem 0 0 0;
    font-family: 'Courier New', monospace;
    color: #60a5fa;
    font-size: 0.9rem;
  }

  .badge {
    background: #3c3c3c;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.85rem;
    color: #999;
  }

  .card-body {
    padding: 1rem;
  }

  .options-preview {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .option-chip {
    background: #3c3c3c;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-size: 0.85rem;
    color: #e0e0e0;
    transition: all 0.2s;
  }

  .option-chip.matching {
    background: #1a4d2e;
    border: 1px solid #33cc66;
    color: #99ffcc;
    font-weight: 600;
  }

  .option-chip.more {
    background: #505050;
    color: #999;
  }

  .option-chip-sm {
    background: #3c3c3c;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    font-size: 0.75rem;
    color: #e0e0e0;
  }

  .option-chip-sm.more {
    background: #505050;
    color: #999;
  }

  .match-reasons {
    font-size: 0.85rem;
    color: #999;
  }

  .card-footer {
    padding: 1rem;
    border-top: 1px solid #3c3c3c;
    display: flex;
    gap: 0.5rem;
  }

  .form-section {
    max-width: 800px;
  }

  .form-section h3 {
    margin-top: 0;
    margin-bottom: 1.5rem;
    color: #e0e0e0;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #e0e0e0;
    font-weight: 500;
  }

  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: 0.75rem;
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
    font-family: inherit;
    font-size: 1rem;
  }

  .form-group small {
    display: block;
    margin-top: 0.25rem;
    color: #999;
    font-size: 0.85rem;
  }

  .options-table {
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .table-header {
    display: grid;
    grid-template-columns: 1fr 1fr auto;
    gap: 1rem;
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #3c3c3c;
    font-weight: 600;
    color: #999;
    font-size: 0.85rem;
  }

  .table-row {
    display: grid;
    grid-template-columns: 1fr 1fr auto;
    gap: 1rem;
    margin-bottom: 0.5rem;
    align-items: center;
  }

  .table-row input {
    padding: 0.5rem;
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
  }

  .row-actions {
    display: flex;
    gap: 0.25rem;
  }

  .row-actions button {
    padding: 0.25rem 0.5rem;
    background: #3c3c3c;
    border: none;
    border-radius: 3px;
    color: #e0e0e0;
    cursor: pointer;
    font-size: 0.85rem;
  }

  .row-actions button:hover:not(:disabled) {
    background: #505050;
  }

  .row-actions button:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .button-group {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
  }

  .btn-primary,
  .btn-secondary {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
  }

  .btn-primary {
    background: #60a5fa;
    color: #000;
    font-weight: 600;
  }

  .btn-primary:hover:not(:disabled) {
    background: #3b82f6;
  }

  .btn-primary:disabled {
    background: #374151;
    color: #6b7280;
    cursor: not-allowed;
    opacity: 0.6;
  }

  .btn-secondary {
    background: #3c3c3c;
    color: #e0e0e0;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #505050;
  }

  .btn-secondary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .success-message,
  .error-message {
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  .success-message {
    background: #003322;
    border: 2px solid #33cc66;
  }

  .success-message h3 {
    color: #99ffcc;
    margin-top: 0;
  }

  .success-message p {
    color: #ccffee;
    margin: 0.5rem 0;
  }

  .pending-notice {
    background: #f59e0b22;
    border: 1px solid #f59e0b;
    border-radius: 4px;
    padding: 0.75rem;
    margin: 1rem 0;
    color: #fbbf24;
    font-size: 0.9rem;
  }

  .error-message {
    background: #331100;
    border: 2px solid #ff3333;
  }

  .error-message h3 {
    color: #ff9999;
    margin-top: 0;
  }

  .error-message p {
    color: #ffcccc;
  }

  .browse-header {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .browse-header input {
    flex: 1;
    padding: 0.75rem;
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    color: #e0e0e0;
  }

  .browse-tree {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .tree-node {
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    overflow: hidden;
  }

  .tree-node summary {
    padding: 1rem;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    user-select: none;
  }

  .tree-node summary:hover {
    background: #333;
  }

  .tree-node .count {
    color: #999;
    font-size: 0.85rem;
  }

  .tree-children {
    padding: 0 1rem 1rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .option-set-item {
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 0.75rem;
  }

  .item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .item-header h4 {
    margin: 0;
    font-size: 0.95rem;
    color: #e0e0e0;
  }

  .btn-sm {
    padding: 0.25rem 0.75rem;
    font-size: 0.8rem;
    background: #3c3c3c;
    color: #e0e0e0;
    border: none;
    border-radius: 3px;
    cursor: pointer;
  }

  .btn-sm:hover {
    background: #505050;
  }

  .empty-state,
  .loading {
    text-align: center;
    padding: 3rem;
    color: #999;
    font-size: 1.1rem;
  }

  /* Live Suggestions Layout */
  .create-layout {
    display: grid;
    grid-template-columns: 1fr 400px;
    gap: 2rem;
    align-items: start;
  }

  .create-layout.three-column {
    grid-template-columns: 380px 1fr 350px;
    gap: 1.5rem;
  }

  .create-form {
    min-width: 0; /* Prevent grid blowout */
  }

  .step-column {
    min-width: 0;
  }

  .suggestions-panel {
    background: #2a2a2a;
    border: 2px solid #4a9eff;
    border-radius: 8px;
    padding: 1.5rem;
    max-height: 80vh;
    overflow-y: auto;
    position: sticky;
    top: 1rem;
  }

  .panel-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .panel-header h4 {
    margin: 0;
    color: #4a9eff;
    font-size: 1.1rem;
  }

  .panel-header .badge {
    background: #4a9eff;
    color: #000;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .panel-hint {
    color: #999;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    line-height: 1.4;
  }

  .suggestions-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .suggestion-card {
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 1rem;
    transition: border-color 0.2s, transform 0.2s;
  }

  .suggestion-card:hover {
    border-color: #4a9eff;
    transform: translateX(4px);
  }

  .suggestion-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .suggestion-header strong {
    color: #ffffff;
    font-size: 1rem;
    font-weight: 600;
  }

  .schema-name-small {
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
    color: #4a9eff;
    margin-bottom: 0.75rem;
  }

  .options-preview-small {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    margin-bottom: 0.5rem;
  }

  .option-chip-tiny {
    background: #3c3c3c;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    font-size: 0.75rem;
    color: #e0e0e0;
    transition: all 0.2s;
  }

  .option-chip-tiny.matching {
    background: #14532d;
    color: #86efac;
    border: 1px solid #15803d;
  }

  .option-chip-tiny.more {
    background: #505050;
    font-style: italic;
  }

  .match-hint {
    font-size: 0.75rem;
    color: #86efac;
    margin-bottom: 0.5rem;
  }

  .match-quality {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .match-badge {
    background: linear-gradient(135deg, #15803d 0%, #14532d 100%);
    color: #86efac;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid #15803d;
  }

  .match-detail {
    font-size: 0.75rem;
    color: #999;
  }

  .suggestion-location {
    font-size: 0.75rem;
    color: #999;
    font-style: italic;
  }

  .more-suggestions {
    text-align: center;
    color: #4a9eff;
    font-size: 0.85rem;
    padding: 0.5rem;
    font-style: italic;
  }

  /* Responsive adjustments */
  @media (max-width: 1400px) {
    .create-layout.three-column {
      grid-template-columns: 1fr 380px;
    }

    .step-column:first-child,
    .step-column.step-options {
      grid-column: 1;
    }

    .step-column:first-child {
      grid-row: 1;
    }

    .step-column.step-options {
      grid-row: 2;
    }

    .suggestions-panel {
      grid-column: 2;
      grid-row: 1 / 3;
    }
  }

  @media (max-width: 1000px) {
    .create-layout,
    .create-layout.three-column {
      grid-template-columns: 1fr;
    }

    .step-column,
    .suggestions-panel {
      grid-column: 1;
      grid-row: auto;
    }

    .suggestions-panel {
      position: static;
      max-height: 400px;
    }
  }

  /* Modal Styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
  }

  .modal-content {
    background: #1a1a1a;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.5);
    max-width: 800px;
    width: 100%;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #3c3c3c;
    flex-shrink: 0;
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: #f59e0b;
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #9ca3af;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .modal-close:hover {
    background: #3c3c3c;
    color: #e0e0e0;
  }

  .modal-body {
    padding: 1.5rem;
    overflow-y: auto;
    flex: 1;
  }

  .modal-warning {
    margin: 0 0 1rem 0;
    padding: 1rem;
    background: #3c2b1f;
    border-left: 4px solid #f59e0b;
    border-radius: 4px;
    color: #fbbf24;
  }

  .modal-suggestions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .modal-suggestion-card {
    background: #2a2a2a;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 1rem;
  }

  .suggestion-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }

  .suggestion-header strong {
    color: #ffffff;
    font-size: 1rem;
    font-weight: 600;
  }

  .modal-suggestion-card .schema-name-small {
    font-size: 0.875rem;
    color: #4a9eff;
    font-family: monospace;
    margin: 0.25rem 0 0.5rem 0;
  }

  .options-preview-small {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    margin-bottom: 0.5rem;
  }

  .modal-suggestion-card .option-chip-tiny {
    display: inline-block;
    padding: 0.125rem 0.5rem;
    background: #3c3c3c;
    border: 1px solid #505050;
    border-radius: 12px;
    font-size: 0.75rem;
    color: #e0e0e0;
  }

  .modal-suggestion-card .option-chip-tiny.more {
    background: #505050;
    color: #9ca3af;
    font-weight: 500;
  }

  .modal-suggestion-card .match-hint {
    font-size: 0.75rem;
    color: #86efac;
    font-style: italic;
    margin: 0.5rem 0;
  }

  .modal-suggestion-card .suggestion-location {
    font-size: 0.75rem;
    color: #9ca3af;
    margin-top: 0.5rem;
  }

  .modal-success {
    text-align: center;
    padding: 2rem 1rem;
  }

  .success-icon {
    width: 64px;
    height: 64px;
    background: #14532d;
    color: #22c55e;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin: 0 auto 1rem;
  }

  .success-text {
    font-size: 1.25rem;
    font-weight: 600;
    color: #22c55e;
    margin: 0 0 0.5rem 0;
  }

  .success-detail {
    color: #9ca3af;
    margin: 0;
  }

  .modal-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 1rem 1.5rem;
    border-top: 1px solid #3c3c3c;
    gap: 1rem;
    flex-shrink: 0;
  }
</style>

