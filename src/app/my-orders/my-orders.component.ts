import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';

interface OrderItem {
  product: {
    id: number;
    product_name: string;
    thumbnail_image: string;
    selling_price: string;
  };
  quantity: number;
  price: string;
}

interface Order {
  status: string;
  total_price: string;
  items: OrderItem[];
  showStatus?: boolean; /* for expanding the timeline */
}

@Component({
  selector: 'app-my-orders',
  standalone: true,
  imports: [CommonModule, HttpClientModule, RouterModule],
  templateUrl: './my-orders.component.html',
  styleUrls: ['./my-orders.component.css']
})
export class MyOrdersComponent implements OnInit {
  orders: Order[] = [];
  loading = false;
  userId: string | null = '';
  readonly API_BASE_URL = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) { }

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
    if (this.userId) {
      this.loadOrders();
    }
  }

  loadOrders(): void {
    this.loading = true;
    const url = `${this.API_BASE_URL}/user/myorders/?user_id=${this.userId}`;
    this.http.get<Order[]>(url, this.getHeaders()).subscribe({
      next: (res) => {
        this.orders = res.map(order => ({
          ...order,
          showStatus: false,
          items: order.items.map(item => ({
            ...item,
            product: {
              ...item.product,
              thumbnail_image: item.product.thumbnail_image?.startsWith('http')
                ? item.product.thumbnail_image
                : `http://127.0.0.1:8000${item.product.thumbnail_image?.startsWith('/') ? '' : '/'}${item.product.thumbnail_image}`
            }
          }))
        }));
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  toggleStatus(order: Order): void {
    order.showStatus = !order.showStatus;
  }

  isNormalStatus(status: string | undefined): boolean {
    if (!status) return true;
    const normal = ['Pending', 'Processing', 'Shipped', 'Out for Delivery', 'Delivered'];
    return normal.includes(status);
  }

  getStatusIndex(status: string | undefined): number {
    if (!status) return 0;
    const order = ['Pending', 'Processing', 'Shipped', 'Out for Delivery', 'Delivered'];
    const idx = order.indexOf(status);
    return idx === -1 ? 0 : idx;
  }
}

