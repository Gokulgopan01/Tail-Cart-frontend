import { Component, OnInit, HostListener } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  cartItems = 3;
  isMobileMenuOpen = false;
  isScrolled = false;
  isPastHalfScreen = false;
  hideTopNav = false;
  hideBottomNav = false;
  
  lastScrollTop = 0;
  isScrollingDown = false;

  constructor(private router: Router) {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      const url = event.urlAfterRedirects;
      this.hideTopNav = url.includes('/profile') || url.includes('/checkout') || url.includes('/shop');
      this.hideBottomNav = url.includes('/checkout');
    });
  }

  ngOnInit() {
    // Load cart items from localStorage if needed
    const savedCart = localStorage.getItem('cart_items');
    if (savedCart) {
      try {
        this.cartItems = JSON.parse(savedCart).length;
      } catch (e) {
        this.cartItems = 0;
      }
    }
  }

  @HostListener('window:scroll', [])
  onWindowScroll() {
    const st = window.scrollY;
    
    this.isScrolled = st > 50;
    this.isPastHalfScreen = st > (window.innerHeight / 2);
    
    // Determine scroll direction for hiding navbar
    if (st > this.lastScrollTop && st > 80) {
      // Downscroll code
      this.isScrollingDown = true;
    } else {
      // Upscroll code
      this.isScrollingDown = false;
    }
    this.lastScrollTop = st <= 0 ? 0 : st; // For Mobile or negative scrolling
  }

  toggleMobileMenu() {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  closeMobileMenu() {
    this.isMobileMenuOpen = false;
  }

  navigateToHome() {
    this.router.navigate(['/home']);
    this.closeMobileMenu();
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/auth']);
    this.closeMobileMenu();
  }
}