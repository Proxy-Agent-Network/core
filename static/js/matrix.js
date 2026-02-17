/**
 * MATRIX ENGINE v1.0
 * "Digital Rain" Generator
 */
window.MatrixEngine = {
    canvas: null,
    ctx: null,
    animationId: null,
    
    // Config
    fontSize: 16,
    drops: [], // Array to track the y-coordinate of each column
    
    // Characters (Katakana + Latin)
    chars: 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    
    init: function() {
        if (document.getElementById('matrix-canvas')) return;

        // 1. Setup Canvas
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'matrix-canvas';
        Object.assign(this.canvas.style, {
            position: 'fixed', top: '0', left: '0', width: '100%', height: '100%',
            zIndex: '-1', background: '#000'
        });
        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        
        // 2. Listeners
        this.resizeHandler = () => this.resize();
        window.addEventListener('resize', this.resizeHandler);
        
        this.resize();
        this.start();
    },

    resize: function() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        
        const columns = this.width / this.fontSize;
        this.drops = [];
        // Initialize all drops at random y positions for organic start
        for (let x = 0; x < columns; x++) {
            this.drops[x] = Math.random() * -100; // Start above screen
        }
    },

    start: function() { if (!this.animationId) this.loop(); },

    stop: function() {
        if (this.animationId) { cancelAnimationFrame(this.animationId); this.animationId = null; }
        if (this.canvas) { this.canvas.remove(); this.canvas = null; }
        if (this.resizeHandler) window.removeEventListener('resize', this.resizeHandler);
    },

    loop: function() {
        // 30FPS is plenty for the matrix effect (looks more cinematic than 60)
        if (Date.now() % 2 === 0) { 
             this.draw();
        }
        this.animationId = requestAnimationFrame(() => this.loop());
    },

    draw: function() {
        // Semi-transparent black fill to create "trail" effect
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        this.ctx.fillStyle = '#0F0'; // Matrix Green
        this.ctx.font = this.fontSize + 'px monospace';
        
        for (let i = 0; i < this.drops.length; i++) {
            // Random character
            const text = this.chars.charAt(Math.floor(Math.random() * this.chars.length));
            
            // Draw
            this.ctx.fillText(text, i * this.fontSize, this.drops[i] * this.fontSize);
            
            // Send drop back to top randomly after it crosses screen
            if (this.drops[i] * this.fontSize > this.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            
            // Increment y coordinate
            this.drops[i]++;
        }
    }
};