import { Component, OnInit, AfterViewInit, inject, HostListener, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router'; // Added Router import
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { trigger, style, animate, transition } from '@angular/animations';

@Component({
  selector: 'app-contact',
  imports: [CommonModule, RouterModule, MatSnackBarModule],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.css',
  animations: [
    trigger('fadeInUp', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(20px)' }),
        animate('0.6s ease-out', style({ opacity: 1, transform: 'translateY(0)' }))
      ])
    ]),
    trigger('floatAnimation', [
      transition(':enter', [
        style({ transform: 'translateY(0)' }),
        animate('3s ease-in-out infinite', 
          style({ transform: 'translateY(-10px)' }))
      ])
    ]),
    trigger('bounceIn', [
      transition(':enter', [
        style({ transform: 'scale(0.3)', opacity: 0 }),
        animate('0.5s cubic-bezier(0.34, 1.56, 0.64, 1)', 
          style({ transform: 'scale(1)', opacity: 1 }))
      ])
    ]),
    trigger('pulse', [
      transition(':enter', [
        animate('1s ease-in-out infinite', 
          style({ transform: 'scale(1.05)' }))
      ])
    ])
  ]
})
export class ContactComponent implements OnInit, AfterViewInit, OnDestroy {
  private snackBar = inject(MatSnackBar);
  private router = inject(Router); // Inject Router
  private clickCount = 0;
  private floatingCart: HTMLElement | null = null;
  private particles: HTMLElement[] = [];
  private observer: IntersectionObserver | null = null;
  
  // Stats data for Tail Cart
  stats = [
    { value: '2M+', label: 'Happy Shoppers', color: 'primary' },
    { value: '50K+', label: 'Products', color: 'accent' },
    { value: '99.9%', label: 'Uptime', color: 'success' },
    { value: '4.9★', label: 'App Rating', color: 'warning' }
  ];
  
  // Features data for Tail Cart
  features = [
    { 
      icon: 'fa-bolt', 
      title: 'Lightning Fast', 
      description: 'Checkout in seconds, not minutes. Because your time matters.',
      color: 'primary' 
    },
    { 
      icon: 'fa-robot', 
      title: 'Smart Suggestions', 
      description: 'AI-powered recommendations that actually get you.',
      color: 'accent' 
    },
    { 
      icon: 'fa-shield-alt', 
      title: 'Secure & Safe', 
      description: 'Bank-level encryption keeps your shopping worry-free.',
      color: 'success' 
    },
    { 
      icon: 'fa-heart', 
      title: 'Save Favorites', 
      description: 'Wishlist everything. Buy when you\'re ready.',
      color: 'info' 
    }
  ];

  // Process steps
  processSteps = [
    { 
      number: 1, 
      title: 'Add to Cart', 
      description: 'Browse products and add them to your smart cart that follows you across devices',
      color: 'primary'
    },
    { 
      number: 2, 
      title: 'Smart Suggestions', 
      description: 'Get personalized recommendations based on your shopping behavior',
      color: 'accent'
    },
    { 
      number: 3, 
      title: 'Secure Checkout', 
      description: 'Complete your purchase with bank-level security in just seconds',
      color: 'success'
    }
  ];

  // Testimonials
  testimonials = [
    {
      name: 'Sarah M.',
      role: 'Frequent Shopper',
      rating: 5,
      content: 'Tail Cart made shopping so much easier! The AI suggestions are spot on.',
      avatarColor: 'primary'
    },
    {
      name: 'James L.',
      role: 'Tech Enthusiast',
      rating: 4.5,
      content: 'The checkout is lightning fast. I save so much time shopping now!',
      avatarColor: 'accent'
    },
    {
      name: 'Maria G.',
      role: 'Online Shopper',
      rating: 5,
      content: 'My cart follows me everywhere. No more losing items between devices!',
      avatarColor: 'success'
    }
  ];

  ngOnInit(): void {
    this.initFloatingCart();
  }

  ngAfterViewInit(): void {
    this.initScrollAnimations();
    this.initStatsCounter();
  }

  ngOnDestroy(): void {
    // Clean up
    this.cleanupFloatingCart();
    this.cleanupParticles();
    if (this.observer) {
      this.observer.disconnect();
    }
  }

  @HostListener('document:mousemove', ['$event'])
  onMouseMove(event: MouseEvent): void {
    if (this.floatingCart) {
      this.floatingCart.style.left = (event.clientX + 20) + 'px';
      this.floatingCart.style.top = (event.clientY + 20) + 'px';
    }
  }

  private initFloatingCart(): void {
    // Create floating cart element
    this.floatingCart = document.createElement('div');
    this.floatingCart.className = 'floating-cart-follow';
    this.floatingCart.style.cssText = `
      position: fixed;
      width: 60px;
      height: 60px;
      background: linear-gradient(135deg, #6366f1, #8b5cf6);
      border-radius: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 24px;
      z-index: 999;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.3s ease;
      box-shadow: 0 10px 25px rgba(99, 102, 241, 0.3);
    `;

    const cartIcon = document.createElement('i');
    cartIcon.className = 'fas fa-shopping-cart';
    this.floatingCart.appendChild(cartIcon);
    document.body.appendChild(this.floatingCart);

    // Show cart after a delay
    setTimeout(() => {
      if (this.floatingCart) {
        this.floatingCart.style.opacity = '1';
      }
    }, 1000);
  }

  private cleanupFloatingCart(): void {
    if (this.floatingCart && this.floatingCart.parentNode) {
      this.floatingCart.parentNode.removeChild(this.floatingCart);
    }
  }

