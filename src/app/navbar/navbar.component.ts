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

  constructor(private router: Router) {}

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
    this.isScrolled = window.scrollY > 100;
  }

  toggleMobileMenu() {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  closeMobileMenu() {
    this.isMobileMenuOpen = false;
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/auth']);
    this.closeMobileMenu();
  }
}