import { Component, OnInit, inject,AfterViewInit  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSnackBarConfig } from '@angular/material/snack-bar';

interface CartItem {
  cart_id: number;
  product_name: string;
  pet_name: string;
  quantity: number;
  product_price: number;
  status: string;
  product_image?: string;
  created_at: string;
  updated_at: string;
  owner: number;
  pet: number;
  product: number;
}

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [CommonModule, HttpClientModule, FormsModule, RouterModule, MatSnackBarModule],
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.css']
})
export class CartComponent implements OnInit, AfterViewInit  {
  cartItems: CartItem[] = [];
  loading = false;
  userId: string | null = '';
  totalAmount = 0;
  readonly API_BASE_URL = 'https://tailcart1.duckdns.org/api';
  readonly TAX_RATE = 0.18;

  
  private snackBar = inject(MatSnackBar);
  private getHeaders() {
  const token = localStorage.getItem('access_token');


  return {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  };
}

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    console.log('🎬 CartComponent ngOnInit() called');
    console.log('📍 Current URL:', window.location.href);
    
    // Check all localStorage
    console.log('📦 localStorage contents:');
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      const value = localStorage.getItem(key!);
      console.log(`${key}: ${value}`);
    }
    
    this.userId = localStorage.getItem('user_id');
    console.log('👤 User ID from localStorage:', this.userId);
    
    if (!this.userId) {
      console.warn('⚠️ No user ID found in localStorage');
      this.showSnackBar('Please log in to view your cart', 'error');
      // Try to redirect to login
      window.location.href = '/auth';
      return;
    }
    
    console.log('🔄 Starting to load cart...');
    
    // Test if component is actually rendered
    setTimeout(() => {
      console.log('⏰ Component should be rendered by now');
      this.loadCart();
    }, 100);
  }
  ngAfterViewInit(): void {
    console.log('🖼️ CartComponent ngAfterViewInit() called');
  }


  /** Show snackbar notification */
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

  /** Load cart items */
    loadCart(): void {
      this.loading = true;

      const url = `${this.API_BASE_URL}/user/cart/?user_id=${this.userId}`;

      this.http.get<CartItem[]>(url, this.getHeaders())
        .subscribe({
          next: (res) => {
            this.cartItems = res.map(item => ({
              ...item,
              product_image: item.product_image?.startsWith('http')
                ? item.product_image
                : `https://tailcart1.duckdns.org/${item.product_image}`
            }));
            this.calculateTotal();
            this.loading = false;
          },
          error: () => {
            this.loading = false;
            this.showSnackBar('Failed to load cart items.', 'error');
          }
        });
    }


  /** Update item quantity */
  updateQuantity(item: CartItem, newQuantity: number): void {
    if (newQuantity < 1 || newQuantity > 10) {
      this.showSnackBar('Quantity must be between 1 and 10', 'warning');
      return;
    }

    const oldQuantity = item.quantity;
    item.quantity = newQuantity;

    this.http.put(
  `${this.API_BASE_URL}/user/cart/`,
  {
    user_id: this.userId,
    cart_id: item.cart_id,
    quantity: newQuantity
  },
  this.getHeaders()
).subscribe({
      next: () => {
        this.calculateTotal();
        this.showSnackBar(`Quantity updated to ${newQuantity}`, 'success');
      },
      error: (err) => {
        item.quantity = oldQuantity;
        console.error('Update quantity error:', err);
        this.showSnackBar('Failed to update quantity. Please try again.', 'error');
      }
    });
  }

  /** Remove item from cart */
  removeItem(item: CartItem): void {
    const snackBarRef = this.snackBar.open(
      `Remove "${item.product_name}" from cart?`,
      'Confirm',
      {
        horizontalPosition: 'right',
        verticalPosition: 'top',
        duration: 5000,
        panelClass: ['snackbar-warning']
      }
    );

    snackBarRef.onAction().subscribe(() => {
      this.http.delete(
        `${this.API_BASE_URL}/user/cart/?cart_id=${item.cart_id}`,
        this.getHeaders()
      )
        .subscribe({
          next: () => {
            this.cartItems = this.cartItems.filter(i => i.cart_id !== item.cart_id);
            this.calculateTotal();
            this.showSnackBar(`"${item.product_name}" removed from cart`, 'success');
          },
          error: (err) => {
            console.error('Failed to delete item:', err);
            this.showSnackBar('Failed to remove item. Please try again.', 'error');
          }
        });
    });
  }

  /** Checkout process */
  checkout(): void {
    if (this.cartItems.length === 0) {
      this.showSnackBar('Your cart is empty! Add items to checkout.', 'info');
      return;
    }

    const unavailableItems = this.cartItems.filter(
      item => item.status !== 'available' && item.status !== 'pending'
    );
    
    if (unavailableItems.length > 0) {
      this.showSnackBar('Some items are currently unavailable. Please remove them to proceed.', 'warning');
      return;
    }

    const formattedTotal = this.formatCurrency(this.totalAmount);
    const snackBarRef = this.snackBar.open(
      `Proceed to checkout? Total: ${formattedTotal}`,
      'Confirm',
      {
        horizontalPosition: 'right',
        verticalPosition: 'top',
        duration: 5000,
        panelClass: ['snackbar-info']
      }
    );

    snackBarRef.onAction().subscribe(() => {
      this.loading = true;
      this.http.post(
  `${this.API_BASE_URL}/checkout/`,
  {
    user_id: this.userId,
    items: this.cartItems,
    total_amount: this.totalAmount
  },
  this.getHeaders()
).subscribe({
        next: (res: any) => {
          this.loading = false;
          this.showSnackBar(res.message || 'Order placed successfully! Thank you for your purchase.', 'success');
          this.cartItems = [];
          this.totalAmount = 0;
        },
        error: (error) => {
          this.loading = false;
          console.error('Checkout error:', error);
          this.showSnackBar('Checkout failed. Please try again.', 'error');
        }
      });
    });
  }

  /** Calculate totals */
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

  formatCurrency(amount: number): string {
    return `₹${amount.toLocaleString('en-IN')}`;
  }
}