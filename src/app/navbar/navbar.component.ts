import { Component, OnInit , HostListener} from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],   // <-- add this
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  username: string | null = '';
  userId: string | null = '';
  hasProfile = false;
  cartItems = 0; 
  isMobileMenuOpen = false;
  isScrolled = false;

   @HostListener('window:scroll', [])
  onWindowScroll() {
    this.isScrolled = window.scrollY > 50;
  }

  @HostListener('window:resize', [])
  onWindowResize() {
    // Close menu on resize to desktop
    if (window.innerWidth > 768 && this.isMobileMenuOpen) {
      this.closeMobileMenu();
    }
  }

  @HostListener('document:click', ['$event'])
onDocumentClick(event: Event) {
  // Close mobile menu when clicking outside
  if (this.isMobileMenuOpen && 
      !(event.target as Element).closest('.mobile-navbar') &&
      !(event.target as Element).closest('.nav-links-container')) {
    this.closeMobileMenu();
  }
}

  constructor(private router: Router) {}

   ngOnInit() {
        this.addScrollEffect();
  }

  toggleMobileMenu() {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
    
    if (this.isMobileMenuOpen) {
      document.body.classList.add('menu-open');
    } else {
      document.body.classList.remove('menu-open');
    }
  }

  onNavLinkClick() {
    if (this.isMobileMenuOpen) {
      this.closeMobileMenu();
    }
  }

  

  closeMobileMenu() {
    this.isMobileMenuOpen = false;
    document.body.classList.remove('menu-open');
  }

  addScrollEffect() {
        window.addEventListener('scroll', () => {
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {
                navbar?.classList.add('scrolled');
            } else {
                navbar?.classList.remove('scrolled');
            }
        });
  }
  
  navigateToProfile(): void {
    this.router.navigate(['/profile']);
  }

  logout(): void {
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    this.router.navigate(['/auth']);
  }
}
