# Server.py Refactor Plan

## Executive Summary

**Current Problem:** `src/planner/server.py` lines 216-1781 contain a 1568-line raw Python string (`_HTML`) with mixed HTML, CSS, and 1000+ lines of JavaScript. This creates severe maintenance issues:
- Quote escaping bugs causing toggle handler failures
- Toggle logic scattered across onclick handlers, CSS rules, and class toggles
- No syntax highlighting or IDE support for embedded code
- Hard to reason about state management
- Difficult to test JavaScript behavior
- Every small UI change risks breaking other parts

**Solution:** 3-phase incremental refactor (total ~2.5 hours) that extracts and modularizes code without breaking the working UI.

---

## Phase 1: Extract Static Resources (45 min) — LOW RISK

**Goal:** Separate CSS and library imports from the main HTML template, reducing complexity.

### Step 1.1: Extract CSS to `_CSS` constant (15 min)

**What:** Move all `<style>` content to a separate Python constant.

**Current state:** Lines 230-610 contain inline CSS within the HTML template.

**Process:**
1. Create new constant `_CSS = r"""..."""` before `_HTML`
2. Copy all CSS from `<style>` tags (lines 230-610)
3. Replace with `<style>${_CSS}</style>` in the template
4. Verify: Load page, check DevTools → Elements → Styles are applied

**Before:**
```python
_HTML = r"""...
<style>
  body { ... }
  .tree-toggle { ... }
  ...
</style>
..."""
```

**After:**
```python
_CSS = r"""
  body { ... }
  .tree-toggle { ... }
  ...
"""

_HTML = r"""...
<style>${_CSS}</style>
..."""
```

**Testing:** Reload browser, verify all colors/fonts/layout unchanged

**Time:** 15 min  
**Risk:** LOW — pure extraction  
**Rollback:** Undo the split, revert to inline CSS  

---

### Step 1.2: Extract library CDN links (10 min)

**What:** Move `<script>` and `<link>` tags for external libraries to a constant.

**Current state:** Lines 224-228 have marked.js and CodeMirror CDN links embedded in HTML.

**Process:**
1. Create `_LIBRARIES_HEAD = r"""..."""`
2. Extract CDN `<script>` and `<link>` tags
3. Replace with `${_LIBRARIES_HEAD}` in template
4. Verify: Check DevTools → Network tab for CDN requests

**Testing:** Reload browser, verify markdown rendering works, CodeMirror loads

**Time:** 10 min  
**Risk:** LOW — pure extraction  
**Rollback:** Inline the libraries again  

---

### Step 1.3: Fix quote escaping in toggle handlers (20 min)

**What:** Replace inline onclick with data-attributes and event delegation to fix quote escaping bugs.

**Current problem:**
```javascript
onclick="toggleTreeItem(event, '${project.id}', ${hasChildren})"
```
This breaks if `project.id` contains single quotes.

**Process:**

1. **Add data-attributes to HTML generation:**
   - Line 1162: Replace inline onclick with data attributes
   ```html
   <!-- Before -->
   <span class="tree-toggle" onclick="toggleTreeItem(event, '${project.id}', ${hasChildren})">...</span>
   
   <!-- After -->
   <span class="tree-toggle" data-toggle-id="${project.id}" data-has-children="${hasChildren}">...</span>
   ```

2. **Add event delegation in JavaScript:**
   ```javascript
   // Add to window.onload or document.ready
   document.addEventListener('click', (e) => {
     if (e.target.classList.contains('tree-toggle')) {
       const id = e.currentTarget.dataset.toggleId;
       const hasChildren = e.currentTarget.dataset.hasChildren === 'true';
       toggleTreeItem(e, id, hasChildren);
     }
   });
   ```

3. **Update toggleTreeItem to use event.delegateTarget** if needed

**Testing:** 
- Toggle items with special characters in ID (e.g., `P001-test's`)
- Verify collapse/expand still works
- Check browser console for no errors

**Time:** 20 min  
**Risk:** LOW-MEDIUM — small logic change, but high impact for robustness  
**Rollback:** Revert HTML to inline onclick, remove event delegation  

---

## Phase 2: Extract JavaScript Modules (90 min) — MEDIUM RISK, HIGH IMPACT

**Goal:** Break the 1000+ line monolithic JavaScript into 8 focused, testable modules.

### Setup: Create static files directory (5 min)

```bash
mkdir -p src/planner/static
touch src/planner/static/{ui,files,search,editor,preview,tree,analytics,nav}.js
```

### Step 2.1: Add Flask static route (5 min)

**In `create_app()` function, after `app = Flask(__name__)`:**

```python
@app.route("/static/<path:filename>")
def static_files(filename):
    static_dir = Path(__file__).parent / "static"
    file_path = (static_dir / filename).resolve()
    if not str(file_path).startswith(str(static_dir.resolve())):
        return "Not found", 404
    if not file_path.exists():
        return "Not found", 404
    return file_path.read_text(encoding="utf-8"), 200, {"Content-Type": "application/javascript"}
```

