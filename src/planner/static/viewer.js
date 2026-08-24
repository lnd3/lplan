class EntityViewer {
  static async show(id, title, type, path) {
    try {
      const res = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
      if (!res.ok) throw new Error('Failed to load entity');
      const content = await res.text();

      const modal = EntityViewer.createModal();
      document.body.appendChild(modal);

      const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
      const body = content.split('---').slice(2).join('---').trim();
      const meta = {};

      if (frontmatterMatch) {
        const lines = frontmatterMatch[1].split('\n');
        for (const line of lines) {
          if (line.includes(':')) {
            const [key, val] = line.split(':').map(s => s.trim());
            meta[key] = val;
          }
        }
      }

      const typeIcon = type === 'project' ? '📋' : (type === 'design' ? '🎨' : '✓');
      const typeLabel = type.charAt(0).toUpperCase() + type.slice(1);

      let contentHtml = `
        <div style="padding: 20px; color: #cdd6f4; max-height: 70vh; overflow-y: auto;">
          <h2 style="color: #89b4fa; margin: 0 0 12px 0; font-size: 20px; font-weight: 700;">${title}</h2>

          <div style="font-size: 11px; color: #6c7086; margin-bottom: 16px; line-height: 1.6;">
            <div>${typeIcon} ${typeLabel} • ${id}</div>
            ${meta.status ? `<div>Status: <span style="color: #a6adc8;">${meta.status}</span></div>` : ''}
            ${meta.priority ? `<div>Priority: <span style="color: #a6adc8;">${meta.priority}</span></div>` : ''}
            ${meta.created ? `<div>Created: <span style="color: #a6adc8;">${meta.created}</span></div>` : ''}
            ${meta.updated ? `<div>Updated: <span style="color: #a6adc8;">${meta.updated}</span></div>` : ''}
            ${meta.parent ? `<div>Parent: <span style="color: #a6adc8;">${meta.parent}</span></div>` : ''}
            ${meta.description ? `<div>Description: <span style="color: #a6adc8;">${meta.description}</span></div>` : ''}
          </div>

          <div style="border-top: 1px solid #313244; padding-top: 12px;">
      `;

      if (body) {
        marked.setOptions({ gfm: true, breaks: false });
        contentHtml += '<div style="color: #cdd6f4; line-height: 1.6;">';
        contentHtml += marked.parse(body);
        contentHtml += '</div>';
      } else {
        contentHtml += '<p style="color: #9399b2; font-style: italic;">No content</p>';
      }

      contentHtml += '</div></div>';

      modal.querySelector('.entity-viewer-content').innerHTML = contentHtml;

      modal.querySelector('.entity-viewer-close').addEventListener('click', () => {
        document.body.removeChild(modal);
      });

      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          document.body.removeChild(modal);
        }
      });
    } catch (e) {
      console.error('Error loading entity:', e);
      alert(`Failed to load entity: ${e.message}`);
    }
  }

  static createModal() {
    const modal = document.createElement('div');
    modal.className = 'entity-viewer-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 20px;
    `;

    const content = document.createElement('div');
    content.className = 'entity-viewer-box';
    content.style.cssText = `
      background: #1e1e2e;
      border: 1px solid #313244;
      border-radius: 8px;
      width: 100%;
      max-width: 700px;
      max-height: 80vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    `;

    const header = document.createElement('div');
    header.style.cssText = `
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      border-bottom: 1px solid #313244;
      flex-shrink: 0;
    `;

    const title = document.createElement('h3');
    title.textContent = 'Entity Details';
    title.style.cssText = 'color: #89b4fa; margin: 0; font-size: 16px; font-weight: 600;';

    const closeBtn = document.createElement('button');
    closeBtn.className = 'entity-viewer-close';
    closeBtn.textContent = '✕';
    closeBtn.style.cssText = `
      background: transparent;
      border: none;
      color: #a6adc8;
      font-size: 24px;
      cursor: pointer;
      padding: 0;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
    `;
    closeBtn.addEventListener('mouseover', () => closeBtn.style.color = '#cdd6f4');
    closeBtn.addEventListener('mouseout', () => closeBtn.style.color = '#a6adc8');

    header.appendChild(title);
    header.appendChild(closeBtn);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'entity-viewer-content';
    contentDiv.style.cssText = 'flex: 1; overflow-y: auto;';

    content.appendChild(header);
    content.appendChild(contentDiv);
    modal.appendChild(content);

    return modal;
  }
}

window.EntityViewer = EntityViewer;
