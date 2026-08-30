# D005 Learnings

Scoped implementation notes for D005 (Template File Family Scaling) — too detailed for D005's own Log, kept here per the convention D005 itself defines.

- **Detection is filename-only, not content-based**: a companion is any `.md` file whose stem contains an underscore. Verified no existing entity or root file uses an underscore in its name (only the `master_plans` directory name does, not a filename) — safe, unambiguous rule.
- **Real bug found by implementing this**: `plan validate` previously treated any non-frontmatter `.md` file dropped into an entity subdirectory as a hard parse error (shown under "✗ N files had parse errors"). A companion like this file would have tripped that before the parser was taught to skip companions first. Fixed in `parser.py`.
- **check-refs companion-link scanning needed a code-fence guard**: D005's own design doc includes an illustrative markdown link to a companion file inside a fenced example block. The naive link scanner flagged it as a dead link (wrong directory, since it was only ever meant as illustration). Fixed by stripping fenced code blocks before scanning.
- **INDEX.md's `id_to_filename` builder needed a companion-skip too**: it previously derived an entity ID via `filename.split('-')[0]`, which is harmless-but-wrong for companions (no hyphen, so ID becomes the whole filename) — now companions are diverted into `companions_by_id` instead.
