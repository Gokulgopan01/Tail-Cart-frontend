import { Component, HostListener, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements AfterViewInit {
  
  isScrolled = false;
  
  @ViewChild('featureVideo', { static: false }) featureVideo!: ElementRef<HTMLVideoElement>;
  @ViewChild('documentsVideo', { static: false }) documentsVideo!: ElementRef<HTMLVideoElement>;

  faqStates: boolean[] = [false, false, false, false];
  
  constructor(private router: Router) {}
  
  ngAfterViewInit(): void {
    // Wait a bit for video to load
    this.initializeVideo();
    this.initializeDocumentsVideo();
    setTimeout(() => {
      this.isScrolled = window.scrollY > 300;
    }, 100);

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
    const container = event.currentTarget.closest('.video-container');
    const video: HTMLVideoElement = container.querySelector('.documents-feature-video');
    const overlay = container.querySelector('.play-button-overlay');

    if (!video) return;

    video.muted = false;
    video.controls = true;

    video.play().then(() => {
      overlay?.classList.add('hidden');
      video.classList.add('playing');
    });
  }
  
  // Documents video event handlers
  onDocumentsVideoPlay(): void {
    const playOverlay = document.querySelector('.documents-video .play-button-overlay');
    if (playOverlay) {
      playOverlay.classList.add('hidden');
    }
  }
  
  onDocumentsVideoPause(): void {
    const playOverlay = document.querySelector('.documents-video .play-button-overlay');
    if (playOverlay) {
      playOverlay.classList.remove('hidden');
    }
  }
  
  onDocumentsVideoEnded(): void {
    const playOverlay = document.querySelector('.documents-video .play-button-overlay');
    if (playOverlay) {
      playOverlay.classList.remove('hidden');
    }
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
    this.router.navigate(['/alerts']);
  }
  
  navigateToDoctor(): void {
    this.router.navigate(['/doctor-ai']);
  }
  
  // Scroll to top function
  scrollToTop(): void {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
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
}