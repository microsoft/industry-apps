<!--
  ModuleSelector.svelte
  
  A reusable module selector component that displays modules in alphabetical order
  by their display name. Only shows modules with .cdsproj files (actual Dataverse modules).
  Integrates with the global modules store.
  
  Props:
    - value: string (two-way binding) - Selected module path
    - disabled: boolean - Disable the selector
    - placeholder: string - Placeholder text for empty selection
    - label: string - Label text
    - showLabel: boolean - Show/hide the label
    - className: string - Additional CSS classes
    - filterFunction: function - Optional filter function to filter modules (module => boolean)
    - allowedPaths: Set|Array - Optional Set or Array of allowed module paths (takes precedence over filterFunction)
  
  Events:
    - change: Dispatched when selection changes { path, module }
  
  Usage:
    <ModuleSelector 
      bind:value={selectedModule}
      on:change={handleModuleChange}
      allowedPaths={myPathsSet}
    />
-->
<script>
  import { modules } from './stores.js';
  import { createEventDispatcher } from 'svelte';

  export let value = '';
  export let disabled = false;
  export let placeholder = '-- Select Module --';
  export let label = 'Module';
  export let showLabel = true;
  export let className = '';
  export let filterFunction = null;
  export let allowedPaths = null; // Set or Array of allowed module paths

  const dispatch = createEventDispatcher();

  // Filter and sort modules alphabetically by display name
  $: sortedModules = [...$modules]
    .filter(module => {
      // If allowedPaths is provided, only show those modules
      if (allowedPaths) {
        const pathsArray = allowedPaths instanceof Set ? Array.from(allowedPaths) : allowedPaths;
        return pathsArray.includes(module.path);
      }
      // Otherwise use filterFunction if provided
      return filterFunction ? filterFunction(module) : true;
    })
    .sort((a, b) => {
      const nameA = a.displayName || a.display_name || a.name || '';
      const nameB = b.displayName || b.display_name || b.name || '';
      return nameA.localeCompare(nameB);
    });

  // Format module display text (just the friendly name)
  function getDisplayText(module) {
    return module.displayName || module.display_name || module.name || module.path;
  }

  // Handle selection change
  function handleChange(event) {
    const selectedPath = event.target.value;
    const selectedModule = sortedModules.find(m => m.path === selectedPath);
    
    dispatch('change', {
      path: selectedPath,
      module: selectedModule
    });
  }
</script>

<div class="module-selector {className}">
  {#if showLabel}
    <label for="module-select">{label}:</label>
  {/if}
  <select 
    id="module-select" 
    bind:value={value}
    on:change={handleChange}
    {disabled}
  >
    <option value="">{placeholder}</option>
    {#each sortedModules as module}
      <option value={module.path}>{getDisplayText(module)}</option>
    {/each}
  </select>
</div>

<style>
  .module-selector {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  label {
    color: #e0e0e0;
    font-weight: 500;
    font-size: 14px;
  }

  select {
    padding: 10px 12px;
    font-size: 14px;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    min-width: 300px;
    background: #2a2a2a;
    color: #e0e0e0;
    cursor: pointer;
    transition: all 0.2s;
  }

  select:hover:not(:disabled) {
    border-color: #60a5fa;
    background: #333;
  }

  select:focus {
    outline: none;
    border-color: #60a5fa;
    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
  }

  select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  select option {
    background: #2a2a2a;
    color: #e0e0e0;
  }
</style>
