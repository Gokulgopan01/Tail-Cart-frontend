import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, AfterViewInit, HostListener } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSnackBarModule } from '@angular/material/snack-bar';


interface Product {
  id: number;
  model: string;
  product_info: string;
  price: number;
  breed: string;
  quantity: number;
  image: string;
  reviews: string;
  deals: string;
}

interface Filters {
  breeds: {
    dog: boolean;
    cat: boolean;
  };
  deals: {
    hotSale: boolean;
    bestseller: boolean;
  };
  materials: {
    glass: boolean;
    wood: boolean;
    plastic: boolean;
  };
  priceRange: number;
  minRating: number;
}

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSnackBarModule],
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.css']
})
export class ProductsComponent implements OnInit, AfterViewInit {
  products: Product[] = [];
  filteredProducts: Product[] = [];
  paginatedProducts: Product[] = [];
  selectedProduct: Product | null = null;
  
  // Pagination
  currentPage: number = 1;
  productsPerPage: number = 12; // Increased for better mobile experience
  totalPages: number = 1;
  
  // Infinite Scroll
  isLoadingMore: boolean = false;
  allProductsLoaded: boolean = false;
  
  // Mobile view
  isMobileView: boolean = false;
  
  // Filters
  filters: Filters = {
    breeds: { dog: false, cat: false },
    deals: { hotSale: false, bestseller: false },
    materials: { glass: false, wood: false, plastic: false },
    priceRange: 1000,
    minRating: 0
  };

  sortOption: string = 'featured';
  isMobileSortOpen = false;
  isMobileFiltersOpen = false;
  
  // Variables for modal cart inputs
  showPetIdInput = false;
  showQuantityInput = false;
  selectedProductForCart: Product | null = null;
  petId: string = '';
  quantity: number = 1;

  constructor(
    private http: HttpClient,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.checkMobileView();
    this.fetchProducts();
  }
  
  ngAfterViewInit() {
    setTimeout(() => {
      this.initScrollAnimations();
    }, 100);
  }
  
  @HostListener('window:resize')
  onResize() {
    this.checkMobileView();
  }
  
  checkMobileView() {
    this.isMobileView = window.innerWidth <= 768;
  }

