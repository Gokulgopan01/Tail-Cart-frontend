import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { RouterLink, Router } from '@angular/router';
import { Component, OnInit, AfterViewInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import lottie, { AnimationItem } from 'lottie-web';

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
  discount_percentage?: number;
}

interface Pet {
  pet_id: string | number;
  pet_name: string;
}

interface ApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Product[];
}

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSnackBarModule, RouterLink],
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.css']
})
export class ProductsComponent implements OnInit, AfterViewInit, OnDestroy {
  products: Product[] = [];
  filteredProducts: Product[] = [];
  nextPageUrl: string | null = null;
  isLoading = false;
  @ViewChild('quickViewScrollContainer') quickViewScrollContainer!: ElementRef;



  // Empty State Lottie
  private emptyStateAnimation: AnimationItem | null = null;
  @ViewChild('noProductsLottie', { static: false }) set noProductsLottie(el: ElementRef<HTMLDivElement> | undefined) {
    if (el && !this.emptyStateAnimation) {
      this.emptyStateAnimation = lottie.loadAnimation({
        container: el.nativeElement,
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: 'assets/No_products.json'
      });
    } else if (!el && this.emptyStateAnimation) {
      this.emptyStateAnimation.destroy();
      this.emptyStateAnimation = null;
    }
  }

  // UI State
  isGridView = true;
  searchQuery = '';
  selectedMaterial = 'ALL';
  sortOption = 'newest';
  showFilters = false;
  maxPrice = 15000;
  materialOptions = ['ALL', 'Wood', 'Metal', 'Steel', 'Fiber', 'Plastic'];
  selectedColor = 'ALL';
  availableColors: string[] = [];
  cartCount = 0;

  // Quick View State
  showQuickView = false;
  selectedProductForQuickView: Product | null = null;
  activeQvTab: 'about' | 'reviews' | 'closet' = 'about';
  primaryQvImage: string | null = null;

  // Selection State
  userPets: Pet[] = [];
  selectedPetId: string = '';
  petSelectError: boolean = false;
  quantity: number = 1;

  private productsApi = 'http://127.0.0.1:8000/api/manager/products/';
  private profileApi = 'http://127.0.0.1:8000/api/user/profile/';

  constructor(private http: HttpClient, private snackBar: MatSnackBar, private router: Router) { }

  ngOnInit() {
    this.fetchProducts();
    this.fetchCartCount();
    this.fetchUserPets();
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

  fetchProducts(url: string = this.productsApi) {
    if (this.isLoading) return;
    this.isLoading = true;

    this.http.get<ApiResponse>(url).subscribe({
      next: (res) => {
        const newProducts = res.results.map(p => ({
          ...p,
          discount_percentage: this.calculateDiscount(p.original_price, p.selling_price)
        }));

        if (url === this.productsApi) {
          this.products = newProducts;
        } else {
          this.products = [...this.products, ...newProducts];
        }

        this.nextPageUrl = res.next;
        this.extractUniqueColors();
        this.applyFilters();
        this.isLoading = false;
      },
      error: (err) => {
        this.showSnackbar('Failed to load products', 'error');
        this.isLoading = false;
      }
    });
  }

  calculateDiscount(original: string, selling: string): number {
    const orig = parseFloat(original);
    const sell = parseFloat(selling);
    if (!orig || orig <= sell) return 0;
    return Math.round(((orig - sell) / orig) * 100);
  }

  extractUniqueColors() {
    const colorSet = new Set<string>();
    this.products.forEach(p => {
      if (p.colours && Array.isArray(p.colours)) {
        p.colours.forEach(c => colorSet.add(c));
      }
    });
    this.availableColors = Array.from(colorSet);
  }

  applyFilters() {
    let temp = [...this.products];

    // Search filter
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      temp = temp.filter(p => p.product_name.toLowerCase().includes(query));
    }

    // Material filter
    if (this.selectedMaterial !== 'ALL') {
      temp = temp.filter(p => p.product_material === this.selectedMaterial);
    }

    // Color filter
    if (this.selectedColor !== 'ALL') {
      temp = temp.filter(p => p.colours && p.colours.includes(this.selectedColor));
    }

    // Price range filter
    temp = temp.filter(p => parseFloat(p.selling_price) <= this.maxPrice);

    // Sorting
    this.filteredProducts = this.sortProducts(temp);
  }

