import { Component, AfterViewInit, HostListener } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements AfterViewInit {
  
  constructor(private router: Router) {}
  
  ngAfterViewInit(): void {
    this.initScrollAnimations();
    this.initParallax();
  }
  
  // Initialize scroll animations
  initScrollAnimations(): void {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate__animated', 'animate__fadeInUp');
        }
      });
    }, observerOptions);
    
    // Observe all reveal elements
    document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
    document.querySelectorAll('.step-card').forEach((el) => observer.observe(el));
    document.querySelectorAll('.stat-card').forEach((el) => observer.observe(el));
  }
  
  // Parallax effect for hero section
  initParallax(): void {
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
      window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        (heroSection as HTMLElement).style.transform = `translate3d(0, ${rate}px, 0)`;
      });
    }
  }
  
  // Navigation methods
  navigateTo(path: string): void {
    this.router.navigate([path]);
  }
  
  scrollToFeatures(): void {
    const featuresSection = document.getElementById('features');
    if (featuresSection) {
      featuresSection.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
  }
  
  // Handle window resize
  @HostListener('window:resize')
  onResize(): void {
    // Reinitialize animations on resize if needed
  }
}