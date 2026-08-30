class OverviewView {
  static data = null;
  static collapsed = new Set(); // section ids collapsed this session

  static TYPE_DIRS = {
    concept: 'concepts',
    thesis: 'theses',
    master_plan: 'master_plans',
    project: 'projects',
    design: 'designs',
    action: 'actions',
  };

  static async show() {
    const buttons = document.querySelectorAll('#toolbar button');
    buttons.forEach(btn => btn.classList.remove('active'));
    buttons[4]?.classList.add('active');

    document.getElementById('file-toolbar').style.display = 'none';
    document.getElementById('preview').style.display = 'none';
    document.getElementById('editor-wrap').style.display = 'none';
    document.getElementById('tree-view').style.display = 'none';
    document.getElementById('sidebar').style.display = 'none';
    document.getElementById('analytics-dashboard').style.display = 'none';
    document.getElementById('status-view').style.display = 'none';

    const container = document.getElementById('overview-view');
    container.style.display = 'block';
    container.innerHTML = '<div style="text-align: center; color: #a6adc8; padding: 40px;">Loading plan health…</div>';

    try {
      const res = await fetch('/api/status-overview');
      const result = await res.json();
      if (!result.ok) throw new Error(result.error || 'Unknown error');
      OverviewView.data = result.data;
      OverviewView.render();
    } catch (e) {
      console.error('Overview load failed:', e);
      container.innerHTML = `<div class="warning-box">Failed to load plan overview: ${e.message}</div>`;
    }
  }

  static goTo(id, title, type, path) {
    const resolvedPath = path || `${OverviewView.TYPE_DIRS[type] || 'projects'}/${id}.md`;
    EntityViewer.show(id, title || id, type, resolvedPath);
  }

  static render() {
    const d = OverviewView.data;
    const container = document.getElementById('overview-view');

    let html = OverviewView.renderTotals(d.totals);
    html += OverviewView.renderNeedsAttention(d.needs_attention, d.stale_days_threshold);
    html += OverviewView.renderRollupSection('master-plans', 'Master Plans', d.master_plan_rollups, 'master_plan');
    html += OverviewView.renderRollupSection('projects', 'Projects', d.project_rollups, 'project');

    container.innerHTML = html;
    OverviewView.attachEventListeners();
  }

  // Wraps a section body in a click-to-collapse header. Collapsed state
  // persists (in memory) across re-renders within the session.
  static renderCollapsible(sectionId, headingHtml, bodyHtml) {
    const isCollapsed = OverviewView.collapsed.has(sectionId);
    return `<div class="overview-section${isCollapsed ? ' collapsed' : ''}" data-section="${sectionId}" style="margin-bottom: 24px;">
      <div class="overview-section-header" data-section-toggle="${sectionId}">
        <span class="overview-section-toggle">${isCollapsed ? '▸' : '▾'}</span>
        ${headingHtml}
      </div>
      <div class="overview-section-body">${bodyHtml}</div>
    </div>`;
  }

  static renderTotals(totals) {
    const order = ['thesis', 'master_plan', 'project', 'design', 'action', 'concept'];
    const labels = { thesis: 'Theses', master_plan: 'Master Plans', project: 'Projects', design: 'Designs', action: 'Actions', concept: 'Concepts' };
    const doneish = new Set(['DONE', 'STABLE', 'HELD']);

    let html = '<div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 24px;">';
    for (const type of order) {
      const counts = totals[type] || {};
      const total = Object.values(counts).reduce((a, b) => a + b, 0);
      const good = Object.entries(counts).filter(([s]) => doneish.has(s)).reduce((a, [, c]) => a + c, 0);
      html += `<div style="background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 12px 16px; min-width: 120px;">
        <div style="font-size: 11px; color: #a6adc8; text-transform: uppercase; letter-spacing: 0.5px;">${labels[type]}</div>
        <div style="font-size: 22px; color: #cdd6f4; font-weight: 600; margin-top: 4px;">${total}</div>
        <div style="font-size: 11px; color: #a6e3a1; margin-top: 2px;">${good}/${total} settled</div>
      </div>`;
    }
    html += '</div>';
    return html;
  }

  static renderNeedsAttention(na, staleDays) {
    const sections = [];

    if (na.stale.length) {
      let rows = na.stale.map(e => `<div style="padding: 6px 0; border-bottom: 1px solid #313244; display: flex; justify-content: space-between; cursor: pointer;" data-id="${e.id}" data-type="${e.type}" data-path="${e.path || ''}" data-title="${OverviewView.escapeAttr(e.title)}">
        <span><span style="color: #f9e2af;">${e.id}</span> ${e.title}</span>
        <span style="color: #fab387; font-size: 12px;">${e.days_since_activity}d idle</span>
      </div>`).join('');
      sections.push(`<div class="needs-attention-section" style="margin-bottom: 12px;">
        <div style="font-size: 13px; color: #fab387; font-weight: 600; margin-bottom: 4px;">⏸ Stale (IN_PROGRESS, no activity ≥ ${staleDays}d)</div>
        ${rows}
      </div>`);
    }

    if (na.blocked.length) {
      let rows = na.blocked.map(e => `<div style="padding: 6px 0; border-bottom: 1px solid #313244; cursor: pointer;" data-id="${e.id}" data-type="${e.type}" data-path="${e.path || ''}" data-title="${OverviewView.escapeAttr(e.title)}">
        <span style="color: #f38ba8;">${e.id}</span> ${e.title}
        ${e.blockers.length ? `<span style="color: #a6adc8; font-size: 12px;"> — blocked by ${e.blockers.join(', ')}</span>` : ''}
      </div>`).join('');
      sections.push(`<div class="needs-attention-section" style="margin-bottom: 12px;">
        <div style="font-size: 13px; color: #f38ba8; font-weight: 600; margin-bottom: 4px;">🚫 Blocked</div>
        ${rows}
      </div>`);
    }

    const refs = na.dangling_references;
    const refIssues = [
      ...refs.orphaned_designs.map(id => ({ id, kind: 'orphaned design (parent project missing)' })),
      ...refs.orphaned_actions.map(id => ({ id, kind: 'orphaned action (parent design missing)' })),
      ...refs.unused_projects.map(id => ({ id, kind: 'unused project (no dependents, no depends)' })),
      ...(refs.dead_companion_links || []).map(d => ({ id: d.from, kind: `dead companion link → ${d.link}` })),
    ];
    if (refIssues.length) {
      let rows = refIssues.map(r => `<div style="padding: 6px 0; border-bottom: 1px solid #313244;">
        <span style="color: #89b4fa;">${r.id}</span> <span style="color: #a6adc8; font-size: 12px;">${r.kind}</span>
      </div>`).join('');
      sections.push(`<div class="needs-attention-section" style="margin-bottom: 12px;">
        <div style="font-size: 13px; color: #89b4fa; font-weight: 600; margin-bottom: 4px;">🔗 Reference issues (from <code>plan check-refs</code>)</div>
        ${rows}
      </div>`);
    }

    const warnings = na.validator_warnings || [];
    if (warnings.length) {
      let rows = warnings.map(w => `<div style="padding: 6px 0; border-bottom: 1px solid #313244; cursor: pointer;" data-id="${w.id}" data-type="${w.type}" data-path="${w.path || ''}" data-title="${OverviewView.escapeAttr(w.id)}">
        <span style="color: #cba6f7;">${w.id}</span> <span style="color: #a6adc8; font-size: 12px;">${OverviewView.escapeAttr(w.message)}</span>
      </div>`).join('');
      sections.push(`<div class="needs-attention-section" style="margin-bottom: 12px;">
        <div style="font-size: 13px; color: #cba6f7; font-weight: 600; margin-bottom: 4px;">⚠ Validator warnings (from <code>plan validate</code>)</div>
        ${rows}
      </div>`);
    }

    const heading = `<span style="font-size: 14px; color: #cdd6f4; font-weight: 600;">Needs Attention</span>`;

    if (!sections.length) {
      return OverviewView.renderCollapsible('needs-attention', heading,
        `<div style="color: #a6e3a1; padding: 8px 0;">✓ Nothing needs attention — no stale, blocked, or reference issues found.</div>`);
    }

    return OverviewView.renderCollapsible('needs-attention', heading, sections.join(''));
  }

  static renderRollupSection(sectionId, heading, rollups, type) {
    if (!rollups.length) return '';
    let rows = rollups.map(r => {
      const barColor = r.status === 'DONE' ? '#a6e3a1' : '#89b4fa';
      const emptyNote = (r.no_children || r.no_projects_yet) ? ' <span style="color:#9399b2; font-size:11px;">(no children yet)</span>' : '';
      // Show whatever fraction actually drove pct_done — showing child counts
      // next to a checkbox-derived percentage would misleadingly imply they're
      // the same measure. See D008 follow-up: checkboxes are the deliberate
      // plan of record; child counts drift as scope gets discovered.
      let fraction, sourceNote;
      if (r.pct_source === 'checkboxes') {
        fraction = `${r.checkbox_done}/${r.checkbox_total} tasks`;
        sourceNote = '';
      } else if (r.pct_source === 'children') {
        fraction = `${r.child_done}/${r.child_count}`;
        sourceNote = ' <span style="color:#9399b2; font-size:10px;" title="No Tasks checkboxes found — falling back to child Design/Action counts, which drift as scope grows.">(by children)</span>';
      } else {
        fraction = '';
        sourceNote = '';
      }
      return `<div style="padding: 8px 0; border-bottom: 1px solid #313244; cursor: pointer;" data-id="${r.id}" data-type="${type}" data-path="${r.path || ''}" data-title="${OverviewView.escapeAttr(r.title)}">
        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;">
          <span><span style="color: #f9e2af;">${r.id}</span> ${r.title}${emptyNote}</span>
          <span style="color: #a6adc8;">${fraction ? fraction + ' · ' : ''}${r.pct_done}%${sourceNote}</span>
        </div>
        <div style="background: #313244; border-radius: 3px; height: 6px; overflow: hidden;">
          <div style="background: ${barColor}; height: 100%; width: ${r.pct_done}%;"></div>
        </div>
      </div>`;
    }).join('');

    const headingHtml = `<span style="font-size: 14px; color: #cdd6f4; font-weight: 600;">${heading}</span> <span style="color: #9399b2; font-size: 12px;">(${rollups.length})</span>`;
    return OverviewView.renderCollapsible(sectionId, headingHtml, rows);
  }

  static attachEventListeners() {
    document.querySelectorAll('#overview-view [data-id][data-type]').forEach(el => {
      el.addEventListener('click', () => OverviewView.goTo(el.dataset.id, el.dataset.title, el.dataset.type, el.dataset.path));
    });

    document.querySelectorAll('#overview-view [data-section-toggle]').forEach(el => {
      el.addEventListener('click', () => {
        const sectionId = el.dataset.sectionToggle;
        const section = document.querySelector(`.overview-section[data-section="${sectionId}"]`);
        if (!section) return;
        const nowCollapsed = section.classList.toggle('collapsed');
        const glyph = section.querySelector('.overview-section-toggle');
        if (glyph) glyph.textContent = nowCollapsed ? '▸' : '▾';
        if (nowCollapsed) OverviewView.collapsed.add(sectionId);
        else OverviewView.collapsed.delete(sectionId);
      });
    });
  }

  static escapeAttr(str) {
    return String(str ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
  }
}

window.OverviewView = OverviewView;