  sortProducts(list: Product[]): Product[] {
    const sorted = [...list];
    switch (this.sortOption) {
      case 'priceLow': return sorted.sort((a, b) => parseFloat(a.selling_price) - parseFloat(b.selling_price));
      case 'priceHigh': return sorted.sort((a, b) => parseFloat(b.selling_price) - parseFloat(a.selling_price));
      case 'name': return sorted.sort((a, b) => a.product_name.localeCompare(b.product_name));
      default: return sorted.sort((a, b) => b.id - a.id);
    }
  }

  loadMore() {
    if (this.nextPageUrl) {
      this.fetchProducts(this.nextPageUrl);
    }
  }

  setMaterial(material: string) {
    this.selectedMaterial = material;
    this.applyFilters();
  }

  toggleFilters() {
    this.showFilters = !this.showFilters;
    if (this.showFilters) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  }

  setColor(color: string) {
    this.selectedColor = color;
    this.applyFilters();
  }

  clearFilters() {
    this.searchQuery = '';
    this.selectedMaterial = 'ALL';
    this.selectedColor = 'ALL';
    this.maxPrice = 15000;
    this.sortOption = 'newest';
    this.applyFilters();
  }

  toggleViewMode(isGrid: boolean) {
    this.isGridView = isGrid;
  }

  // Quick View Methods
  openQuickView(product: Product, event: Event) {
    event.stopPropagation();
    this.selectedProductForQuickView = product;
    this.primaryQvImage = product.thumbnail_image; // default main image
    this.activeQvTab = 'about'; // reset tab
    this.quantity = 1; // reset quantity
    this.selectedPetId = ''; // default "None"
    this.petSelectError = false;

    this.showQuickView = true;
    document.body.style.overflow = 'hidden'; // Lock scroll
    document.body.classList.add('qv-modal-open'); // Hook for global CSS to hide navbar

    // Reset scroll position to top
    setTimeout(() => {
      if (this.quickViewScrollContainer) {
        this.quickViewScrollContainer.nativeElement.scrollTop = 0;
      }
    }, 100);
  }

  closeQuickView() {
    this.showQuickView = false;
    this.selectedProductForQuickView = null;
    this.primaryQvImage = null;
    document.body.style.overflow = ''; // Unlock scroll
    document.body.classList.remove('qv-modal-open');
  }

  setQvMainImage(imgUrl: string | undefined) {
    if (imgUrl) {
      this.primaryQvImage = imgUrl;
    }
  }

  setQvTab(tab: 'about' | 'reviews' | 'closet') {
    this.activeQvTab = tab;
  }

  incrementQuantity() {
    this.quantity++;
  }

  decrementQuantity() {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }

  ngAfterViewInit() {
    // Banner lottie removed, empty state initializes when needed via ViewChild setter
  }

  ngOnDestroy(): void {
    this.emptyStateAnimation?.destroy();
  }

  showSnackbar(message: string, type: 'success' | 'error' = 'success') {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: [`snackbar-${type}`]
    });
  }

  /** Add product to cart via POST /api/user/cart/ */
  addToCart(product: Product): void {
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
    formData.append('product', product.id.toString());
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

  fetchCartCount() {
    const userId = localStorage.getItem('user_id');
    if (!userId) return;

    // Attempting to fetch cart items for this user
    this.http.get<any>(`http://127.0.0.1:8000/api/user/cart/?owner=${userId}`).subscribe({
      next: (res) => {
        // Handle both Array response or Paginated response
        if (Array.isArray(res)) {
          this.cartCount = res.length;
        } else if (res && typeof res.count === 'number') {
          this.cartCount = res.count;
        }
      },
      error: () => {
        console.warn('Could not fetch cart count');
      }
    });
  }

  buyNow(): void {
    this.closeQuickView();
    this.router.navigate(['/cart']);
  }
}
