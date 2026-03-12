import { Component, OnInit, HostListener } from '@angular/core';
import { Router } from '@angular/router';
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

  constructor(private router: Router) { }

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
    this.isScrolled = window.scrollY > 50;
    this.isPastHalfScreen = window.scrollY > (window.innerHeight / 2);
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