import streamlit as st
import streamlit.components.v1 as components

def inject_custom_ui():
    """Jailbreaks Streamlit via a postMessage bridge to bypass CORS, inherit themes, and block native scrolling."""
    
    CUSTOM_CSS = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=Inter:wght@400;700&family=Orbitron:wght@400;700&family=Press+Start+2P&family=Special+Elite&family=Shrikhand&family=Montserrat&family=UnifrakturMaguntia&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
        
        /* THEME VARIABLES */
        :root, [data-theme="business"] { --bg: #f4f7f6; --card-bg: #ffffff; --text: #2c3e50; --accent: #2980b9; --border: #dcdde1; --font: 'Inter', sans-serif; --danger: #e74c3c; }
        [data-theme="retro"] { --bg: #2b033d; --card-bg: #4c066b; --text: #00ffff; --accent: #ff00ff; --border: #ff00ff; --font: 'Press Start 2P', cursive; --danger: #ff0000; }
        [data-theme="paperback"] { --bg: #f5e6d3; --card-bg: #fff; --text: #3b3b3b; --accent: #2c3e50; --border: #bca08d; --font: 'Special Elite', cursive; --danger: #c0392b; }
        [data-theme="cyberpunk"] { --bg: #000; --card-bg: #111; --text: #fee715; --accent: #ea00d9; --border: #fee715; --font: 'Orbitron', sans-serif; --danger: #ff003c; }
        [data-theme="deepsea"] { --bg: #001219; --card-bg: #005f73; --text: #94d2bd; --accent: #ee9b00; --border: #0a9396; --font: 'Montserrat', sans-serif; --danger: #ae2012; }
        [data-theme="vampire"] { --bg: #1a0000; --card-bg: #2a0000; --text: #8b0000; --accent: #ffd700; --border: #4a0000; --font: 'UnifrakturMaguntia', serif; --danger: #ff0000; }
        [data-theme="groovy"] { --bg: #b2ebf2; --card-bg: #ffffff; --text: #512da8; --accent: #fbc02d; --border: #ff8a65; --font: 'Shrikhand', cursive; --danger: #e64a19; }

        .stApp { background-color: transparent !important; transition: all 0.3s; }
        .stApp > header { display: none !important; }
        
        .block-container { padding-top: 1rem !important; padding-bottom: 10rem !important; }
        [data-testid="stSidebarUserContent"] { padding-top: 0.5rem !important; }
        [data-testid="stSidebarHeader"] { padding: 0 !important; }

        /* LEFT PANEL SAFE THEME INTEGRATION */
        section[data-testid="stSidebar"] { 
            background-color: var(--card-bg) !important; 
            border-right: 2px solid var(--accent) !important; 
        }
        
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span:not(.material-symbols-rounded):not([data-testid="stIconMaterial"]):not(.stIconMaterial),
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] label {
            color: var(--text) !important; font-family: var(--font) !important;
        }
        
        [data-testid="stExpander"] { background-color: var(--bg) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input { background-color: var(--bg) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
        
        /* HIGH VISIBILITY ARROWS */
        [data-testid="collapsedControl"], button[kind="header"] {
            background-color: var(--card-bg) !important; border: 2px solid var(--accent) !important; border-radius: 50% !important; color: var(--accent) !important; box-shadow: 0 0 15px var(--accent) !important; top: 1rem !important; left: 1rem !important; z-index: 999999 !important; transition: transform 0.3s ease, background-color 0.3s ease;
        }
        [data-testid="collapsedControl"] *, button[kind="header"] * { font-family: 'Material Symbols Rounded' !important; }
        [data-testid="collapsedControl"]:hover, button[kind="header"]:hover { transform: scale(1.1); background-color: var(--accent) !important; }
        [data-testid="collapsedControl"] svg, button[kind="header"] svg { fill: var(--accent) !important; color: var(--accent) !important; }
        [data-testid="collapsedControl"]:hover svg, button[kind="header"]:hover svg { fill: var(--bg) !important; color: var(--bg) !important; }
        
        .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; font-weight: normal !important;}
        .stMarkdown p, h1, h2, h3, li, div[data-testid="stMarkdownContainer"] > p { color: var(--text) !important; font-family: var(--font) !important; }
        
        /* SLEEK TABS */
        .stTabs [data-baseweb="tab-list"] { 
            background-color: transparent !important; 
            border-bottom: 2px solid rgba(128,128,128,0.3) !important; 
            padding: 0 !important; gap: 30px; display: flex; justify-content: center; 
        }
        .stTabs [data-baseweb="tab"] { 
            background: transparent !important; border: none !important; 
            padding: 12px 0 !important; 
            border-bottom: 3px solid transparent !important; margin-bottom: -3px; 
        }
        .stTabs [data-baseweb="tab"] p {
            color: var(--text) !important; font-family: var(--font) !important; 
            font-weight: 800 !important; text-transform: uppercase; 
            font-size: 1.1rem !important; opacity: 0.6; 
            text-shadow: 1px 1px 3px rgba(0,0,0,0.9); 
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover p { opacity: 1; color: var(--accent) !important; }
        .stTabs [aria-selected="true"] p { color: var(--accent) !important; opacity: 1; text-shadow: 0px 0px 12px var(--accent), 1px 1px 3px rgba(0,0,0,0.9); }
        .stTabs [aria-selected="true"] { border-bottom: 3px solid var(--accent) !important; }
        
        /* 🌟 RETRO ARCADE FONT OVERRIDES 🌟 */
        [data-theme="retro"] .stTabs [data-baseweb="tab"] p { font-size: 0.65rem !important; }
        [data-theme="retro"] section[data-testid="stSidebar"] h2 { font-size: 0.9rem !important; }
        [data-theme="retro"] section[data-testid="stSidebar"] h1 { font-size: 1rem !important; }
        [data-theme="retro"] [data-testid="stExpander"] summary p { font-size: 0.75rem !important; }
        
        /* MAIN BODY ELEMENTS */
        .stButton > button { background-color: var(--card-bg) !important; color: var(--text) !important; border: 1px solid var(--accent) !important; font-family: var(--font) !important; border-radius: 4px; transition: all 0.2s; text-transform: uppercase; font-weight: bold;}
        .stButton > button:hover { background-color: var(--accent) !important; color: var(--bg) !important; box-shadow: 0 0 15px var(--accent); }
        div[data-testid="stChatMessage"] { background-color: var(--card-bg) !important; border: 1px solid var(--border) !important; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
        .stChatInputContainer { background-color: var(--card-bg) !important; border: 1px solid var(--border) !important; }
        hr { border-color: var(--border) !important; }
        .stProgress > div > div > div > div { background-color: var(--accent) !important; }

        /* MARVIN CHOREOGRAPHY */
        .marvin-tutorial {
            position: fixed; right: 40px; z-index: 99999; display: flex; align-items: flex-end; 
            bottom: -250px; opacity: 0; pointer-events: none;
            animation: marvinSequence 8s cubic-bezier(0.25, 1, 0.5, 1) forwards 2s;
        }
        .marvin-tutorial.active { pointer-events: auto; }
        .marvin-tutorial img { width: 180px; cursor: pointer; pointer-events: auto; animation: marvinSmoke 8s ease-in-out forwards 2s; }
        .speech-bubble {
            background: var(--card-bg); color: var(--text); border: 2px solid var(--accent); padding: 15px; border-radius: 12px; font-family: var(--font); font-size: 0.9rem; max-width: 250px; margin-right: 15px; margin-bottom: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); position: relative;
        }
        .speech-bubble:after { content: ''; position: absolute; right: -12px; top: 50%; border-width: 10px 0 10px 12px; border-style: solid; border-color: transparent transparent transparent var(--accent); transform: translateY(-50%); }
        
        @keyframes marvinSequence { 0% { bottom: -250px; opacity: 0; } 15% { bottom: 30px; opacity: 1; } 85% { bottom: 30px; opacity: 1; } 100% { bottom: -250px; opacity: 0; } }
        @keyframes marvinSmoke { 0% { filter: drop-shadow(0 0 0 transparent); } 10% { filter: drop-shadow(0 0 50px #8e44ad); } 20% { filter: drop-shadow(0 0 15px var(--accent)); } 80% { filter: drop-shadow(0 0 15px var(--accent)); } 90% { filter: drop-shadow(0 0 50px #8e44ad); } 100% { filter: drop-shadow(0 0 0 transparent); } }
        
        .laughing-anim { animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both !important; }
        @keyframes shake { 10%, 90% { transform: translate3d(-2px, 0, 0); } 20%, 80% { transform: translate3d(4px, 0, 0); } 30%, 50%, 70% { transform: translate3d(-6px, 0, 0); } 40%, 60% { transform: translate3d(6px, 0, 0); } }
    </style>
    """
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # INJECT MARVIN (AUDIO NATIVELY INSIDE IFRAME NOW)
    MARVIN_HTML = """
    <div class="marvin-tutorial" id="marvin-tutor-container">
        <div class="speech-bubble">
            <strong id="marvin-greeting">Welcome to Command!</strong><br><br>
            <span id="marvin-desc">Use the Tabs below to switch between the Roster, Breakroom, and Immigration Office.</span>
        </div>
        <audio id="marvin-audio" preload="auto"></audio>
        <img id="marvin-img" src="" alt="Marvin" ondblclick="window.parent.playLocalMarvinAudio()"/>
    </div>
    """
    st.markdown(MARVIN_HTML, unsafe_allow_html=True)

    # THE POST-MESSAGE RECEIVER
    JS_BRIDGE = """
    <script>
        const streamlitWin = window.parent;
        const streamlitDoc = streamlitWin.document;

        // Audio Engine
        streamlitWin.playLocalMarvinAudio = function() {
            const audio = streamlitDoc.getElementById('marvin-audio');
            if(audio) {
                audio.currentTime = 0;
                audio.volume = 1.0;
                audio.play().catch(e => console.log('Audio error:', e));
            }
            const img = streamlitDoc.getElementById('marvin-img');
            if(img) {
                img.classList.add('laughing-anim');
                setTimeout(() => img.classList.remove('laughing-anim'), 1000);
            }
        };

        // PREVENT TAB AUTO-SCROLL JUMPING
        streamlitDoc.addEventListener('click', function(e) {
            if(e.target.closest('[data-baseweb="tab"]')) {
                try {
                    const flaskWin = streamlitWin.parent;
                    const scrollPos = flaskWin.scrollY;
                    const lockScroll = setInterval(() => flaskWin.scrollTo(0, scrollPos), 5);
                    setTimeout(() => clearInterval(lockScroll), 150);
                } catch(err) {} 
            }
        }, true);

        // SECURE MESSAGE LISTENER
        streamlitWin.addEventListener('message', (event) => {
            const data = event.data;
            if (!data || !data.theme) return;

            if (streamlitDoc.documentElement.getAttribute('data-theme') !== data.theme) {
                streamlitDoc.documentElement.setAttribute('data-theme', data.theme);
            }

            const marvinContainer = streamlitDoc.getElementById('marvin-tutor-container');
            if (marvinContainer) {
                marvinContainer.style.display = (data.theme === 'business' || data.theme === 'paperback') ? 'none' : 'flex';
            }

            const img = streamlitDoc.getElementById('marvin-img');
            if (img && !img.src.includes('magic_marvin_dance.webp')) {
                img.src = data.origin + '/static/images/magic_marvin_dance.webp';
            }
            const audio = streamlitDoc.getElementById('marvin-audio');
            if (audio && !audio.src.includes('marvin_laughing.mp3')) {
                audio.src = data.origin + '/static/audio/marvin_laughing.mp3';
            }

            const RATES = { SATS: 1, BTC: 0.00000001, USD: 0.00065, CAD: 0.00088, CNY: 0.0047, TWD: 0.021, EUR: 0.00060, GBP: 0.00051, JPY: 0.1, MXN: 0.012, KRW: 0.90, AUD: 0.0010 };
            const rate = RATES[data.currency] || 1;
            const rawDataNode = streamlitDoc.getElementById('raw-dashboard-data');
            
            if (rawDataNode) {
                const rem = parseInt(rawDataNode.getAttribute('data-budget') || 0) - parseInt(rawDataNode.getAttribute('data-spent') || 0);
                const metricVals = streamlitDoc.querySelectorAll('[data-testid="stMetricValue"] div');
                if (metricVals.length > 0) {
                    let displayVal = rem * rate;
                    if (data.currency === 'SATS') metricVals[0].innerText = Math.floor(displayVal).toLocaleString() + " SATS";
                    else if (data.currency === 'BTC') metricVals[0].innerText = displayVal.toFixed(8) + " BTC";
                    else metricVals[0].innerText = displayVal.toLocaleString(data.language, {style: 'currency', currency: data.currency});
                }
            }

            const tDict = data.translations;
            if (tDict && tDict[data.language]) {
                const dict = tDict[data.language];
                const tabs = streamlitDoc.querySelectorAll('.stTabs [data-baseweb="tab"] p');
                tabs.forEach(t => {
                    const txt = t.innerText;
                    if (txt.includes('Terminal') || txt.includes('Command') || txt.includes('指挥') || txt.includes('コマ')) t.innerText = '💬 ' + (dict.nav_command || 'Terminal');
                    if (txt.includes('Roster') || txt.includes('Global') || txt.includes('排名') || txt.includes('ラン')) t.innerText = '📈 ' + (dict.panel_global || 'Roster');
                    if (txt.includes('Breakroom') || txt.includes('Rival') || txt.includes('对手') || txt.includes('休憩')) t.innerText = '☕ ' + (dict.panel_rivals || 'Breakroom');
                    if (txt.includes('Immigration') || txt.includes('Catalog') || txt.includes('目录') || txt.includes('入国')) t.innerText = '🛂 ' + (dict.panel_catalog || 'Immigration');
                });
                
                const mGrt = streamlitDoc.getElementById('marvin-greeting');
                const mDesc = streamlitDoc.getElementById('marvin-desc');
                if(mGrt && mDesc) {
                    if (data.language === 'zh-CN') { mGrt.innerText = "欢迎来到指挥中心！"; mDesc.innerText = "使用下方的标签在名册、休息室和移民办公室之间切换。"; } 
                    else if (data.language === 'es') { mGrt.innerText = "¡Bienvenido al Comando!"; mDesc.innerText = "Usa las pestañas de abajo para cambiar entre la Lista, la Sala de Descanso y la Oficina de Inmigración."; } 
                    else if (data.language === 'ja') { mGrt.innerText = "コマンドへようこそ！"; mDesc.innerText = "下のタブを使用して、名簿、休憩室、入国管理局を切り替えます。"; } 
                    else { mGrt.innerText = "Welcome to Command!"; mDesc.innerText = "Use the Tabs below to switch between the Roster, Breakroom, and Immigration Office."; }
                }
            }
        });
    </script>
    """
    components.html(JS_BRIDGE, height=0, width=0)