import { Component, HostListener, AfterViewInit, ElementRef, ViewChild, OnDestroy, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { NgFor, NgIf, UpperCasePipe } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [NgFor, NgIf, RouterModule, UpperCasePipe],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class HomeComponent implements OnInit, AfterViewInit, OnDestroy {
  // ── Banner Carousel State ─────────────────────────────────────
  activeBannerIndex: number = 0;
  private bannerTimer: any;

  offerBanners = [
    {
      img: 'assets/Home/discount_add.png'
    },
    {
      img: 'assets/Home/free_delivery_add.png'
    },
    {
      img: 'assets/Home/buy2_add.png'
    }
  ];

  // ── Bento Grid Ecosystem State ────────────────────────────────
  activeVaultStep: number = 1;
  vaultToastMessage: string = '';
  private vaultAnimationTimer: any;

  services = [
    {
      id: 'keychain',
      name: 'Tail Tag',
      desc: 'Premium aerospace-grade smart tags with instant scan recovery technology.',
      img: 'assets/images/hero_qr_keychain.png',
      color: '#003c30',
      route: '/shop',
      cta: 'Explore Tags'
    },
    {
      id: 'vault',
      name: 'Tail Vault',
      desc: 'Securely manage all your pet\'s health records and paperwork in one place.',
      img: 'assets/images/hero_document_locker.png',
      color: '#fbc02d',
      route: '/documents',
      cta: 'Open Vault'
    },
    {
      id: 'reminders',
      name: 'Smart Scheduler',
      desc: 'Never miss a critical care date with intelligent alerts.',
      img: 'assets/images/hero_alert_system.png',
      color: '#8e24aa',
      route: '/document',
      cta: 'Set Reminders'
    },
    {
      id: 'doctor',
      name: 'Tail Care+',
      desc: '24/7 AI-powered health insights for your pets.',
      img: 'assets/images/hero_ai_doctor.png',
      color: '#43a047',
      route: '/doctor-ai',
      cta: 'Ask AI Doctor'
    }
  ];

  products = [
    {
      id: 1,
      name: 'Guardian Alpha',
      subtitle: 'Polished Gold Edition',
      price: '₹688.00',
      img: 'assets/images/product_trending_1.png',
      badge: 'BESTSELLER',
      badgeClass: 'badge-gold',
      category: 'DOGS',
      rating: 4.8,
      reviews: 1240,
    },
    {
      id: 2,
      name: 'Wooden Frame',
      subtitle: 'Artisan Walnut Craft',
      price: '₹499.00',
      img: 'assets/images/product_trending_2.jpg',
      badge: 'CLASSIC',
      badgeClass: 'badge-amber',
      category: 'CATS',
      rating: 4.5,
      reviews: 1024,
    },
    {
      id: 3,
      name: 'Fiber Frame',
      subtitle: 'Lightweight Carbon',
      price: '₹499.00',
      img: 'assets/images/product_trending_3.png',
      badge: 'DURABLE',
      badgeClass: 'badge-silver',
      category: 'BIRDS',
      rating: 4.6,
      reviews: 1102,
    },
    {
      id: 4,
      name: 'Stealth Carbon',
      subtitle: 'Waterproof Performance',
      price: '₹499.00',
      img: 'assets/images/product_trending_4.png',
      badge: 'LIMITED',
      badgeClass: 'badge-dark',
      category: 'DOGS',
      rating: 4.7,
      reviews: 1150,
    },
    {
      id: 5,
      name: 'Guardian Onyx',
      subtitle: 'Matte Black Series',
      price: '₹750.00',
      img: 'assets/images/product_trending_1.png',
      badge: 'NEW',
      badgeClass: 'badge-dark',
      category: 'FISH',
      rating: 4.4,
      reviews: 1080,
    },
    {
      id: 6,
      name: 'Guardian Aero',
      subtitle: 'Titanium Finish',
      price: '₹899.00',
      img: 'assets/images/product_trending_3.png',
      badge: 'PREMIUM',
      badgeClass: 'badge-gold',
      category: 'CATS',
      rating: 4.7,
      reviews: 1150,
    }
  ];

  categories = [
    { name: 'All Products', icon: 'fas fa-th-large' },
    { name: 'Dogs', img: 'assets/images/cat_dog.png' },
    { name: 'Cats', img: 'assets/images/cat_cat.png' },
    { name: 'Birds', img: 'assets/images/cat_bird.png' },
    { name: 'Small Pets', img: 'assets/images/cat_other.png' },
    { name: 'Fish', icon: 'fas fa-fish' },
    { name: 'Food & Treats', icon: 'fas fa-bone' },
    { name: 'Toys & Accessories', icon: 'fas fa-baseball-ball' }
  ];
  selectedCategory: string = 'All Products';





  // State flags
  isScrolled = false;
  faqStates: boolean[] = [false, false, false, false];
  isDetailedVideoMuted = true;
  isDetailedVideoPlaying = false;
  private hasAutoPlayed = false;

  @ViewChild('ecoCarousel', { static: false }) ecoCarousel!: ElementRef<HTMLDivElement>;
  @ViewChild('featureVideo', { static: false }) featureVideo!: ElementRef<HTMLVideoElement>;

  activeEcosystemIndex: number = 0;

  constructor(private router: Router) { }

  ngOnInit(): void {
    this.startBannerTimer();
    this.startVaultAnimation();
    this.checkScroll();

    // Load cart items count
    const savedCart = localStorage.getItem('cart_items');
    if (savedCart) {
      try {
        // this.cartItems = JSON.parse(savedCart).length; 
        // Note: cartItems count logic is currently handled in ngOnInit but no cartItems property exists in the class yet.
        // I'll add the property if needed, but for now I'll just focus on fixing the logical flow.
      } catch (e) {
        console.error('Error parsing cart items', e);
      }
    }
  }

  ngAfterViewInit(): void {
    this.initializeVideo();
  }

  ngOnDestroy(): void {
    this.stopBannerTimer();
    this.stopVaultAnimation();
  }

  // ── Banner Carousel Logic ─────────────────────────────────────
  private startBannerTimer() {
    this.bannerTimer = setInterval(() => {
      this.nextBanner();
    }, 5000);
  }

  private stopBannerTimer() {
    if (this.bannerTimer) clearInterval(this.bannerTimer);
  }

  nextBanner() {
    this.activeBannerIndex = (this.activeBannerIndex + 1) % this.offerBanners.length;
  }

  setBanner(index: number) {
    this.activeBannerIndex = index;
    this.stopBannerTimer();
    this.startBannerTimer();
  }

  // ── Category Filtering Logic ────────────────────────────────
  selectCategory(category: string): void {
    this.selectedCategory = category;
  }

  get filteredProducts() {
    if (this.selectedCategory === 'All Products') return this.products;
    return this.products.filter(p => (p as any).category.toUpperCase() === this.selectedCategory.toUpperCase());
  }

  // ── Ecosystem Carousel Logic ────────────────────────────────
  selectEcosystemTab(index: number): void {
    this.activeEcosystemIndex = index;
    const carousel = this.ecoCarousel.nativeElement;
    const slideWidth = carousel.offsetWidth;
    carousel.scrollTo({ left: index * slideWidth, behavior: 'smooth' });
  }

  onEcosystemScroll(event: any): void {
    const carousel = event.target;
    const newIndex = Math.round(carousel.scrollLeft / carousel.offsetWidth);
    if (newIndex !== this.activeEcosystemIndex) this.activeEcosystemIndex = newIndex;
  }

  // ── Video & Scroll Logic ─────────────────────────────────────
  private initializeVideo(): void {
    const video = this.featureVideo?.nativeElement;
    if (!video) return;
    video.muted = true;
    video.autoplay = true;
    video.playsInline = true;
    video.load();
    if (!this.hasAutoPlayed) {
      video.play().then(() => this.hasAutoPlayed = true).catch(() => this.showPlayButton());
    }
  }

  @HostListener('window:scroll', [])
  onWindowScroll(): void {
    this.checkScroll();
  }

  private checkScroll(): void {
    const scrollPosition = window.scrollY;
    this.isScrolled = scrollPosition > 300;

    // Hide button when near footer for clean look
    const footer = document.querySelector('.premium-luxury-footer');
    if (footer) {
      const footerRect = footer.getBoundingClientRect();
      if (footerRect.top < window.innerHeight) this.isScrolled = false;
    }
  }

  scrollToTop(): void {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  toggleFaq(index: number): void {
    this.faqStates[index] = !this.faqStates[index];
  }

  showPlayButton(): void {
    document.querySelector('.play-button-overlay')?.classList.remove('hidden');
  }

  getStars(rating: number): number[] {
    const fullStars = Math.floor(rating);
    return Array(fullStars).fill(0);
  }

  // Helper method to check if half star is needed
  hasHalfStar(rating: number): boolean {
    return rating % 1 !== 0;
  }

  // Add to cart method (implement as needed)
  addToCart(product: any): void {
    // Your add to cart logic here
    console.log('Added to cart:', product);
    // Example: this.cartService.addItem(product);
  }

  // ── Navigation methods ───────────────────────────────────────
  navigateToShop(): void { this.router.navigate(['/shop']); }
  navigateToDocuments(): void { this.router.navigate(['/documents']); }
  navigateToAlerts(): void { this.router.navigate(['/document']); }
  navigateToProfile(): void { this.router.navigate(['/profile']); }
  navigateToDoctor(): void { this.router.navigate(['/doctor-ai']); }
  navigateToAbout(): void { this.router.navigate(['/about']); }
  navigateToService(route: string): void { this.router.navigate([route]); }

  // ── Vault Animation Logic ────────────────────────────────────
  private startVaultAnimation(): void {
    this.vaultAnimationTimer = setInterval(() => {
      this.activeVaultStep = (this.activeVaultStep % 4) + 1;
      if (this.activeVaultStep === 2) {
        setTimeout(() => {
          this.vaultToastMessage = 'Document uploaded successfully!';
          setTimeout(() => this.vaultToastMessage = '', 2000);
        }, 1000);
      } else if (this.activeVaultStep === 4) {
        setTimeout(() => {
          this.vaultToastMessage = 'Reminder set for Buddy!';
          setTimeout(() => this.vaultToastMessage = '', 2000);
        }, 800);
      }
    }, 4000);
  }

  private stopVaultAnimation(): void {
    if (this.vaultAnimationTimer) clearInterval(this.vaultAnimationTimer);
  }
}