  initScrollAnimations() {
    // Trigger hero animations immediately
    const heroElements = document.querySelectorAll('.hero-badge, .hero-content h1, .hero-content p, .hero-stats');
    heroElements.forEach((el, index) => {
      setTimeout(() => {
        el.classList.add('animated');
      }, index * 200);
    });

    // Scroll animations for product cards and other elements
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animated');
          entry.target.classList.add('animate');
          
          // Add staggered animation for product cards
          if (entry.target.classList.contains('product-card')) {
            const cards = document.querySelectorAll('.product-card');
            cards.forEach((card, index) => {
              setTimeout(() => {
                card.classList.add('animated');
              }, index * 100);
            });
          }
        }
      });
    }, { 
      threshold: 0.1,
      rootMargin: '0px 0px -10% 0px'
    });

    // Observe all elements that need scroll animations
    const scrollElements = document.querySelectorAll(
      '.scroll-animate, .scroll-animate-left, .scroll-animate-right, .product-card, .filter-card, .products-header'
    );
    
    scrollElements.forEach(el => observer.observe(el));
  }

  fetchProducts() {
    this.http.get<Product[]>('https://tailcart.duckdns.org/api/admin/products/').subscribe({
      next: (products) => {
        this.products = products;
        this.applyFilters();
      },
      error: (error) => {
        console.error('Error fetching products:', error);
        this.showSnackbar('Failed to load products', 'error');
      }
    });
  }

  applyFilters() {
    this.filteredProducts = this.products.filter(product => {
      if (product.price > this.filters.priceRange) return false;

      if ((this.filters.breeds.dog || this.filters.breeds.cat) &&
          !((this.filters.breeds.dog && product.breed === 'Dog') ||
            (this.filters.breeds.cat && product.breed === 'Cat'))) return false;

      if ((this.filters.deals.hotSale || this.filters.deals.bestseller) &&
          !((this.filters.deals.hotSale && product.deals === 'Hot Sale') ||
            (this.filters.deals.bestseller && product.deals === 'Bestseller'))) return false;

      if ((this.filters.materials.glass || this.filters.materials.wood || this.filters.materials.plastic)) {
        const description = product.product_info.toLowerCase();
        let materialMatch = false;
        if (this.filters.materials.glass && description.includes('glass')) materialMatch = true;
        if (this.filters.materials.wood && description.includes('wood')) materialMatch = true;
        if (this.filters.materials.plastic && description.includes('transparent')) materialMatch = true;
        if (!materialMatch) return false;
      }

      // Rating filter
      if (this.filters.minRating > 0) {
        const rating = parseFloat(product.reviews) || 0;
        if (rating < this.filters.minRating) return false;
      }

      return true;
    });

    this.applySorting();
    this.updatePagination();
  }

  toggleMobileFilters() {
    this.isMobileFiltersOpen = !this.isMobileFiltersOpen;
    const sidebar = document.querySelector('.filter-sidebar-mobile');
    const overlay = document.querySelector('.filter-overlay');
    
    if (this.isMobileFiltersOpen) {
      sidebar?.classList.add('active');
      overlay?.classList.add('active');
      document.body.style.overflow = 'hidden';
    } else {
      sidebar?.classList.remove('active');
      overlay?.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  closeMobileFilters() {
    this.isMobileFiltersOpen = false;
    const sidebar = document.querySelector('.filter-sidebar-mobile');
    const overlay = document.querySelector('.filter-overlay');
    sidebar?.classList.remove('active');
    overlay?.classList.remove('active');
    document.body.style.overflow = '';
  }

  toggleMobileSort() {
    this.isMobileSortOpen = !this.isMobileSortOpen;
    const sortModal = document.querySelector('.sort-sidebar-mobile');
    const sortOverlay = document.querySelector('.sort-overlay');
    
    if (this.isMobileSortOpen) {
      sortModal?.classList.add('active');
      sortOverlay?.classList.add('active');
      document.body.style.overflow = 'hidden';
    } else {
      sortModal?.classList.remove('active');
      sortOverlay?.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  closeMobileSort() {
    this.isMobileSortOpen = false;
    const sortModal = document.querySelector('.sort-sidebar-mobile');
    const sortOverlay = document.querySelector('.sort-overlay');
    sortModal?.classList.remove('active');
    sortOverlay?.classList.remove('active');
    document.body.style.overflow = '';
  }

  applySorting() {
    switch(this.sortOption) {
      case 'priceLow': 
        this.filteredProducts.sort((a,b) => a.price - b.price); 
        break;
      case 'priceHigh': 
        this.filteredProducts.sort((a,b) => b.price - a.price); 
        break;
      case 'name': 
        this.filteredProducts.sort((a,b) => a.model.localeCompare(b.model)); 
        break;
      case 'rating': 
        this.filteredProducts.sort((a,b) => {
          const ratingA = parseFloat(a.reviews) || 0;
          const ratingB = parseFloat(b.reviews) || 0;
          return ratingB - ratingA;
        });
        break;
      default: 
        // For 'featured', sort by ID or keep original order
        this.filteredProducts.sort((a,b) => a.id - b.id);
        break;
    }
    this.updatePagination();
  }

  updatePagination() {
    this.totalPages = Math.ceil(this.filteredProducts.length / this.productsPerPage);
    this.currentPage = Math.min(this.currentPage, Math.max(1, this.totalPages));
    const startIndex = (this.currentPage - 1) * this.productsPerPage;
    const endIndex = startIndex + this.productsPerPage;
    this.paginatedProducts = this.filteredProducts.slice(0, endIndex);
    this.allProductsLoaded = endIndex >= this.filteredProducts.length;
  }

  // Generate star rating based on review number
  generateStars(reviewCount: string): string {
    const rating = parseFloat(reviewCount) || 0;
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5 ? 1 : 0;
    const emptyStars = 5 - fullStars - halfStar;
    
    return '★'.repeat(fullStars) + (halfStar ? '½' : '') + '☆'.repeat(emptyStars);
  }

  // Get rating number for display
  getRatingNumber(reviewCount: string): number {
    return parseFloat(reviewCount) || 0;
  }

  getProductCountByBreed(breed: string): number {
    return this.products.filter(product => product.breed === breed).length;
  }

  clearFilters() {
    this.filters = {
      breeds: { dog: false, cat: false },
      deals: { hotSale: false, bestseller: false },
      materials: { glass: false, wood: false, plastic: false },
      priceRange: 1000,
      minRating: 0
    };
    this.applyFilters();
    this.closeMobileFilters();
  }

  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.updatePagination();
    }
  }

  previousPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.updatePagination();
    }
  }

  // Load more products for infinite scroll
  loadMoreProducts() {
    if (this.isLoadingMore || this.allProductsLoaded) return;
    
    this.isLoadingMore = true;
    
    setTimeout(() => {
      this.currentPage++;
      const startIndex = (this.currentPage - 1) * this.productsPerPage;
      const endIndex = startIndex + this.productsPerPage;
      const newProducts = this.filteredProducts.slice(startIndex, endIndex);
      
      this.paginatedProducts = [...this.paginatedProducts, ...newProducts];
      this.allProductsLoaded = endIndex >= this.filteredProducts.length;
      this.isLoadingMore = false;
    }, 500);
  }
