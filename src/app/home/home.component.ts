import { Component, HostListener, AfterViewInit, ElementRef, ViewChild, OnDestroy, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { NgFor, NgIf, UpperCasePipe, CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [NgFor, RouterModule, CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class HomeComponent implements OnInit, AfterViewInit, OnDestroy {
  // ── Banner Carousel State ─────────────────────────────────────
  activeBannerIndex: number = 0;
  private bannerTimer: any;

  slideDirection: 'forward' | 'backward' = 'forward';

  contentState: 'idle' | 'exit' | 'enter' = 'idle';
  imageState: 'idle' | 'exit' | 'enter' = 'idle';

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
      img: 'assets/Home/tailtag.png',
      color: '#003c30',
      route: '/shop',
      cta: 'Explore Tags'
    },
    {
      id: 'vault',
      name: 'Tail Vault',
      desc: 'Securely manage all your pet\'s health records and paperwork in one place.',
      img: 'assets/Home/tailvault.png',
      color: '#6b4f1d',
      route: '/documents',
      cta: 'Open Vault'
    },
    {
      id: 'reminders',
      name: 'Smart Scheduler',
      desc: 'Never miss a critical care date with intelligent alerts.',
      img: 'assets/Home/SmartScheduler.png',
      color: '#1f2a44',
      route: '/document',
      cta: 'Set Reminders'
    },
    {
      id: 'doctor',
      name: 'Tail Care+',
      desc: '24/7 AI-powered health insights for your pets.',
      img: 'assets/Home/Doctor.png',
      color: '#4a1f36',
      route: '/doctor-ai',
      cta: 'Ask AI Doctor'
    }
  ];

  products = [
    {
      id: 1,
      name: 'Wooden QR Keychain',
      price: '₹688',
      img: 'assets/images/product_trending_1.png',
      category: 'DOGS'
    },
    {
      id: 2,
      name: 'Metal QR Keychain',
      price: '₹499',
      img: 'assets/images/product_trending_2.jpg',
      category: 'CATS'
    },
    {
      id: 3,
      name: 'Fiberglass QR Keychain',
      price: '₹499',
      img: 'assets/images/product_trending_3.png',
      category: 'BIRDS'
    },
    {
      id: 4,
      name: 'GPS Tracker Collar',
      price: '₹499',
      img: 'assets/images/product_trending_4.png',
      category: 'DOGS'
    }
  ];

  categories = [
    { name: 'Dogs', img: 'assets/Home/dog_catagory.png' },
    { name: 'Cats', img: 'assets/Home/cat_catagory.png' },
    { name: 'Toys', img: 'assets/Home/toys_catagory.png' },
    { name: 'Other', img: 'assets/Home/accesories.png' },
    { name: 'QR Keychains', img: 'assets/images/product_trending_1.png' },
    { name: 'GPRS Belts', img: 'assets/images/product_trending_3.png' }
  ];
  selectedCategory: string = 'All Products';

  // State flags
  isScrolled = false;
  faqStates: boolean[] = [false, false, false, false, false];
  isDetailedVideoMuted = true;
  isDetailedVideoPlaying = false;
  private hasAutoPlayed = false;

  @ViewChild('featureVideo', { static: false }) featureVideo!: ElementRef<HTMLVideoElement>;

  // ── Hero Background Video State ───────────────────────────────
  @ViewChild('heroVideo', { static: false }) heroVideo!: ElementRef<HTMLVideoElement>;
  isHeroPlaying = true;
  isHeroMuted = true; // must start muted for autoplay to be allowed by browsers
  private heroHasAutoPlayed = false;

  activeEcosystemIndex = 0;

  contentAnimating = false;
  imageAnimating = false;

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
    this.initializeHeroVideo();
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
  selectEcosystemTab(index: number) {
    if (index === this.activeEcosystemIndex) return;

    this.slideDirection = index > this.activeEcosystemIndex ? 'forward' : 'backward';

    // Phase 1: EXIT
    this.contentState = 'exit';
    this.imageState = 'exit';

    setTimeout(() => {
      // Phase 2: swap slide, then trigger ENTER
      this.activeEcosystemIndex = index;
      this.contentState = 'enter';
      this.imageState = 'enter';

      // Phase 3: settle back to idle
      setTimeout(() => {
        this.contentState = 'idle';
        this.imageState = 'idle';
      }, 700);
    }, 550);
  }


  getSlideClass(index: number): string {
    if (index === this.activeEcosystemIndex) return 'active';
    if (index === (this.activeEcosystemIndex - 1 + this.services.length) % this.services.length) return 'prev';
    if (index === (this.activeEcosystemIndex + 1) % this.services.length) return 'next';
    return 'hidden';
  }

  // ── Feature Video & Scroll Logic ──────────────────────────────
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

  // ── Hero Background Video Logic ───────────────────────────────
  private initializeHeroVideo(): void {
    const video = this.heroVideo?.nativeElement;
    if (!video) return;
    video.muted = this.isHeroMuted;
    video.autoplay = true;
    video.playsInline = true;
    video.load();
    if (!this.heroHasAutoPlayed) {
      video.play()
        .then(() => {
          this.heroHasAutoPlayed = true;
          this.isHeroPlaying = true;
        })
        .catch(() => {
          this.isHeroPlaying = false;
        });
    }
  }

  toggleHeroPlay(): void {
    const video = this.heroVideo?.nativeElement;
    if (!video) return;

    if (video.paused) {
      video.play();
      this.isHeroPlaying = true;
    } else {
      video.pause();
      this.isHeroPlaying = false;
    }
  }

  toggleHeroMute(): void {
    const video = this.heroVideo?.nativeElement;
    if (!video) return;

    video.muted = !video.muted;
    this.isHeroMuted = video.muted;
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
    const isOpen = this.faqStates[index];

    // Close every item
    this.faqStates = this.faqStates.map(() => false);

    // If the clicked item was closed, open it
    if (!isOpen) {
      this.faqStates[index] = true;
    }
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

  scrollToHowItWorks(): void {
    const el = document.querySelector('.protection-how-it-works');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }


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