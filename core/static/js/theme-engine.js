/**
 * THEME ENGINE v4.2 (Shop Redirect Fix)
 * - Redirects locked themes to /shop (Provisioning)
 * - Cleaner Dropdown Labels
 */
const ThemeEngine = {
    init: function(selectorId) {
        const selector = document.getElementById(selectorId);
        if (!selector) return;

        // 1. STANDARD THEMES
        const standardThemes = [
            { id: 'business',  name: '👔 Business Class' },
            { id: 'retro',     name: '👾 Retro Arcade' },
            { id: 'paperback', name: '📜 Paperback Writer' },
            { id: 'cyberpunk', name: '🦾 Cyberpunk 2077' },
            { id: 'deepsea',   name: '🌊 Deep Sea' },
            { id: 'vampire',   name: '🧛 Vampire Hunter' },
            { id: 'groovy',    name: '🕺 Groovy Bus' }
        ];

        // 2. PREMIUM THEMES
        const premiumThemes = [
            { id: 'theme_neon', name: '🐝 Hex-Hive (Premium)' },
            { id: 'disco',     name: '🪩 Studio 54 (Premium)' },
            { id: 'matrix',    name: '🟩 The Matrix (Promo)' }
        ];

        // 3. GET OWNERSHIP
        const owned = window.OWNED_THEMES || [];

        // 4. BUILD DROPDOWN
        let html = '';

        // Group 1: Standard
        html += `<optgroup label="Standard Licenses">`;
        standardThemes.forEach(t => {
            html += `<option value="${t.id}">${t.name}</option>`;
        });
        html += `</optgroup>`;

        // Group 2: Premium
        html += `<optgroup label="Premium Licenses">`;
        premiumThemes.forEach(t => {
            if (owned.includes(t.id)) {
                // UNLOCKED
                html += `<option value="${t.id}">${t.name}</option>`;
            } else {
                // LOCKED -> REDIRECT LINK
                // Clean Name: "🔒 Hex-Hive (Premium)"
                html += `<option value="BUY_THEME">🔒 ${t.name}</option>`;
            }
        });
        html += `</optgroup>`;

        selector.innerHTML = html;

        // 5. LOAD SAVED PREFERENCE
        let savedTheme = localStorage.getItem('selectedTheme') || 'business';
        
        // Safety: If saved theme is premium but not owned, revert
        const isPremium = premiumThemes.some(p => p.id === savedTheme);
        if (isPremium && !owned.includes(savedTheme)) {
            savedTheme = 'business';
        }

        selector.value = savedTheme;
        this.applyTheme(savedTheme);

        // 6. LISTEN FOR CHANGES (The Redirect Logic)
        selector.addEventListener('change', (e) => {
            const val = e.target.value;

            // CHECK IF IT'S A 'BUY' LINK
            if (val === 'BUY_THEME') {
                // Redirect to Provisioning (Shop)
                window.location.href = '/shop';
                // Reset dropdown to previous valid theme (visuals)
                e.target.value = localStorage.getItem('selectedTheme');
                return;
            }

            // Otherwise, apply theme normally
            this.applyTheme(val);
        });
    },

    applyTheme: function(themeId) {
        localStorage.setItem('selectedTheme', themeId);
        document.documentElement.setAttribute('data-theme', themeId);

        // Routing Logic
        if (themeId === 'theme_neon') {
            this.loadScript('/static/js/synthwave.js', 'SynthwaveEngine', 'HIVE');
        } else {
            this.unloadEngine('SynthwaveEngine');
        }

        if (themeId === 'disco') {
            this.loadScript('/static/js/disco.js', 'DiscoEngine', 'DISCO');
        } else {
            this.unloadEngine('DiscoEngine');
        }

        if (themeId === 'matrix') {
            this.loadScript('/static/js/matrix.js', 'MatrixEngine', 'MATRIX');
        } else {
            this.unloadEngine('MatrixEngine');
        }
    },

    loadScript: function(path, engineName, logName) {
        if (window[engineName]) {
            window[engineName].init();
            return;
        }
        let script = document.querySelector(`script[src="${path}"]`);
        if (!script) {
            script = document.createElement('script');
            script.src = path;
            script.onload = () => {
                console.log(`✨ ${logName} ENGINE LOADED`);
                if (window[engineName]) window[engineName].init();
            };
            document.body.appendChild(script);
        } else {
            if (window[engineName]) window[engineName].init();
        }
    },

    unloadEngine: function(engineName) {
        if (window[engineName] && typeof window[engineName].stop === 'function') {
            window[engineName].stop();
        }
    }
};