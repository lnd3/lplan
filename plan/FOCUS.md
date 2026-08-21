# lplan Focus

## Active

Currently shipping Tier 2 Operational/Governance/Visibility features:
- `plan serve` web UI (read-only + edit modes)
- 13 new CLI commands (stats, timeline, log, update, report, watch, etc.)
- Enhanced scaffolding (FOCUS.md, REFLECTION.md templates)
- Validator improvements with typo suggestions

## Blocked

None currently. P001 ✅, P002 ✅ complete.

## Next

1. **Polish priorities** (this cycle):
   - Fix changelog formatting (separate lines, not append-same-line)
   - Auto-regenerate INDEX.md on HTTP access (plan serve)
   - Add FOCUS.md + REFLECTION.md to lplan's own plan/ (dogfood)

2. **Tier 3 (Backlog)**:
   - Advanced analytics (impact analysis, DSM, bottleneck detection)
   - Gantt chart generation
   - Capacity vs. work tracking
   - Metrics: depth, fan-in/out

3. **Integrations (Backlog)**:
   - GitHub Actions workflow validation
   - Pre-commit hook scaffolding
   - CLI integration with git branches
