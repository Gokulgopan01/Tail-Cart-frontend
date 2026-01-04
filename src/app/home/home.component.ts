import { Component, AfterViewInit, HostListener, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import lottie from 'lottie-web'; // Import Lottie

interface Product {
  id: number;
  model: string;
  product_info: string;
  price: number;
  breed: string;
  quantity: number;
  image: string;
  reviews: string;
  deals: string | null;
}

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  imports: [CommonModule]
})
export class HomeComponent implements AfterViewInit, OnInit, OnDestroy {
  
  currentSlide = 0;
  currentTab: 'smart-qr' | 'doc-locker' | 'ai-pet' = 'smart-qr';
  autoSlideInterval: any;
  
  // Add these properties for products
  products: Product[] = [];
  displayedProducts: Product[] = [];
  isLoading: boolean = true;
  errorMessage: string = '';
  
  // Lottie animations
  private lottieAnimations: any[] = [];
  
  constructor(
    private router: Router,
    private http: HttpClient
  ) {}
  
  ngOnInit(): void {
    this.loadProducts();
  }
  
  ngAfterViewInit(): void {
    this.initCarousel();
    this.initTabs();
    this.startAutoSlide();
    this.loadLottieAnimations();
  }
  
  // Load Lottie animations
  loadLottieAnimations(): void {
    // Lottie JSON URLs (you can also import from assets)
    const lottieConfigs = [
      {
        container: document.getElementById('lottie-1'),
        path: '/assets/pet_doctor.json', // or use direct URL
        loop: true,
        autoplay: false // We'll control playback
      },
      {
        container: document.getElementById('lottie-2'),
        path: '/assets/pet_doctor.json',
        loop: true,
        autoplay: false
      },
      {
        container: document.getElementById('lottie-3'),
        path: '/assets/pet_doctor.json',
        loop: true,
        autoplay: false
      }
    ];
    
    // If you want to use the same animation for all slides
    const lottieUrls = [
      'assets/buy_product.json', // Pet location animation
      'assets/manage_docs.json', // Document animation
      'assets/pet_doctor.json', // AI chat animation
    ];
    
    // Initialize Lottie animations
    setTimeout(() => {
      lottieUrls.forEach((url, index) => {
        if (document.getElementById(`lottie-${index + 1}`)) {
          const animation = lottie.loadAnimation({
            container: document.getElementById(`lottie-${index + 1}`) as HTMLElement,
            renderer: 'svg',
            loop: true,
            autoplay: index === 0, // Play only first slide initially
            path: url
          });
          
          this.lottieAnimations.push(animation);
          
          // Optional: Adjust animation speed
          animation.setSpeed(0.8);
        }
      });
    }, 500);
  }
  
  // Play animation for current slide
  playCurrentSlideAnimation(): void {
    // Pause all animations
    this.lottieAnimations.forEach(anim => anim.pause());
    
    // Play animation for current slide
    if (this.lottieAnimations[this.currentSlide]) {
      this.lottieAnimations[this.currentSlide].play();
    }
  }
  
  // Load products from API
  loadProducts(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    const apiUrl = 'https://tailcart1.duckdns.org/api/admin/products/';
    
    this.http.get<Product[]>(apiUrl).subscribe({
      next: (data) => {
        this.products = data;
        
        // Take first 4 products only
        if (this.products.length >= 4) {
          this.displayedProducts = this.products.slice(0, 4);
        } else {
          this.displayedProducts = [...this.products];
        }
        
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading products:', error);
        this.isLoading = false;
        this.errorMessage = 'Failed to load products. Please try again.';
      }
    });
  }
  
  // Handle broken images
  handleImageError(event: any): void {
    event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPHJlY3Qgd2lkdGg9IjMwMCIgaGVpZ2h0PSIyMDAiIGZpbGw9IiNlM2U0ZTYiLz4KICA8dGV4dCB4PSIxNTAiIHk9IjEwMCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj5Qcm9kdWN0IEltYWdlPC90ZXh0Pgo8L3N2Zz4=';
  }
  
  // Navigate to product page
  goToProduct(productId: number): void {
    this.router.navigate(['/product', productId]);
  }
  
  // Navigate to shop page
  goToShop(): void {
    this.router.navigate(['/shop']);
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
    
    // Play animation for current slide
    this.playCurrentSlideAnimation();
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
    this.switchTab('smart-qr');
  }
  
  switchTab(tabId: 'smart-qr' | 'doc-locker' | 'ai-pet'): void {
    this.currentTab = tabId;
    
    const tabs = document.querySelectorAll('.platform-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));
    
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
    
    // Destroy Lottie animations
    this.lottieAnimations.forEach(animation => {
      animation.destroy();
    });
  }
}