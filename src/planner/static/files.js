class FileBrowser {
  static async loadTree() {
    const res  = await fetch('/api/tree');
    const tree = await res.json();
    const sb   = document.getElementById('sidebar-content');
    sb.innerHTML = '';
    FileBrowser.renderTree(sb, tree);
  }

  static renderTree(parent, nodes) {
    for (const node of nodes) {
      if (node.type === 'file') {
        const el = document.createElement('div');
        el.className = 'tree-item';
        el.style.display = 'flex';
        el.style.alignItems = 'center';
        el.dataset.path = node.path;
        el.onclick = () => FileBrowser.loadFile(node.path);

        const spacer = document.createElement('span');
        spacer.className = 'arrow';
        spacer.style.visibility = 'hidden';
        el.appendChild(spacer);

        const nameSpan = document.createElement('span');
        nameSpan.textContent = node.name;
        el.appendChild(nameSpan);

        parent.appendChild(el);
      } else {
        const hdr = document.createElement('div');
        hdr.className = 'tree-dir';
        const toggle = document.createElement('span');
        toggle.className = 'arrow';
        toggle.textContent = node.children && node.children.length > 0 ? '-' : '•';
        hdr.appendChild(toggle);
        const nameSpan = document.createElement('span');
        nameSpan.textContent = node.name;
        hdr.appendChild(nameSpan);
        parent.appendChild(hdr);

        const children = document.createElement('div');
        children.className = 'tree-children';
        FileBrowser.renderTree(children, node.children);
        parent.appendChild(children);

        hdr.onclick = () => {
          hdr.classList.toggle('collapsed');
          children.classList.toggle('hidden');
          if (node.children && node.children.length > 0) {
            toggle.textContent = children.classList.contains('hidden') ? '+' : '-';
          }
        };
      }
    }
  }

  static async loadFile(path) {
    const res = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
    if (!res.ok) { UI.showError(`Failed to load: ${path}`); return; }
    window.currentRaw  = await res.text();
    window.currentPath = path;

    // Callers other than the Files browser (e.g. Tree view's "Full Doc" button)
    // leave #file-toolbar hidden — without this, there's no Edit button to reach,
    // so Save is never reachable either even though the editor itself works fine.
    document.getElementById('file-toolbar').style.display = 'flex';
    document.getElementById('preview').style.display = '';
    document.getElementById('editor-wrap').style.display = 'none';
    document.getElementById('tree-view').style.display = 'none';
    document.getElementById('analytics-dashboard').style.display = 'none';
    document.getElementById('items-view').style.display = 'none';
    document.getElementById('status-view').style.display = 'none';

    document.querySelectorAll('.tree-item').forEach(el => {
      el.classList.toggle('active', el.dataset.path === path);
    });

    document.getElementById('current-path').textContent = path;
    UI.hideBanner();
    FilePreview.showPreview(window.currentRaw);
    FilePreview.displayParentContext(window.currentRaw, path);
  }

  static async showBrowser() {
    const buttons = document.querySelectorAll('#toolbar button');
    buttons.forEach(btn => btn.classList.remove('active'));
    buttons[0].classList.add('active');

    document.getElementById('file-toolbar').style.display = 'flex';
    document.getElementById('preview').style.display = '';
    document.getElementById('tree-view').style.display = 'none';
    document.getElementById('analytics-dashboard').style.display = 'none';
    document.getElementById('items-view').style.display = 'none';
    document.getElementById('status-view').style.display = 'none';
    document.getElementById('sidebar').style.display = '';

    await FileBrowser.loadTree();
  }
}

window.FileBrowser = FileBrowser;
