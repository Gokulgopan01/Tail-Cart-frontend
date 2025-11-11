import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import Swal from 'sweetalert2';

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
  imports: [CommonModule, FormsModule],
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.css']
})
export class ProductsComponent implements OnInit {
  products: Product[] = [];
  filteredProducts: Product[] = [];
  paginatedProducts: Product[] = [];
  selectedProduct: Product | null = null;
  
  // Pagination
  currentPage: number = 1;
  productsPerPage: number = 8;
  totalPages: number = 1;
  
  // Filters
  filters: Filters = {
    breeds: { dog: false, cat: false },
    deals: { hotSale: false, bestseller: false },
    materials: { glass: false, wood: false, plastic: false },
    priceRange: 1000,
    minRating: 0
  };

  sortOption: string = 'featured';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.fetchProducts();
  }

  fetchProducts() {
    this.http.get<Product[]>('https://tailcart.duckdns.org/api/admin/products/').subscribe({
      next: (products) => {
        this.products = products;
        this.applyFilters();
      },
      error: (error) => {
        console.error('Error fetching products:', error);
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

      return true;
    });

    this.applySorting();
    this.updatePagination();
  }

  applySorting() {
    switch(this.sortOption) {
      case 'priceLow': this.filteredProducts.sort((a,b) => a.price - b.price); break;
      case 'priceHigh': this.filteredProducts.sort((a,b) => b.price - a.price); break;
      case 'name': this.filteredProducts.sort((a,b) => a.model.localeCompare(b.model)); break;
      default: break;
    }
  }

  updatePagination() {
    this.totalPages = Math.ceil(this.filteredProducts.length / this.productsPerPage);
    this.currentPage = Math.min(this.currentPage, Math.max(1, this.totalPages));
    const startIndex = (this.currentPage - 1) * this.productsPerPage;
    this.paginatedProducts = this.filteredProducts.slice(startIndex, startIndex + this.productsPerPage);
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

  openProductModal(product: Product) {
    this.selectedProduct = product;
  }

  closeModal() {
    this.selectedProduct = null;
  }

  async addToCart(product: Product) {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      await Swal.fire({
        icon: 'warning',
        title: 'Login Required',
        text: 'Please log in first.'
      });
      return;
    }

    // Modern Pet ID Selection (dropdown)
    const petResult = await Swal.fire({
      title: 'Select Your Pet',
      html: `
        <select id="petSelect" class="swal2-select" style="width:100%;padding:10px;border-radius:8px;border:1px solid #ccc;">
          <option value="">--Select Pet--</option>
          <option value="1">Pet 1</option>
          <option value="2">Pet 2</option>
          <option value="3">Pet 3</option>
        </select>
      `,
      focusConfirm: false,
      preConfirm: () => {
        const petId = (document.getElementById('petSelect') as HTMLSelectElement).value;
        if (!petId) Swal.showValidationMessage('Please select a pet!');
        return petId;
      },
      showCancelButton: true
    });

    if (!petResult.value) return;
    const petId = petResult.value;

    // Modern Quantity Input with + / - buttons
    const quantityResult = await Swal.fire({
      title: 'Enter Quantity',
      html: `
        <div style="display:flex;align-items:center;gap:10px;justify-content:center;">
          <button type="button" id="dec" class="swal2-confirm swal2-styled">-</button>
          <input type="number" id="quantityInput" class="swal2-input" value="1" min="1" style="width:60px;text-align:center;border-radius:8px;border:1px solid #ccc;">
          <button type="button" id="inc" class="swal2-confirm swal2-styled">+</button>
        </div>
      `,
      focusConfirm: false,
      preConfirm: () => {
        const qty = Number((document.getElementById('quantityInput') as HTMLInputElement).value);
        if (!qty || qty <= 0) Swal.showValidationMessage('Please enter a valid quantity!');
        return qty;
      },
      didOpen: () => {
        const decBtn = document.getElementById('dec')!;
        const incBtn = document.getElementById('inc')!;
        const input = document.getElementById('quantityInput') as HTMLInputElement;

        decBtn.addEventListener('click', () => {
          if (+input.value > 1) input.value = String(+input.value - 1);
        });
        incBtn.addEventListener('click', () => input.value = String(+input.value + 1));
      },
      showCancelButton: true
    });

    if (!quantityResult.value) return;
    const quantity = quantityResult.value;

    const payload = { owner: userId, pet: petId, product: product.id, quantity };

    this.http.post('https://tailcart.duckdns.org/api/user/cart/', payload).subscribe({
      next: (res: any) => {
        Swal.fire({
          icon: 'success',
          title: 'Added to Cart',
          text: `${product.model} added to your cart!`,
          timer: 2000,
          showConfirmButton: false
        });
        this.closeModal();
      },
      error: (error) => {
        console.error('Error adding to cart:', error);
        let errorMessage = 'Error uploading document. Please try again';
        if (error.error) {
          if (typeof error.error === 'string') errorMessage += `: ${error.error}`;
          else if (error.error.detail) errorMessage = error.error.detail;
          else {
            errorMessage = Object.entries(error.error)
              .map(([field, messages]) => `${field}: ${(Array.isArray(messages) ? messages.join(', ') : messages)}`)
              .join('\n');
          }
        }
        Swal.fire({ icon: 'error', title: 'Failed', text: errorMessage });
      }
    });
  }
}
