/**
 * Shared Cytoscape configuration — node types, colors, styles, and utilities.
 * Extracted from ArchExplorer.astro. Used by GraphBlock and AtlasPage.
 */

export const typeConfig: Record<string, { bg: string; border: string; text: string; shape: string }> = {
  group:            { bg: '#2a2a4e', border: '#4a4a6e', text: '#aaa', shape: 'roundrectangle' },
  component:        { bg: '#4a90d9', border: '#3a78c0', text: '#fff', shape: 'roundrectangle' },
  frontend:         { bg: '#4a90d9', border: '#3a78c0', text: '#fff', shape: 'roundrectangle' },
  service:          { bg: '#3498db', border: '#2980b9', text: '#fff', shape: 'roundrectangle' },
  'external-service': { bg: '#e67e22', border: '#cf6d14', text: '#fff', shape: 'diamond' },
  endpoint:         { bg: '#d4740e', border: '#b8640c', text: '#fff', shape: 'diamond' },
  route:            { bg: '#1abc9c', border: '#14a085', text: '#fff', shape: 'hexagon' },
  library:          { bg: '#9b59b6', border: '#8244a0', text: '#fff', shape: 'roundrectangle' },
  config:           { bg: '#c0392b', border: '#a93226', text: '#fff', shape: 'ellipse' },
  gateway:          { bg: '#e67e22', border: '#cf6d14', text: '#fff', shape: 'diamond' },
  store:            { bg: '#1abc9c', border: '#14a085', text: '#fff', shape: 'barrel' },
  worker:           { bg: '#2ecc71', border: '#27ae60', text: '#fff', shape: 'roundrectangle' },
  api:              { bg: '#3498db', border: '#2980b9', text: '#fff', shape: 'roundrectangle' },
  external:         { bg: '#e74c3c', border: '#c0392b', text: '#fff', shape: 'octagon' },
  actor:            { bg: '#14b8a6', border: '#0d9488', text: '#fff', shape: 'ellipse' },
  broker:           { bg: '#f97316', border: '#ea580c', text: '#fff', shape: 'hexagon' },
  cli:              { bg: '#64748b', border: '#475569', text: '#fff', shape: 'diamond' },
  scheduler:        { bg: '#6366f1', border: '#4f46e5', text: '#fff', shape: 'roundrectangle' },
};

export function getTypeConfig(type: string) {
  return typeConfig[type] || typeConfig.component;
}

export const severityColors: Record<string, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#f59e0b',
  low: '#22c55e',
  none: '#555',
};

export const confidenceColors: Record<string, { bg: string; text: string; border: string }> = {
  high:   { bg: '#22c55e33', text: '#22c55e', border: '#22c55e' },
  medium: { bg: 'transparent', text: '#f59e0b', border: '#f59e0b' },
  low:    { bg: 'transparent', text: '#64748b', border: '#64748b' },
};

export const flowColors = [
  '#7b68ee', '#e74c3c', '#2ecc71', '#e67e22', '#3498db',
  '#9b59b6', '#1abc9c', '#f39c12', '#e91e63', '#00bcd4',
];

/** Cytoscape stylesheet shared across all graph instances */
export const cytoscapeStyles = [
  // Base node
  {
    selector: 'node',
    style: {
      'label': 'data(label)',
      'text-valign': 'center',
      'text-halign': 'center',
      'font-size': '11px',
      'color': '#fff',
      'text-wrap': 'wrap',
      'text-max-width': '120px',
      'min-zoomed-font-size': 8,
    }
  },
  // Typed nodes — applied dynamically via classes
  ...Object.entries(typeConfig).map(([type, cfg]) => ({
    selector: `node[nodeType="${type}"]`,
    style: {
      'background-color': cfg.bg,
      'border-color': cfg.border,
      'color': cfg.text,
      'shape': cfg.shape,
      'border-width': 1.5,
    }
  })),
  // Group/parent nodes
  {
    selector: 'node[?collapsed][?hasChildren]',
    style: {
      'border-style': 'dashed',
      'border-width': 1,
      'opacity': 0.85,
    }
  },
  // Hover glow
  {
    selector: 'node.hover-glow',
    style: {
      'overlay-color': '#7b68ee',
      'overlay-padding': 6,
      'overlay-opacity': 0.25,
    }
  },
  // Flow highlighting
  {
    selector: 'node.flow-halo',
    style: {
      'border-width': 3,
      'border-color': '#7b68ee',
      'overlay-color': '#7b68ee',
      'overlay-padding': 4,
      'overlay-opacity': 0.15,
    }
  },
  // Dimmed
  {
    selector: '.dimmed',
    style: { 'opacity': 0.08 }
  },
  // Debt border rings
  {
    selector: 'node[debtColor]',
    style: {
      'border-width': 2.5,
      'border-color': 'data(debtColor)',
    }
  },
  // Base edge
  {
    selector: 'edge',
    style: {
      'width': 1.5,
      'line-color': 'rgba(255,255,255,0.15)',
      'target-arrow-color': 'rgba(255,255,255,0.15)',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'arrow-scale': 0.8,
      'font-size': '9px',
      'color': 'rgba(255,255,255,0.4)',
      'text-background-color': '#1a1a2e',
      'text-background-opacity': 0.8,
      'text-background-padding': '2px',
    }
  },
  // Edge label (hidden by default, shown on hover)
  {
    selector: 'edge[label]',
    style: { 'label': 'data(label)' }
  },
  {
    selector: 'edge[?hideLabel]',
    style: { 'label': '' }
  },
  // Highlighted edge
  {
    selector: 'edge.highlighted',
    style: {
      'width': 2.5,
      'line-color': '#7b68ee',
      'target-arrow-color': '#7b68ee',
    }
  },
  // Read/write edges (data lineage)
  {
    selector: 'edge[edgeType="reads"]',
    style: { 'line-color': '#22c55e', 'target-arrow-color': '#22c55e' }
  },
  {
    selector: 'edge[edgeType="writes"]',
    style: { 'line-color': '#ef4444', 'target-arrow-color': '#ef4444' }
  },
];
