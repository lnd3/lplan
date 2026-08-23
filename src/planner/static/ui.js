class UI {
  static showBanner(ok, text) {
    const el = document.getElementById('validate-banner');
    el.className = ok ? 'ok' : 'error';
    el.textContent = text;
    el.style.display = '';
  }

  static hideBanner() {
    document.getElementById('validate-banner').style.display = 'none';
  }

  static showError(msg) {
    document.getElementById('preview').innerHTML =
      `<p style="color:#f38ba8">${msg}</p>`;
  }
}

window.UI = UI;