**Testing:** Open `/static/ui.js` in browser, verify it loads (will be 404 until we create files)

---

### Step 2.2: Extract UI utilities to `ui.js` (10 min)

**Extract functions:** `showBanner()`, `hideBanner()`, `showError()`

**File:** `src/planner/static/ui.js`

```javascript
class UI {
  static showBanner(ok, text) {
    const el = document.getElementById('validate-banner');
    el.className = ok ? 'ok' : 'error';
    el.textContent = text;
    el.style.display = '';
  }

  static hideBanner() {
    document.getElementById('validate-banner').style.display = 'none';
  }

  static showError(msg) {
    document.getElementById('preview').innerHTML = `<p style="color:#f38ba8">${msg}</p>`;
  }
}

// Export for use in other modules
window.UI = UI;
```

**In HTML template:** Replace inline functions with `<script src="/static/ui.js"></script>`

**Testing:** Trigger error, verify banner appears/disappears correctly

---

### Step 2.3: Extract File Browser to `files.js` (15 min)

**Extract functions:** `loadTree()`, `renderTree()`, `loadFile()`, `showBrowser()`

**File:** `src/planner/static/files.js`

```javascript
class FileBrowser {
  static async loadTree() {
    // Current loadTree() code
  }

  static renderTree(parent, nodes) {
    // Current renderTree() code
  }

  static async loadFile(path) {
    // Current loadFile() code
  }

  static async showBrowser() {
    // Current showBrowser() code
  }
}

window.FileBrowser = FileBrowser;
```

**Testing:** Click Files tab, verify file tree loads and items open

---

### Step 2.4: Extract Search to `search.js` (15 min)

**Extract:** `loadFilesForSearch()`, `collectFiles()`, search input listener

**File:** `src/planner/static/search.js`

```javascript
class FileSearch {
  static async loadFilesForSearch() { ... }
  static collectFiles(nodes, arr) { ... }
  static initSearchInput() {
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', (e) => { ... });
  }
}

window.FileSearch = FileSearch;
```

**Testing:** Type in search box, verify dropdown appears with matching files

---

### Step 2.5: Extract Editor to `editor.js` (15 min)

**Extract:** `enterEdit()`, `cancelEdit()`, `saveFile()`, editor initialization

**File:** `src/planner/static/editor.js`

```javascript
class FileEditor {
  static enterEdit() { ... }
  static cancelEdit() { ... }
  static async saveFile() { ... }
}

window.FileEditor = FileEditor;
```

**Testing:** Click Edit button, make change, save — verify save works

---

### Step 2.6: Extract Preview to `preview.js` (15 min)

**Extract:** `showPreview()`, markdown rendering logic

**File:** `src/planner/static/preview.js`

```javascript
class FilePreview {
  static async showPreview(raw) {
    // Current showPreview() code
  }
}

window.FilePreview = FilePreview;
```

**Testing:** Open any file, verify markdown is rendered correctly

---

### Step 2.7: Extract Tree View to `tree.js` (20 min)

**Extract:** `buildTreeHTML()`, `buildChildrenHTML()`, `toggleTreeItem()`, `showTreeRoot()`, `renderHierarchyView()`, tree state variables

**File:** `src/planner/static/tree.js`

```javascript
class TreeView {
  static treeHierarchy = null;
  static selectedTreeItem = null;

  static buildTreeHTML(projects, indent = 0) { ... }
  static buildChildrenHTML(parent, indent) { ... }
  static toggleTreeItem(event, id, hasChildren) { ... }
  static async showTreeRoot(id, title, type, path) { ... }
  static async renderHierarchyView(node, type, depth = 0) { ... }
  static showTree() {
    // Current showTree() code
  }
}

window.TreeView = TreeView;
```

**Testing:** Click Tree tab, expand/collapse items, verify hierarchy displays

---

### Step 2.8: Extract Analytics & Navigation (15 min)

**Analytics:** `showAnalytics()`, `renderAnalyticsDashboard()`, `loadCharts()` → `analytics.js`

**Navigation:** Tab button handlers, `showBrowser()`, `showTree()`, `showAnalytics()` → `nav.js`

**Files:** `src/planner/static/analytics.js`, `src/planner/static/nav.js`

**Testing:** Click each tab, verify content loads correctly

---

### Step 2.9: Update HTML template (15 min)

**What:** Remove all JavaScript from `_HTML`, add `<script>` tags to load modules.

**Process:**

1. Remove lines ~912-1430 (all JavaScript functions)
2. Add at end of `<head>`:
   ```html
   <script src="/static/ui.js"></script>
   <script src="/static/files.js"></script>
   <script src="/static/search.js"></script>
   <script src="/static/editor.js"></script>
   <script src="/static/preview.js"></script>
   <script src="/static/tree.js"></script>
   <script src="/static/analytics.js"></script>
   <script src="/static/nav.js"></script>
   ```

