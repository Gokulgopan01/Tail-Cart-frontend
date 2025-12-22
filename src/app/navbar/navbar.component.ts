import { Component, OnInit, HostListener, OnDestroy, Inject, PLATFORM_ID, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, NavigationEnd } from '@angular/router';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { filter, Subscription } from 'rxjs';
import { DOCUMENT } from '@angular/common';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSnackBarConfig } from '@angular/material/snack-bar';
import { RouterOutlet } from '@angular/router';

// Declare Lottie
declare global {
  interface Window {
    lottie: any;
  }
}

// Page data interface
interface PageData {
  lottieUrl: string;
  title: string;
  subtitle: string;
  showLottie?: boolean;
  lottieHeight?: string;
  titleSize?: string;
}

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule, MatSnackBarModule],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit, OnDestroy {
  username: string | null = '';
  userId: string | null = '';
  hasProfile = false;
  cartItems = 3;
  isMobileMenuOpen = false;
  isScrolled = false;
  currentYear: number = new Date().getFullYear();
  showBackToTop = false;
  
  // Page-specific data
  currentPageData: PageData | null = null;
  private lottieAnimation: any = null;
  private mobileLottieAnimation: any = null;
  private isLottieLoaded = false;
  
  // Page data configuration
  private pageDataMap: { [key: string]: PageData } = {
    
    '/auth': {
      lottieUrl: 'assets/Login_banner.json', // This should work
      title: 'Let\'s Go',
      subtitle: 'Your Pet\'s Ultimate Digital Companion',
      showLottie: true,
      lottieHeight: '200px',
      titleSize: '3rem'
    },

      '/': {
      lottieUrl: 'assets/Login_banner.json',
      title: "Let\'s Go",
      subtitle: "Your Pet\'s Ultimate Digital Companion",
      showLottie: true,
      lottieHeight: '200px',
      titleSize: '3rem'
    },

    '/home': {
      lottieUrl: 'assets/home_banner.json',
      title: 'Pet\'s Digital Home',
      subtitle: 'Manage care, shop smarter, and stay organized.',
      showLottie: true,
      lottieHeight: '200px',
      titleSize: '3rem'
    },

    '/shop': {
      lottieUrl: 'assets/shop_page_banner.json',
      title: 'Pet Accessories',
      subtitle: 'Thoughtfully designed items for your pet.',
      showLottie: true,
      lottieHeight: '180px',
      titleSize: '2.5rem'
    },
    
    '/document': {
      lottieUrl: 'assets/document_banner.json',
      title: 'Records & Reminders',
      subtitle: 'Manage documents, track vaccinations, and set reminders.',
      showLottie: true,
      lottieHeight: '160px'
    },

    '/doctor-ai': {
      lottieUrl: 'assets/Doctor_AI.json',
      title: 'Pet Care Assistant',
      subtitle: 'Ask questions. Get instant pet health insights.',
      showLottie: true,
      lottieHeight: '180px'
    },
    
    '/contact': {
      lottieUrl: 'assets/Contact_Us.json',
      title: 'Talk to Us!',
      subtitle: 'Let’s make your pet’s day paw-some 🐾',
      showLottie: true,
      lottieHeight: '170px'
    },

    '/cart': {
      lottieUrl: 'https://assets10.lottiefiles.com/packages/lf20_57TxAX.json',
      title: 'Cart-tastic!',
      subtitle: 'Stay on top of your pet shopping adventures',
      showLottie: true,
      lottieHeight: '150px'
    },

    '/profile': {
      lottieUrl: 'https://assets10.lottiefiles.com/packages/lf20_6xfqjauq.json',
      title: 'Me & My Pet',
      subtitle: 'Update your info and pamper your furry companion',
      showLottie: true,
      lottieHeight: '160px'
    }
  };

  private routerSubscription!: Subscription;
  private isBrowser: boolean;
  private scrollThreshold = 300;
  private lastScrollTop = 0;

  @HostListener('window:scroll', [])
  onWindowScroll() {
  // if (this.isMobileMenuOpen) return;

  // const currentScroll =
  //   window.pageYOffset || document.documentElement.scrollTop;

  // if (currentScroll > this.lastScrollTop && currentScroll > 80) {
  //   this.isScrolled = true;
  // } else {
  //   this.isScrolled = false;
  // }

  // this.lastScrollTop = Math.max(currentScroll, 0);
  const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
  this.showBackToTop = scrollPosition > 300;
  this.lastScrollTop = scrollPosition;

}

  @HostListener('window:resize', [])
  onWindowResize() {
    if (!this.isBrowser) return;
    
    if (window.innerWidth > 768 && this.isMobileMenuOpen) {
      this.closeMobileMenu();
    }
  }

  constructor(
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object,
    @Inject(DOCUMENT) private document: Document
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  ngOnInit() {
    this.loadUserData();
    this.setupRouterEvents();
    this.setupSmoothScrolling();
    this.loadLottieScript();
    this.setCurrentPageData(this.router.url);
  }

  ngOnDestroy() {
    if (this.routerSubscription) {
      this.routerSubscription.unsubscribe();
    }
    this.removeMenuOpenClass();
    this.removeScrollRestoration();
    
    if (this.lottieAnimation) {
      this.lottieAnimation.destroy();
    }
    if (this.mobileLottieAnimation) {
      this.mobileLottieAnimation.destroy();
    }
  }

  private loadLottieScript(): void {
    if (this.isBrowser && !this.isLottieLoaded) {
      const script = this.document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js';
      script.onload = () => {
        this.isLottieLoaded = true;
        // Load animation after script is loaded
        if (this.currentPageData) {
          this.loadLottieAnimation(this.currentPageData.lottieUrl);
          this.loadMobileLottieAnimation(this.currentPageData.lottieUrl);
        }
      };
      this.document.head.appendChild(script);
    }
  }

  private setCurrentPageData(url: string): void {
    const basePath = url.split('?')[0].split('#')[0];
    const pageData = this.pageDataMap[basePath];
    
    if (pageData) {
      this.currentPageData = pageData;
      if (this.isLottieLoaded) {
        this.loadLottieAnimation(pageData.lottieUrl);
        this.loadMobileLottieAnimation(pageData.lottieUrl);
      }
    } else {
      this.currentPageData = {
        lottieUrl: 'https://assets10.lottiefiles.com/packages/lf20_gn0tojcq.json',
        title: 'Tail Cart',
        subtitle: 'Your Pet\'s Digital Companion',
        showLottie: true,
        lottieHeight: '180px'
      };
      if (this.isLottieLoaded) {
        this.loadLottieAnimation(this.currentPageData.lottieUrl);
        this.loadMobileLottieAnimation(this.currentPageData.lottieUrl);
      }
    }
  }

  private loadLottieAnimation(url: string): void {
    if (!this.isBrowser || !window.lottie) return;

    if (this.lottieAnimation) {
      this.lottieAnimation.destroy();
    }

    const container = this.document.querySelector('.lottie-container');
    if (!container) return;

    container.innerHTML = '';

    try {
      this.lottieAnimation = window.lottie.loadAnimation({
        container: container,
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: url,
        rendererSettings: {
          progressiveLoad: true,
          hideOnTransparent: true
        }
      });
    } catch (error) {
      console.error('Error loading desktop Lottie:', error);
    }
  }

  private loadMobileLottieAnimation(url: string): void {
    if (!this.isBrowser || !window.lottie) return;

    if (this.mobileLottieAnimation) {
      this.mobileLottieAnimation.destroy();
    }

    const container = this.document.querySelector('.mobile-lottie-container');
    if (!container) return;

    container.innerHTML = '';

    try {
      this.mobileLottieAnimation = window.lottie.loadAnimation({
        container: container,
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: url,
        rendererSettings: {
          progressiveLoad: true,
          hideOnTransparent: true
        }
      });
    } catch (error) {
      console.error('Error loading mobile Lottie:', error);
    }
  }

  private loadUserData() {
    if (this.isBrowser) {
      this.userId = localStorage.getItem('user_id') || 'Guest';
      this.username = localStorage.getItem('username') || 'Guest User';
      this.hasProfile = !!localStorage.getItem('has_profile');
      
      const cartData = localStorage.getItem('cart_items');
      if (cartData) {
        try {
          this.cartItems = JSON.parse(cartData).length;
        } catch (e) {
          this.cartItems = 0;
        }
      }
    }
  }

  private setupRouterEvents() {
  this.routerSubscription = this.router.events
    .pipe(filter(event => event instanceof NavigationEnd))
    .subscribe((event: any) => {
      // Reset scroll state
      this.isScrolled = false;  // ADD THIS LINE
      
      this.smoothScrollToTop();
      this.closeMobileMenu();
      this.setCurrentPageData(event.urlAfterRedirects || event.url);
      
      if (this.isBrowser) {
        this.saveScrollPosition();
      }
    });
}

  private setupSmoothScrolling() {
    if (this.isBrowser) {
      this.document.addEventListener('click', (event) => {
        const target = event.target as HTMLElement;
        const link = target.closest('a[href^="#"]');
        
        if (link && link.getAttribute('href') !== '#') {
          event.preventDefault();
          const targetId = link.getAttribute('href')?.substring(1);
          if (targetId) {
            const targetElement = this.document.getElementById(targetId);
            if (targetElement) {
              this.smoothScrollToElement(targetElement);
            }
          }
        }
      });

      
    }
  }


  smoothScrollToTop(instant: boolean = false) {
    if (!this.isBrowser) return;
    
    if (instant) {
      window.scrollTo({ top: 0 });
      this.document.documentElement.scrollTop = 0;
      this.document.body.scrollTop = 0;
      return;
    }
    
    const duration = 800;
    const start = window.pageYOffset;
    const startTime = performance.now();
    
    const easeInOutCubic = (t: number): number => {
      return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    };
    
    const animateScroll = (currentTime: number) => {
      const elapsedTime = currentTime - startTime;
      const progress = Math.min(elapsedTime / duration, 1);
      const easeProgress = easeInOutCubic(progress);
      
      window.scrollTo(0, start * (1 - easeProgress));
      
      if (progress < 1) {
        requestAnimationFrame(animateScroll);
      } else {
        this.document.documentElement.scrollTop = 0;
        this.document.body.scrollTop = 0;
      }
    };
    
    requestAnimationFrame(animateScroll);
  }

  smoothScrollToElement(element: HTMLElement, offset: number = 80) {
    if (!this.isBrowser) return;
    
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;
    
    const duration = 600;
    const start = window.pageYOffset;
    const distance = offsetPosition - start;
    const startTime = performance.now();
    
    const easeInOutCubic = (t: number): number => {
      return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    };
    
    const animateScroll = (currentTime: number) => {
      const elapsedTime = currentTime - startTime;
      const progress = Math.min(elapsedTime / duration, 1);
      const easeProgress = easeInOutCubic(progress);
      
      window.scrollTo(0, start + distance * easeProgress);
      
      if (progress < 1) {
        requestAnimationFrame(animateScroll);
      }
    };
    
    requestAnimationFrame(animateScroll);
  }

  private saveScrollPosition() {
    if (this.isBrowser) {
      const scrollPosition = window.pageYOffset || this.document.documentElement.scrollTop;
      localStorage.setItem('scrollPosition', scrollPosition.toString());
    }
  }

  private removeScrollRestoration() {
    if (this.isBrowser) {
      localStorage.removeItem('scrollPosition');
    }
  }

  toggleMobileMenu() {
  this.isMobileMenuOpen = !this.isMobileMenuOpen;
  
  if (this.isMobileMenuOpen) {
    // Prevent body scroll when menu is open
    this.document.body.classList.add('menu-open');
    
    // Add a slight delay for smooth animation
    setTimeout(() => {
      const bottomSheet = this.document.querySelector('.mobile-bottom-sheet');
      if (bottomSheet) {
        bottomSheet.classList.add('active');
      }
    }, 10);
  } else {
    this.closeMobileMenu();
  }
}

  onNavLinkClick() {
    this.smoothScrollToTop();
    this.closeMobileMenu();
  }

  closeMobileMenu() {
  this.isMobileMenuOpen = false;
  
  // Remove active class with animation
  const bottomSheet = this.document.querySelector('.mobile-bottom-sheet');
  if (bottomSheet) {
    bottomSheet.classList.remove('active');
  }
  
  // Remove menu-open class after animation completes
  setTimeout(() => {
    this.removeMenuOpenClass();
  }, 400); // Match this with CSS transition duration
}

  private removeMenuOpenClass() {
  this.document.body.classList.remove('menu-open');
}

  
  navigateToProfile(): void {
    this.router.navigate(['/profile']);
    this.smoothScrollToTop();
  }

  private snackBar = inject(MatSnackBar);

  private showSnackBar(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
    const config: MatSnackBarConfig = {
      duration: type === 'error' || type === 'warning' ? 5000 : 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: [`snackbar-${type}`],
      politeness: 'polite'
    };
    
    this.snackBar.open(message, 'Close', config);
  }

  logout(): void {
    if (this.isBrowser) {
      localStorage.clear();
      sessionStorage.clear();
      
      this.showSnackBar('Logged Out! Please login to continue', 'success');
      this.router.navigate(['/auth']);
      
      this.closeMobileMenu();
    }
  }

  @HostListener('document:touchstart', ['$event'])
handleTouchStart(event: TouchEvent) {
  if (!this.isBrowser) return;
  
  if (this.isMobileMenuOpen && 
      !(event.target as Element).closest('.mobile-bottom-sheet') &&
      !(event.target as Element).closest('.menu-toggle') &&
      !(event.target as Element).closest('.sheet-handle')) {
    this.closeMobileMenu();
  }
}

  handleNavigation(route: string, anchor?: string) {
    this.router.navigate([route]).then(() => {
      if (anchor) {
        setTimeout(() => {
          const element = this.document.getElementById(anchor);
          if (element) {
            this.smoothScrollToElement(element);
          }
        }, 100);
      } else {
        this.smoothScrollToTop();
      }
    });
    
    this.closeMobileMenu();
  }
}