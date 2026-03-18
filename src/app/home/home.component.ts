import { Component, HostListener, AfterViewInit, ElementRef, ViewChild, OnDestroy } from '@angular/core';
import { NgFor, NgIf } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [NgFor, NgIf, RouterModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements AfterViewInit, OnDestroy {

  // ── Hero Carousel ──────────────────────────────────────────────
  heroSlide = 0;
  heroSlides = [0, 1, 2, 3];
  heroAutoPlay = true;
  heroAutoPlayDuration = 5000;
  private heroTimer: any;

  nextHeroSlide(): void {
    this.heroSlide = (this.heroSlide + 1) % 4;
    this.restartTimer();
  }

  prevHeroSlide(): void {
    this.heroSlide = (this.heroSlide + 3) % 4;
    this.restartTimer();
  }

  goToHeroSlide(index: number): void {
    this.heroSlide = index;
    this.restartTimer();
  }

  private startTimer(): void {
    this.heroTimer = setInterval(() => this.nextHeroSlide(), this.heroAutoPlayDuration);
  }

  private restartTimer(): void {
    clearInterval(this.heroTimer);
    this.startTimer();
  }

  // Touch swipe support
  private touchStartX = 0;
  onHeroTouchStart(event: TouchEvent): void {
    this.touchStartX = event.touches[0].clientX;
  }
  onHeroTouchEnd(event: TouchEvent): void {
    const diff = this.touchStartX - event.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) {
      diff > 0 ? this.nextHeroSlide() : this.prevHeroSlide();
    }
  }

  // ── How It Works Carousel ──────────────────────────────────────
  processSlide = 0;
  private processTouchStartX = 0;

  nextProcessSlide(): void {
    if (this.processSlide < 4) {
      this.processSlide++;
    } else {
      this.processSlide = 0; // Loop back
    }
  }

  prevProcessSlide(): void {
    if (this.processSlide > 0) {
      this.processSlide--;
    } else {
      this.processSlide = 4; // Loop to end
    }
  }

  goToProcessSlide(index: number): void {
    this.processSlide = index;
  }

  onProcessTouchStart(event: TouchEvent): void {
    this.processTouchStartX = event.touches[0].clientX;
  }

  onProcessTouchEnd(event: TouchEvent): void {
    const diff = this.processTouchStartX - event.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) {
      diff > 0 ? this.nextProcessSlide() : this.prevProcessSlide();
    }
  }

  // ── Services 3D Carousel ──────────────────────────────────────
  activeServiceIndex = 0;
  serviceAutoPlayDuration = 6000;
  private serviceTimer: any;

  services = [
    {
      id: 'keychain',
      name: 'Tail Tag',
      desc: 'Secure tracking for your pet with instant notification technology anywhere in the world.',
      img: 'assets/images/service_keychain.png',
      color: '#fb8c00', // orange
      bgColor: 'rgba(251, 140, 0, 0.1)',
      route: '/shop',
      cta: 'Get Item'
    },
    {
      id: 'reminders',
      name: 'Tail Scheduler',
      desc: 'Never miss a vet visit or medication with intelligent scheduling and smart reminders.',
      img: 'assets/images/service_reminders.png',
      color: '#8e24aa', // purple
      bgColor: 'rgba(142, 36, 170, 0.1)',
      route: '/document',
      cta: 'Add Document'
    },
    {
      id: 'notifications',
      name: 'Live Alerts',
      desc: 'Get instant map alerts when your lost pet\'s tag is scanned by anyone with a smartphone.',
      img: 'assets/images/service_notifications.png',
      color: '#1e88e5', // blue
      bgColor: 'rgba(30, 136, 229, 0.1)',
      route: '/profile',
      cta: 'Add Pet'
    },
    {
      id: 'doctor',
      name: 'Tail Care+',
      desc: 'Instant pediatric and behavioral health insights from our advanced AI model for your pet.',
      img: 'assets/images/service_doctor.png',
      color: '#43a047', // emerald
      bgColor: 'rgba(67, 160, 71, 0.1)',
      route: '/doctor-ai',
      cta: 'Visit Doctor'
    },
    {
      id: 'vault',
      name: 'Tail Vault',
      desc: 'Securely store and share all your pet paperwork, vaccinations, and history in one smart cloud.',
      img: 'assets/images/service_vault.png',
      color: '#fbc02d', // gold
      bgColor: 'rgba(251, 192, 45, 0.1)',
      route: '/documents',
      cta: 'Upload Document'
    }
  ];

  nextService(): void {
    this.activeServiceIndex = (this.activeServiceIndex + 1) % this.services.length;
    this.restartServiceTimer();
  }

  prevService(): void {
    this.activeServiceIndex = (this.activeServiceIndex - 1 + this.services.length) % this.services.length;
    this.restartServiceTimer();
  }

  goToService(index: number): void {
    this.activeServiceIndex = index;
    this.restartServiceTimer();
  }

  private startServiceTimer(): void {
    this.serviceTimer = setInterval(() => this.nextService(), this.serviceAutoPlayDuration);
  }

  private restartServiceTimer(): void {
    clearInterval(this.serviceTimer);
    this.startServiceTimer();
  }

  navigateToService(route: string): void {
    this.router.navigate([route]);
  }
  // ───────────────────────────────────────────────────────────────
  // ───────────────────────────────────────────────────────────────

  isScrolled = false;

  @ViewChild('featureVideo', { static: false }) featureVideo!: ElementRef<HTMLVideoElement>;
  @ViewChild('documentsVideo', { static: false }) documentsVideo!: ElementRef<HTMLVideoElement>;

  faqStates: boolean[] = [false, false, false, false];
  isDetailedVideoMuted = true;
  isDetailedVideoPlaying = false;
  isDocumentsVideoMuted = true;
  isDocumentsVideoPlaying = false;

  constructor(private router: Router) { }

  ngAfterViewInit(): void {
    this.startTimer();
    // Wait a bit for video to load
    this.initializeVideo();
    this.initializeDocumentsVideo();
    setTimeout(() => {
      this.isScrolled = window.scrollY > 300;
    }, 100);

    this.startServiceTimer();

    //how it works section scroll animation
    const cards = document.querySelectorAll('.step-card');

    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.2 }
    );
    cards.forEach(card => observer.observe(card));
  }


  toggleFaq(index: number): void {
    this.faqStates[index] = !this.faqStates[index];
  }

  private hasAutoPlayed = false;
  private documentsHasAutoPlayed = false;

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

  // Initialize documents video
  private initializeDocumentsVideo(): void {
    const video = this.documentsVideo?.nativeElement;
    if (!video) return;

    video.muted = true;
    video.autoplay = true;
    video.playsInline = true;
    video.preload = 'auto';
    video.controls = true;

    video.load();

    if (!this.documentsHasAutoPlayed) {
      video.play()
        .then(() => {
          this.documentsHasAutoPlayed = true;
          video.classList.add('playing');
        })
        .catch(err => {
          console.warn('Documents video autoplay blocked:', err);
        });
    }

    video.addEventListener('play', () => this.onDocumentsVideoPlay());
    video.addEventListener('pause', () => this.onDocumentsVideoPause());
    video.addEventListener('ended', () => this.onDocumentsVideoEnded());
  }

  // Play documents video when custom button is clicked
  playDocumentsVideo(event: any): void {
    const container = event.currentTarget.closest('.video-container-premium');
    const video: HTMLVideoElement = container.querySelector('.documents-feature-video');
    const overlay = container.querySelector('.play-button-overlay-luxury');

    if (!video) return;

    video.muted = false;
    video.controls = true;

    video.play().then(() => {
      overlay?.classList.add('hidden');
      video.classList.add('playing');
      this.isDocumentsVideoPlaying = true;
      this.isDocumentsVideoMuted = false;
    });
  }


  // Documents video event handlers
  onDocumentsVideoPlay(): void {
    const playOverlay = document.querySelector('.pet-documents-section .play-button-overlay-luxury');
    if (playOverlay) {
      playOverlay.classList.add('hidden');
    }
  }

  onDocumentsVideoPause(): void {
    const playOverlay = document.querySelector('.pet-documents-section .play-button-overlay-luxury');
    if (playOverlay) {
      playOverlay.classList.remove('hidden');
    }
  }

  onDocumentsVideoEnded(): void {
    const playOverlay = document.querySelector('.pet-documents-section .play-button-overlay-luxury');
    if (playOverlay) {
      playOverlay.classList.remove('hidden');
    }
  }

  toggleDocumentsVideo(): void {
    const video = this.documentsVideo.nativeElement;
    if (video.paused) {
      video.play();
      this.isDocumentsVideoPlaying = true;
    } else {
      video.pause();
      this.isDocumentsVideoPlaying = false;
    }
  }

  toggleDocumentsMute(): void {
    const video = this.documentsVideo.nativeElement;
    video.muted = !video.muted;
    this.isDocumentsVideoMuted = video.muted;
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

  ngOnDestroy(): void {
    clearInterval(this.heroTimer);
    clearInterval(this.serviceTimer);
  }
}