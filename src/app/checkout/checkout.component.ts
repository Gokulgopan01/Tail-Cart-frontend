import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

interface CartItem {
  cart_id: number;
  product_name: string;
  pet_name: string;
  quantity: number;
  product_price: number;
  product_image?: string;
  status: string;
  product_details?: {
    product_name: string;
    selling_price: string;
    thumbnail_image: string;
  };
}

@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [CommonModule, HttpClientModule, FormsModule, RouterModule, MatSnackBarModule],
  templateUrl: './checkout.component.html',
  styleUrls: ['./checkout.component.css']
})
export class CheckoutComponent implements OnInit {
  cartItems: CartItem[] = [];
  loading = false;
  userId: string | null = '';
  totalAmount = 0;
  readonly API_BASE_URL = 'http://127.0.0.1:8000/api';
  readonly TAX_RATE = 0.18;

  private snackBar = inject(MatSnackBar);

  constructor(private http: HttpClient, private router: Router) { }

  private getHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      }
    };
  }

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id');
    if (!this.userId) {
      this.showSnackBar('Please log in to checkout', 'error');
      this.router.navigate(['/auth']);
      return;
    }
    this.loadCart();
  }

  private showSnackBar(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    this.snackBar.open(message, 'Close', {
      duration: type === 'success' ? 4000 : 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: [`snackbar-${type}`]
    });
  }

  loadCart(): void {
    this.loading = true;
    const url = `${this.API_BASE_URL}/user/cart/?user_id=${this.userId}`;
    this.http.get<CartItem[]>(url, this.getHeaders()).subscribe({
      next: (res) => {
        this.cartItems = res.map(item => {
          const details = item.product_details;
          const rawImageUrl = details?.thumbnail_image || item.product_image;
          return {
            ...item,
            product_name: details?.product_name || item.product_name,
            product_price: details ? parseFloat(details.selling_price) : item.product_price,
            product_image: rawImageUrl?.startsWith('http')
              ? rawImageUrl
              : `http://127.0.0.1:8000${rawImageUrl?.startsWith('/') ? '' : '/'}${rawImageUrl}`
          };
        });
        this.calculateTotal();
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.showSnackBar('Failed to load summary.', 'error');
      }
    });
  }

  placeOrder(): void {
    if (this.cartItems.length === 0) return;
    this.loading = true;
    this.http.post(
      `${this.API_BASE_URL}/user/checkout/`,
      { user: this.userId },
      this.getHeaders()
    ).subscribe({
      next: (res: any) => {
        this.loading = false;
        this.showSnackBar(res.message || 'Order placed successfully!', 'success');
        this.router.navigate(['/myorders']);
      },
      error: (error) => {
        this.loading = false;
        this.showSnackBar('Checkout failed. Please try again.', 'error');
      }
    });
  }

  getSubtotal(): number {
    return this.cartItems.reduce((sum, item) => sum + (item.product_price * item.quantity), 0);
  }

  getTax(): number {
    return Math.round(this.getSubtotal() * this.TAX_RATE);
  }

  calculateTotal(): void {
    this.totalAmount = this.getSubtotal() + this.getTax();
  }

  getTotalItems(): number {
    return this.cartItems.reduce((total, item) => total + item.quantity, 0);
  }
}
