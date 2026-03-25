import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

interface TimelineItem {
  label: string;
  date: string | null;
  completed: boolean;
}

interface OrderItem {
  product: {
    id: number;
    product_name: string;
    thumbnail_image: string;
    selling_price: string;
    color?: string;
    size?: string;
  };
  quantity: number;
  price: string;
}

interface Order {
  order_id: number;
  status: string;
  total_price: string;
  items: OrderItem[];
  timeline: TimelineItem[];
  created_at?: string;
  showStatus?: boolean; /* for expanding the timeline (legacy) */
}

@Component({
  selector: 'app-my-orders',
  standalone: true,
  imports: [CommonModule, HttpClientModule, RouterModule, FormsModule],
  templateUrl: './my-orders.component.html',
  styleUrls: ['./my-orders.component.css']
})
export class MyOrdersComponent implements OnInit {
  orders: Order[] = [];
  searchTerm: string = '';
  loading = false;
  showTrackingModal = false;
  selectedTrackingItem: any = null;
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
      next: (res: Order[]) => {
        this.orders = res.map((order: Order) => ({
          ...order,
          showStatus: false,
          items: order.items.map((item: OrderItem) => ({
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

  get flattenedItems() {
    const allItems: any[] = [];
    this.orders.forEach(order => {
      if (order.items && order.items.length > 0) {
        order.items.forEach(item => {
          allItems.push({
            ...item,
            orderId: order.order_id,
            orderStatus: order.status,
            orderDate: order.created_at || new Date().toISOString(),
            showStatus: order.showStatus,
            timeline: order.timeline,
            total_price: order.total_price,
            fullOrder: order
          });
        });
      } else {
        // Handle orders with no items
        allItems.push({
          product: {
            id: 0,
            product_name: `Order #${order.order_id}`,
            thumbnail_image: 'assets/images/photo2.jpg',
            selling_price: order.total_price
          },
          quantity: 0,
          price: order.total_price,
          orderId: order.order_id,
          orderStatus: order.status,
          orderDate: order.created_at || new Date().toISOString(),
          showStatus: order.showStatus,
          timeline: order.timeline,
          total_price: order.total_price,
          fullOrder: order
        });
      }
    });

    // Custom Sorting: Delivered at last, others by date preference
    allItems.sort((a, b) => {
      if (a.orderStatus === 'Delivered' && b.orderStatus !== 'Delivered') return 1;
      if (a.orderStatus !== 'Delivered' && b.orderStatus === 'Delivered') return -1;
      
      const dateA = new Date(a.orderDate).getTime();
      const dateB = new Date(b.orderDate).getTime();
      return dateB - dateA; // Newest first for non-delivered
    });

    if (!this.searchTerm) return allItems;

    const term = this.searchTerm.toLowerCase();
    return allItems.filter(item =>
      item.product.product_name.toLowerCase().includes(term) ||
      item.orderStatus.toLowerCase().includes(term)
    );
  }

  openTracking(item: any): void {
    this.selectedTrackingItem = item;
    this.showTrackingModal = true;
    document.body.style.overflow = 'hidden'; // Prevent scroll
  }

  closeTracking(): void {
    this.showTrackingModal = false;
    this.selectedTrackingItem = null;
    document.body.style.overflow = 'auto';
  }

  cancelOrder(orderId: number): void {
    if (confirm('Are you sure you want to cancel this order?')) {
      console.log('Cancelling order:', orderId);
      // Implementation for cancellation API would go here
      alert('Cancellation request submitted for Order #' + orderId);
    }
  }

  getStatusDate(item: any): any {
    if (!item.timeline || !item.orderStatus) return item.orderDate;
    // Find the step in timeline that matches the current status
    const step = item.timeline.find((s: any) => s.label.toLowerCase() === item.orderStatus.toLowerCase());
    return (step && step.date) ? step.date : item.orderDate;
  }

  isStepCompleted(item: any, stepLabel: string): boolean {
    if (!item || !item.orderStatus) return false;
    const statusOrder = ['Order Placed', 'Confirmed', 'Shipped', 'Out for Delivery', 'Delivered'];
    const currentIdx = statusOrder.findIndex(s => s.toLowerCase() === item.orderStatus.toLowerCase());
    const stepIdx = statusOrder.findIndex(s => s.toLowerCase() === stepLabel.toLowerCase());
    
    // Step is completed if it's at or before the current status,
    // AND if the API also says it's completed (to respect 'Confirmed' being skipped/false)
    const apiStep = item.timeline?.find((s: any) => s.label === stepLabel);
    return stepIdx <= currentIdx && (apiStep ? apiStep.completed : true);
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

