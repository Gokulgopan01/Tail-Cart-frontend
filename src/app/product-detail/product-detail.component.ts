import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

interface Product {
  id: number;
  product_name: string;
  product_material: string;
  reviews_stars: string;
  colours: string[];
  original_price: string;
  selling_price: string;
  product_long_description: string;
  product_other_specifications: string;
  thumbnail_image: string;
  second_image_1: string;
  in_stock: boolean;
  deals: string;
}

interface Pet {
  pet_id: string | number;
  pet_name: string;
}

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSnackBarModule, RouterLink],
  templateUrl: './product-detail.component.html',
  styleUrls: ['./product-detail.component.css']
})
export class ProductDetailComponent implements OnInit {
  product: Product | null = null;
  isLoading = true;
  mainImage: string = '';

  // Selection State
  userPets: Pet[] = [];
  selectedPetId: string = '';
  quantity: number = 1;
  petSelectError = false;

  private profileApi = 'http://127.0.0.1:8000/api/user/profile/';

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.fetchProduct(id);
      }
    });
    this.fetchUserPets();
  }

  fetchProduct(id: string) {
    this.isLoading = true;
    this.http.get<Product>(`http://127.0.0.1:8000/api/manager/products/${id}/`).subscribe({
      next: (res) => {
        this.product = res;
        this.mainImage = res.thumbnail_image;
        this.isLoading = false;
      },
      error: (err) => {
        this.showSnackbar('Failed to load product details', 'error');
        this.isLoading = false;
      }
    });
  }

  fetchUserPets() {
    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('access_token');
    if (!userId || !token) return;

    this.http.get<any>(`${this.profileApi}?user_id=${userId}`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res) => {
        if (res && res.pets) {
          this.userPets = res.pets;
          if (this.userPets.length > 0) {
            this.selectedPetId = this.userPets[0].pet_id.toString();
          }
        }
      },
      error: (err) => console.error('Failed to load user pets', err)
    });
  }

  setMainImage(imgUrl: string) {
    this.mainImage = imgUrl;
  }

  incrementQuantity() {
    this.quantity++;
  }

  decrementQuantity() {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }

  showSnackbar(message: string, type: 'success' | 'error' = 'success') {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: [`snackbar-${type}`]
    });
  }

  addToCart(): void {
    if (!this.product) return;
    
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      this.showSnackbar('Please log in first', 'error');
      return;
    }

    if (!this.selectedPetId) {
      this.petSelectError = true;
      this.showSnackbar('Please select a pet for this product', 'error');
      return;
    }

    this.petSelectError = false;

    const formData = new FormData();
    formData.append('owner', userId);
    formData.append('pet', this.selectedPetId);
    formData.append('product', this.product.id.toString());
    formData.append('quantity', this.quantity.toString());

    const token = localStorage.getItem('access_token');
    const headers: any = token ? { Authorization: `Bearer ${token}` } : {};

    this.http.post('http://127.0.0.1:8000/api/user/cart/', formData, { headers }).subscribe({
      next: (res: any) => {
        this.showSnackbar(res.message || 'Item added to cart successfully!', 'success');
      },
      error: (err) => {
        this.showSnackbar('Failed to add item to cart', 'error');
      }
    });
  }

  calculateDiscount(original: string, selling: string): number {
    const orig = parseFloat(original);
    const sell = parseFloat(selling);
    if (!orig || orig <= sell) return 0;
    return Math.round(((orig - sell) / orig) * 100);
  }
}