3. Update `window.onload` to use new module methods:
   ```javascript
   window.onload = async () => {
     if (!editEnabled) {
       document.getElementById('btn-edit').style.display = 'none';
     }
     document.querySelectorAll('#toolbar button')[0].classList.add('active');
     await TreeView.loadTree();
     await FileSearch.loadFilesForSearch();
     await FilePreview.showPreview(/* ... */);
   };
   ```

**Verification Checklist:**
- [ ] Page loads without console errors
- [ ] All tabs work (Files, Tree, Analytics)
- [ ] File browser loads and items open
- [ ] Search works
- [ ] Edit/Save works
- [ ] Tree view loads hierarchy
- [ ] Analytics dashboard loads
- [ ] All toggle animations work
- [ ] No quote escaping errors in browser console

**Testing:** Full end-to-end test:
1. Load page
2. Browse files in Files tab
3. Search for a file
4. Open file, edit, save
5. Switch to Tree tab, expand/collapse items
6. Switch to Analytics tab
7. Check DevTools → Console for no errors

**Time:** 15 min  
**Risk:** MEDIUM — most invasive step, high impact if wrong  
**Rollback:** Revert to previous commit, will have inline JS again  

---

## Phase 3: Improve Patterns (Optional, Lower Priority)

### Step 3.1: Event Delegation Cleanup
Consolidate onclick handlers into central event dispatcher.

### Step 3.2: State Management Class
Create centralized AppState class for UI state (current tab, selected item, etc.)

### Step 3.3: Extract CSS to separate file
Move `_CSS` to `static/style.css`

### Step 3.4: Component Registry
Create mapping of UI components for easier lifecycle management

---

## Quick Reference Checklist

### Phase 1 (Static Resources)
- [ ] 1.1: Extract CSS to `_CSS` constant
- [ ] 1.2: Extract library CDN links
- [ ] 1.3: Fix quote escaping with data-attributes

### Phase 2 (JavaScript Modules)
- [ ] 2.1: Add Flask `/static/` route
- [ ] 2.2: Create `ui.js`
- [ ] 2.3: Create `files.js`
- [ ] 2.4: Create `search.js`
- [ ] 2.5: Create `editor.js`
- [ ] 2.6: Create `preview.js`
- [ ] 2.7: Create `tree.js`
- [ ] 2.8: Create `analytics.js` and `nav.js`
- [ ] 2.9: Update HTML, load all modules, full test

### Phase 3 (Polish)
- [ ] 3.1: Event delegation cleanup
- [ ] 3.2: State management class
- [ ] 3.3: Extract CSS to file
- [ ] 3.4: Component registry

---

## Rollback Strategy

**If anything breaks at any step:**

1. Run `git diff` to see exactly what changed
2. Run `git checkout src/planner/server.py` to revert (or just the one file)
3. Reload browser, verify it works again
4. Analyze what went wrong before re-attempting
5. Commit a fix, not a revert (to keep history)

**Safe points to stop:**
- After Step 1.3 — CSS and libraries are extracted, quote escaping is fixed
- After Step 2.1 — Static route is ready, no modules yet
- After each Step 2.x — Each module can be developed/tested independently
- After Step 2.9 — Full refactor complete, time to celebrate

---

## Expected Outcome

**Before:**
- 1568-line Python string with mixed code
- No IDE support, quote escaping bugs
- Hard to test, hard to modify

**After:**
- Modular, focused 8 JavaScript files (~150-200 lines each)
- CSS extracted and organized
- Event delegation fixes quote escaping
- Testable, maintainable code
- Same UI/UX, zero functionality changes

**Commit message for Phase 1 completion:**
```
Refactor: Extract CSS, libraries, and fix quote escaping in toggle handlers

- Move inline CSS to _CSS constant
- Extract CDN links to _LIBRARIES_HEAD
- Replace unsafe inline onclick with data-attributes and event delegation
- Eliminates quote escaping vulnerabilities in toggle handlers
- No functionality changes, pure refactoring
```

**Commit message for Phase 2 completion:**
```
Refactor: Extract JavaScript into modular components

- Create 8 focused JS modules (ui, files, search, editor, preview, tree, analytics, nav)
- Each module handles one concern with clear class interface
- Add Flask /static/ route for module delivery
- Update HTML to load modules via <script> tags
- No functionality changes, same UI/UX behavior
```

---

## Notes for Next Session

1. **Run tests after Phase 1.3** — This is the highest-risk part of Phase 1
2. **Commit after each major step** — Keep commits atomic for easy rollback
3. **Keep browser DevTools open** — Watch Network tab and Console for issues
4. **Take 15-min breaks** — This is focused work, don't rush
5. **Test comprehensively at 2.9** — This is where everything comes together

Good luck! This refactor will make future changes 10x easier.
