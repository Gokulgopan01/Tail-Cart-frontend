import { Component, OnInit, HostListener, OnDestroy, Inject, PLATFORM_ID,inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, NavigationEnd } from '@angular/router';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { filter, Subscription } from 'rxjs';
import { DOCUMENT } from '@angular/common';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSnackBarConfig } from '@angular/material/snack-bar';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule,MatSnackBarModule],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit, OnDestroy {
  username: string | null = '';
  userId: string | null = '';
  hasProfile = false;
  cartItems = 3; // Default value for demo
  isMobileMenuOpen = false;
  isScrolled = false;
  currentYear: number = new Date().getFullYear();
  showBackToTop = false;
  private routerSubscription!: Subscription;
  private isBrowser: boolean;
  private scrollThreshold = 300; // When to show back-to-top button
  private lastScrollTop = 0;

  @HostListener('window:scroll', [])
  onWindowScroll() {
    if (!this.isBrowser) return;
    
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    this.isScrolled = scrollTop > 20;
    
    // Show/hide back to top button
    this.showBackToTop = scrollTop > this.scrollThreshold;
    
    // Add animation based on scroll direction
    this.handleScrollDirection(scrollTop);
    this.lastScrollTop = scrollTop;
  }

  @HostListener('window:resize', [])
  onWindowResize() {
    if (!this.isBrowser) return;
    
    // Close menu on resize to desktop
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
    this.initializeAnimations();
  }

  ngOnDestroy() {
    if (this.routerSubscription) {
      this.routerSubscription.unsubscribe();
    }
    this.removeMenuOpenClass();
    this.removeScrollRestoration();
  }

  private loadUserData() {
    if (this.isBrowser) {
      this.userId = localStorage.getItem('user_id') || 'Guest';
      this.username = localStorage.getItem('username') || 'Guest User';
      this.hasProfile = !!localStorage.getItem('has_profile');
      
      // Load cart items count
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
    // Handle scroll to top on route changes
    this.routerSubscription = this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.smoothScrollToTop();
        this.closeMobileMenu();
        
        // Reset scroll position for the new route
        if (this.isBrowser) {
          this.saveScrollPosition();
        }
      });
  }

  private setupSmoothScrolling() {
    if (this.isBrowser) {
      // Add smooth scrolling to anchor links
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

      // Prevent default touch behavior that might cause bounce
      this.document.addEventListener('touchmove', (e) => {
        if (e.target instanceof Element && e.target.closest('.mobile-nav-content')) {
          e.preventDefault();
        }
      }, { passive: false });
    }
  }

  private initializeAnimations() {
    if (this.isBrowser) {
      // Add scroll animation to navbar
      window.addEventListener('scroll', () => {
        const navbar = this.document.querySelector('.navbar');
        const mobileNavbar = this.document.querySelector('.mobile-navbar');
        
        if (window.scrollY > 20) {
          navbar?.classList.add('scrolled');
          mobileNavbar?.classList.add('scrolled');
        } else {
          navbar?.classList.remove('scrolled');
          mobileNavbar?.classList.remove('scrolled');
        }
      });
    }
  }

  private handleScrollDirection(currentScrollTop: number) {
    if (!this.isBrowser) return;
    
    const navbar = this.document.querySelector('.navbar');
    const mobileNavbar = this.document.querySelector('.mobile-navbar');
    
    if (currentScrollTop > this.lastScrollTop && currentScrollTop > 100) {
      // Scrolling down
      navbar?.classList.add('hide');
      mobileNavbar?.classList.add('hide');
    } else {
      // Scrolling up
      navbar?.classList.remove('hide');
      mobileNavbar?.classList.remove('hide');
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
    
    // Smooth scroll with easing
    const duration = 800; // ms
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
        // Ensure we're at the very top
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
    
    const duration = 600; // ms
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
      if (this.isBrowser) {
        this.document.body.classList.add('menu-open');
        // Prevent background scrolling when menu is open
        this.document.body.style.overflow = 'hidden';
      }
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
    this.removeMenuOpenClass();
  }

  private removeMenuOpenClass() {
    if (this.isBrowser) {
      this.document.body.classList.remove('menu-open');
      this.document.body.style.overflow = '';
    }
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
      
      // Show logout message
      this.showSnackBar('Loged Out.! Please login to continue', 'success');
      // Navigate to auth page
      this.router.navigate(['/auth']);
      
      // Close mobile menu if open
      this.closeMobileMenu();
    }
  }

  // Add touch device support
  @HostListener('document:touchstart', ['$event'])
  handleTouchStart(event: TouchEvent) {
    if (!this.isBrowser) return;
    
    // Close menu when touching outside on mobile
    if (this.isMobileMenuOpen && 
        !(event.target as Element).closest('.mobile-nav-content') &&
        !(event.target as Element).closest('.menu-toggle')) {
      this.closeMobileMenu();
    }
  }

  // Handle navigation with animations
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