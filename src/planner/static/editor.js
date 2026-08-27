class FileEditor {
  static editor = null;

  static enterEdit() {
    const editEnabled = window.editEnabled;
    if (!editEnabled || !window.currentRaw) return;

    const preview = document.getElementById('preview');
    const wrap    = document.getElementById('editor-wrap');

    preview.style.display = 'none';
    wrap.style.display    = 'flex';

    // #btn-save/#btn-cancel have `display: none` baked into their base CSS
    // rule (style.css), so clearing the inline override (style.display = '')
    // doesn't reveal them — it just falls back to that stylesheet rule and
    // they stay hidden. Must set an explicit visible value instead.
    document.getElementById('btn-edit').style.display   = 'none';
    document.getElementById('btn-save').style.display   = 'inline-block';
    document.getElementById('btn-cancel').style.display = 'inline-block';

    if (!FileEditor.editor) {
      const textarea = document.createElement('textarea');
      wrap.appendChild(textarea);
      FileEditor.editor = CodeMirror.fromTextArea(textarea, {
        mode: 'markdown',
        theme: 'dracula',
        lineNumbers: true,
        lineWrapping: true,
        autofocus: true,
      });
      FileEditor.editor.getWrapperElement().style.flex = '1';
    }
    FileEditor.editor.setValue(window.currentRaw);
    FileEditor.editor.refresh();
  }

  static cancelEdit() {
    document.getElementById('editor-wrap').style.display  = 'none';
    document.getElementById('preview').style.display      = '';
    document.getElementById('btn-edit').style.display     = window.editEnabled ? '' : 'none';
    document.getElementById('btn-save').style.display     = 'none';
    document.getElementById('btn-cancel').style.display   = 'none';
    UI.hideBanner();
  }

  static async saveFile() {
    if (!FileEditor.editor || !window.currentPath) return;
    const content = FileEditor.editor.getValue();

    const res = await fetch(`/api/file?path=${encodeURIComponent(window.currentPath)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      body: content,
    });

    const data = await res.json();

    if (!res.ok || !data.ok) {
      UI.showBanner(false, data.output || 'Save failed.');
      return;
    }

    window.currentRaw = content;
    UI.showBanner(true, data.output || '✓ Saved');
    FileEditor.cancelEdit();
    FilePreview.showPreview(window.currentRaw);

    if (window.currentPath !== 'README.md' && window.currentPath !== 'FOCUS.md' && window.currentPath !== 'REFLECTION.md') {
      setTimeout(() => FilePreview.autoValidateAndPriority(), 300);
    }
  }
}

window.FileEditor = FileEditor;
