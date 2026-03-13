import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, AfterViewInit, HostListener, ViewChild, ElementRef, OnDestroy } from '@angular/core';
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

interface ApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Product[];
}

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSnackBarModule],
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.css']
})
export class ProductsComponent implements OnInit, AfterViewInit, OnDestroy {
  products: Product[] = [];
  filteredProducts: Product[] = [];
  nextPageUrl: string | null = null;
  isLoading = false;

  // Banner
  @ViewChild('shopBannerLottie', { static: true })
  shopBannerLottie!: ElementRef<HTMLDivElement>;
  private bannerAnimation: AnimationItem | null = null;

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

  // Quick View State
  showQuickView = false;
  selectedProductForQuickView: Product | null = null;
  currentQuickImageIndex = 0;

  private productsApi = 'http://127.0.0.1:8000/api/manager/products/';

  constructor(private http: HttpClient, private snackBar: MatSnackBar) { }

  ngOnInit() {
    this.fetchProducts();
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
  }

  clearFilters() {
    this.searchQuery = '';
    this.selectedMaterial = 'ALL';
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
    this.currentQuickImageIndex = 0;
    this.showQuickView = true;
    document.body.style.overflow = 'hidden'; // Lock scroll
  }

  closeQuickView() {
    this.showQuickView = false;
    this.selectedProductForQuickView = null;
    document.body.style.overflow = ''; // Unlock scroll
  }

  nextQuickImage() {
    if (this.selectedProductForQuickView) {
      this.currentQuickImageIndex = (this.currentQuickImageIndex + 1) % 2;
    }
  }

  prevQuickImage() {
    if (this.selectedProductForQuickView) {
      this.currentQuickImageIndex = this.currentQuickImageIndex === 0 ? 1 : 0;
    }
  }

  ngAfterViewInit() {
    this.bannerAnimation = lottie.loadAnimation({
      container: this.shopBannerLottie.nativeElement,
      renderer: 'svg',
      loop: true,
      autoplay: true,
      path: 'assets/Shoping_Website.json'
    });
  }

  ngOnDestroy(): void {
    this.bannerAnimation?.destroy();
    this.emptyStateAnimation?.destroy();
  }

  showSnackbar(message: string, type: 'success' | 'error' = 'success') {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: [`snackbar-${type}`]
    });
  }
}
