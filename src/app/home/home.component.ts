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
      color: '#fb8c00',
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
      badgeClass: 'badge-gold'
    },
    {
      id: 2,
      name: 'Wooden Frame',
      subtitle: 'Artisan Walnut Craft',
      price: '₹499.00',
      img: 'assets/images/product_trending_2.jpg',
      badge: 'CLASSIC',
      badgeClass: 'badge-amber'
    },
    {
      id: 3,
      name: 'Fiber Frame',
      subtitle: 'Lightweight Carbon',
      price: '₹499.00',
      img: 'assets/images/product_trending_3.png',
      badge: 'DURABLE',
      badgeClass: 'badge-silver'
    },
    {
      id: 4,
      name: 'Stealth Carbon',
      subtitle: 'Waterproof Performance',
      price: '₹499.00',
      img: 'assets/images/product_trending_4.png',
      badge: 'LIMITED',
      badgeClass: 'badge-dark'
    },
    {
      id: 5,
      name: 'Guardian Onyx',
      subtitle: 'Matte Black Series',
      price: '₹750.00',
      img: 'assets/images/product_trending_1.png',
      badge: 'NEW',
      badgeClass: 'badge-dark'
    },
    {
      id: 6,
      name: 'Guardian Aero',
      subtitle: 'Titanium Finish',
      price: '₹899.00',
      img: 'assets/images/product_trending_3.png',
      badge: 'PREMIUM',
      badgeClass: 'badge-gold'
    }
  ];

  // ── Ecosystem Carousel Logic ────────────────────────────────
  activeEcosystemIndex: number = 0;
  @ViewChild('ecoCarousel', { static: false }) ecoCarousel!: ElementRef<HTMLDivElement>;

  selectEcosystemTab(index: number): void {
    this.activeEcosystemIndex = index;
    const carousel = this.ecoCarousel.nativeElement;
    const slideWidth = carousel.offsetWidth;

    carousel.scrollTo({
      left: index * slideWidth,
      behavior: 'smooth'
    });
  }

  onEcosystemScroll(event: any): void {
    const carousel = event.target;
    const scrollPosition = carousel.scrollLeft;
    const slideWidth = carousel.offsetWidth;
    const newIndex = Math.round(scrollPosition / slideWidth);

    if (newIndex !== this.activeEcosystemIndex) {
      this.activeEcosystemIndex = newIndex;
    }
  }

  navigateToService(route: string): void {
    this.router.navigate([route]);
  }
  // ───────────────────────────────────────────────────────────────
  // ───────────────────────────────────────────────────────────────

  isScrolled = false;

  @ViewChild('featureVideo', { static: false }) featureVideo!: ElementRef<HTMLVideoElement>;

  faqStates: boolean[] = [false, false, false, false];
  isDetailedVideoMuted = true;
  isDetailedVideoPlaying = false;

  constructor(private router: Router) { }

  ngOnInit(): void {
    this.startVaultAnimation();
    this.isScrolled = window.scrollY > 300;
  }

  ngAfterViewInit(): void {
    // Wait a bit for video to load
    this.initializeVideo();
    setTimeout(() => {
      this.isScrolled = window.scrollY > 300;
    }, 100);

    // Fade-in observer
    const fadeElements = document.querySelectorAll('.fade-in');
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1 }
    );
    fadeElements.forEach(el => observer.observe(el));
  }


  toggleFaq(index: number): void {
    this.faqStates[index] = !this.faqStates[index];
  }

  private hasAutoPlayed = false;

  // Initialize first video
  private initializeVideo(): void {
    const video = this.featureVideo?.nativeElement;
    if (!video) return;

    video.muted = true;
    video.autoplay = true;
    video.playsInline = true;
    video.preload = 'auto';
    video.controls = true;

    video.load();

    if (!this.hasAutoPlayed) {
      video.play()
        .then(() => {
          this.hasAutoPlayed = true;
          video.classList.add('playing');
        })
        .catch(err => {
          console.warn('Autoplay blocked:', err);
          this.showPlayButton();
        });
    }

    video.addEventListener('play', () => this.onVideoPlay());
    video.addEventListener('pause', () => this.onVideoPause());
    video.addEventListener('ended', () => this.onVideoEnded());
  }



  // Existing video methods (keep all existing code below)
  playVideo(event: any): void {
    const container = event.currentTarget.closest('.video-container');
    const video: HTMLVideoElement = container.querySelector('.feature-video');
    const overlay = container.querySelector('.play-button-overlay');

    if (!video) return;

    video.muted = false;
    video.controls = true;

    video.play().then(() => {
      overlay?.classList.add('hidden');
      video.classList.add('playing');
    });
  }

  showPlayButton(): void {
    const videoElement = this.featureVideo?.nativeElement;
    if (videoElement) {
      const playOverlay = document.querySelector('.play-button-overlay');
      if (playOverlay) {
        playOverlay.classList.remove('hidden');
      }
      videoElement.classList.remove('playing');
    }
  }

  onVideoPlay(): void {
    const playOverlay = document.querySelector('.play-button-overlay');
    if (playOverlay) {
      playOverlay.classList.add('hidden');
    }
  }

  onVideoPause(): void {
    this.showPlayButton();
  }

  onVideoEnded(): void {
    this.showPlayButton();
  }

  toggleDetailedVideo(): void {
    const video = this.featureVideo.nativeElement;
    if (video.paused) {
      video.play();
      this.isDetailedVideoPlaying = true;
    } else {
      video.pause();
      this.isDetailedVideoPlaying = false;
    }
  }

  toggleDetailedMute(): void {
    const video = this.featureVideo.nativeElement;
    video.muted = !video.muted;
    this.isDetailedVideoMuted = video.muted;
  }

  // Navigation methods
  navigateToShop(): void {
    this.router.navigate(['/shop']);
  }

  watchDemo(): void {
    console.log('Opening demo video...');
  }

  navigateToDocuments(): void {
    this.router.navigate(['/documents']);
  }

  navigateToAlerts(): void {
    this.router.navigate(['/document']);
  }

  navigateToProfile(): void {
    this.router.navigate(['/profile']);
  }

  navigateToDoctor(): void {
    this.router.navigate(['/doctor-ai']);
  }

  navigateToAbout(): void {
    this.router.navigate(['/about']);
  }

  // Scroll to top function - Custom slow smooth scroll
  scrollToTop(): void {
    const duration = 2500; // 1.5 seconds for a slower feel
    const start = window.scrollY;
    const startTime = performance.now();

    const animateScroll = (currentTime: number) => {
      const elapsedTime = currentTime - startTime;
      const progress = Math.min(elapsedTime / duration, 1);

      // Ease out cubic function for a premium feel
      const easeProgress = 1 - Math.pow(1 - progress, 3);

      window.scrollTo(0, start * (1 - easeProgress));

      if (progress < 1) {
        requestAnimationFrame(animateScroll);
      }
    };

    requestAnimationFrame(animateScroll);
  }

  // Listen to scroll events to show/hide scroll-to-top button
  @HostListener('window:scroll', [])
  onWindowScroll(): void {
    const scrollPosition = window.scrollY;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;

    // Show button when scrolled down 300px
    this.isScrolled = scrollPosition > 300;

    // Hide button when near footer
    const footer = document.querySelector('.luxury-footer');
    if (footer) {
      const footerRect = footer.getBoundingClientRect();
      const footerTop = footerRect.top + scrollPosition;

      // If we're within 200px of the footer, hide the button
      if (scrollPosition + windowHeight > footerTop - 200) {
        this.isScrolled = false;
      }
    }
  }

  @HostListener('window:scroll', [])
  onScroll(): void {
    const elements = document.querySelectorAll('.fade-in');

    elements.forEach((el) => {
      const rect = el.getBoundingClientRect();
      const isVisible = rect.top < window.innerHeight - 100;

      if (isVisible) {
        el.classList.add('visible');
      }
    });
  }

  // Card hover effects
  onCardHover(event: any): void {
    const card = event.currentTarget;
    card.style.transform = 'translateY(-8px)';
  }

  onCardLeave(event: any): void {
    const card = event.currentTarget;
    card.style.transform = 'translateY(0)';
  }

  // Vault Animation Logic
  startVaultAnimation(): void {
    if (this.vaultAnimationTimer) clearInterval(this.vaultAnimationTimer);

    this.vaultAnimationTimer = setInterval(() => {
      this.activeVaultStep++;

      if (this.activeVaultStep === 2) {
        // Step 2: Simulate "Add Document" click and success
        setTimeout(() => {
          this.vaultToastMessage = 'Document uploaded successfully!';
          setTimeout(() => this.vaultToastMessage = '', 2000);
        }, 1000);
      } else if (this.activeVaultStep === 3) {
        // Step 3: Switch to Reminders tab
        this.vaultToastMessage = '';
      } else if (this.activeVaultStep === 4) {
        // Step 4: Show Reminder toast
        setTimeout(() => {
          this.vaultToastMessage = 'Reminder set for Buddy!';
          setTimeout(() => this.vaultToastMessage = '', 2000);
        }, 800);
      }

      if (this.activeVaultStep > 4) {
        this.activeVaultStep = 1;
        this.vaultToastMessage = '';
      }
    }, 4000); // 4 seconds per state
  }

  ngOnDestroy(): void {
    if (this.vaultAnimationTimer) clearInterval(this.vaultAnimationTimer);
  }
}