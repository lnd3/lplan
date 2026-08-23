class EventDispatcher {
  static init() {
    document.addEventListener('click', (event) => {
      const target = event.target;
      const action = target.dataset.action;

      if (!action) return;

      event.preventDefault();
      event.stopPropagation();

      switch (action) {
        case 'show-browser':
          FileBrowser.showBrowser();
          break;
        case 'show-tree':
          TreeView.showTree();
          break;
        case 'show-analytics':
          Analytics.showAnalytics();
          break;
        case 'edit-file':
          FileEditor.enterEdit();
          break;
        case 'save-file':
          FileEditor.saveFile();
          break;
        case 'cancel-edit':
          FileEditor.cancelEdit();
          break;
        case 'load-file':
          FileBrowser.loadFile(target.dataset.path);
          break;
        case 'generate-report':
          Analytics.generateReport();
          break;
      }
    });
  }
}

window.EventDispatcher = EventDispatcher;
