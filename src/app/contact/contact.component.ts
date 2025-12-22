import { Component, OnInit, AfterViewInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
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
    ])
  ]
})
export class ContactComponent implements OnInit, AfterViewInit {
  private snackBar = inject(MatSnackBar);
  
  // Stats data
  stats = [
    { value: '500+', label: 'Pets Protected', color: 'primary' },
    { value: '99%', label: 'Recovery Rate', color: 'success' },
    { value: '24/7', label: 'AI Support', color: 'warning' },
    { value: '50+', label: 'Design Options', color: 'info' }
  ];
  
  services = [
    { icon: 'fa-qrcode', title: 'Smart QR Keychains', description: 'QR-enabled keychains and belts for instant pet identification' },
    { icon: 'fa-bell', title: 'Instant Alerts', description: 'Quick notifications when your lost pet is found and scanned' },
    { icon: 'fa-syringe', title: 'Health Records', description: 'Secure vaccination and medical history storage' },
    { icon: 'fa-robot', title: 'AI Vet Assistant', description: '24/7 AI-generated veterinary guidance and support' }
  ];
  
  features = [
    { icon: 'fa-bolt', title: 'Instant Recovery System', description: 'Our QR technology ensures quick pet recovery with immediate alerts to owners', color: 'success' },
    { icon: 'fa-tags', title: 'Affordable Protection', description: 'Premium pet safety solutions at prices every pet owner can afford', color: 'warning' },
    { icon: 'fa-palette', title: 'Wide Collection', description: 'Stylish belts and keychains in various designs to match every pet\'s personality', color: 'info' }
  ];

  ngOnInit(): void {
    
  }

  ngAfterViewInit(): void {
    // Add scroll animations
    this.initScrollAnimations();
  }

  private initScrollAnimations(): void {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.1 });

    // Observe all animate-on-scroll elements
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
      observer.observe(el);
    });
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

  // Method to handle CTA button clicks
  onShopClick(): void {
    this.showSnackBar('Redirecting to our shop...', 'info');
  }

  onLearnMoreClick(): void {
    this.showSnackBar('Loading more information...', 'info');
  }

  // Method to handle service card clicks (if needed)
  onServiceClick(service: any): void {
    console.log('Service clicked:', service);
    this.showSnackBar(`Learn more about ${service.title}`, 'info');
  }

  // Method to animate stats counter (optional)
  animateCounter(element: HTMLElement, start: number, end: number, duration: number): void {
    let startTimestamp: number | null = null;
    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const value = Math.floor(progress * (end - start) + start);
      element.textContent = value + '+';
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };
    window.requestAnimationFrame(step);
  }
}
  
