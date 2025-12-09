import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule, MatSnackBarModule],
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css']
})
export class FooterComponent {
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  navigateTo(path: string): void {
    this.router.navigate([path]);
  }

  subscribeNewsletter(email: string): void {
    if (email && this.isValidEmail(email)) {
      this.snackBar.open('Thank you for subscribing to our newsletter!', 'Close', {
        duration: 3000,
        horizontalPosition: 'center',
        verticalPosition: 'top',
        panelClass: ['snackbar-success']
      });
    } else {
      this.snackBar.open('Please enter a valid email address', 'Close', {
        duration: 3000,
        horizontalPosition: 'center',
        verticalPosition: 'top',
        panelClass: ['snackbar-warning']
      });
    }
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Optional: Method to handle quick actions
  handleQuickAction(action: string): void {
    switch (action) {
      case 'contact':
        this.snackBar.open('Redirecting to contact page...', 'Close', {
          duration: 2000,
          horizontalPosition: 'center',
          verticalPosition: 'top'
        });
        setTimeout(() => {
          this.navigateTo('/contact');
        }, 500);
        break;
      case 'shop':
        this.snackBar.open('Opening shop...', 'Close', {
          duration: 2000,
          horizontalPosition: 'center',
          verticalPosition: 'top'
        });
        setTimeout(() => {
          this.navigateTo('/shop');
        }, 500);
        break;
    }
  }
}