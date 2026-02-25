import { writable } from 'svelte/store';

// Global configuration from backend
export const config = writable(null);

// Modules list
export const modules = writable([]);

// Environments/tenants structure
export const tenants = writable([]);

// Available deployment names
export const deployments = writable([]);

// Categories extracted from modules
export const categories = writable(new Set());

// Operation output state
export const outputLines = writable([]);
export const operationStatus = writable(''); // '', 'running', 'success', 'error', 'cancelled'
export const activeOperation = writable(null);
export const currentOperationId = writable(null);

// Sidebar state
export const sidebarCollapsed = writable(false);

// Helper function to load config
export async function loadConfig() {
  try {
    const response = await fetch('/api/config');
    if (!response.ok) {
      console.error('Failed to load config:', response.status, response.statusText);
      return false;
    }
    const data = await response.json();
    console.log('Loaded config:', data);
    config.set(data);
    deployments.set(Object.keys(data.deployments || {}));
    return true;
  } catch (error) {
    console.error('Error loading config:', error);
    return false;
  }
}

// Helper function to load modules
export async function loadModules() {
  try {
    const response = await fetch('/api/modules');
    if (!response.ok) {
      console.error('Failed to load modules:', response.status, response.statusText);
      return false;
    }
    const data = await response.json();
    console.log('Loaded modules:', data);
    modules.set(data.modules || []);
    
    // Extract unique categories
    const cats = new Set((data.modules || []).map(m => m.category));
    categories.set(cats);
    return true;
  } catch (error) {
    console.error('Error loading modules:', error);
    return false;
  }
}

// Helper function to load environments
export async function loadEnvironments() {
  try {
    const response = await fetch('/api/environments');
    if (!response.ok) {
      console.error('Failed to load environments:', response.status, response.statusText);
      return false;
    }
    const data = await response.json();
    console.log('Loaded environments:', data);
    tenants.set(data.tenants || []);
    return true;
  } catch (error) {
    console.error('Error loading environments:', error);
    return false;
  }
}

// Stream response helper
export async function streamResponse(response) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
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
            console.log('[DEBUG] SSE data:', data);
            
            if (data.type === 'output') {
              outputLines.update(lines => [...lines, data.line]);
            } else if (data.type === 'complete') {
              operationStatus.set(data.exitCode === 0 ? 'success' : 'error');
              outputLines.update(lines => [...lines, `\n${data.exitCode === 0 ? '✓' : '✗'} Completed with exit code: ${data.exitCode}`]);
            } else if (data.type === 'error') {
              operationStatus.set('error');
              console.error('[ERROR] Backend error:', data);
              outputLines.update(lines => [...lines, `\n✗ Error: ${data.message || 'Unknown error'}`]);
            }
          } catch (parseError) {
            console.error('Failed to parse SSE data:', line, parseError);
            outputLines.update(lines => [...lines, `\n✗ Parse error: ${line}`]);
          }
        }
      }
    }
  } catch (error) {
    operationStatus.set('error');
    outputLines.update(lines => [...lines, `\n✗ Stream error: ${error.message || error}`]);
  }
}

// Clear output
export function clearOutput() {
  outputLines.set([]);
  activeOperation.set(null);
  operationStatus.set('');
  currentOperationId.set(null);
}

// Cancel operation
export async function cancelOperation() {
  let opId;
  currentOperationId.subscribe(value => opId = value)();
  
  if (!opId) {
    console.warn('No operation to cancel');
    return;
  }
  
  try {
    operationStatus.set('cancelling');
    outputLines.update(lines => [...lines, '\n⏸ Cancelling operation...']);
    
    const response = await fetch('/api/cancel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ operationId: opId })
    });
    
    const result = await response.json();
    
    if (result.success) {
      operationStatus.set('cancelled');
      outputLines.update(lines => [...lines, '✗ Operation cancelled by user']);
    } else {
      operationStatus.set('error');
      outputLines.update(lines => [...lines, `✗ Failed to cancel: ${result.message}`]);
    }
  } catch (error) {
    operationStatus.set('error');
    outputLines.update(lines => [...lines, `✗ Cancel error: ${error.message}`]);
  }
}
