import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, AfterViewInit, HostListener } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { ViewChild, ElementRef } from '@angular/core';

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

interface Pet {
  pet_id: number;
  pet_name: string;
  species: string;
  breed: string;
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
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
  products: Product[] = [];
  filteredProducts: Product[] = [];
  paginatedProducts: Product[] = [];
  selectedProduct: Product | null = null;
  userPets: Pet[] = [];
  loadingPets = false;
  
  // Admin variables
  showAddProductModal = false;
  isCreatingProduct = false;
  editingProduct: Product | null = null;
  showDeleteModal = false;
  productToDelete: Product | null = null;
  isDeleting = false;
  isDraggingOver = false;
  
  newProduct = {
    model: '',
    product_info: '',
    price: 0,
    breed: '',
    quantity: 0,
    reviews: '',
    deals: '',
    image: null as File | null
  };
  
  // Pagination
  currentPage: number = 1;
  productsPerPage: number = 12;
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

  private getHeaders(useFormData: boolean = false) {
    const token = localStorage.getItem('access_token');
    
    if (useFormData) {
      return {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      };
    }
    
    // For JSON requests
    return {
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      }
    };
  }

  constructor(private http: HttpClient, private snackBar: MatSnackBar) {}

  private petsApi = 'https://tailcart1.duckdns.org/api/user/pets/';
  private productsApi = 'https://tailcart1.duckdns.org/api/admin/products/';

  ngOnInit() {
    this.checkMobileView();
    this.fetchProducts();
    this.loadUserPets();

    console.log('LocalStorage role:', localStorage.getItem('access_role'));
    console.log('Is Admin?', this.isAdmin());
    console.log('Full localStorage:', localStorage);
  }
  
  ngAfterViewInit() {
    setTimeout(() => {
      this.initScrollAnimations();
    }, 100);
  }

  triggerFileInput() {
    this.fileInput.nativeElement.click();
  }

  loadUserPets(): void {
    const userId = localStorage.getItem('user_id');
    if (!userId) return;

    this.loadingPets = true;

    this.http.get<Pet[]>(`${this.petsApi}?user_id=${userId}`,this.getHeaders())
      .subscribe({
        next: (pets) => {
          this.userPets = pets;
          this.loadingPets = false;
        },
        error: () => {
          this.loadingPets = false;
          this.showSnackbar('Failed to load pets', 'error');
        }
      });
  }
  
  @HostListener('window:resize')
  onResize() {
    this.checkMobileView();
  }
  
  checkMobileView() {
    this.isMobileView = window.innerWidth <= 768;
  }

  initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animated');
          entry.target.classList.add('animate');
        }
      });
    }, { 
      threshold: 0.1,
      rootMargin: '0px 0px -10% 0px'
    });

    const scrollElements = document.querySelectorAll(
      '.scroll-animate, .scroll-animate-left, .scroll-animate-right, .product-card, .filter-card, .products-header'
    );
    
    scrollElements.forEach(el => observer.observe(el));
  }

  fetchProducts() {
  this.http
    .get<Product[]>(this.productsApi, this.getHeaders())
    .subscribe({
      next: (products) => {
        this.products = products;
        this.applyFilters();
      },
      error: () => {
        this.showSnackbar('Failed to load products', 'error');
      }
    });
}

  // Admin Methods
  isAdmin(): boolean {
    return localStorage.getItem('access_role') === 'admin';
  }

  openAddProductModal() {
    this.resetNewProduct();
    this.showAddProductModal = true;
    this.editingProduct = null;
  }

  openEditProductModal(product: Product) {
    this.newProduct = {
      model: product.model,
      product_info: product.product_info,
      price: product.price,
      breed: product.breed,
      quantity: product.quantity,
      reviews: product.reviews,
      deals: product.deals,
      image: null
    };
    this.editingProduct = product;
    this.showAddProductModal = true;
  }

  closeAddProductModal() {
    this.showAddProductModal = false;
    this.editingProduct = null;
    this.resetNewProduct();
  }

  resetNewProduct() {
    this.newProduct = {
      model: '',
      product_info: '',
      price: 0,
      breed: '',
      quantity: 0,
      reviews: '',
      deals: '',
      image: null
    };
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.validateAndSetImage(file);
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDraggingOver = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDraggingOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDraggingOver = false;
    
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      this.validateAndSetImage(file);
    }
  }

  validateAndSetImage(file: File) {
    // Check file type
    if (!file.type.startsWith('image/')) {
      this.showSnackbar('Please select an image file', 'error');
      return;
    }

    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      this.showSnackbar('Image size should be less than 5MB', 'error');
      return;
    }

    this.newProduct.image = file;
  }

  saveProduct() {
  if (!this.validateProductData()) return;

  this.isCreatingProduct = true;

  const formData = new FormData();
  formData.append('model', this.newProduct.model);
  formData.append('product_info', this.newProduct.product_info);
  formData.append('price', this.newProduct.price.toString());
  formData.append('breed', this.newProduct.breed);
  formData.append('quantity', this.newProduct.quantity.toString());
  
  if (this.newProduct.reviews) {
    formData.append('reviews', this.newProduct.reviews);
  }
  
  if (this.newProduct.deals) {
    formData.append('deals', this.newProduct.deals);
  }
  
  if (this.newProduct.image) {
    formData.append('image', this.newProduct.image, this.newProduct.image.name);
  }

  // For FormData, use the second parameter as true
  const headers = this.getHeaders(true);

  if (this.editingProduct) {
    this.http.put(`${this.productsApi}${this.editingProduct.id}/`, formData, headers)
      .subscribe({
        next: (response: any) => {
          this.showSnackbar('Product updated successfully!', 'success');
          this.fetchProducts();
          this.closeAddProductModal();
          this.isCreatingProduct = false;
        },
        error: (error) => {
          this.handleProductError(error);
          this.isCreatingProduct = false;
        }
      });
  } else {
    this.http.post(this.productsApi, formData, headers)
      .subscribe({
        next: (res: any) => {
          this.showSnackbar('Product added successfully!', 'success');
          this.fetchProducts();
          this.closeAddProductModal();
          this.isCreatingProduct = false;
        },
        error: (err) => {
          this.handleProductError(err);
          this.isCreatingProduct = false;
        }
      });
  }
}

  validateProductData(): boolean {
  if (!this.newProduct.model.trim()) {
    this.showSnackbar('Product model is required', 'error');
    return false;
  }
  
  if (!this.newProduct.product_info.trim()) {
    this.showSnackbar('Product description is required', 'error');
    return false;
  }
  
  if (this.newProduct.price <= 0) {
    this.showSnackbar('Price must be greater than 0', 'error');
    return false;
  }
  
  if (!this.newProduct.breed) {
    this.showSnackbar('Please select a pet type', 'error');
    return false;
  }
  
  // Check if quantity is at least 0 (or 1 if required)
  if (this.newProduct.quantity < 0) {
    this.showSnackbar('Quantity cannot be negative', 'error');
    return false;
  }
  
  // Optional: require at least 1 in stock
  if (this.newProduct.quantity < 1) {
    this.showSnackbar('Quantity must be at least 1', 'error');
    return false;
  }
  
  if (this.newProduct.reviews && (parseFloat(this.newProduct.reviews) < 1 || parseFloat(this.newProduct.reviews) > 5)) {
    this.showSnackbar('Rating must be between 1 and 5', 'error');
    return false;
  }

  return true;
}

  handleProductError(error: any) {
    let errorMessage = 'Error saving product. Please try again';
    if (error.error) {
      if (typeof error.error === 'string') {
        errorMessage += `: ${error.error}`;
      } else if (error.error.detail) {
        errorMessage = error.error.detail;
      } else {
        errorMessage = Object.entries(error.error)
          .map(([field, messages]) => `${field}: ${(Array.isArray(messages) ? messages.join(', ') : messages)}`)
          .join('\n');
      }
    }
    this.showSnackbar(errorMessage, 'error');
  }

  editProduct(product: Product, event: Event) {
    event.stopPropagation();
    this.openEditProductModal(product);
  }

  deleteProduct(productId: number, event: Event) {
    event.stopPropagation();
    const product = this.products.find(p => p.id === productId);
    if (product) {
      this.productToDelete = product;
      this.showDeleteModal = true;
    }
  }

  closeDeleteModal() {
    this.showDeleteModal = false;
    this.productToDelete = null;
    this.isDeleting = false;
  }

  confirmDelete() {
    if (!this.productToDelete) return;

    this.isDeleting = true;
    
    this.http.delete(`${this.productsApi}${this.productToDelete.id}/`, this.getHeaders())

      .subscribe({
        next: () => {
          this.showSnackbar('Product deleted successfully!', 'success');
          this.fetchProducts();
          this.closeDeleteModal();
          this.isDeleting = false;
        },
        error: (error) => {
          this.showSnackbar('Failed to delete product', 'error');
          this.isDeleting = false;
        }
      });
  }

  // Existing methods (unchanged)
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

  generateStars(reviewCount: string): string {
    const rating = parseFloat(reviewCount) || 0;
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5 ? 1 : 0;
    const emptyStars = 5 - fullStars - halfStar;
    
    return '★'.repeat(fullStars) + (halfStar ? '½' : '') + '☆'.repeat(emptyStars);
  }

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
  
  @HostListener('window:scroll')
  onWindowScroll() {
    if (!this.isMobileView || this.isLoadingMore || this.allProductsLoaded) return;
    
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    
    if (scrollTop + windowHeight >= documentHeight * 0.8) {
      this.loadMoreProducts();
    }
  }

  openProductModal(product: Product) {
    this.selectedProduct = product;
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

  onAddToCartClick(product: any, event: Event): void {
    event.stopPropagation();
    this.openProductModal(product);
    this.addToCart(product);
  }

  async addToCart(product: Product) {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      this.showSnackbar('Please log in first', 'warning');
      return;
    }

    this.selectedProductForCart = product;
    
    if (this.isMobileView) {
      this.showPetIdInput = true;
      this.showQuantityInput = false;
    } else {
      this.showPetIdInput = true;
      this.showQuantityInput = false;
    }
  }

  submitPetId() {
    if (!this.petId) {
      this.showSnackbar('Please select a pet!', 'error');
      return;
    }

    this.showPetIdInput = false;
    this.showQuantityInput = true;
  }

  submitQuantity() {
    if (!this.quantity || this.quantity <= 0) {
      this.showSnackbar('Please enter a valid quantity!', 'error');
      return;
    }
    
    this.confirmAddToCart();
  }

  confirmAddToCart() {
    if (!this.selectedProductForCart || !this.petId || !this.quantity) {
      this.showSnackbar('Missing required information', 'error');
      return;
    }
    const headers = this.getHeaders(true);
    const userId = localStorage.getItem('user_id');
    const payload = { 
      owner: userId, 
      pet: this.petId, 
      product: this.selectedProductForCart.id, 
      quantity: this.quantity 
    };

    this.http.post('https://tailcart1.duckdns.org/api/user/cart/', payload, headers).subscribe({
      next: (res: any) => {
        this.showSnackbar(`${this.selectedProductForCart!.model} added to your cart!`, 'success');
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

  showSnackbar(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: [`snackbar-${type}`]
    });
  }

  incrementQuantity() {
    this.quantity++;
  }

  decrementQuantity() {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }

  cancelCartProcess() {
    this.showPetIdInput = false;
    this.showQuantityInput = false;
    this.selectedProductForCart = null;
    this.petId = '';
    this.quantity = 1;
  }
}