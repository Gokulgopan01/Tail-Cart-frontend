import { Component, AfterViewInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { Router } from '@angular/router';
import lottie, { AnimationItem } from 'lottie-web';

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements AfterViewInit, OnDestroy {

  hasProfile = false;
  private observer!: IntersectionObserver;
  private animations: AnimationItem[] = [];

  // Desktop Lottie refs
  @ViewChild('lottieDoc', { static: false }) lottieDoc!: ElementRef<HTMLDivElement>;
  @ViewChild('lottieCart', { static: false }) lottieCart!: ElementRef<HTMLDivElement>;
  @ViewChild('lottieDoctor', { static: false }) lottieDoctor!: ElementRef<HTMLDivElement>;
  @ViewChild('lottieProfile', { static: false }) lottieProfile!: ElementRef<HTMLDivElement>;
  @ViewChild('lottieCommunity', { static: false }) lottieCommunity!: ElementRef<HTMLDivElement>;

  // Mobile Lottie refs
  @ViewChild('lottieDocMob', { static: false }) lottieDocMob!: ElementRef<HTMLDivElement>;
  @ViewChild('lottieCartMob', { static: false }) lottieCartMob!: ElementRef<HTMLDivElement>;
  @ViewChild('lottieDoctorMob', { static: false }) lottieDoctorMob!: ElementRef<HTMLDivElement>;
  @ViewChild('lottieProfileMob', { static: false }) lottieProfileMob!: ElementRef<HTMLDivElement>;
  @ViewChild('lottieCommunityMob', { static: false }) lottieCommunityMob!: ElementRef<HTMLDivElement>;

  constructor(private router: Router) {}

  ngAfterViewInit(): void {
    this.initAnimations();
    this.initCarousel();
    this.initScrollObserver();
  }

  // Initialize modern carousel
  initCarousel(): void {
    const carousel = document.getElementById('featuresCarousel');
    const dots = document.querySelectorAll('.carousel-dot');
    
    if (!carousel) return;
    
    // Update active dot on scroll
    carousel.addEventListener('scroll', () => {
      const slideIndex = Math.round(carousel.scrollLeft / carousel.offsetWidth);
      this.updateActiveDot(slideIndex);
      this.playMobileAnimation(slideIndex);
    });
    
    // Dot click navigation
    dots.forEach((dot, index) => {
      dot.addEventListener('click', () => {
        this.goToSlide(index);
      });
    });
    
    // Auto scroll every 5 seconds
    setInterval(() => {
      this.autoScrollCarousel();
    }, 5000);
    
    // Play first slide animation
    if (this.animations[5]) this.animations[5].play();
  }
  
  // Auto scroll carousel
  autoScrollCarousel(): void {
    const carousel = document.getElementById('featuresCarousel');
    if (!carousel) return;
    
    const slideWidth = carousel.offsetWidth;
    const currentIndex = Math.round(carousel.scrollLeft / slideWidth);
    const nextIndex = (currentIndex + 1) % 5;
    
    this.goToSlide(nextIndex);
  }
  
  // Go to specific slide
  goToSlide(index: number): void {
    const carousel = document.getElementById('featuresCarousel');
    if (carousel) {
      const slideWidth = carousel.offsetWidth;
      carousel.scrollTo({
        left: slideWidth * index,
        behavior: 'smooth'
      });
      this.updateActiveDot(index);
      this.playMobileAnimation(index);
    }
  }
  
  // Update active dot
  updateActiveDot(index: number): void {
    const dots = document.querySelectorAll('.carousel-dot');
    dots.forEach((dot, i) => {
      if (i === index) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });
  }
  
  // Play Lottie animation for current slide
  playMobileAnimation(index: number): void {
    // Stop all mobile animations
    for (let i = 5; i < this.animations.length; i++) {
      if (this.animations[i]) this.animations[i].stop();
    }
    // Play animation for current slide
    if (this.animations[5 + index]) {
      this.animations[5 + index].play();
    }
  }

  // Load all Lottie animations
  initAnimations(): void {
    const desktopAnimations = [
      { ref: this.lottieDoc, path: 'assets/manage_docs.json' },
      { ref: this.lottieCart, path: 'assets/buy_product.json' },
      { ref: this.lottieDoctor, path: 'assets/pet_doctor.json' },
      { ref: this.lottieProfile, path: 'assets/manage_pets.json' },
      { ref: this.lottieCommunity, path: 'assets/pet_community.json' }
    ];

    const mobileAnimations = [
      { ref: this.lottieDocMob, path: 'assets/manage_docs.json' },
      { ref: this.lottieCartMob, path: 'assets/buy_product.json' },
      { ref: this.lottieDoctorMob, path: 'assets/pet_doctor.json' },
      { ref: this.lottieProfileMob, path: 'assets/manage_pets.json' },
      { ref: this.lottieCommunityMob, path: 'assets/pet_community.json' }
    ];

    [...desktopAnimations, ...mobileAnimations].forEach(item => {
      if (item.ref?.nativeElement) {
        const anim = lottie.loadAnimation({
          container: item.ref.nativeElement,
          renderer: 'svg',
          loop: true,
          autoplay: false,
          path: item.path
        });
        this.animations.push(anim);
      }
    });
  }

  // Scroll observer for animations
  initScrollObserver(): void {
    this.observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const allCards = Array.from(document.querySelectorAll('.feature-card, .carousel-slide'));
        const index = allCards.indexOf(entry.target as Element);
        const animationItem = this.animations[index];
        if (animationItem) {
          if (entry.isIntersecting) animationItem.play();
          else animationItem.stop();
        }
      });
    }, { threshold: 0.2 });

    document.querySelectorAll('.feature-card, .carousel-slide').forEach(el => this.observer.observe(el));
  }

  navigateTo(path: string): void {
    this.router.navigate([path]);
  }

  navigateToProfile(): void {
    this.router.navigate(['/profile']);
  }

  ngOnDestroy(): void {
    this.animations.forEach(anim => anim.destroy());
    this.animations = [];
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}