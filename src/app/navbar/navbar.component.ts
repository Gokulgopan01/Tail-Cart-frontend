import { Component, OnInit, HostListener } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { HttpClient } from '@angular/common/http';

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
  activeIndex = 0;

  // Mobile sidebar accordion states
  activeSidebarGroup: string | null = null;

  ownerName: string = '';
  ownerPhoto: string = 'assets/icons/nav_profile_icon.jpeg';

  constructor(private router: Router, private http: HttpClient) {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      const url = event.urlAfterRedirects;
      const isPetPublic = url.includes('/pet-public') || url.startsWith('/pet/') || /\/pet\//.test(url);
      this.hideTopNav = url.includes('/profile') || url.includes('/checkout') || url.includes('/product') || url.includes('/shop') || isPetPublic;
      this.hideBottomNav = url.includes('/auth') || url.includes('/product') || url.includes('/checkout') || isPetPublic;
      this.updateActiveIndex(url);

      // Check auth state on navigation (e.g. after login)
      const token = localStorage.getItem('access_token');
      if (token && !this.ownerName) {
        this.fetchUserProfile();
      } else if (!token) {
        this.ownerName = '';
        this.ownerPhoto = 'assets/icons/nav_profile_icon.jpeg';
      }
    });
  }

  toggleSidebarGroup(groupName: string) {
    if (this.activeSidebarGroup === groupName) {
      this.activeSidebarGroup = null;
    } else {
      this.activeSidebarGroup = groupName;
    }
  }


  private updateActiveIndex(url: string) {
    if (url.includes('/home')) this.activeIndex = 0;
    else if (url.includes('/shop')) this.activeIndex = 1;
    else if (url.includes('/document')) this.activeIndex = 2;
    else if (url.includes('/profile')) this.activeIndex = 3;
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

    this.fetchUserProfile();
  }

  fetchUserProfile() {
    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('access_token');
    const headers = { Authorization: `Bearer ${token}` };

    if (userId && token) {
      this.http.get<any>(`http://127.0.0.1:8000/api/user/profile/shared_use/?user_id=${userId}`, { headers })
        .subscribe({
          next: (res) => {
            if (res && res.owner_name) {
              this.ownerName = res.owner_name.split(' ')[0];
            }
            if (res && res.owner_photo) {
              this.ownerPhoto = `http://127.0.0.1:8000${res.owner_photo}`;
            }
          },
          error: (err) => {
            console.error('Error fetching user profile in navbar', err);
          }
        });
    }
  }

  @HostListener('window:scroll', [])
  onWindowScroll() {
    const st = window.scrollY;

    this.isScrolled = st > 50;
    this.isPastHalfScreen = st > (window.innerHeight / 2);

    // Determine scroll direction for hiding navbar
    const isHomePage = this.router.url === '/' || this.router.url.startsWith('/home');
    if (st > this.lastScrollTop && st > 80) {
      // Downscroll code - only hide on home page
      this.isScrollingDown = isHomePage;
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