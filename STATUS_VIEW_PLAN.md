# Status View Implementation Plan

## Overview

Add a new **Status** tab to the planner UI that displays a comprehensive table view of all projects, designs, and actions with filtering and sorting capabilities.

**Goal:** Provide a quick overview dashboard where users can see, filter, and sort all plan entities at once.

---

## Architecture

### Backend API Endpoint

**Endpoint:** `GET /api/status`

**Response:**
```json
{
  "ok": true,
  "data": {
    "projects": [
      {
        "id": "P001",
        "title": "Tier 1 - Python Execution Engine",
        "type": "project",
        "status": "DONE",
        "priority": "HIGH",
        "created": "2024-01-15",
        "updated": "2024-08-20",
        "description": "Build the core...",
        "depends_on": ["P002"],
        "blocks": [],
        "task_count": 5,
        "task_done": 5
      },
      ...
    ],
    "designs": [...],
    "actions": [...]
  }
}
```

### Frontend Components

**New Module:** `src/planner/static/status.js`

**Class:** `StatusView` with methods:
- `init()` - Initialize status tab and event listeners
- `loadStatus()` - Fetch status data from API
- `renderTable(data)` - Render table with data
- `applyFilters(filterConfig)` - Apply column filters
- `sortTable(column, direction)` - Sort by column
- `toggleColumnVisibility(column)` - Show/hide columns

**Features:**
- Multi-column search/filter (live as user types)
- Click-to-sort on column headers
- Column visibility toggle
- Status badge styling (color-coded)
- Priority badge styling
- Entity type indicators
- Progress indicators (for designs/actions with task counts)

---

## Data Model

### Table Columns

**Core (Always Visible):**
- `ID` - Entity ID with type indicator
- `Title` - Entity title (clickable to view full)
- `Type` - Project/Design/Action icon
- `Status` - Status badge (IDEA, PLANNING, IN_PROGRESS, BLOCKED, DONE, etc.)
- `Priority` - Priority level (HIGH, MEDIUM, LOW)

**Optional (Toggleable):**
- `Created` - Creation date
- `Updated` - Last update date
- `Description` - First 100 chars with ellipsis
- `Dependencies` - Count of "depends_on" refs
- `Blocks` - Count of "blocks" refs
- `Progress` - Task completion % (for designs/actions)
- `Parent` - Parent project ID (for designs/actions)

### Filter Configuration

**Filter Types:**
1. **Text Search** - Search in ID, Title, Description (fuzzy)
2. **Status Filter** - Multi-select checkboxes
3. **Priority Filter** - Multi-select checkboxes
4. **Type Filter** - Project/Design/Action toggles
5. **Date Range** - Min/Max date sliders (optional)

**Filter UI:**
- Compact filter bar above table
- "Clear all filters" button
- Filter count badge
- "Save filter" option (localStorage)

---

## UI Layout

