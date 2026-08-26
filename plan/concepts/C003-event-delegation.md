---
id: C003
title: Event Delegation Pattern
type: pattern
status: STABLE
created: 2026-08-21
updated: 2026-08-26
related:
  - D003
  - P004
---

## Goal

Route all UI events through a single centralized handler that dispatches to appropriate handlers based on element attributes, rather than attaching listeners to each element.

## Pattern Description

### Mechanism

1. **Single listener** on document for a specific event (e.g., `click`)
2. **Check event.target** for `data-action` attribute
3. **Route** to appropriate module method based on action value
4. **Module updates** state and rerenders as needed

### Example

```html
<!-- HTML: defines action and passes context -->
<button data-action="open-editor" data-id="P001">Edit</button>

<!-- Dispatcher: central listener -->
document.addEventListener('click', (e) => {
  const action = e.target.dataset.action;
  if (action === 'open-editor') {
    const id = e.target.dataset.id;
    FileEditor.openEditor(id);
  }
});
```

### Benefits

- **Reduced overhead** — 1 listener vs 100+ listeners on large pages
- **Dynamic content** — new elements added to DOM automatically handled
- **Centralized logic** — all routing in one place
- **Loose coupling** — modules don't need to know about DOM structure
- **Memory efficient** — no listener cleanup needed when elements removed

### lplan Implementation

- **Dispatcher** module handles routing
- **Data-attributes** define action: `data-action="search"`, `data-id="P001"`, etc.
- **Module methods** handle side effects and re-rendering
- **State** stored in module static variables, not on DOM

## Trade-offs

- **Debugging** — requires understanding attribute naming convention
- **Accessibility** — must ensure keyboard events also routed
- **Learning curve** — developers new to pattern need context
- **Performance** — trivial for typical UI sizes

## Log

2026-08-26 — Formalized as lplan UI pattern.
2026-08-21 — Pattern validated through P004 refactoring.
