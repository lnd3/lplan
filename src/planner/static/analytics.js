class Analytics {
  static async showAnalytics() {
    const buttons = document.querySelectorAll('#toolbar button');
    buttons.forEach(btn => btn.classList.remove('active'));
    buttons[2].classList.add('active');

    document.getElementById('file-toolbar').style.display = 'none';
    document.getElementById('preview').style.display = 'none';
    document.getElementById('tree-view').style.display = 'none';
    document.getElementById('sidebar').style.display = 'none';

    const dashboard = document.getElementById('analytics-dashboard');
    dashboard.style.display = '';
    dashboard.innerHTML = '<div style="text-align: center; color: #a6adc8;">Loading analytics...</div>';

    try {
      const res = await fetch('/api/analytics');
      if (!res.ok) {
        const text = await res.text();
        console.error('Analytics API error:', res.status, text);
        dashboard.innerHTML = `<div class="warning-box">API Error: ${res.status}</div><pre style="color: #f38ba8; font-size: 0.8em;">${text}</pre>`;
        return;
      }

      const data = await res.json();
      console.log('Analytics data:', data);

      if (!data.ok) {
        const errMsg = data.error || 'Unknown error';
        console.error('Analytics error:', errMsg);
        dashboard.innerHTML = `<div class="warning-box">Error: ${errMsg}</div>`;
        return;
      }

      Analytics.renderAnalyticsDashboard(data.data);
    } catch (e) {
      console.error('Analytics fetch failed:', e);
      dashboard.innerHTML = `<div class="warning-box">Failed to load analytics: ${e.message}</div><pre style="color: #f38ba8; font-size: 0.8em;">${e.stack}</pre>`;
    }
  }

  static renderAnalyticsDashboard(analytics) {
    try {
      const dashboard = document.getElementById('analytics-dashboard');
      if (!dashboard) throw new Error('Dashboard element not found');
      if (!analytics) throw new Error('Analytics data is null');

      const metrics = analytics.metrics || {};
      const bottlenecks = analytics.bottlenecks || {};
      const capacity = analytics.capacity || {};
      const impactful = analytics.impactful_projects || [];

      console.log('Rendering with:', { metrics, bottlenecks, capacity, impactful });
      console.log('Analytics keys:', Object.keys(analytics));
      if (typeof metrics !== 'object') throw new Error('Metrics is not an object: ' + typeof metrics);

      let html = '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">';
      html += '<div class="analytics-header" style="margin: 0;">📊 Analytics Dashboard</div>';
      html += '<button id="report-btn" onclick="Analytics.generateReport()" style="padding: 8px 16px; background: #313244; color: #89b4fa; border: 1px solid #45475a; border-radius: 4px; cursor: pointer; font-weight: bold;">📊 Generate Report</button>';
      html += '</div>';

      html += '<div class="analytics-section">';
      html += '<div class="section-title">Summary</div>';
      html += '<div class="stat-cards">';

      const projectCount = Object.keys(metrics).length || 0;
      html += `<div class="stat-card">
        <div class="stat-card-value">${projectCount}</div>
        <div class="stat-card-label">Projects</div>
      </div>`;

      html += `<div class="stat-card">
        <div class="stat-card-value">${capacity.total_effort_days || 0}</div>
        <div class="stat-card-label">Days (Total)</div>
      </div>`;

      html += `<div class="stat-card">
        <div class="stat-card-value">${capacity.critical_path_days || 0}</div>
        <div class="stat-card-label">Days (Critical Path)</div>
      </div>`;

      html += `<div class="stat-card">
        <div class="stat-card-value">${capacity.compression_ratio || 1}x</div>
        <div class="stat-card-label">Parallelization Ratio</div>
      </div>`;

      html += '</div></div>';

      if (bottlenecks.summary) {
        html += '<div class="analytics-section">';
        html += '<div class="section-title">⚠ Bottlenecks</div>';
        html += `<div class="warning-box">${bottlenecks.summary}</div>`;
        if (bottlenecks.blocking_count > 0) {
          html += `<p><strong>${bottlenecks.blocking_count}</strong> blocking project(s)</p>`;
        }
        if (bottlenecks.chain_count > 0) {
          html += `<p><strong>${bottlenecks.chain_count}</strong> deep dependency chain(s)</p>`;
        }
        html += '</div>';
      }

      if (Array.isArray(impactful) && impactful.length > 0) {
        html += '<div class="analytics-section">';
        html += '<div class="section-title">🎯 Most Impactful Projects</div>';
        html += '<table class="analytics-table">';
        html += '<tr><th>Project</th><th>Unblocks</th><th>Downstream</th><th>Impact</th></tr>';

        for (const p of impactful) {
          html += `<tr>
            <td><strong>${p.project_id}</strong></td>
            <td>${p.num_unblocked || 0}</td>
            <td>${p.num_downstream || 0}</td>
            <td>${(p.impact_ratio * 100).toFixed(0)}%</td>
          </tr>`;
        }

        html += '</table></div>';
      }

      const metricKeys = Object.keys(metrics || {});
      if (metricKeys.length > 0) {
        html += '<div class="analytics-section">';
        html += '<div class="section-title">📈 Project Metrics</div>';
        html += '<table class="analytics-table">';
        html += '<tr><th>Project</th><th>Fan-In</th><th>Fan-Out</th><th>Depth</th><th>Criticality</th></tr>';

        try {
          for (const [pid, m] of Object.entries(metrics)) {
            const critColor = (m.criticality || 0) > 0.7 ? 'critical' : '';
            html += `<tr>
              <td><strong>${m.project_id || pid}</strong></td>
              <td>${m.fan_in || 0}</td>
              <td>${m.fan_out || 0}</td>
              <td>${m.depth || 0}</td>
              <td><span class="${critColor}">${(m.criticality || 0).toFixed(2)}</span></td>
            </tr>`;
          }
        } catch (e) {
          console.error('Error rendering metrics:', e);
          html += '<tr><td colspan="5">Error rendering metrics table</td></tr>';
        }

        html += '</table></div>';
      }

      if (capacity.timeline_phases && Array.isArray(capacity.timeline_phases)) {
        html += '<div class="analytics-section">';
        html += '<div class="section-title">📅 Timeline Phases</div>';
        html += '<table class="analytics-table">';
        html += '<tr><th>Phase</th><th>Projects</th><th>Effort</th><th>Duration</th></tr>';

        for (const phase of capacity.timeline_phases) {
          html += `<tr>
            <td>Phase ${phase.phase}</td>
            <td>${phase.project_count}</td>
            <td>${phase.total_effort_days} days</td>
            <td>~${phase.ideal_duration_days} days</td>
          </tr>`;
        }

        html += '</table></div>';
      } else if (capacity.timeline_phases) {
        console.warn('timeline_phases exists but is not an array:', capacity.timeline_phases);
      }

      html += '<div class="analytics-section">';
      html += '<div class="section-title">📈 Charts</div>';
      html += '<div id="charts-container" style="display: grid; grid-template-columns: 1fr; gap: 20px;"></div>';
      html += '</div>';

      dashboard.innerHTML = html;

      Analytics.loadCharts();
    } catch (e) {
      console.error('Error rendering analytics:', e);
      const dashboard = document.getElementById('analytics-dashboard');
      dashboard.innerHTML = `<div class="warning-box">Rendering error: ${e.message}</div><pre style="color: #f38ba8; font-size: 0.8em;">${e.stack}</pre>`;
    }
  }

  static async loadCharts() {
    try {
      const container = document.getElementById('charts-container');
      if (!container) return;

      try {
        const ganttRes = await fetch('/api/chart/gantt');
        const ganttData = await ganttRes.json();
        if (ganttData.ok && ganttData.svg) {
          const ganttDiv = document.createElement('div');
          ganttDiv.innerHTML = `<div class="section-title">📅 Gantt Chart</div>${ganttData.svg}`;
          container.appendChild(ganttDiv);
        }
      } catch (e) {
        console.error('Error loading Gantt:', e);
      }

      try {
        const burndownRes = await fetch('/api/chart/burndown');
        const burndownData = await burndownRes.json();
        if (burndownData.ok && burndownData.svg) {
          const burndownDiv = document.createElement('div');
          burndownDiv.innerHTML = `<div class="section-title">🔥 Burndown Chart</div>${burndownData.svg}`;
          container.appendChild(burndownDiv);
        }
      } catch (e) {
        console.error('Error loading Burndown:', e);
      }
    } catch (e) {
      console.error('Error loading charts:', e);
    }
  }

  static async generateReport() {
    const reportBtn = document.getElementById('report-btn');
    const originalText = reportBtn.textContent;
    reportBtn.textContent = '⏳ Generating...';
    reportBtn.disabled = true;

    try {
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'report' })
      });
      const data = await res.json();

      if (data.ok) {
        reportBtn.textContent = '✓ Report generated';
        window.open('/report', '_blank');
        setTimeout(() => {
          reportBtn.textContent = originalText;
          reportBtn.disabled = false;
        }, 2000);
      } else {
        reportBtn.textContent = '✗ Error';
        setTimeout(() => {
          reportBtn.textContent = originalText;
          reportBtn.disabled = false;
        }, 2000);
      }
    } catch (e) {
      console.error('Report generation failed:', e);
      reportBtn.textContent = '✗ Failed';
      setTimeout(() => {
        reportBtn.textContent = originalText;
        reportBtn.disabled = false;
      }, 2000);
    }
  }
}

window.Analytics = Analytics;
