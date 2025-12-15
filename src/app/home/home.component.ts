import { Component, AfterViewInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { Router } from '@angular/router';
import lottie, { AnimationItem } from 'lottie-web';

declare var bootstrap: any;

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

  // Desktop Lottie refs (static: false for hidden elements)
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

  // Initialize bootstrap carousel
  initCarousel() {
    const el = document.getElementById('featuresCarousel');
    if (el) {
      const carousel = new bootstrap.Carousel(el, {
        interval: 4500,
        pause: false,
        touch: true
      });

      // Play Lottie when slide changes
      el.addEventListener('slid.bs.carousel', (event: any) => {
        const activeIndex = event.to;
        const mobileAnimations = [
          this.lottieDocMob, this.lottieCartMob, this.lottieDoctorMob,
          this.lottieProfileMob, this.lottieCommunityMob
        ];
        mobileAnimations.forEach((ref, i) => {
          if (this.animations[5 + i]) this.animations[5 + i].stop();
        });
        if (this.animations[5 + activeIndex]) this.animations[5 + activeIndex].play();
      });

      // Play first mobile Lottie initially
      if (this.animations[5]) this.animations[5].play();
    }
  }

  // Load all Lottie animations
  initAnimations() {
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
          autoplay: true,
          path: item.path
        });
        this.animations.push(anim);
      }
    });
  }

  // Scroll-based play/pause for desktop
  initScrollObserver() {
    this.observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const allCards = Array.from(document.querySelectorAll('.feature-card, .feature-card-mobile'));
        const index = allCards.indexOf(entry.target as Element);
        const animationItem = this.animations[index];
        if (animationItem) {
          if (entry.isIntersecting) animationItem.play();
          else animationItem.stop();
        }
      });
    }, { threshold: 0.2 });

    document.querySelectorAll('.feature-card, .feature-card-mobile').forEach(el => this.observer.observe(el));
  }

  navigateTo(path: string) {
    this.router.navigate([path]);
  }

  navigateToProfile() {
    this.router.navigate(['/profile']);
  }

  ngOnDestroy(): void {
    this.animations.forEach(anim => anim.destroy());
    this.animations = [];
    this.observer.disconnect();
  }
}
