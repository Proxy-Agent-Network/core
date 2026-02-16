/**
 * 🎨 THEME ENGINE v1.2
 * Decoupled logic for cross-page theme management
 */

const ThemeEngine = {
    // Current available themes
    themes: [
        { id: 'business', label: '👔 Business' },
        { id: 'cyberpunk', label: '🦾 Cyberpunk' },
        { id: 'retro', label: '👾 Retro Arcade' },
        { id: 'deepsea', label: '🌊 Deep Sea' },
        { id: 'vampire', label: '🧛 Vampire' },
        { id: 'paperback', label: '📜 Paperback' },
        { id: 'groovy', label: '🕺 Groovy' }
    ],

    // Initialize the engine
    init: function(selectorId) {
        const savedTheme = localStorage.getItem('theme') || 'business';
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
        
        // Custom logic for Magic Marvin visibility
        const marvin = document.getElementById('magic-marvin');
        if (marvin) {
            marvin.style.display = (themeId === 'business' || themeId === 'paperback') ? 'none' : 'block';
        }
    },

    // Dynamically fill any <select> element with theme options
    populateSelector: function(element, activeTheme) {
        element.innerHTML = this.themes.map(t => 
            `<option value="${t.id}" ${t.id === activeTheme ? 'selected' : ''}>${t.label}</option>`
        ).join('');
    }
};

// Auto-run pre-render injection
(function() {
    const savedTheme = localStorage.getItem('theme') || 'business';
    document.documentElement.setAttribute('data-theme', savedTheme);
})();