```
┌─────────────────────────────────────────────────────────┐
│ 📊 Status                                               │
├─────────────────────────────────────────────────────────┤
│ 🔍 [Search box]  [Status ▼]  [Priority ▼]  [Type ▼]   │
│ [⚙️ Columns]  [Clear Filters]  [3 filters active]      │
├─────────────────────────────────────────────────────────┤
│ ID    │ Title              │ Type │ Status     │ Pri... │
├───────┼────────────────────┼──────┼────────────┼────────┤
│ P001  │ Tier 1 Engine      │ 📋   │ ✓ DONE     │ HIGH   │
│ P002  │ Tier 2 Analysis    │ 📋   │ ✓ DONE     │ MED    │
│ D001  │ Priority Engine    │ 🎨   │ ✓ DONE     │ HIGH   │
│ A001  │ Write tests        │ ✓    │ ✓ DONE     │ MED    │
├─────────────────────────────────────────────────────────┤
│ Showing 4 of 12 results                     [1 2 3 ...] │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Backend API (15 min)

**File:** `src/planner/server.py`

Create `/api/status` endpoint that:
1. Parses all projects, designs, actions
2. Collects metadata (created, updated, deps, blocks)
3. Returns flattened JSON with type indicator
4. Caches result (regenerate when data changes)

### Phase 2: Frontend Module (45 min)

**File:** `src/planner/static/status.js`

Implement `StatusView` class:
- Table rendering with headers
- Column-specific CSS classes
- Sort indicators (arrows)
- Filter state management
- localStorage for column preferences

### Phase 3: Filter & Search (30 min)

Add to `status.js`:
- Text input listener with debounce
- Multi-select checkboxes for Status/Priority
- Fuzzy search in title/description
- Real-time table filtering
- Results counter

### Phase 4: UI Polish (15 min)

- Color-coded status badges
- Icon indicators (📋 📎 ✓)
- Hover effects on rows
- Click rows to view full entity
- Responsive layout
- Dark theme styling (match existing)

### Phase 5: Integration (10 min)

- Add "Status" tab to toolbar
- Add route in dispatcher
- Add module to HTML template
- Test all filtering combinations

---

## Technical Details

### CSS Classes

```css
.status-table { /* Main table */ }
.status-header { /* Column headers */ }
.status-row { /* Table rows */ }
.status-row.type-project { /* Project styling */ }
.status-row.type-design { /* Design styling */ }
.status-row.type-action { /* Action styling */ }
.status-badge { /* Status badge */ }
.status-badge.done { background: #a6e3a1; }
.status-badge.blocked { background: #f38ba8; }
.status-badge.in-progress { background: #89b4fa; }
.filter-bar { /* Filter controls */ }
.column-toggle { /* Show/hide columns */ }
```

### JavaScript Patterns

```javascript
class StatusView {
  static data = null;
  static filters = {};
  static sortConfig = { column: 'id', direction: 'asc' };
  static visibleColumns = ['id', 'title', 'type', 'status', 'priority'];

  static async init() { ... }
  static async loadStatus() { ... }
  static renderTable(data) { ... }
  static filterData() { ... }
  static sortData() { ... }
}
```

### API Response Format

```python
{
  "ok": True,
  "data": {
    "timestamp": "2024-08-24T12:30:00Z",
    "entities": [
      {
        "id": "P001",
        "title": "...",
        "type": "project",
        "status": "DONE",
        "priority": "HIGH",
        "created": "2024-01-15",
        "updated": "2024-08-20",
        "description": "...",
        "depends_on_count": 0,
        "blocks_count": 2,
        "task_stats": {
          "total": 5,
          "done": 5,
          "percentage": 100
        }
      },
      ...
    ]
  }
}
```

---

## Features

### Sorting

- Click column header to sort ascending
- Click again to sort descending
- Visual indicator (↑↓) on sorted column
- Numeric/date/alphabetic sorting as appropriate

### Filtering

1. **Search Box** - Filters by ID, title, description (case-insensitive, fuzzy)
2. **Status Dropdown** - Select multiple statuses
3. **Priority Dropdown** - Select multiple priorities
4. **Type Toggles** - Show/hide Project/Design/Action
5. **Date Range** - Optional min/max created/updated dates

### Column Visibility

- Gear icon opens column toggle menu
- Checkboxes for each column
- Remembers preferences in localStorage
- Minimum 3 columns always visible (id, title, status)

### Row Interactions

- Click row → Opens full entity view (calls `FileBrowser.loadFile()` or `TreeView.showTreeRoot()`)
- Hover → Subtle background highlight
- Right-click → Context menu (copy ID, open in tree, etc.) [optional]

### Pagination

- Show X results per page (default 20, options: 10, 20, 50, 100)
- Previous/Next buttons
- Jump to page input
- Results counter (e.g., "Showing 1-20 of 47")

---

## Testing Plan

**Manual Tests:**
1. ✓ All entities load correctly
2. ✓ Search filters work (partial matches)
3. ✓ Status/Priority filters work independently
4. ✓ Combine multiple filters
5. ✓ Sort by each column
6. ✓ Column visibility toggle persists
7. ✓ Clicking row opens entity
8. ✓ Responsive on mobile/narrow screens
9. ✓ Dark theme contrast is acceptable
10. ✓ Performance with 100+ entities

**Edge Cases:**
- No results (show "No entities match filters")
- Empty plan (show "No entities in plan")
- Large datasets (pagination/virtualization)
- Special characters in titles (proper escaping)

---

## Optional Enhancements (Future)

- Export to CSV
- Bulk actions (status update, bulk assign)
- Grouping by project/status
- Custom columns (user-defined formulas)
- Charts/stats based on filtered data
- Starred/bookmarked entities
- Time-series view (status history over time)
- Comparison mode (view A vs B)

---

## Files to Modify/Create

1. **src/planner/server.py** - Add `/api/status` endpoint
2. **src/planner/static/status.js** - New module (StatusView class)
3. **src/planner/static/dispatcher.js** - Add 'show-status' action
4. **plan/INDEX.md** - Add Status tab info (optional)

---

## Effort Estimate

- **Backend API:** 15 min
- **Frontend Module:** 45 min
- **Filtering/Search:** 30 min
- **UI Polish:** 15 min
- **Integration:** 10 min
- **Testing:** 20 min

**Total: ~135 minutes (~2.25 hours)**

---

## Success Criteria

- ✅ Status view loads all entities in table format
- ✅ Filtering works on at least 3 columns (status, priority, search)
- ✅ Sorting works on all columns
- ✅ Performance acceptable (< 500ms load, < 100ms filter)
- ✅ Clicking row navigates to full entity view
- ✅ Dark theme matches existing UI
- ✅ No test regressions (100% pass rate maintained)
- ✅ Code follows existing module patterns
- ✅ Atomic commits (one per phase)

