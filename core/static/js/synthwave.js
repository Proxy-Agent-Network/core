/**
 * SYNTHWAVE ENGINE v2.1
 * Fixed: Explicit Global Scope Attachment
 */

// CHANGE THIS LINE: explicit window assignment
window.SynthwaveEngine = {
    canvas: null,
    ctx: null,
    animationId: null,
    
    // Physics & Config
    hexSize: window.HEX_SIZE || 35,
    hexColor: '#1a1a2e',
    pulseSpeed: window.HEX_SPEED || 0.02,
    spawnRate: window.HEX_DENSITY || 0.05,
    
    // State
    width: 0,
    height: 0,
    cols: 0,
    rows: 0,
    activeCells: [],
    
    init: function() {
        // Prevent duplicates
        if (document.getElementById('synthwave-canvas')) return;

        this.canvas = document.createElement('canvas');
        this.canvas.id = 'synthwave-canvas';
        
        Object.assign(this.canvas.style, {
            position: 'fixed',
            top: '0',
            left: '0',
            width: '100%',
            height: '100%',
            zIndex: '-1', // Behind everything
            background: 'radial-gradient(circle at 50% 50%, #16213e 0%, #0f0c29 100%)'
        });
        
        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        
        // Bind resize to this instance
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
        
        this.cols = Math.ceil(this.width / (this.hexSize * Math.sqrt(3)));
        this.rows = Math.ceil(this.height / (this.hexSize * 1.5));
    },

    start: function() {
        if (!this.animationId) this.loop();
    },

    stop: function() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        if (this.canvas) {
            this.canvas.remove();
            this.canvas = null;
        }
        if (this.resizeHandler) {
            window.removeEventListener('resize', this.resizeHandler);
        }
    },

    loop: function() {
        this.update();
        this.draw();
        this.animationId = requestAnimationFrame(() => this.loop());
    },

    update: function() {
        // Spawn pulses
        if (Math.random() < this.spawnRate) {
            this.activeCells.push({
                c: Math.floor(Math.random() * this.cols),
                r: Math.floor(Math.random() * this.rows),
                life: 1.0,
                color: Math.random() > 0.5 ? '#00ffff' : '#ff00ff'
            });
        }

        // Age pulses
        for (let i = this.activeCells.length - 1; i >= 0; i--) {
            this.activeCells[i].life -= this.pulseSpeed;
            if (this.activeCells[i].life <= 0) {
                this.activeCells.splice(i, 1);
            }
        }
    },

    draw: function() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        // Base Grid
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
        this.ctx.lineWidth = 1;
        
        for (let r = 0; r <= this.rows; r++) {
            for (let c = 0; c <= this.cols; c++) {
                this.drawHex(c, r, false);
            }
        }

        // Active Pulses
        this.ctx.shadowBlur = 15;
        this.activeCells.forEach(cell => {
            this.ctx.fillStyle = cell.color;
            this.ctx.shadowColor = cell.color;
            this.ctx.globalAlpha = cell.life;
            this.drawHex(cell.c, cell.r, true);
            this.ctx.globalAlpha = 1.0;
        });
        this.ctx.shadowBlur = 0;
    },

    drawHex: function(col, row, fill) {
        const xOffset = (row % 2) * (Math.sqrt(3) * this.hexSize / 2);
        const x = col * (Math.sqrt(3) * this.hexSize) + xOffset;
        const y = row * (this.hexSize * 1.5);

        this.ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const angle = 2 * Math.PI / 6 * i;
            const px = x + this.hexSize * Math.sin(angle);
            const py = y + this.hexSize * Math.cos(angle);
            if (i === 0) this.ctx.moveTo(px, py);
            else this.ctx.lineTo(px, py);
        }
        this.ctx.closePath();

        if (fill) this.ctx.fill();
        else this.ctx.stroke();
    }
};