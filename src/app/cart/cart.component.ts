import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import Swal from 'sweetalert2';

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
  imports: [CommonModule, FormsModule],
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.css']
})
export class CartComponent implements OnInit {
  cartItems: CartItem[] = [];
  loading = false;
  userId: string | null = '';
  totalAmount = 0;
  readonly TAX_RATE = 0.18;
  errorMessage = '';
  successMessage = '';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id');
    if (!this.userId) {
      Swal.fire('Login Required', 'Please log in to view your cart.', 'warning');
      return;
    }
    this.loadCart();
  }

  /** 🛒 Load all cart items for user */
  loadCart(): void {
    this.loading = true;
    this.http.get<CartItem[]>(`http://127.0.0.1:8000/api/user/cart/?user_id=${this.userId}`)
      .subscribe({
        next: (res) => {
          this.cartItems = res.map(item => ({
            ...item,
            product_image: item.product_image?.startsWith('http')
              ? item.product_image
              : 'http://127.0.0.1:8000' + item.product_image
          }));
          this.calculateTotal();
          this.loading = false;
        },
        error: () => {
          this.loading = false;
          Swal.fire('Error', 'Failed to load cart items.', 'error');
        }
      });
  }

  /** 🔄 Update quantity via buttons */
  updateQuantity(item: CartItem, newQuantity: number): void {
    if (newQuantity < 1 || newQuantity > 10) {
      Swal.fire('Invalid Quantity', 'Quantity must be between 1 and 10.', 'warning');
      return;
    }

    const oldQuantity = item.quantity;
    item.quantity = newQuantity; // Update instantly on UI

    this.http.put(`http://127.0.0.1:8000/api/user/cart/`, {
      user_id: this.userId,
      cart_id: item.cart_id,
      quantity: newQuantity
    }).subscribe({
      next: () => {
        this.calculateTotal();
      },
      error: (err) => {
        item.quantity = oldQuantity;
        console.error('Update quantity error:', err);
        Swal.fire('Error', 'Failed to update quantity. Please try again.', 'error');
      }
    });
  }

  /** 🗑️ Remove item from cart */
  removeItem(item: CartItem): void {
    Swal.fire({
      title: `Remove ${item.product_name}?`,
      text: 'This will delete the item from your cart.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Yes, remove it'
    }).then(result => {
      if (!result.isConfirmed) return;

      this.http.delete(`http://127.0.0.1:8000/api/user/cart/?cart_id=${item.cart_id}`)
        .subscribe({
          next: () => {
            this.cartItems = this.cartItems.filter(i => i.cart_id !== item.cart_id);
            this.calculateTotal();
            Swal.fire('Deleted!', `${item.product_name} removed from cart.`, 'success');
          },
          error: (err) => {
            console.error('Failed to delete item:', err);
            Swal.fire('Error', 'Failed to remove item from cart.', 'error');
          }
        });
    });
  }

  /** 💰 Checkout */
  checkout(): void {
    if (this.cartItems.length === 0) {
      Swal.fire('Empty Cart', 'Your cart is empty!', 'info');
      return;
    }

    const unavailableItems = this.cartItems.filter(
      item => item.status !== 'available' && item.status !== 'pending'
    );
    if (unavailableItems.length > 0) {
      Swal.fire('Unavailable Items', 'Some items are currently unavailable.', 'warning');
      return;
    }

    Swal.fire({
      title: 'Proceed to Checkout?',
      text: `Total: ₹${this.totalAmount.toLocaleString('en-IN')}`,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Yes, Checkout',
      cancelButtonText: 'Cancel',
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33'
    }).then(result => {
      if (!result.isConfirmed) return;

      this.loading = true;
      this.http.post(`http://127.0.0.1:8000/api/checkout/`, {
        user_id: this.userId,
        items: this.cartItems,
        total_amount: this.totalAmount
      }).subscribe({
        next: (res: any) => {
          this.loading = false;
          Swal.fire('Order Placed!', res.message || 'Order placed successfully!', 'success');
          this.cartItems = [];
          this.totalAmount = 0;
        },
        error: (error) => {
          this.loading = false;
          console.error('Checkout error:', error);
          Swal.fire('Checkout Failed', 'Something went wrong. Please try again.', 'error');
        }
      });
    });
  }

  /** 🧮 Totals & Helpers */
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
