# Priority Framework

## Overview

Priority is computed from drivers. This framework defines drivers and scoring rules.

## Driver Definitions

### Core Drivers

| Driver | Weight | Definition |
|--------|--------|-----------|
| `critical_live_path_only` | +2.5 | Required infrastructure for live trading; currently unavailable; one of multiple alternatives must be completed |
| `live_critical` | +2.0 | Blocks live trading deployment of core strategy |
| `improves_active` | +1.5 | Improves quality/completeness of IN_PROGRESS projects |
| `enables_multiple` | +1.5 | Infrastructure that unblocks multiple downstream projects |
| `strategic_edge` | +1.0 | New trading alpha or signal source |
| `improves_accuracy` | +1.0 | Reduces backtest↔live discrepancy or fidelity gap |
| `technical_debt` | +0.5 | Robustness, correctness, or QoL improvements |
| `blocked_on_infrastructure` | -2.5 | Cannot proceed; blocked by unavailable required infrastructure |
| `deferred_wait_*` | -2.0 | Blocked by dependency on another project; reduces base priority |

### Custom Drivers

Repos can define additional drivers specific to their domain. Follow naming: `domain_specific_name` (lowercase_with_underscores).

Example:
```yaml
priority_drivers:
  - strategic_edge          # +1.0 (framework)
  - regulatory_compliance   # +2.0 (custom, defined locally)
```

Document custom drivers in `plan/PRIORITY_DRIVERS.md` (inherit from framework, add local).

## Score Mapping

| Score | Priority | Status | Interpretation |
|-------|----------|--------|-----------------|
| ≥ 2.0 | HIGH | IN_PROGRESS or PLANNING | On critical path; required or blocks strategy deployment |
| 1.0–1.9 | MEDIUM | IN_PROGRESS or PLANNING | Enables or improves active work; infrastructure or alpha opportunity |
| < 1.0 | LOW | DEFERRED | QoL, tech debt, or deferred pending dependency completion |
| < 0 | BLOCKED | BLOCKED | Waiting on critical infrastructure or external blocker; cannot proceed |

## Computation

### Algorithm

1. **Identify drivers** from `priority_drivers: [...]` in project frontmatter
2. **Look up weights** from Driver Definitions table above
3. **Sum weights**:
   ```
   score = sum(weight for each driver)
   ```
4. **Map to priority**:
   ```
   if score ≥ 2.0: priority = HIGH
   elif score < 0: priority = BLOCKED
   elif score < 1.0: priority = LOW
   else: priority = MEDIUM
   ```
5. **Validate**: Does computed priority match declared priority? Update if not.

### Example

**Project P005: HyperLiquid API**
```yaml
priority_drivers:
  - critical_live_path_only    # +2.5
# Computation:
#   score = 2.5
#   2.5 ≥ 2.0 → priority = HIGH ✓
priority: HIGH
```

**Project P001: Price Levels Strategy (blocked)**
```yaml
priority_drivers:
  - strategic_edge              # +1.0
  - blocked_on_infrastructure  # -2.5
# Computation:
#   score = 1.0 + (-2.5) = -1.5
#   -1.5 < 0 → priority = BLOCKED ✓
#   But: declared priority = HIGH (strategy value, not executable)
priority: HIGH
status: BLOCKED
```

Note: Priority indicates *strategic importance*, not *executable readiness*. Status indicates *readiness*.

## Updating Drivers & Priority

When external factors change (e.g., Binance unavailable):

1. **Identify affected projects**: Which ones depend on this factor?
2. **Update drivers**: Add/remove/modify drivers for each project
3. **Recalculate scores**: Apply algorithm
4. **Update priority**: If computed ≠ declared, update declared
5. **Update status** (if needed): Blocked projects get status=BLOCKED
6. **Append to CHANGELOG.md**:
   ```
   YYYY-MM-DD | P001 | IN_PROGRESS → BLOCKED | Binance unavailable; P005/P006 now critical path
   ```

## Multi-Repo Scoring

When aggregating across repos, scorers can be:
- **Local**: Computed per-repo (P001 is HIGH within TradeFlow, independent of ltools)
- **Aggregate**: Considers cross-repo dependencies (P005 is HIGH globally because it blocks P001 globally)

By default, each repo scores independently. Aggregation tools can optionally re-weight based on global impact.

## Framework Extension

To customize priority computation for a repo:

1. Create `plan/PRIORITY_DRIVERS.md` (override/extend this file)
2. Add custom drivers with definitions
3. Update score mapping if needed
4. Document rationale
5. tools/validate.sh checks against this file

Example:
```markdown
# TradeFlow Priority Framework

Inherits from planner-framework schema.

## Custom Drivers

| Driver | Weight | Definition |
| --- | --- | --- |
| `regulatory_compliance` | +2.0 | Blocks trading due to compliance requirement |
| `backtest_validation` | +1.0 | Improves confidence before live |
```

## Rationale & History

- **2026-08-20**: Added `critical_live_path_only` and `blocked_on_infrastructure` drivers in response to Binance unavailability
- **2026-05-30**: Initial framework defined with core drivers
