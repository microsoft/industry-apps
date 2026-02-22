<script>
  export let title = 'Page Title';
  export let description = '';
</script>

<header class="page-header">
  <div class="header-content">
    <h1>{title}</h1>
    {#if description}
      <p class="description">{description}</p>
    {/if}
  </div>
  <div class="header-actions">
    <slot></slot>
  </div>
</header>

<style>
  .page-header {
    padding: 1.5rem 2rem;
    background: #1a1a1a;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
  }

  .header-content h1 {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 700;
    color: #ffffff;
  }

  .description {
    margin: 0.5rem 0 0 0;
    font-size: 0.9rem;
    color: #94a3b8;
  }

  .header-actions {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  @media (max-width: 768px) {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
    }
  }
</style>
