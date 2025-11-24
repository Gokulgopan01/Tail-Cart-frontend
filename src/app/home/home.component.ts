import { Component, OnInit, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit, AfterViewInit {
  username: string | null = '';
  userId: string | null = '';
  hasProfile = false;
  cartItems = 3; // Example cart items count

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.username = localStorage.getItem('username');
    this.userId = localStorage.getItem('user_id');
    
    if (this.userId) {
      this.checkProfile();
    }
  }

  ngAfterViewInit() {
    setTimeout(() => {
      this.initScrollAnimations();
    }, 100);
  }

  initScrollAnimations() {
    // First, trigger hero animations immediately
    const heroAnimations = document.querySelectorAll(
      '.animate-fade-in, .animate-slide-left, .animate-slide-right, .animate-fade-in-delay, .animate-bounce-in, .animate-float'
    );
    
    heroAnimations.forEach(el => {
      el.classList.add('animated');
    });

    // Trigger stagger animations with delays
    const staggerElements = document.querySelectorAll('.animate-stagger > *');
    staggerElements.forEach((el, index) => {
      setTimeout(() => {
        el.classList.add('animated');
      }, index * 200);
    });

    // Scroll animations
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animated');
          entry.target.classList.add('visible');
          
          // Add slight delay for multiple elements in grid
          if (entry.target.classList.contains('feature-card') || 
              entry.target.classList.contains('category-card') ||
              entry.target.classList.contains('testimonial-card')) {
            setTimeout(() => {
              entry.target.classList.add('animate-visible');
            }, 100);
          }
        }
      });
    }, { 
      threshold: 0.1,
      rootMargin: '0px 0px -10% 0px'
    });

    // Observe scroll-triggered elements
    const scrollElements = document.querySelectorAll(
      '.animate-on-scroll, .scroll-trigger, .feature-card, .category-card, .testimonial-card'
    );
    
    scrollElements.forEach(el => observer.observe(el));
  }

  checkProfile(): void {
    this.http.get<any>(`https://tailcart.duckdns.org/api/user/profile/?user_id=${this.userId}`)
      .subscribe({
        next: (response) => {
          this.hasProfile = !!response.owner_name;
        },
        error: (error) => {
          this.hasProfile = false;
        }
      });
  }

  navigateToProfile(): void {
    this.router.navigate(['/profile']);
  }

  logout(): void {
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    this.router.navigate(['/auth']);
  }

  navigateTo(path: string): void {
    this.router.navigate([path]);
  }
}