<script>
  import { outputLines, operationStatus, clearOutput } from './stores.js';
  import Modal from './Modal.svelte';

  $: showModal = $outputLines.length > 0 || $operationStatus === 'running';
  $: canClose = $operationStatus !== 'running';
</script>

<Modal 
  show={showModal} 
  title="Operation Output"
  size="large"
  status={$operationStatus}
  onClose={canClose ? clearOutput : null}
  closeOnOverlayClick={canClose}
>
  <div class="output-container">
    {#each $outputLines as line}
      <div class="output-line">{line}</div>
    {/each}
    {#if $operationStatus === 'running'}
      <div class="output-line processing">⏳ Processing...</div>
    {/if}
  </div>

  <svelte:fragment slot="footer">
    {#if $operationStatus !== 'running'}
      <button class="btn btn-primary" on:click={clearOutput}>
        Close
      </button>
    {/if}
  </svelte:fragment>
</Modal>

<style>
  .output-container {
    background: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 1rem;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    color: #e0e0e0;
    max-height: 60vh;
    overflow-y: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
  }

  .output-line {
    margin: 0;
    padding: 2px 0;
  }

  .output-line.processing {
    color: #4fc3f7;
    font-weight: 600;
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.6;
    }
  }

  .btn {
    padding: 0.625rem 1.25rem;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
  }

  .btn-primary {
    background-color: #0078d4;
    color: white;
  }

  .btn-primary:hover {
    background-color: #1a86e0;
  }

  /* Custom scrollbar for output */
  .output-container::-webkit-scrollbar {
    width: 8px;
  }

  .output-container::-webkit-scrollbar-track {
    background: #0d0d0d;
  }

  .output-container::-webkit-scrollbar-thumb {
    background: #3c3c3c;
    border-radius: 4px;
  }

  .output-container::-webkit-scrollbar-thumb:hover {
    background: #505050;
  }
</style>
