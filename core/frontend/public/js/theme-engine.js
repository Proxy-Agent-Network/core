/**
 * 🎨 PAN TACTICAL THEME ENGINE v2026.1.0
 * Decoupled logic for Sector Command cross-page theme management
 */

const ThemeEngine = {
    // Current available PAN Command themes
    themes: [
        { id: 'slate', label: '🌑 Slate (NOC Default)' },
        { id: 'high-vis', label: '🦺 High-Vis (Field Ops)' },
        { id: 'corporate', label: '📄 Corporate (Compliance)' }
    ],

    // Initialize the engine
    init: function(selectorId) {
        // Fallback to 'slate' if a legacy theme (e.g., 'business', 'cyberpunk') is still cached
        let savedTheme = localStorage.getItem('theme') || 'slate';
        if (!this.themes.find(t => t.id === savedTheme)) {
            savedTheme = 'slate';
        }
        
        this.apply(savedTheme);

        const selector = document.getElementById(selectorId);
        if (selector) {
            this.populateSelector(selector, savedTheme);
            selector.addEventListener('change', (e) => this.apply(e.target.value));
        }
    },

    // Apply theme to the document
    apply: function(themeId) {
        document.documentElement.setAttribute('data-theme', themeId);
        localStorage.setItem('theme', themeId);
    },

    // Dynamically fill any <select> element with theme options
    populateSelector: function(element, activeTheme) {
        element.innerHTML = this.themes.map(t => 
            `<option value="${t.id}" ${t.id === activeTheme ? 'selected' : ''}>${t.label}</option>`
        ).join('');
    }
};

// Auto-run pre-render injection to prevent FOUC (Flash of Unstyled Content)
(function() {
    let savedTheme = localStorage.getItem('theme') || 'slate';
    // Ensure we don't accidentally load a deprecated v1 theme on the first paint
    const validThemes = ['slate', 'high-vis', 'corporate'];
    if (!validThemes.includes(savedTheme)) {
        savedTheme = 'slate';
    }
    document.documentElement.setAttribute('data-theme', savedTheme);
})();