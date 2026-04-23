---
kind: concept
name: block-content
signatures: {}
type: pattern
abstraction:
- data
- content
scope: domain
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `block`, `Block`, `block_type` fields defining typed content units
- `children` arrays on blocks forming a nested tree structure
- `rich_text`, `RichText` models or fields with inline formatting spans
- Slate.js: `slate`, `slate-react`, `Editable`, `Element`, `Leaf` components
- ProseMirror: `prosemirror-model`, `prosemirror-state`, `Schema`, `Node`, `Mark`
- Tiptap: `@tiptap/core`, `@tiptap/starter-kit`, `Editor`, custom `Extension`
- Draft.js: `draft-js`, `EditorState`, `ContentBlock`, `convertToRaw`
- Editor.js: `@editorjs/editorjs`, `tools` configuration, block-based output JSON
- Python: Wagtail `StreamField`, `StructBlock`, `ListBlock`, `RichTextBlock`
- `content_block`, `BlockSerializer`, `block_data` in API payloads

### Confidence

- **high** -- ProseMirror/Slate/Tiptap editor with typed block schema, nested block hierarchy, and collaborative editing support
- **medium** -- Editor.js or Wagtail StreamField with block type definitions and structured JSON output
- **low** -- HTML blob stored in a text column with client-side WYSIWYG editing but no block structure

## Architecture

### Relationship To Other Concepts

- `block-content` is the content-domain model itself: typed blocks, hierarchy, serialization, and editing semantics.
- Use `component` for the rendering tree, not for the persisted content structure.
- Use `versioned-document` when document history or collaboration lineage is the main concern.
- Use `search-index` when the important concern is flattened retrieval or faceting over block content.

### When to use
- Content management systems where editors need structured, reusable content blocks
- Collaborative editing platforms requiring granular change tracking per block
- Applications where content must render across multiple targets (web, mobile, email) from a single structured source

### Anti-patterns
- Storing content as raw HTML, losing semantic structure and making cross-platform rendering brittle
- Deeply nested block hierarchies without depth limits, causing rendering performance issues
- Building a custom block editor instead of using ProseMirror/Slate/Tiptap, which handle edge cases in text editing

### Complements
- [versioned-document](/concepts/versioned-document) — block content benefits from per-block version tracking
- [component](/concepts/component) — content blocks map to rendering components in the frontend
- [search-index](/concepts/search-index) — block content must be flattened for full-text indexing

### Boundary

Prefer `block-content` only when the code models content as typed, nested blocks. A WYSIWYG editor storing a single HTML or Markdown blob is not enough.

## Impact

Block-based content structures determine how content is stored, edited, and rendered across platforms. The choice of editor framework cascades into serialization format, collaboration protocol, and rendering pipeline, making it a foundational architectural decision.
