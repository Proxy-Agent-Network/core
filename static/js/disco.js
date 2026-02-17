/**
 * DISCO ENGINE v3.0 (Web Audio Synth)
 * Features:
 * - "Stayin' Alive" Floor Animation
 * - Built-in Web Audio Synthesizer (No MP3 required)
 * - Secret Cheat Code ('dance') & DJ Booth
 */

window.DiscoEngine = {
    canvas: null, ctx: null, animationId: null,
    
    // Config
    tileSize: 80,
    colors: ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff', '#ffffff'],
    bpm: 104,
    
    // Audio State
    audioCtx: null,
    isPlaying: false,
    nextNoteTime: 0.0,
    beatCount: 0,
    timerID: null,
    
    // Secret State
    keySequence: [],
    secretCode: 'dance',
    
    init: function() {
        if (document.getElementById('disco-canvas')) return;

        // 1. Setup Canvas
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'disco-canvas';
        Object.assign(this.canvas.style, {
            position: 'fixed', top: '0', left: '0', width: '100%', height: '100%',
            zIndex: '-1', background: '#000'
        });
        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        
        // 2. Setup Listeners
        this.resizeHandler = () => this.resize();
        window.addEventListener('resize', this.resizeHandler);
        
        this.keyHandler = (e) => this.checkCode(e);
        window.addEventListener('keydown', this.keyHandler);

        // DJ Booth (Triple Click H1)
        const header = document.querySelector('h1');
        if (header) {
            this.clickHandler = (e) => {
                if (e.detail === 3) { e.preventDefault(); this.toggleMusic(); }
            };
            header.addEventListener('click', this.clickHandler);
            header.title = "Triple-click for a good time 🕺";
        }
        
        this.resize();
        this.start();
    },

    // --- VISUALS ---
    resize: function() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        this.cols = Math.ceil(this.width / this.tileSize);
        this.rows = Math.ceil(this.height / this.tileSize);
        this.grid = [];
        for(let r=0; r<this.rows; r++) {
            for(let c=0; c<this.cols; c++) {
                this.grid.push({c, r, color: this.pickColor(), intensity: Math.random()});
            }
        }
    },
    pickColor: function() { return this.colors[Math.floor(Math.random() * this.colors.length)]; },
    start: function() { if (!this.animationId) this.loop(); },
    stop: function() {
        if (this.animationId) { cancelAnimationFrame(this.animationId); this.animationId = null; }
        if (this.canvas) { this.canvas.remove(); this.canvas = null; }
        this.stopMusic();
        if (this.resizeHandler) window.removeEventListener('resize', this.resizeHandler);
        if (this.keyHandler) window.removeEventListener('keydown', this.keyHandler);
        const header = document.querySelector('h1');
        if (header && this.clickHandler) header.removeEventListener('click', this.clickHandler);
    },
    loop: function() {
        if (Date.now() % 4 === 0) { this.update(); this.draw(); }
        this.animationId = requestAnimationFrame(() => this.loop());
    },
    update: function() {
        for(let i=0; i<this.grid.length; i++) {
            if(Math.random() < 0.05) {
                this.grid[i].color = this.pickColor();
                this.grid[i].intensity = 0.4 + (Math.random() * 0.6);
            }
        }
    },
    draw: function() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        this.grid.forEach(tile => {
            this.ctx.fillStyle = tile.color;
            this.ctx.globalAlpha = tile.intensity * 0.6;
            this.ctx.fillRect(tile.c * this.tileSize, tile.r * this.tileSize, this.tileSize - 4, this.tileSize - 4);
        });
        // Grout
        this.ctx.globalAlpha = 1.0; this.ctx.strokeStyle = '#111'; this.ctx.lineWidth = 4;
        this.ctx.beginPath();
        for(let x=0; x<=this.width; x+=this.tileSize) { this.ctx.moveTo(x,0); this.ctx.lineTo(x,this.height); }
        for(let y=0; y<=this.height; y+=this.tileSize) { this.ctx.moveTo(0,y); this.ctx.lineTo(this.width,y); }
        this.ctx.stroke();
    },

    // --- AUDIO SYNTH ENGINE ---
    initAudio: function() {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.audioCtx = new AudioContext();
    },

    toggleMusic: function() {
        if (!this.audioCtx) this.initAudio();
        
        // Resume context if suspended (browser policy)
        if (this.audioCtx.state === 'suspended') this.audioCtx.resume();

        if (this.isPlaying) {
            this.stopMusic();
            this.showToast("🤫 Party's Over");
        } else {
            this.isPlaying = true;
            this.nextNoteTime = this.audioCtx.currentTime;
            this.beatCount = 0;
            this.scheduler();
            this.showToast("🎵 WEB SYNTH: ACTIVATED");
            // Flash Floor
            this.colors = ['#ffffff', '#ff00ff', '#00ffff'];
            setTimeout(() => this.colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff', '#ffffff'], 1000);
        }
    },

    stopMusic: function() {
        this.isPlaying = false;
        window.clearTimeout(this.timerID);
    },

    scheduler: function() {
        // While there are notes that will need to play before the next interval, schedule them
        const lookahead = 25.0; // ms
        const scheduleAheadTime = 0.1; // sec
        
        while (this.nextNoteTime < this.audioCtx.currentTime + scheduleAheadTime) {
            this.playBeat(this.nextNoteTime, this.beatCount);
            
            // Advance time (16th notes)
            const secondsPerBeat = 60.0 / this.bpm;
            this.nextNoteTime += 0.25 * secondsPerBeat; // 16th note
            this.beatCount++;
        }
        
        if (this.isPlaying) {
            this.timerID = window.setTimeout(() => this.scheduler(), lookahead);
        }
    },

    playBeat: function(time, beatIndex) {
        // 16th note loop (0-15)
        const step = beatIndex % 16;
        
        // --- DRUMS ---
        // Kick: 1, 5, 9, 13 (4-on-the-floor)
        if (step % 4 === 0) this.synthKick(time);
        
        // HiHat: Every odd 16th note (off-beats)
        if (step % 2 !== 0) this.synthHat(time);
        
        // Snare: 5, 13 (Backbeat)
        if (step === 4 || step === 12) this.synthSnare(time);

        // --- BASSLINE (F Minor Riff) ---
        // Pattern: F(1), Eb(4), F(7), Ab(11), F(14)
        const root = 87.31; // F2
        const flat7 = 77.78; // Eb2
        const min3 = 103.83; // Ab2
        
        if (step === 0) this.synthBass(time, root);
        if (step === 3) this.synthBass(time, flat7);
        if (step === 6) this.synthBass(time, root);
        if (step === 10) this.synthBass(time, min3);
        if (step === 14) this.synthBass(time, root);
    },

    // --- SYNTH INSTRUMENTS ---
    synthKick: function(time) {
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        
        osc.frequency.setValueAtTime(150, time);
        osc.frequency.exponentialRampToValueAtTime(0.01, time + 0.5);
        gain.gain.setValueAtTime(1, time);
        gain.gain.exponentialRampToValueAtTime(0.01, time + 0.5);
        
        osc.start(time);
        osc.stop(time + 0.5);
    },

    synthSnare: function(time) {
        // Noise Buffer
        const bufferSize = this.audioCtx.sampleRate * 0.2; // 200ms
        const buffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;

        const noise = this.audioCtx.createBufferSource();
        noise.buffer = buffer;
        
        const filter = this.audioCtx.createBiquadFilter();
        filter.type = 'highpass';
        filter.frequency.value = 1000;
        
        const gain = this.audioCtx.createGain();
        gain.gain.setValueAtTime(0.5, time);
        gain.gain.exponentialRampToValueAtTime(0.01, time + 0.2);
        
        noise.connect(filter);
        filter.connect(gain);
        gain.connect(this.audioCtx.destination);
        noise.start(time);
    },

    synthHat: function(time) {
        const bufferSize = this.audioCtx.sampleRate * 0.05; // 50ms
        const buffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;

        const noise = this.audioCtx.createBufferSource();
        noise.buffer = buffer;
        
        const filter = this.audioCtx.createBiquadFilter();
        filter.type = 'highpass';
        filter.frequency.value = 5000;
        
        const gain = this.audioCtx.createGain();
        gain.gain.setValueAtTime(0.3, time);
        gain.gain.exponentialRampToValueAtTime(0.01, time + 0.05);
        
        noise.connect(filter);
        filter.connect(gain);
        gain.connect(this.audioCtx.destination);
        noise.start(time);
    },

    synthBass: function(time, freq) {
        const osc = this.audioCtx.createOscillator();
        osc.type = 'sawtooth'; // Funky!
        osc.frequency.setValueAtTime(freq, time);
        
        const filter = this.audioCtx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(800, time); // Wah effect start
        filter.frequency.exponentialRampToValueAtTime(100, time + 0.2); // Wah effect end
        
        const gain = this.audioCtx.createGain();
        gain.gain.setValueAtTime(0.5, time);
        gain.gain.exponentialRampToValueAtTime(0.01, time + 0.4);
        
        osc.connect(filter);
        filter.connect(gain);
        gain.connect(this.audioCtx.destination);
        
        osc.start(time);
        osc.stop(time + 0.4);
    },

    // --- UTILS ---
    checkCode: function(e) {
        this.keySequence.push(e.key.toLowerCase());
        if (this.keySequence.length > this.secretCode.length) this.keySequence.shift();
        if (this.keySequence.join('') === this.secretCode) this.toggleMusic();
    },

    showToast: function(msg) {
        let toast = document.createElement('div');
        toast.innerText = msg;
        Object.assign(toast.style, {
            position: 'fixed', bottom: '20px', right: '20px',
            background: '#ff00ff', color: '#fff', padding: '15px 25px',
            borderRadius: '50px', fontWeight: 'bold', boxShadow: '0 0 20px #ff00ff',
            zIndex: '9999', fontFamily: 'Montserrat, sans-serif', fontSize: '1.2rem',
            animation: 'popIn 0.3s ease-out'
        });
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }
};