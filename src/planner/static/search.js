class FileSearch {
  static allFiles = [];

  static async loadFilesForSearch() {
    try {
      const res = await fetch('/api/tree');
      const tree = await res.json();
      FileSearch.allFiles = [];
      FileSearch.collectFiles(tree, FileSearch.allFiles);
    } catch (e) {
      console.error('Failed to load files for search:', e);
    }
  }

  static collectFiles(nodes, arr) {
    for (const node of nodes) {
      if (node.type === 'file') {
        arr.push(node);
      } else if (node.children) {
        FileSearch.collectFiles(node.children, arr);
      }
    }
  }

  static initSearchInput() {
    const searchInput = document.getElementById('search-input');
    const searchDropdown = document.getElementById('search-dropdown');

    searchInput.addEventListener('input', async (e) => {
      const query = e.target.value.toLowerCase().trim();

      if (!query) {
        searchDropdown.style.display = 'none';
        return;
      }

      const results = [];

      for (const file of FileSearch.allFiles) {
        try {
          const res = await fetch(`/api/file?path=${encodeURIComponent(file.path)}`);
          if (!res.ok) continue;
          const content = await res.text();

          const fileName = file.name.toLowerCase();
          const fileMatch = fileName.includes(query);

          const contentLines = content.split('\n');
          const matches = [];
          contentLines.forEach((line, idx) => {
            if (line.toLowerCase().includes(query)) {
              const preview = line.trim().substring(0, 70);
              matches.push(preview);
            }
          });

          if (fileMatch || matches.length > 0) {
            results.push({
              path: file.path,
              name: file.name,
              preview: matches[0] || '(filename match)',
              matchType: fileMatch ? 'name' : 'content'
            });
          }
        } catch (e) {
        }

        if (results.length >= 20) break;
      }

      if (results.length === 0) {
        searchDropdown.innerHTML = '<div style="padding: 12px; color: #6c7086; text-align: center; font-size: 12px;">No matches found</div>';
        searchDropdown.style.display = '';
        return;
      }

      searchDropdown.innerHTML = results.map((r, i) => `
        <div class="search-result-item" onclick="FileBrowser.loadFile('${r.path}')">
          <div class="search-result-file">${r.name}</div>
          <div class="search-result-preview">${r.preview}</div>
        </div>
      `).join('');
      searchDropdown.style.display = '';
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('#sidebar-search')) {
        searchDropdown.style.display = 'none';
      }
    });
  }
}

window.FileSearch = FileSearch;
