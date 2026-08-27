class FilePreview {
  static showPreview(markdown) {
    FileEditor.cancelEdit();
    const preview = document.getElementById('preview');

    if (window.currentPath === 'CHANGELOG.md' || window.currentPath === 'REFLECTION.md') {
      preview.innerHTML = `<pre style="font-family: monospace; font-size: 12px; white-space: pre-wrap; word-wrap: break-word; color: #bac2de;">${markdown.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>`;
    } else if (markdown.startsWith('---')) {
      const parts = markdown.split('---');
      if (parts.length >= 3) {
        const frontmatter = parts[1].trim();
        const body = parts.slice(2).join('---').trim();

        let html = '<div style="padding: 8px 12px;">';

        if (frontmatter) {
          html += '<div style="font-size: 11px; color: #6c7086; margin-bottom: 12px;">';
          frontmatter.split('\n').forEach(line => {
            if (line.trim()) {
              const [key, ...valueParts] = line.split(':');
              const value = valueParts.join(':').trim();
              html += `<div style="margin-bottom: 2px;"><span style="color: #6c7086;">${key}:</span> <span style="color: #a6adc8;">${value}</span></div>`;
            }
          });
          html += '</div>';
        }

        if (body) {
          marked.setOptions({ gfm: true, breaks: false });
          html += marked.parse(body);
        }

        html += '</div>';
        preview.innerHTML = html;
        FilePreview.interceptLinks(preview);
      } else {
        marked.setOptions({ gfm: true, breaks: false });
        preview.innerHTML = marked.parse(markdown);
        FilePreview.interceptLinks(preview);
      }
    } else {
      marked.setOptions({ gfm: true, breaks: false });
      preview.innerHTML = marked.parse(markdown);
      FilePreview.interceptLinks(preview);
    }
    preview.style.display = '';
  }

  static interceptLinks(container) {
    container.querySelectorAll('a[href]').forEach(a => {
      const href = a.getAttribute('href');
      if (!href.startsWith('http://') && !href.startsWith('https://') && !href.startsWith('#')) {
        a.addEventListener('click', e => {
          e.preventDefault();
          let path = href.replace(/^\.\//, '').split('#')[0];
          FileBrowser.loadFile(path);
        });
        a.style.cursor = 'pointer';
      } else if (href.startsWith('http://') || href.startsWith('https://')) {
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
      }
    });
  }

  static displayParentContext(markdown, path) {
    const lines = markdown.split('\n');
    let inFrontmatter = false;
    let parent = null;

    for (const line of lines) {
      if (line.trim() === '---') {
        if (!inFrontmatter) {
          inFrontmatter = true;
          continue;
        } else {
          break;
        }
      }
      if (inFrontmatter && line.includes('parent:')) {
        const match = line.match(/parent:\s*(.+)/);
        if (match) parent = match[1].trim();
      }
    }

    const pathEl = document.getElementById('current-path');
    if (parent) {
      const type = path.split('/')[0];
      let icon = '📁';
      if (type === 'projects') icon = '📋';
      else if (type === 'designs') icon = '🎨';
      else if (type === 'actions') icon = '✓';

      pathEl.innerHTML = `<span style="opacity: 0.6;">${parent}</span> <span style="opacity: 0.8;">/</span> <span style="font-weight: 500;">${icon} ${path.split('/').pop()}</span>`;
    } else if (FileEditor.isGenerated(path)) {
      pathEl.innerHTML = `${path} <span style="opacity: 0.6; font-style: italic;">(generated — regenerated on every view, not editable)</span>`;
    } else {
      pathEl.textContent = path;
    }
  }

  static async autoValidateAndPriority() {
    try {
      const validateRes = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'validate' })
      });
      const validateData = await validateRes.json();

      const priorityRes = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'priority' })
      });
      const priorityData = await priorityRes.json();

      let bannerClass = (validateData.ok && priorityData.ok) ? 'ok' : 'error';
      let bannerText = validateData.output + '\n\n' + priorityData.output;

      const banner = document.getElementById('validate-banner');
      banner.textContent = bannerText;
      banner.className = bannerClass;
      banner.style.display = '';
    } catch (e) {
      console.error('Auto-validation failed:', e);
    }
  }
}

window.FilePreview = FilePreview;
