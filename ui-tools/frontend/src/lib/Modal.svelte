<script>
  export let show = false;
  export let title = '';
  export let onClose = null;
  export let size = 'medium'; // 'small', 'medium', 'large'
  export let status = null; // null, 'running', 'success', 'error'
  export let closeOnOverlayClick = true;

  function handleOverlayClick() {
    if (closeOnOverlayClick && onClose) {
      onClose();
    }
  }

  function handleCloseClick() {
    if (onClose) {
      onClose();
    }
  }
</script>

{#if show}
  <div class="modal-overlay" on:click={handleOverlayClick}>
    <div 
      class="modal {size} {status || ''}" 
      on:click={(e) => e.stopPropagation()}
    >
      {#if title}
        <div class="modal-header">
          <h2>
            {#if status === 'running'}⏳{:else if status === 'success'}✅{:else if status === 'error'}❌{/if}
            {title}
          </h2>
          {#if onClose && status !== 'running'}
            <button class="close-btn" on:click={handleCloseClick} title="Close">
              ✕
            </button>
          {/if}
        </div>
      {/if}
      
      <div class="modal-content">
        <slot></slot>
      </div>
      
      {#if $$slots.footer}
        <div class="modal-footer">
          <slot name="footer"></slot>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.75);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(2px);
  }

  .modal {
    background: #252526;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    border: 1px solid #3c3c3c;
    max-width: 95%;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    animation: modalSlideIn 0.2s ease-out;
  }

  @keyframes modalSlideIn {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .modal.small {
    width: 400px;
  }

  .modal.medium {
    width: 600px;
  }

  .modal.large {
    width: 1000px;
  }

  .modal.running {
    border-top: 4px solid #0078d4;
  }

  .modal.success {
    border-top: 4px solid #4caf50;
  }

  .modal.error {
    border-top: 4px solid #f44336;
  }

  .modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid #3c3c3c;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.25rem;
    color: #ffffff;
    font-weight: 600;
  }

  .close-btn {
    background: transparent;
    border: none;
    color: #cccccc;
    font-size: 1.5rem;
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

  .close-btn:hover {
    background: #3c3c3c;
    color: #ffffff;
  }

  .modal-content {
    padding: 1.5rem;
    overflow-y: auto;
    flex: 1;
    min-height: 0;
  }

  .modal-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid #3c3c3c;
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
  }

  /* Custom scrollbar */
  .modal-content::-webkit-scrollbar {
    width: 8px;
  }

  .modal-content::-webkit-scrollbar-track {
    background: #1e1e1e;
  }

  .modal-content::-webkit-scrollbar-thumb {
    background: #3c3c3c;
    border-radius: 4px;
  }

  .modal-content::-webkit-scrollbar-thumb:hover {
    background: #505050;
  }
</style>
