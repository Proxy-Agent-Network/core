const LanguageEngine = {
    init: function(selectorId) {
        const savedLang = localStorage.getItem('selectedLanguage') || 'en';
        const selector = document.getElementById(selectorId);
        
        if (selector) {
            selector.value = savedLang;
            selector.onchange = (e) => this.setLanguage(e.target.value);
        }
        
        this.applyLanguage(savedLang);
    },

    setLanguage: function(langCode) {
        localStorage.setItem('selectedLanguage', langCode);
        this.applyLanguage(langCode);
    },

    applyLanguage: function(langCode) {
        const dict = TRANSLATIONS[langCode] || TRANSLATIONS['en'];
        const elements = document.querySelectorAll('[data-i18n]');
        
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) {
                // Preserve icons if present (e.g. settings buttons)
                if (el.children.length > 0) {
                    // Complex case: update only text node if mixed with icons
                    // For now, simpler approach: just assume text replacement or innerHTML
                    // We'll use innerHTML to allow icons in translation strings if needed, 
                    // but safer to just replace textContent for security.
                    // However, our keys map to pure text.
                    el.innerText = dict[key];
                } else {
                    el.innerText = dict[key];
                }
            }
        });
    }
};