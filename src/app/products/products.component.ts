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
  reviews?: Review[];
  review_count?: number;
}

interface Review {
  id: number;
  username: string;
  rating: string;
  comment: string;
  created_at: string;
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

interface Category {
  id: string;
  label: string;
  image: string;
  count: number;
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
  showFilters = false; // mobile filter sheet
  maxPrice = 15000;
  materialOptions = ['ALL', 'Wood', 'Metal', 'Steel', 'Fiber', 'Plastic'];
  selectedColor = 'ALL';
  availableColors: string[] = [];
  cartCount = 0;

  // Quick View State
  showQuickView = false;
  selectedProductForQuickView: Product | null = null;
  activeQvTab: 'about' | 'reviews' = 'about';
  primaryQvImage: string | null = null;
  selectedShadeIndex = 0;

  // Selection State
  userPets: Pet[] = [];
  selectedPetId: string = '';
  petSelectError: boolean = false;
  quantity: number = 1;

  categoryFilter = 'all';
  activeCategory = 'all';

  private productsApi = 'http://127.0.0.1:8000/api/manager/products/';
  private profileApi = 'http://127.0.0.1:8000/api/user/profile/';

  categories: Category[] = [
    {
      id: 'all',
      label: 'All',
      image: 'assets/products/catdog_friends-HomeCover1.png',
      count: 250
    },
    {
      id: 'dogs',
      label: 'Dogs',
      image: 'assets/products/Dog.png',
      count: 120
    },
    {
      id: 'cats',
      label: 'Cats',
      image: 'assets/products/cat.png',
      count: 95
    },
    {
      id: 'food',
      label: 'Food',
      image: 'assets/products/food.png',
      count: 80
    },
    {
      id: 'toys',
      label: 'Toys',
      image: 'assets/products/toys.png',
      count: 65
    },
    {
      id: 'accessories',
      label: 'Accessories',
      image: 'assets/products/accessories.png',
      count: 70
    }
  ];

  constructor(private http: HttpClient, private snackBar: MatSnackBar, private router: Router) { }

  ngOnInit() {
    this.fetchProducts();
    this.fetchCartCount();
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

  calculateOfferPrice(selling: string): number {
    const sell = parseFloat(selling);
    if (!sell) return 0;
    // Extra flat discount shown as "Offer Price" (adjust % as per your business logic)
    return Math.round(sell * 0.7);
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

    // Category filter
    if (this.categoryFilter !== 'all') {
      temp = temp.filter(product =>
        product.product_material?.toLowerCase() === this.categoryFilter.toLowerCase()
      );

      // If your API has a category field, replace the above with:
      // product.category === this.categoryFilter
    }

    // Search
    if (this.searchQuery.trim()) {
      const query = this.searchQuery.toLowerCase();
      temp = temp.filter(product =>
        product.product_name.toLowerCase().includes(query)
      );
    }

    // Material
    if (this.selectedMaterial !== 'ALL') {
      temp = temp.filter(
        product => product.product_material === this.selectedMaterial
      );
    }

    // Color
    if (this.selectedColor !== 'ALL') {
      temp = temp.filter(
        product => product.colours?.includes(this.selectedColor)
      );
    }

    // Price
    temp = temp.filter(
      product => parseFloat(product.selling_price) <= this.maxPrice
    );

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

  selectCategory(categoryId: string): void {
    this.activeCategory = categoryId;
    this.categoryFilter = categoryId;
    this.applyFilters();
  }



  // Count of active filters, used for the mobile filter button badge
  get activeFilterCount(): number {
    let count = 0;
    if (this.selectedMaterial !== 'ALL') count++;
    if (this.selectedColor !== 'ALL') count++;
    if (this.maxPrice < 15000) count++;
    return count;
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
      document.body.classList.add('qv-modal-open');
    } else {
      document.body.style.overflow = '';
      document.body.classList.remove('qv-modal-open');
    }
  }

  setColor(color: string) {
    this.selectedColor = color;
    this.applyFilters();
  }

  setSort(option: string) {
    this.sortOption = option;
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

    // Scroll window to top first to fix the modal positioning issue
    window.scrollTo({ top: 0, behavior: 'smooth' });

    this.selectedProductForQuickView = product;
    this.primaryQvImage = product.thumbnail_image; // default main image
    this.activeQvTab = 'about'; // reset tab
    this.quantity = 1; // reset quantity
    this.selectedPetId = this.userPets.length > 0 ? this.userPets[0].pet_id.toString() : '';
    this.petSelectError = false;
    this.selectedShadeIndex = 0;

    this.showQuickView = true;

    // Delay locking scroll to allow smooth scroll to top to finish
    setTimeout(() => {
      document.body.style.overflow = 'hidden'; // Lock scroll
      document.body.classList.add('qv-modal-open'); // Hook for global CSS to hide navbar
    }, 500);

    // Reset scroll position to top of modal
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

  setQvTab(tab: 'about' | 'reviews') {
    this.activeQvTab = tab;
  }

  setShade(index: number) {
    this.selectedShadeIndex = index;
  }

  incrementQuantity() {
    this.quantity++;
  }

  decrementQuantity() {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }

  // Splits the free-text specifications string into a clean list for display.
  // Accepts newline, pipe, or comma separated values from the API.
  getSpecsList(product: Product | null): string[] {
    const raw = product?.product_other_specifications;
    if (!raw) return [];
    return raw
      .split(/\r?\n|\||;/)
      .map(s => s.trim())
      .filter(s => s.length > 0);
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
    if (!this.selectedProductForQuickView) return;
    if (!this.selectedPetId) {
      this.petSelectError = true;
      this.showSnackbar('Please select a pet for this product', 'error');
      return;
    }
    this.closeQuickView();
    this.router.navigate(['/cart']);
  }
}