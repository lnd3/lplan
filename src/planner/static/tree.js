class TreeView {
  static treeHierarchy = null;
  static selectedTreeItem = null;

  static TYPE_COLORS = { thesis: '#cba6f7', master_plan: '#f9e2af', project: '#89b4fa', design: '#a6adc8', action: '#9399b2' };

  static parentBadge(id, color) {
    return `<span style="font-size:10px;color:${color};background:${color}1a;border-radius:3px;padding:1px 4px;margin-left:3px;flex-shrink:0;">${id}</span>`;
  }

  static buildTreeHTML(projects, indent = 0) {
    let html = '';
    for (const project of projects) {
      const hasChildren = project.children && project.children.length > 0;
      const paddingLeft = indent * 20;
      const mpBadges = (project.parent_master_plan || [])
        .map(m => TreeView.parentBadge(m, TreeView.TYPE_COLORS.master_plan)).join('');

      html += `<div class="tree-item" style="padding-left: ${paddingLeft}px;" id="tree-${project.id}">
        <div style="display: flex; align-items: center; flex-wrap: wrap;">
          <span class="tree-toggle" style="transition: transform 0.15s;" data-toggle-id="${project.id}" data-has-children="${hasChildren}">${hasChildren ? '+' : '•'}</span>
          ${TreeView.parentBadge(project.id, TreeView.TYPE_COLORS.project)}
          <div class="tree-node tree-node-project" onclick='TreeView.showTreeRoot("${project.id}", "${project.title}", "project", "${project.path}")' data-id="${project.id}">${project.title}</div>
          ${mpBadges}
        </div>
        ${TreeView.buildChildrenHTML(project, indent + 1)}
      </div>`;
    }
    return html;
  }

  static buildChildrenHTML(parent, indent) {
    if (!parent.children || parent.children.length === 0) return '';

    let html = `<div id="children-${parent.id}" class="tree-children" style="display: none;">`;
    for (const child of parent.children) {
      const hasGrandchildren = child.children && child.children.length > 0;
      const paddingLeft = indent * 20;
      const childType = child.id.charAt(0) === 'D' ? 'design' : 'action';
      const childColor = TreeView.TYPE_COLORS[childType] || '#a6adc8';
      // Parent badge: designs show project ID (blue), actions show design ID (gray)
      const parentId = childType === 'design' ? parent.id : (child.parent_design || '');
      const parentColor = childType === 'design' ? TreeView.TYPE_COLORS.project : TreeView.TYPE_COLORS.design;
      const parentBadge = parentId ? TreeView.parentBadge(parentId, parentColor) : '';

      html += `<div class="tree-item" style="padding-left: ${paddingLeft}px;" id="tree-${child.id}">
        <div style="display: flex; align-items: center; flex-wrap: wrap;">
          <span class="tree-toggle" style="transition: transform 0.15s;" data-toggle-id="${child.id}" data-has-children="${hasGrandchildren}">${hasGrandchildren ? '+' : '•'}</span>
          ${TreeView.parentBadge(child.id, childColor)}
          <div class="tree-node tree-node-design" style="color:${childColor};" onclick='TreeView.showTreeRoot("${child.id}", "${child.title}", "${childType}", "${child.path}")' data-id="${child.id}">${child.title}</div>
          ${parentBadge}
        </div>
        ${TreeView.buildChildrenHTML(child, indent + 1)}
      </div>`;
    }
    html += '</div>';
    return html;
  }

  static toggleTreeItem(event, id, hasChildren) {
    if (!hasChildren) return;
    event.stopPropagation();

    const childrenDiv = document.getElementById(`children-${id}`);
    const toggle = event.currentTarget;
    const treeItem = document.getElementById(`tree-${id}`);

    if (childrenDiv) {
      const isHidden = childrenDiv.style.display === 'none';
      childrenDiv.style.display = isHidden ? '' : 'none';
      toggle.textContent = isHidden ? '-' : '+';
      if (treeItem) {
        treeItem.classList.toggle('collapsed');
      }
    }
  }

  static highlightTreeItem(id) {
    if (TreeView.selectedTreeItem) {
      const prevItem = document.getElementById(`tree-${TreeView.selectedTreeItem}`);
      if (prevItem) prevItem.classList.remove('active');
    }

    const item = document.getElementById(`tree-${id}`);
    if (item) {
      item.classList.add('active');
      TreeView.selectedTreeItem = id;
    }
  }

  static async showTree() {
    const buttons = document.querySelectorAll('#toolbar button');
    buttons.forEach(btn => btn.classList.remove('active'));
    buttons[1].classList.add('active');

    document.getElementById('file-toolbar').style.display = 'none';
    document.getElementById('preview').style.display = 'none';
    document.getElementById('tree-view').style.display = 'none';
    document.getElementById('analytics-dashboard').style.display = 'none';
    document.getElementById('status-view').style.display = 'none';

    document.getElementById('sidebar').style.display = '';
    const sidebarContent = document.getElementById('sidebar-content');
    sidebarContent.innerHTML = '<div style="text-align: center; color: #a6adc8; padding: 20px;">Loading tree...</div>';

    try {
      const res = await fetch('/api/hierarchy');
      const hierarchy = await res.json();

      TreeView.treeHierarchy = hierarchy.projects || [];
      const theses = hierarchy.theses || [];
      const masterPlans = hierarchy.master_plans || [];

      let html = '';

      // Theses → Master Plans (many-to-many)
      if (theses.length > 0) {
        html += '<div style="padding: 10px 0; border-bottom: 1px solid #313244; margin-bottom: 4px;">';
        html += '<div style="font-weight: bold; color: #cba6f7; padding: 5px 10px; font-size: 12px;">THESES</div>';
        for (const t of theses) {
          const hasMPs = t.master_plans && t.master_plans.length > 0;
          const childrenId = `thesis-children-${t.id}`;
          // Start open (no .collapsed class) so CSS rotates the + to show expanded state
          html += `<div class="tree-item" id="tree-${t.id}">
            <div style="display: flex; align-items: center; flex-wrap: wrap;">
              <span class="tree-toggle" style="transition: transform 0.15s; cursor:pointer; user-select:none;"
                data-has-children="${hasMPs}"
                onclick="const item=document.getElementById('tree-${t.id}'); const c=document.getElementById('${childrenId}'); const closing=!item.classList.contains('collapsed'); c.style.display=closing?'none':''; item.classList.toggle('collapsed', closing);">${hasMPs ? '+' : '•'}</span>
              ${TreeView.parentBadge(t.id, TreeView.TYPE_COLORS.thesis)}
              <div class="tree-node tree-node-project" style="color:#cba6f7;"
                onclick='TreeView.showTreeRoot("${t.id}", "${t.title}", "thesis", "${t.path}")' data-id="${t.id}">${t.title}</div>
            </div>
            <div id="${childrenId}" style="padding-left: 18px; display:${hasMPs ? '' : 'none'};">
              ${hasMPs ? t.master_plans.map(mp => `
              <div class="tree-item" id="tree-${t.id}-${mp.id}">
                <div style="display: flex; align-items: center; flex-wrap: wrap;">
                  <span class="tree-toggle" style="cursor:default;" data-has-children="false">•</span>
                  ${TreeView.parentBadge(mp.id, TreeView.TYPE_COLORS.master_plan)}
                  <div class="tree-node tree-node-project" style="color:#f9e2af; font-size:12px;"
                    onclick='TreeView.showTreeRoot("${mp.id}", "${mp.title}", "master_plan", "${mp.path}")' data-id="${mp.id}">${mp.title}</div>
                </div>
              </div>`).join('') : ''}
            </div>
          </div>`;
        }
        html += '</div>';
      }

      // Master Plans (flat list for plans not linked to any thesis)
      const linkedMPIds = new Set(theses.flatMap(t => (t.master_plans || []).map(mp => mp.id)));
      const unlinkedMPs = masterPlans.filter(mp => !linkedMPIds.has(mp.id));
      if (masterPlans.length > 0) {
        html += '<div style="padding: 10px 0; border-bottom: 1px solid #313244; margin-bottom: 10px;">';
        html += '<div style="font-weight: bold; color: #f9e2af; padding: 5px 10px; font-size: 12px;">MASTER PLANS</div>';
        for (const mp of masterPlans) {
          const thesisBadges = (mp.theses || [])
            .map(t => TreeView.parentBadge(t, TreeView.TYPE_COLORS.thesis)).join('');
          html += `<div class="tree-item" id="tree-mp-${mp.id}">
            <div style="display: flex; align-items: center; flex-wrap: wrap;">
              <span class="tree-toggle" data-has-children="false">•</span>
              ${TreeView.parentBadge(mp.id, TreeView.TYPE_COLORS.master_plan)}
              <div class="tree-node tree-node-project" style="color:#f9e2af;" onclick='TreeView.showTreeRoot("${mp.id}", "${mp.title}", "master_plan", "${mp.path}")' data-id="${mp.id}">${mp.title}</div>
              ${thesisBadges}
            </div>
          </div>`;
        }
        html += '</div>';
      }

      // Projects section
      html += '<div style="padding: 10px 0;">';
      html += '<div style="font-weight: bold; color: #89b4fa; padding: 5px 10px; font-size: 12px;">PROJECTS</div>';
      html += TreeView.buildTreeHTML(TreeView.treeHierarchy);
      html += '</div>';

      sidebarContent.innerHTML = html;

      const preview = document.getElementById('preview');
      if (theses.length > 0) {
        await TreeView.showTreeRoot(theses[0].id, theses[0].title, 'thesis', theses[0].path);
      } else if (masterPlans.length > 0) {
        await TreeView.showTreeRoot(masterPlans[0].id, masterPlans[0].title, 'master_plan', masterPlans[0].path);
      } else if (TreeView.treeHierarchy.length > 0) {
        await TreeView.showTreeRoot(TreeView.treeHierarchy[0].id, TreeView.treeHierarchy[0].title, 'project', TreeView.treeHierarchy[0].path);
      } else {
        preview.style.display = '';
        preview.innerHTML = '<div style="padding: 20px; color: #a6adc8; text-align: center;">No items in hierarchy</div>';
      }
    } catch (e) {
      console.error('Failed to load hierarchy:', e);
      sidebarContent.innerHTML = '<div style="color: #f38ba8; padding: 20px;">Failed to load hierarchy</div>';
    }
  }

  static async showTreeRoot(id, title, type, path) {
    if (typeof id === 'object' && id.dataset) {
      const element = id;
      id = element.dataset.id;
      title = element.dataset.title;
      type = element.dataset.type;
      path = element.dataset.path;
    }

    TreeView.highlightTreeItem(id);

    const preview = document.getElementById('preview');
    preview.style.display = '';
    preview.innerHTML = '<div style="text-align: center; color: #a6adc8;">Loading...</div>';

    try {
      const res = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
      if (!res.ok) throw new Error('File not found');
      const content = await res.text();

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

      const preview_text = meta.ingress || (body.length > 100000 ? body.substring(0, 100000) + '\n... (truncated)' : body);

      let hierarchyHTML = '';
      if (type !== 'master_plan' && type !== 'thesis') {
        const currentNode = TreeView.findNodeInHierarchy(id, TreeView.treeHierarchy);
        if (!currentNode) throw new Error('Node not found');
        hierarchyHTML = await TreeView.renderHierarchyView(currentNode, type, 1);
      }

      const typeLabel = { master_plan: 'Master Plan', thesis: 'Thesis', project: 'Project', design: 'Design', action: 'Action' }[type] || type;
      const typeIcons = { thesis: '💡', master_plan: '🎯', project: '📋', design: '🎨', action: '✓' };
      const typeIcon = typeIcons[type] || '•';
      const TYPE_COLORS = { thesis: '#cba6f7', master_plan: '#f9e2af', project: '#89b4fa', design: '#a6adc8', action: '#9399b2' };
      const typeColor = TYPE_COLORS[type] || '#cdd6f4';

      preview.innerHTML = `
        <div style="padding: 8px 12px; max-width: 1000px; margin: 0 auto;">
          <h1 style="color: #cdd6f4; margin: 0 0 2px 0; font-size: 20px; font-weight: 700; line-height: 1.2;">${title}</h1>

          <div style="font-size: 10px; color: #6c7086; margin-bottom: 4px;">
            ${typeIcon} ${typeLabel} • ${id}
            ${meta.created ? ` • Created: <span style="color: #a6adc8;">${meta.created}</span>` : ''}
            ${meta.status ? ` • Status: <span style="color: #a6adc8;">${meta.status}</span>` : ''}
            ${meta.priority ? ` • Priority: <span style="color: #a6adc8;">${meta.priority}</span>` : ''}
          </div>
          ${meta.description ? `<div style="color: #a6adc8; font-size: 12px; margin-bottom: 8px;">${meta.description}</div>` : ''}

          ${preview_text ? `<div style="margin-bottom: 8px; background: rgba(88, 166, 255, 0.1); border-radius: 2px; border: 1px solid rgba(88, 166, 255, 0.2);">
            <div style="padding: 4px 8px; display: flex; align-items: center; gap: 4px; color: #a6adc8; font-size: 10px; cursor: pointer;" onclick="const expanded = this.parentElement.querySelector('.content-expanded'); expanded.style.display = expanded.style.display === 'none' ? '' : 'none'; this.querySelector('.expand-btn').textContent = expanded.style.display === 'none' ? '+' : '-';">
              <span class="expand-btn" style="flex-shrink: 0; width: 12px; text-align: center; font-weight: bold; font-size: 14px; transition: transform 0.15s;">+</span>
              <span>Content</span>
            </div>
            <div class="content-expanded" style="display: none; padding: 4px 8px; border-top: 1px solid rgba(88, 166, 255, 0.2); color: #a6adc8; font-size: 11px; white-space: pre-wrap; word-wrap: break-word; line-height: 1.4; resize: vertical; overflow: auto; max-height: 200px; min-height: 100px;">${preview_text}</div>
          </div>` : ''}

          ${hierarchyHTML ? `<div style="margin-top: 8px;">
            <div style="display: flex; align-items: center; gap: 4px; cursor: pointer; padding: 4px 8px; margin-bottom: 4px;" onclick="const section = this.nextElementSibling; const toggle = this.querySelector('.children-toggle'); section.style.display = section.style.display === 'none' ? '' : 'none'; toggle.textContent = section.style.display === 'none' ? '+' : '-';">
              <span class="children-toggle" style="flex-shrink: 0; width: 12px; font-size: 14px; transition: transform 0.15s;">-</span>
              <span style="font-size: 11px; font-weight: 600; color: #6c7086; text-transform: uppercase;">${type === 'project' ? 'Designs' : 'Actions'}</span>
            </div>
            <div style="padding-top: 8px;">
              ${hierarchyHTML}
            </div>
          </div>` : ''}

          <div style="margin-top: 8px; padding-top: 8px;">
            <button onclick="FileBrowser.loadFile('${path}')" style="padding: 4px 8px; background: transparent; color: #89b4fa; border: 1px solid #45475a; border-radius: 2px; cursor: pointer; font-size: 11px; transition: transform 0.15s;">📄 Full Doc</button>
          </div>
        </div>
      `;
    } catch (e) {
      console.error(e);
      preview.innerHTML = `<div style="color: #f38ba8; padding: 20px;">Error loading entity</div>`;
    }
  }

  static findNodeInHierarchy(id, nodes) {
    for (const node of nodes) {
      if (node.id === id) return node;
      if (node.children) {
        const found = TreeView.findNodeInHierarchy(id, node.children);
        if (found) return found;
      }
    }
    return null;
  }

  static async renderHierarchyView(node, type, depth = 0) {
    if (!node.children || node.children.length === 0) return '';

    const childType = type === 'project' ? 'design' : 'action';
    const typeIcon = childType === 'design' ? '🎨' : '✓';
    const bgColor = childType === 'design' ? 'rgba(166, 172, 200, 0.1)' : 'rgba(147, 153, 178, 0.1)';
    const borderColor = childType === 'design' ? 'rgba(166, 172, 200, 0.2)' : 'rgba(147, 153, 178, 0.2)';

    let html = `<div style="margin-left: ${depth * 32}px; margin-top: 8px; padding-top: 8px;">`;

    for (const child of node.children) {
      const hasGrandchildren = child.children && child.children.length > 0;
      const toggleId = `hierarchy-${child.id}`;
      const contentId = `hierarchy-content-${child.id}`;

      let childMeta = {};
      let childPreview = '';
      try {
        const res = await fetch(`/api/file?path=${encodeURIComponent(child.path)}`);
        if (res.ok) {
          const content = await res.text();
          const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
          const body = content.split('---').slice(2).join('---').trim();
          if (frontmatterMatch) {
            const lines = frontmatterMatch[1].split('\n');
            for (const line of lines) {
              if (line.includes(':')) {
                const [key, val] = line.split(':').map(s => s.trim());
                childMeta[key] = val;
              }
            }
          }
          childPreview = childMeta.ingress || (body.length > 100000 ? body.substring(0, 100000) + '\n... (truncated)' : body);
        }
      } catch (e) {
        console.error('Failed to load child data:', e);
      }

      html += `<div style="padding: 8px; background: ${bgColor}; border-radius: 2px; margin-bottom: 4px; border: 1px solid ${borderColor};">
        <h3 style="color: #cdd6f4; margin: 0 0 2px 0; font-size: 14px; font-weight: 700;">${child.title}</h3>

        <div style="font-size: 10px; color: #6c7086; margin-bottom: 4px;">
          ${typeIcon} ${childType} • ${child.id}
          ${childMeta.created ? ` • Created: <span style="color: #a6adc8;">${childMeta.created}</span>` : ''}
          ${childMeta.status ? ` • Status: <span style="color: #a6adc8;">${childMeta.status}</span>` : ''}
          ${childMeta.priority ? ` • Priority: <span style="color: #a6adc8;">${childMeta.priority}</span>` : ''}
        </div>
        ${childMeta.description ? `<div style="color: #a6adc8; font-size: 11px; margin-bottom: 4px;">${childMeta.description}</div>` : ''}

        ${childPreview ? `<div style="background: #1e1e2e; border-radius: 2px; margin-bottom: 8px;">
          <div style="padding: 4px 8px; display: flex; align-items: center; gap: 4px; color: #a6adc8; font-size: 10px; cursor: pointer;" onclick="const expanded = this.parentElement.querySelector('.content-expanded'); expanded.style.display = expanded.style.display === 'none' ? '' : 'none'; this.querySelector('.expand-btn').textContent = expanded.style.display === 'none' ? '+' : '-';">
            <span class="expand-btn" style="flex-shrink: 0; width: 12px; text-align: center; font-weight: bold;">+</span>
            <span>Content</span>
          </div>
          <div class="content-expanded" style="display: none; padding: 4px 8px; border-top: 1px solid #313244; color: #a6adc8; font-size: 11px; white-space: pre-wrap; word-wrap: break-word; line-height: 1.4; resize: vertical; overflow: auto; max-height: 200px; min-height: 100px;">${childPreview}</div>
        </div>` : ''}

        ${hasGrandchildren ? `
          <div style="display: flex; align-items: center; gap: 4px; margin-top: 4px; cursor: pointer;" onclick="const kids = document.getElementById('${toggleId}-children'); const toggle = document.getElementById('${toggleId}-toggle'); const wrapper = toggle.parentElement; const isHidden = kids.style.display === 'none'; kids.style.display = isHidden ? '' : 'none'; toggle.textContent = isHidden ? '-' : '+'; wrapper.classList.toggle('collapsed');">
            <span id="${toggleId}-toggle" class="tree-toggle" style="flex-shrink: 0; font-size: 14px; transition: transform 0.15s;">+</span>
            <span style="font-size: 10px; color: #6c7086; font-weight: 600;">${childType === 'design' ? 'Actions' : 'Items'}</span>
          </div>
          <div id="${toggleId}-children" style="display: none; padding-top: 8px; margin-top: 8px;">
            ${await TreeView.renderHierarchyView(child, childType, depth + 1)}
          </div>
        ` : ''}
      </div>`;
    }

    html += '</div>';
    return html;
  }
}

document.addEventListener('click', (event) => {
  if (event.target.classList.contains('tree-toggle') && event.target.dataset.toggleId) {
    const id = event.target.dataset.toggleId;
    const hasChildren = event.target.dataset.hasChildren === 'true';
    TreeView.toggleTreeItem(event, id, hasChildren);
  }
});

window.TreeView = TreeView;
