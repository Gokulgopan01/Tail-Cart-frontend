import { AfterViewInit, Component, ElementRef, ViewChild, OnDestroy, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.css']
})
export class ContactComponent implements AfterViewInit, OnDestroy {
  @ViewChild('particleCanvas') canvasRef!: ElementRef<HTMLCanvasElement>;

  private ctx!: CanvasRenderingContext2D | null;
  private particles: Particle[] = [];
  private mouseX = 0;
  private mouseY = 0;
  private animationFrameId: number | null = null;
  private clickCount = 0;

  ngAfterViewInit(): void {
    this.initCanvas();
    this.createParticles();
    this.setupEventListeners();
    this.animate();
    this.initClickCounter();
  }

  private initCanvas(): void {
    const canvas = this.canvasRef.nativeElement;
    this.ctx = canvas.getContext('2d', { alpha: true });

    if (!this.ctx) {
      console.error('Failed to get canvas context');
      return;
    }

    this.resizeCanvas();
  }

  private resizeCanvas(): void {
    const canvas = this.canvasRef.nativeElement;
    const container = canvas.parentElement;

    if (container) {
      canvas.width = container.clientWidth;
      canvas.height = container.clientHeight;
    }
  }

  private setupEventListeners(): void {
    const canvas = this.canvasRef.nativeElement;
    canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
    canvas.addEventListener('mouseleave', () => this.mouseX = this.mouseY = -1000);
  }

  @HostListener('window:resize')
  handleResize(): void {
    this.resizeCanvas();
    this.createParticles();
  }

  private handleMouseMove(e: MouseEvent): void {
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    this.mouseX = e.clientX - rect.left;
    this.mouseY = e.clientY - rect.top;
  }

  private createParticles(): void {
    const canvas = this.canvasRef.nativeElement;
    const particleCount = Math.floor((canvas.width * canvas.height) / 6000);

    this.particles = [];

    for (let i = 0; i < particleCount; i++) {
      this.particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.8,
        vy: (Math.random() - 0.5) * 0.8,
        size: Math.random() * 3 + 1,
        color: this.getRandomColor(),
        opacity: Math.random() * 0.4 + 0.1,
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: 0.02 + Math.random() * 0.03
      });
    }
  }

  private getRandomColor(): string {
    const colors = ['#00a68c', '#006d5b', '#c9a14a'];
    return colors[Math.floor(Math.random() * colors.length)];
  }

  private animate(): void {
    const canvas = this.canvasRef.nativeElement;
    const ctx = this.ctx;
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    this.particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;

      // Wrap around screen
      if (p.x > canvas.width) p.x = 0;
      if (p.x < 0) p.x = canvas.width;
      if (p.y > canvas.height) p.y = 0;
      if (p.y < 0) p.y = canvas.height;

      // Draw particle
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = 0.4;
      ctx.fill();
    });

    this.animationFrameId = requestAnimationFrame(() => this.animate());
  }

  private hexToRgb(hex: string): string {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ?
      `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` :
      '0, 166, 140';
  }

  private initClickCounter(): void {
    const button = document.getElementById('startShoppingBtn');
    const counter = document.getElementById('clickCounter');
    const countSpan = document.getElementById('clickCount');

    if (button && counter && countSpan) {
      button.addEventListener('click', () => {
        this.clickCount++;
        countSpan.textContent = this.clickCount.toString();
        counter.style.display = 'block';

        // Add ripple effect
        this.createRipple(button);

        // Hide after 3 seconds
        setTimeout(() => {
          if (this.clickCount === 0) {
            counter.style.display = 'none';
          }
        }, 3000);
      });
    }
  }

  private createRipple(element: HTMLElement): void {
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    element.appendChild(ripple);

    setTimeout(() => {
      ripple.remove();
    }, 1000);
  }

  ngOnDestroy(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }
}

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  color: string;
  opacity: number;
  pulse: number;
  pulseSpeed: number;
}