onImageLoad(event: Event) {
  const img = event.target as HTMLImageElement;
  img.classList.add('loaded');
}
onImageError(event: Event) {
  const img = event.target as HTMLImageElement;
  img.src = 'assets/images/default-product.jpg';
  img.classList.add('loaded');
}
  // Handle scroll for infinite loading
  @HostListener('window:scroll')
  onWindowScroll() {
    // Only enable infinite scroll on mobile
    if (!this.isMobileView || this.isLoadingMore || this.allProductsLoaded) return;
    
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    
    // Load more when user reaches 80% of the page
    if (scrollTop + windowHeight >= documentHeight * 0.8) {
      this.loadMoreProducts();
    }
  }

  openProductModal(product: Product) {
    this.selectedProduct = product;
    // Reset cart input states when opening modal
    this.showPetIdInput = false;
    this.showQuantityInput = false;
    this.selectedProductForCart = null;
    this.petId = '';
    this.quantity = 1;
  }

  closeModal() {
    this.selectedProduct = null;
    this.showPetIdInput = false;
    this.showQuantityInput = false;
    this.selectedProductForCart = null;
    this.petId = '';
    this.quantity = 1;
  }

  // New method to handle add to cart flow for mobile
  async addToCart(product: Product) {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      this.showSnackbar('Please log in first', 'warning');
      return;
    }

    // Store the product for the cart process
    this.selectedProductForCart = product;
    
    // For mobile view, show inputs inside the modal
    if (this.isMobileView) {
      // Start the flow by showing pet ID input
      this.showPetIdInput = true;
      this.showQuantityInput = false;
    } else {
      // For desktop, use the original flow
      this.showPetIdInput = true;
      this.showQuantityInput = false;
    }
  }

  // Method to handle pet ID submission
  submitPetId() {
    if (!this.petId || isNaN(Number(this.petId)) || Number(this.petId) <= 0) {
      this.showSnackbar('Please enter a valid numeric Pet ID!', 'error');
      return;
    }
    
    this.showPetIdInput = false;
    this.showQuantityInput = true;
  }

  // Method to handle quantity submission
  submitQuantity() {
    if (!this.quantity || this.quantity <= 0) {
      this.showSnackbar('Please enter a valid quantity!', 'error');
      return;
    }
    
    this.confirmAddToCart();
  }

  // Final method to confirm and add to cart
  confirmAddToCart() {
    if (!this.selectedProductForCart || !this.petId || !this.quantity) {
      this.showSnackbar('Missing required information', 'error');
      return;
    }

    const userId = localStorage.getItem('user_id');
    const payload = { 
      owner: userId, 
      pet: this.petId, 
      product: this.selectedProductForCart.id, 
      quantity: this.quantity 
    };

    this.http.post('https://tailcart.duckdns.org/api/user/cart/', payload).subscribe({
      next: (res: any) => {
        this.showSnackbar(`${this.selectedProductForCart!.model} added to your cart!`, 'success');
        
        // Reset all states
        this.closeModal();
        this.selectedProductForCart = null;
        this.petId = '';
        this.quantity = 1;
      },
      error: (error) => {
        console.error('Error adding to cart:', error);
        let errorMessage = 'Error adding to cart. Please try again';
        if (error.error) {
          if (typeof error.error === 'string') errorMessage += `: ${error.error}`;
          else if (error.error.detail) errorMessage = error.error.detail;
          else {
            errorMessage = Object.entries(error.error)
              .map(([field, messages]) => `${field}: ${(Array.isArray(messages) ? messages.join(', ') : messages)}`)
              .join('\n');
          }
        }
        this.showSnackbar(errorMessage, 'error');
      }
    });
  }

  // Helper method to show snackbar notifications
  showSnackbar(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: [`snackbar-${type}`]
    });
  }

  // Quantity control methods
  incrementQuantity() {
    this.quantity++;
  }

  decrementQuantity() {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }

  // Cancel cart process
  cancelCartProcess() {
    this.showPetIdInput = false;
    this.showQuantityInput = false;
    this.selectedProductForCart = null;
    this.petId = '';
    this.quantity = 1;
  }
}