// irqhomedb shared helpers — extracted from base.html + list templates.

// Mobile sidebar (was duplicated inline in base.html)
function toggleSidebar() {
    var sidebar = document.getElementById('sidebarMobile');
    var overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('show');
}

// Highlight active sidebar link
document.addEventListener('DOMContentLoaded', function () {
    var path = window.location.pathname;
    document.querySelectorAll('.sidebar nav a, .sidebar-mobile nav a').forEach(function (a) {
        if (a.getAttribute('href') === path) {
            a.classList.add('active');
        }
    });
});

// Fetch a JSON endpoint and return the parsed body.
function apiFetch(url, options) {
    return fetch(url, options).then(function (r) { return r.json(); });
}

// Escape a string for safe interpolation into innerHTML templates
// (item/box/location names are user-provided and were previously injected raw).
function esc(s) {
    return String(s == null ? '' : s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Confirm + DELETE helper used by several list pages.
function confirmDelete(url, label, onDone) {
    if (!confirm('🗑️ Hapus "' + (label || 'ini') + '"?')) return;
    apiFetch(url, { method: 'DELETE' }).then(function (data) {
        if (data.success) onDone();
        else alert(data.detail || 'Gagal');
    });
}
