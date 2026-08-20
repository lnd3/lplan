# Aggregation Rules

Defines how the aggregation tool (`aggregate-local.sh`) discovers submodules, links plans, and generates hierarchical views.

## Discovery Algorithm

### Step 1: Find All Plan Directories

```bash
# Starting from repo root, recursively find plan/ directories:
find . -type d -name "plan" | grep -v ".git" | sort

# Expected output:
# ./plan
# ./deps/ltools/plan
# ./deps/ldeps/plan
```

### Step 2: Read Repo Metadata

For each plan directory, read frontmatter from all project files:

```bash
for plan_dir in $(find . -type d -name "plan" -not -path "./.git/*"); do
  repo_name=$(basename $(dirname $plan_dir))  # e.g., "ltools" from "deps/ltools"
  read_projects "$plan_dir/projects/*.md" into $repo_name namespace
done
```

### Step 3: Parse Frontmatter

For each project file, extract:
- `id`: Project ID (P001, L001, D001)
- `title`: Project title
- `status`: Current status
- `priority`: Priority level
- `depends`: List of "repo:ID" references
- `enables`: List of "repo:ID" references
- `external_dependencies`: Dependencies on features not formalized as projects

### Step 4: Build Dependency Graph

Create a graph of all cross-repo references:

```
P001 ← P005        (P005 enables P001)
P001 ← P006        (P006 enables P001)
P005 → ltools:L001 (P005 depends on ltools:L001)
P003 ← P001        (P001 enables P003)
```

Validate that all references are resolvable (file exists).

## Aggregated View Generation

### Hierarchical Sections

Generate INDEX.md with sections:

1. **Local Projects** (sorted by priority, then status)
2. **Linked Submodules** (one section per submodule, sorted by path)
3. **Dependency Graph** (optional visualization)
4. **Critical Path** (optional, if tied to strategic goal)

### Impact Annotation

For each submodule project, annotate with how it impacts the local repo:

```markdown
| [L001](../deps/ltools/plan/projects/L001.md) | Node Registry | DONE | — | P005 depends; available ✓ |
```

Logic:
1. Check if any local project **depends** on submodule:project
2. If yes, check if submodule:project is DONE
3. If DONE: "✓ available"
4. If not DONE: "⏳ blocked; needed for P005"

## Conflict Resolution

### Circular Dependencies
If A → B → A detected, warn but don't fail. Document in report.

### Missing References
If project references "repo:ID" that doesn't exist:
- Warn: "P005 references unknown ltools:L002"
- Suggest: Create ltools/plan/projects/L002.md or remove reference
- Mark as error in validation report

### Duplicate IDs
If two projects have the same ID in the same repo:
- Error: Cannot aggregate
- Fix: Rename one ID
- Validation will catch before aggregation runs

## Temporal Consistency

### Timestamp Ordering

When collecting changes:
1. Read CHANGELOG.md from each repo
2. Extract date from each entry
3. Merge and sort by date
4. Generate aggregated CHANGELOG with entries from all repos

Example:
```
2026-08-20 | tradeflow/P005 | IDEA → PLANNING | HyperLiquid critical path
2026-08-20 | tradeflow/P001 | IN_PROGRESS → BLOCKED | Binance unavailable
2026-08-15 | ltools/L002 | PLANNING → IN_PROGRESS | Serialization work starts
```

## Submodule Metadata

Each submodule is located via:
1. **Path**: Detected via `find` (step 1 above)
2. **Name**: Derived from directory name or `.git/config` submodule entry

For git submodules specifically:
```bash
# Extract submodule info:
git config --file .gitmodules --get-regexp path | while read path_line; do
  submodule_name=$(echo $path_line | cut -d. -f2)
  submodule_path=$(echo $path_line | awk '{print $2}')
  echo "$submodule_name → $submodule_path"
done
```

## Output

Aggregator generates:
1. **INDEX.md** (hierarchical view with local + submodules)
2. **DEPENDENCY_GRAPH.md** (optional; lists all cross-repo links)
3. **CRITICAL_PATH.md** (optional; shows path to strategic goal)

## Modes

### Full Aggregation
```bash
./aggregate-local.sh
# Reads all plans, generates all outputs, commits to git
```

### Validation Only
```bash
./aggregate-local.sh --validate
# Check for errors; don't generate/commit
```

### Dry Run
```bash
./aggregate-local.sh --dry-run
# Print what would be generated; don't commit
```

### Filter
```bash
./aggregate-local.sh --priority HIGH
# Show only HIGH-priority work across repos
```

## Caching & Invalidation

Aggregator can cache results to avoid re-reading all files:

```
.aggregation-cache/
  repos.json         ← Names and paths of all discovered repos
  graph.json         ← Dependency graph
  last-run.txt       ← Timestamp of last aggregation
```

Invalidate cache if:
- Any `plan/**/*.md` file is newer than `last-run.txt`
- `.gitmodules` changes
- `repos.yml` (if used) changes

## Example: Multi-Repo Aggregation

**Input State**:
```
my-app/plan/projects/P001.md (status=PLANNING, depends=["core-lib:L001"])
my-app/plan/projects/P002.md (status=BLOCKED, depends=["P001"])
deps/core-lib/plan/projects/L001.md (status=IN_PROGRESS, enables=["my-app:P001"])
```

**Aggregator Output**:
```
## Local Projects (my-app)

| ID | Title | Status | Priority |
| P001 | Core Feature | PLANNING | HIGH |
| P002 | Secondary Feature | BLOCKED | MEDIUM |

## Linked Dependencies

### core-lib (deps/core-lib/)

| ID | Title | Status | Enables |
| L001 | Infrastructure | IN_PROGRESS | P001 ✓ |

## Dependency Summary

P001 (PLANNING) ← L001 (IN_PROGRESS) ⏳
P002 (BLOCKED) ← P001 (PLANNING) ⏳
```

**Insight**: Once L001 completes, P001 can proceed, which unblocks P002.
