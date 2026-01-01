import { Component, AfterViewInit, HostListener, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements AfterViewInit, OnDestroy {
  
  currentSlide = 0;
  currentTab: 'smart-qr' | 'doc-locker' | 'ai-pet' = 'smart-qr';
  autoSlideInterval: any;
  
  constructor(private router: Router) {}
  
  ngAfterViewInit(): void {
    this.initCarousel();
    this.initTabs();
    this.startAutoSlide();
  }
  
  // Carousel functionality
  initCarousel(): void {
    this.goToSlide(0);
  }
  
  goToSlide(index: number): void {
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.carousel-dot');
    
    if (slides.length === 0 || dots.length === 0) return;
    
    // Remove active class from all slides and dots
    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));
    
    // Add active class to current slide and dot
    if (slides[index]) {
      slides[index].classList.add('active');
    }
    if (dots[index]) {
      dots[index].classList.add('active');
    }
    
    this.currentSlide = index;
    this.resetAutoSlide();
  }
  
  nextSlide(): void {
    const slides = document.querySelectorAll('.carousel-slide');
    if (slides.length === 0) return;
    
    const nextIndex = (this.currentSlide + 1) % slides.length;
    this.goToSlide(nextIndex);
  }
  
  prevSlide(): void {
    const slides = document.querySelectorAll('.carousel-slide');
    if (slides.length === 0) return;
    
    const prevIndex = (this.currentSlide - 1 + slides.length) % slides.length;
    this.goToSlide(prevIndex);
  }
  
  startAutoSlide(): void {
    this.autoSlideInterval = setInterval(() => {
      this.nextSlide();
    }, 5000);
  }
  
  resetAutoSlide(): void {
    if (this.autoSlideInterval) {
      clearInterval(this.autoSlideInterval);
      this.startAutoSlide();
    }
  }
  
  // Tab functionality
  initTabs(): void {
    // Initialize first tab as active
    this.switchTab('smart-qr');
  }
  
  switchTab(tabId: 'smart-qr' | 'doc-locker' | 'ai-pet'): void {
  this.currentTab = tabId;
  
  // Remove active class from all tabs and tab contents
  const tabs = document.querySelectorAll('.platform-tab');
  const tabContents = document.querySelectorAll('.tab-content');
  
  tabs.forEach(tab => tab.classList.remove('active'));
  tabContents.forEach(content => content.classList.remove('active'));
  
  // Add active class to current tab and content
  document.querySelector(`.platform-tab[data-tab="${tabId}"]`)?.classList.add('active');
  document.getElementById(`${tabId}-content`)?.classList.add('active');
}
  
  // Handle add to cart
  addToCart(productTitle: string): void {
    console.log(`Added ${productTitle} to cart!`);
    // Add actual cart logic here
  }
  
  // Clean up
  ngOnDestroy(): void {
    if (this.autoSlideInterval) {
      clearInterval(this.autoSlideInterval);
    }
  }
}