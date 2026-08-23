class StatusView {
  static data = null;
  static filteredData = null;
  static filters = {
    search: '',
    statuses: [],
    priorities: [],
    types: []
  };
  static sortConfig = { column: 'id', direction: 'asc' };
  static visibleColumns = ['id', 'title', 'type', 'status', 'priority', 'created', 'depends_on_count'];
  static pageSize = 20;
  static currentPage = 1;

  static async show() {
    const buttons = document.querySelectorAll('#toolbar button');
    buttons.forEach(btn => btn.classList.remove('active'));
    buttons[3]?.classList.add('active');

    document.getElementById('file-toolbar').style.display = 'none';
    document.getElementById('preview').style.display = 'none';
    document.getElementById('tree-view').style.display = 'none';
    document.getElementById('sidebar').style.display = 'none';
    document.getElementById('analytics-dashboard').style.display = 'none';
    document.getElementById('editor-wrap').style.display = 'none';

    const statusContainer = document.getElementById('status-view');
    statusContainer.style.display = 'block';

    await StatusView.loadStatus();
    StatusView.render();
  }

  static async loadStatus() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) throw new Error('Failed to load status data');
      const result = await res.json();
      if (!result.ok) throw new Error(result.error || 'Unknown error');
      StatusView.data = result.data.entities;
      StatusView.applyFilters();
    } catch (e) {
      console.error('Status load failed:', e);
      const container = document.getElementById('status-view');
      container.innerHTML = `<div style="color: #f38ba8; padding: 20px;">Error loading status: ${e.message}</div>`;
    }
  }

  static render() {
    const container = document.getElementById('status-view');

    if (!container.querySelector('.status-filter-bar')) {
      let html = '<div style="padding: 20px;">';
      html += StatusView.renderFilterBar();
      html += '<div class="status-results-container"></div>';
      html += '</div>';
      container.innerHTML = html;
      StatusView.attachEventListeners();
    }

    const resultsContainer = container.querySelector('.status-results-container');
    let html = StatusView.renderTable() + StatusView.renderPagination();
    resultsContainer.innerHTML = html;
    StatusView.attachTableEventListeners();
  }

  static renderFilterBar() {
    const resultCount = StatusView.filteredData?.length || 0;
    const activeFilters = (StatusView.filters.search ? 1 : 0) +
                         StatusView.filters.statuses.length +
                         StatusView.filters.priorities.length +
                         StatusView.filters.types.length;

    let html = `<div class="status-filter-bar" style="margin-bottom: 16px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">`;

    html += `<input type="text" id="status-search" placeholder="🔍 Search ID, title, description..."
      style="padding: 6px 12px; background: #0f111b; border: 1px solid #313244; border-radius: 4px;
             color: #cdd6f4; font-size: 13px; flex: 1; min-width: 200px;" value="${StatusView.filters.search}">`;

    html += `<select id="status-filter" multiple style="padding: 6px 8px; background: #313244;
             border: 1px solid #45475a; border-radius: 4px; color: #cdd6f4; font-size: 12px; min-height: 24px;">
      <option value="IDEA" ${StatusView.filters.statuses.includes('IDEA') ? 'selected' : ''}>IDEA</option>
      <option value="PLANNING" ${StatusView.filters.statuses.includes('PLANNING') ? 'selected' : ''}>PLANNING</option>
      <option value="IN_PROGRESS" ${StatusView.filters.statuses.includes('IN_PROGRESS') ? 'selected' : ''}>IN_PROGRESS</option>
      <option value="BLOCKED" ${StatusView.filters.statuses.includes('BLOCKED') ? 'selected' : ''}>BLOCKED</option>
      <option value="DONE" ${StatusView.filters.statuses.includes('DONE') ? 'selected' : ''}>DONE</option>
      <option value="DEFERRED" ${StatusView.filters.statuses.includes('DEFERRED') ? 'selected' : ''}>DEFERRED</option>
      <option value="CANCELLED" ${StatusView.filters.statuses.includes('CANCELLED') ? 'selected' : ''}>CANCELLED</option>
    </select>`;

    html += `<select id="priority-filter" multiple style="padding: 6px 8px; background: #313244;
             border: 1px solid #45475a; border-radius: 4px; color: #cdd6f4; font-size: 12px; min-height: 24px;">
      <option value="HIGH" ${StatusView.filters.priorities.includes('HIGH') ? 'selected' : ''}>HIGH</option>
      <option value="MEDIUM" ${StatusView.filters.priorities.includes('MEDIUM') ? 'selected' : ''}>MEDIUM</option>
      <option value="LOW" ${StatusView.filters.priorities.includes('LOW') ? 'selected' : ''}>LOW</option>
    </select>`;

    html += `<select id="type-filter" multiple style="padding: 6px 8px; background: #313244;
             border: 1px solid #45475a; border-radius: 4px; color: #cdd6f4; font-size: 12px; min-height: 24px;">
      <option value="project" ${StatusView.filters.types.includes('project') ? 'selected' : ''}>Project</option>
      <option value="design" ${StatusView.filters.types.includes('design') ? 'selected' : ''}>Design</option>
      <option value="action" ${StatusView.filters.types.includes('action') ? 'selected' : ''}>Action</option>
    </select>`;

    html += `<button id="clear-filters" style="padding: 6px 12px; background: #45475a;
             border: 1px solid #45475a; border-radius: 4px; color: #cdd6f4; cursor: pointer; font-size: 12px;">
      Clear</button>`;

    if (activeFilters > 0) {
      html += `<span style="font-size: 12px; color: #89b4fa; background: #313244; padding: 4px 8px;
               border-radius: 3px;">${activeFilters} filter${activeFilters !== 1 ? 's' : ''}</span>`;
    }

    html += `<span style="font-size: 12px; color: #a6adc8; margin-left: auto;">
      Showing ${Math.min((StatusView.currentPage - 1) * StatusView.pageSize + 1, resultCount)}-${Math.min(StatusView.currentPage * StatusView.pageSize, resultCount)} of ${resultCount}
    </span>`;

    html += '</div>';
    return html;
  }

  static renderTable() {
    if (!StatusView.filteredData || StatusView.filteredData.length === 0) {
      return '<div style="color: #a6adc8; padding: 40px; text-align: center;">No entities match your filters</div>';
    }

    const start = (StatusView.currentPage - 1) * StatusView.pageSize;
    const end = start + StatusView.pageSize;
    const pageData = StatusView.filteredData.slice(start, end);

    let html = '<table style="width: 100%; border-collapse: collapse; font-size: 13px;">';

    html += '<thead><tr style="background: #313244; border-bottom: 2px solid #45475a;">';
    const columns = ['id', 'title', 'type', 'status', 'priority', 'created', 'updated', 'depends_on_count'];
    for (const col of columns) {
      const label = col.replace(/_/g, ' ').toUpperCase();
      const isSorted = StatusView.sortConfig.column === col;
      const arrow = isSorted ? (StatusView.sortConfig.direction === 'asc' ? ' ↑' : ' ↓') : '';
      html += `<th style="padding: 8px 12px; text-align: left; color: #89b4fa; cursor: pointer; user-select: none;"
               data-column="${col}"><strong>${label}${arrow}</strong></th>`;
    }
    html += '</tr></thead>';

    html += '<tbody>';
    for (const entity of pageData) {
      const statusColor = StatusView.getStatusColor(entity.status);
      const typeIcon = StatusView.getTypeIcon(entity.type);
      html += `<tr style="border-bottom: 1px solid #313244; cursor: pointer;" data-id="${entity.id}" data-type="${entity.type}">
        <td style="padding: 8px 12px; color: #89b4fa;">${entity.id}</td>
        <td style="padding: 8px 12px; color: #cdd6f4;">${entity.title}</td>
        <td style="padding: 8px 12px; color: #a6adc8;">${typeIcon}</td>
        <td style="padding: 8px 12px;"><span style="background: ${statusColor}; padding: 2px 8px; border-radius: 3px; font-size: 11px; color: #1e1e2e; font-weight: 600;">${entity.status}</span></td>
        <td style="padding: 8px 12px; color: #a6adc8;">${entity.priority}</td>
        <td style="padding: 8px 12px; color: #9399b2; font-size: 12px;">${StatusView.formatDate(entity.created)}</td>
        <td style="padding: 8px 12px; color: #9399b2; font-size: 12px;">${StatusView.formatDate(entity.updated)}</td>
        <td style="padding: 8px 12px; text-align: center; color: #a6adc8;">${entity.depends_on_count || 0}</td>
      </tr>`;
    }
    html += '</tbody></table>';

    return html;
  }

  static renderPagination() {
    const totalPages = Math.ceil((StatusView.filteredData?.length || 0) / StatusView.pageSize);
    if (totalPages <= 1) return '';

    let html = '<div style="margin-top: 16px; display: flex; gap: 8px; align-items: center; justify-content: center;">';

    if (StatusView.currentPage > 1) {
      html += `<button class="pagination-btn" data-page="${StatusView.currentPage - 1}" style="padding: 4px 8px; background: #313244; border: 1px solid #45475a; color: #cdd6f4; cursor: pointer; border-radius: 3px;">← Prev</button>`;
    }

    for (let i = 1; i <= Math.min(totalPages, 5); i++) {
      const isActive = i === StatusView.currentPage;
      html += `<button class="pagination-btn" data-page="${i}" style="padding: 4px 8px; background: ${isActive ? '#89b4fa' : '#313244'}; border: 1px solid #45475a; color: ${isActive ? '#1e1e2e' : '#cdd6f4'}; cursor: pointer; border-radius: 3px; font-weight: ${isActive ? 'bold' : 'normal'};">${i}</button>`;
    }

    if (totalPages > 5) {
      html += '<span style="color: #a6adc8;">...</span>';
      html += `<button class="pagination-btn" data-page="${totalPages}" style="padding: 4px 8px; background: #313244; border: 1px solid #45475a; color: #cdd6f4; cursor: pointer; border-radius: 3px;">${totalPages}</button>`;
    }

    if (StatusView.currentPage < totalPages) {
      html += `<button class="pagination-btn" data-page="${StatusView.currentPage + 1}" style="padding: 4px 8px; background: #313244; border: 1px solid #45475a; color: #cdd6f4; cursor: pointer; border-radius: 3px;">Next →</button>`;
    }

    html += '</div>';
    return html;
  }

  static attachEventListeners() {
    const searchInput = document.getElementById('status-search');
    if (searchInput && !searchInput._attached) {
      searchInput._attached = true;
      searchInput.addEventListener('input', (e) => {
        StatusView.filters.search = e.target.value;
        StatusView.currentPage = 1;
        StatusView.applyFilters();
        StatusView.render();
      });
    }

    const statusFilter = document.getElementById('status-filter');
    if (statusFilter && !statusFilter._attached) {
      statusFilter._attached = true;
      statusFilter.addEventListener('change', (e) => {
        StatusView.filters.statuses = Array.from(e.target.selectedOptions).map(o => o.value).filter(v => v);
        StatusView.currentPage = 1;
        StatusView.applyFilters();
        StatusView.render();
      });
    }

    const priorityFilter = document.getElementById('priority-filter');
    if (priorityFilter && !priorityFilter._attached) {
      priorityFilter._attached = true;
      priorityFilter.addEventListener('change', (e) => {
        StatusView.filters.priorities = Array.from(e.target.selectedOptions).map(o => o.value).filter(v => v);
        StatusView.currentPage = 1;
        StatusView.applyFilters();
        StatusView.render();
      });
    }

    const typeFilter = document.getElementById('type-filter');
    if (typeFilter && !typeFilter._attached) {
      typeFilter._attached = true;
      typeFilter.addEventListener('change', (e) => {
        StatusView.filters.types = Array.from(e.target.selectedOptions).map(o => o.value).filter(v => v);
        StatusView.currentPage = 1;
        StatusView.applyFilters();
        StatusView.render();
      });
    }

    const clearBtn = document.getElementById('clear-filters');
    if (clearBtn && !clearBtn._attached) {
      clearBtn._attached = true;
      clearBtn.addEventListener('click', () => {
        StatusView.filters = { search: '', statuses: [], priorities: [], types: [] };
        StatusView.currentPage = 1;
        document.getElementById('status-search').value = '';
        document.getElementById('status-filter').value = '';
        document.getElementById('priority-filter').value = '';
        document.getElementById('type-filter').value = '';
        StatusView.applyFilters();
        StatusView.render();
      });
    }

    document.querySelectorAll('th[data-column]').forEach(th => {
      if (!th._attached) {
        th._attached = true;
        th.addEventListener('click', () => {
          const column = th.dataset.column;
          if (StatusView.sortConfig.column === column) {
            StatusView.sortConfig.direction = StatusView.sortConfig.direction === 'asc' ? 'desc' : 'asc';
          } else {
            StatusView.sortConfig.column = column;
            StatusView.sortConfig.direction = 'asc';
          }
          StatusView.applyFilters();
          StatusView.render();
        });
      }
    });
  }

  static attachTableEventListeners() {
    document.querySelectorAll('.pagination-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        StatusView.currentPage = parseInt(btn.dataset.page);
        StatusView.render();
      });
    });

    document.querySelectorAll('tr[data-id]').forEach(row => {
      row.addEventListener('click', () => {
        const id = row.dataset.id;
        const type = row.dataset.type;
        if (type === 'project') {
          const proj = StatusView.data.find(e => e.id === id && e.type === 'project');
          if (proj) TreeView.showTreeRoot(id, proj.title, 'project', proj.path || `projects/${id}.md`);
        } else {
          const entity = StatusView.data.find(e => e.id === id);
          if (entity?.path) FileBrowser.loadFile(entity.path);
        }
      });
      row.style.transition = 'background 0.15s';
      row.addEventListener('mouseover', () => row.style.background = '#313244');
      row.addEventListener('mouseout', () => row.style.background = '');
    });
  }

  static applyFilters() {
    let filtered = [...(StatusView.data || [])];

    if (StatusView.filters.search) {
      const q = StatusView.filters.search.toLowerCase();
      filtered = filtered.filter(e =>
        e.id.toLowerCase().includes(q) ||
        e.title.toLowerCase().includes(q) ||
        (e.description?.toLowerCase().includes(q) || false)
      );
    }

    if (StatusView.filters.statuses.length > 0) {
      filtered = filtered.filter(e => StatusView.filters.statuses.includes(e.status));
    }

    if (StatusView.filters.priorities.length > 0) {
      filtered = filtered.filter(e => StatusView.filters.priorities.includes(e.priority));
    }

    if (StatusView.filters.types.length > 0) {
      filtered = filtered.filter(e => StatusView.filters.types.includes(e.type));
    }

    StatusView.sortData(filtered);
    StatusView.filteredData = filtered;
  }

  static sortData(data) {
    const col = StatusView.sortConfig.column;
    const dir = StatusView.sortConfig.direction;

    data.sort((a, b) => {
      let aVal = a[col];
      let bVal = b[col];

      if (aVal == null) aVal = '';
      if (bVal == null) bVal = '';

      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (aVal < bVal) return dir === 'asc' ? -1 : 1;
      if (aVal > bVal) return dir === 'asc' ? 1 : -1;
      return 0;
    });
  }

  static getStatusColor(status) {
    const colors = {
      'DONE': '#a6e3a1',
      'IN_PROGRESS': '#89b4fa',
      'PLANNING': '#cba6f7',
      'IDEA': '#f5c2e7',
      'BLOCKED': '#f38ba8',
      'DEFERRED': '#9399b2',
      'CANCELLED': '#6c7086'
    };
    return colors[status] || '#a6adc8';
  }

  static getTypeIcon(type) {
    const icons = { project: '📋', design: '🎨', action: '✓' };
    return icons[type] || '•';
  }

  static formatDate(dateStr) {
    if (!dateStr) return '—';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  }
}

window.StatusView = StatusView;
