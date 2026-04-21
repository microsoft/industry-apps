<!--
  EnvironmentSelector.svelte
  
  A reusable environment selector component that displays environments
  from a selected deployment configuration.
  
  Props:
    - deployment: object - The selected deployment object with Environments property
    - value: string (two-way binding) - Selected environment key
    - disabled: boolean - Disable the selector
    - placeholder: string - Placeholder text for empty selection
    - label: string - Label text
    - showLabel: boolean - Show/hide the label
    - className: string - Additional CSS classes
  
  Events:
    - change: Dispatched when selection changes { key, name }
  
  Usage:
    <EnvironmentSelector 
      deployment={selectedDeployment}
      bind:value={selectedEnvKey}
      on:change={handleEnvironmentChange}
    />
-->
<script>
  import { createEventDispatcher } from 'svelte';

  export let deployment = null;
  export let value = '';
  export let disabled = false;
  export let placeholder = '-- Select Environment --';
  export let label = 'Environment';
  export let showLabel = true;
  export let className = '';

  const dispatch = createEventDispatcher();

  // Get sorted environment list from deployment
  $: environments = deployment && deployment.Environments 
    ? Object.entries(deployment.Environments).sort((a, b) => a[0].localeCompare(b[0]))
    : [];

  // Handle selection change
  function handleChange(event) {
    const selectedKey = event.target.value;
    const selectedEnv = environments.find(([key]) => key === selectedKey);
    
    dispatch('change', {
      key: selectedKey,
      name: selectedEnv ? selectedEnv[1] : null
    });
  }

  // Reset value when deployment changes
  $: if (deployment) {
    // Check if current value is valid for new deployment
    const isValid = environments.some(([key]) => key === value);
    if (!isValid) {
      value = '';
    }
  }
</script>

<div class="environment-selector {className}">
  {#if showLabel}
    <label for="environment-select">{label}:</label>
  {/if}
  <select 
    id="environment-select" 
    bind:value={value}
    on:change={handleChange}
    disabled={disabled || !deployment || environments.length === 0}
  >
    <option value="">{placeholder}</option>
    {#each environments as [key, name]}
      <option value={key}>{key}</option>
    {/each}
  </select>
</div>

<style>
  .environment-selector {
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
    transition: all 0.2s ease;
  }

  select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  select:not(:disabled):hover {
    border-color: #1e90ff;
    background: #333333;
  }

  select:focus {
    outline: none;
    border-color: #1e90ff;
    box-shadow: 0 0 0 2px rgba(30, 144, 255, 0.1);
  }

  option {
    background: #2a2a2a;
    color: #e0e0e0;
    padding: 8px;
  }
</style>
