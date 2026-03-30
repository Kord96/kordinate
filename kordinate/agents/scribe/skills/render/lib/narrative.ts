/**
 * Narrative parsing — bold refs, markdown headings, escaping.
 * Extracted from ArchExplorer.astro.
 */

export function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/**
 * Parse narrative text into HTML.
 * - Splits on double newlines into paragraphs
 * - Converts **bold refs** into clickable spans with data-node-id
 * - Converts markdown headings (##, ###) into HTML headings
 * - Converts -- into em dashes
 *
 * @param text Raw narrative text
 * @param resolveNodeId Function that maps a name to an atlas node ID (or null)
 */
export function parseNarrativeToHtml(
  text: string,
  resolveNodeId: (name: string) => string | null
): string {
  if (!text) return '';
  var blocks = text.split(/\n\n+/);
  return blocks.map(function(block) {
    var trimmed = block.trim();
    if (!trimmed) return '';

    // Markdown headings
    var headingMatch = trimmed.match(/^(#{1,3})\s+(.*)$/);
    if (headingMatch) {
      var level = headingMatch[1].length + 1;
      var hText = parseBoldRefs(headingMatch[2], resolveNodeId);
      return '<h' + level + '>' + hText + '</h' + level + '>';
    }

    // Regular paragraph
    var html = parseBoldRefs(trimmed, resolveNodeId);
    html = html.replace(/ -- /g, ' — ');
    html = html.replace(/\n/g, '<br>');
    return '<p>' + html + '</p>';
  }).join('');
}

/**
 * Convert **bold text** into clickable node refs or plain <strong>.
 */
function parseBoldRefs(
  text: string,
  resolveNodeId: (name: string) => string | null
): string {
  return escapeHtml(text).replace(/\*\*([^*]+)\*\*/g, function(_m, name) {
    var nid = resolveNodeId(name);
    if (nid) {
      return '<span class="node-ref" data-node-id="' + escapeHtml(nid) + '">' + escapeHtml(name) + '</span>';
    }
    return '<strong>' + escapeHtml(name) + '</strong>';
  });
}