  private cleanupParticles(): void {
    this.particles.forEach(particle => {
      if (particle && particle.parentNode) {
        particle.parentNode.removeChild(particle);
      }
    });
    this.particles = [];
  }

  private initScrollAnimations(): void {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          
          // Add specific animation for stat cards
          if (entry.target.classList.contains('stat-card')) {
            entry.target.classList.add('animate-stat');
          }
        }
      });
    }, { threshold: 0.1 });

    // Observe all animate-on-scroll elements
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
      if (this.observer) {
        this.observer.observe(el);
      }
    });
  }

  private initStatsCounter(): void {
    // Initialize stats counter animation
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach((stat, index) => {
      // Add animation delay based on index
      (stat as HTMLElement).style.animationDelay = `${index * 0.1}s`;
    });
  }

  private createParticles(x: number, y: number): void {
    for (let i = 0; i < 8; i++) {
      const particle = document.createElement('div');
      particle.style.cssText = `
        position: fixed;
        width: 10px;
        height: 10px;
        background: ${i % 2 === 0 ? '#f97316' : '#6366f1'};
        border-radius: 50%;
        left: ${x}px;
        top: ${y}px;
        z-index: 1000;
        pointer-events: none;
        transform: translate(0, 0);
        opacity: 1;
      `;
      
      const angle = Math.random() * Math.PI * 2;
      const distance = 30 + Math.random() * 40;
      const tx = Math.cos(angle) * distance;
      const ty = Math.sin(angle) * distance;
      
      document.body.appendChild(particle);
      this.particles.push(particle);
      
      // Animate particle
      setTimeout(() => {
        particle.style.transform = `translate(${tx}px, ${ty}px) scale(0)`;
        particle.style.opacity = '0';
        particle.style.transition = 'all 0.6s ease';
      }, 10);
      
      // Remove particle after animation
      setTimeout(() => {
        if (particle.parentNode) {
          particle.parentNode.removeChild(particle);
          this.particles = this.particles.filter(p => p !== particle);
        }
      }, 700);
    }
  }

  private showSnackBar(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
    const config = {
      duration: 3000,
      horizontalPosition: 'right' as const,
      verticalPosition: 'top' as const,
      panelClass: [`snackbar-${type}`]
    };
    
    this.snackBar.open(message, 'Close', config);
  }

  // Method to handle Start Shopping button clicks
  onStartShoppingClick(event: MouseEvent): void {
    this.clickCount++;
    
    // Create particle effects
    this.createParticles(event.clientX, event.clientY);

    // Make cart bounce
    if (this.floatingCart) {
      this.floatingCart.style.animation = 'none';
      setTimeout(() => {
        this.floatingCart!.style.animation = 'bounce 0.5s ease';
      }, 10);
      setTimeout(() => {
        this.floatingCart!.style.animation = '';
      }, 500);
    }

    // Show different messages based on click count
    let message = 'Starting your shopping journey...';
    if (this.clickCount === 3) {
      message = 'Wow! You love clicking! Shopping cart is excited!';
    } else if (this.clickCount === 5) {
      message = 'Your cart is getting full of excitement!';
    } else if (this.clickCount >= 10) {
      message = 'You\'re a shopping pro!';
    }

    this.showSnackBar(message, 'info');
    
    // Redirect to shop page after a short delay to show animation
    setTimeout(() => {
      // Update '/shop' to your actual shop route path
      this.router.navigate(['/shop']);
    }, 800); // 800ms delay to allow animations to complete
  }

  // Method to handle Watch Demo button clicks
  onWatchDemoClick(): void {
    this.showSnackBar('Playing demo video...', 'info');
  }

  // Method to handle feature card clicks
  onFeatureClick(feature: any): void {
    this.showSnackBar(`Learn more about ${feature.title}`, 'info');
    
    // Add visual feedback
    if (this.floatingCart) {
      this.floatingCart.style.animation = 'none';
      setTimeout(() => {
        this.floatingCart!.style.animation = 'pulse 0.3s ease';
      }, 10);
      setTimeout(() => {
        this.floatingCart!.style.animation = '';
      }, 300);
    }
  }

  // Method to handle stat card clicks
  onStatClick(stat: any): void {
    this.showSnackBar(`${stat.value} ${stat.label} and counting!`, 'success');
  }

  // Method to handle testimonial card clicks
  onTestimonialClick(testimonial: any): void {
    this.showSnackBar(`Read ${testimonial.name}'s full review`, 'info');
  }

  // Method to handle process step clicks
  onProcessStepClick(step: any): void {
    this.showSnackBar(`Step ${step.number}: ${step.title}`, 'info');
  }

  // Utility method to generate star rating HTML
  getStarRating(rating: number): string {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    let stars = '';
    
    for (let i = 0; i < fullStars; i++) {
      stars += '<i class="fas fa-star"></i>';
    }
    
    if (hasHalfStar) {
      stars += '<i class="fas fa-star-half-alt"></i>';
    }
    
    return stars;
  }

  // Method to handle shop now CTA - Alternative method that also redirects
  onShopNowClick(): void {
    this.showSnackBar('Redirecting to shop...', 'success');
    
    // Add cart animation
    if (this.floatingCart) {
      this.floatingCart.style.animation = 'none';
      setTimeout(() => {
        this.floatingCart!.style.animation = 'float 1s ease-in-out';
      }, 10);
      setTimeout(() => {
        this.floatingCart!.style.animation = '';
      }, 1000);
    }
    
    // Redirect to shop page
    setTimeout(() => {
      this.router.navigate(['/shop']);
    }, 1000);
  }
}