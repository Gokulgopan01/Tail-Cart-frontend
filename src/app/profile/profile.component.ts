import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';

export interface Alert {
  id: number;
  sender_name: string;
  phone: string;
  location: string;
  message: string;
  created_at: string;
  resolved?: boolean;
}

export interface Pet {
  pet_id: number | null;
  pet_name: string;
  species: string;
  breed: string;
  age: number;
  is_lost: boolean;
  pet_photo: string | null;
  alerts?: Alert[];
  owner?: number;

}

export interface UserProfile {
  owner_name: string;
  owner_address: string;
  owner_phone: string;
  owner_city: string;
  owner_state: string;
  owner_photo: string | null;
  pets: Pet[];
}

import { trigger, transition, style, animate } from '@angular/animations';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
  animations: [
    trigger('tabAnimation', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(10px)' }),
        animate('400ms cubic-bezier(0.16, 1, 0.3, 1)', style({ opacity: 1, transform: 'translateY(0)' }))
      ])
    ]),
    trigger('modalFade', [
      transition(':enter', [
        style({ opacity: 0 }),
        animate('300ms ease-out', style({ opacity: 1 }))
      ]),
      transition(':leave', [
        animate('200ms ease-in', style({ opacity: 0 }))
      ])
    ])
  ]
})
export class ProfileComponent implements OnInit {
  // Profile data
  profile: UserProfile = {
    owner_name: '',
    owner_address: '',
    owner_phone: '',
    owner_city: '',
    owner_state: '',
    owner_photo: null,
    pets: []
  };

  pets: Pet[] = [];
  allpets: Pet[] = [];
  selectedPet: Pet | null = null;
  isAlertModalOpen = false;
  isPreviewModalOpen = false;

  // File upload
  ownerPhotoFile: File | null = null;
  petPhotoFile: File | null = null;
  ownerPhotoPreview: string | null = null;
  petPhotoPreview: string | null = null;

  // UI states
  activeTab: 'owner' | 'pets' = 'owner';
  activePetFilter: 'all' | 'dogs' | 'cats' | 'other' = 'all';
  isEditMode = false;
  isLoading = false;
  hasProfile = false;
  userId: string | null = '';
  loadingPets = false;
  isPetFormVisible = false;
  editingPet = false;
  currentPet: Pet = {
    pet_id: null,
    pet_name: '',
    species: '',
    breed: '',
    age: 0,
    is_lost: false,
    pet_photo: null,
    alerts: []
  };

  // Frontend avatars for pets (backup)
  petAvatars: Map<number, string> = new Map();
  currentPetAvatar: string = 'pet1';

  private profileApi = 'http://127.0.0.1:8000/api/user/profile/';
  private petsApi = 'http://127.0.0.1:8000/api/user/pets/';
  private petApi = 'http://127.0.0.1:8000/api/user/pet/';
  private resolveAlertApi = 'http://127.0.0.1:8000/api/alerts/resolve/';

  constructor(
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id');
    if (!this.userId) {
      this.router.navigate(['/auth']);
      return;
    }
    this.loadProfile();

    // Check for tab query parameter
    this.route.queryParams.subscribe(params => {
      if (params['tab'] === 'pets') {
        this.switchTab('pets');
      }
    });
  }

  switchTab(tab: 'owner' | 'pets'): void {
    this.activeTab = tab;
    if (tab === 'pets') {
      this.loadPets();
    }
  }

  loadProfile(): void {
    this.isLoading = true;
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<UserProfile>(
      `${this.profileApi}?user_id=${this.userId}`,
      { headers }
    ).subscribe({
      next: (response) => {
        this.isLoading = false;
        if (response && response.owner_name) {
          this.profile = response;
          this.hasProfile = true;
          this.isEditMode = false;
          this.ownerPhotoPreview = response.owner_photo;
          this.pets = response.pets || [];
          this.allpets = response.pets || [];

          // Initialize pet avatars if not already set
          response.pets?.forEach(pet => {
            if (pet.pet_id && !this.petAvatars.has(pet.pet_id)) {
              this.petAvatars.set(pet.pet_id, this.getDefaultPetAvatar(pet.species));
            }
          });
        } else {
          this.isEditMode = true;
          this.hasProfile = false;
        }
      },
      error: (error) => {
        this.isLoading = false;
        if (error.status === 404) {
          this.isEditMode = true;
          this.hasProfile = false;
        }
      }
    });
  }

  handleImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = this.getDefaultPetAvatar(this.selectedPet?.species || '');
  }

  handleOwnerImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = 'assets/icons/avatar.svg';
  }

  toggleEditMode(): void {
    this.isEditMode = !this.isEditMode;
  }

  onOwnerPhotoSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.ownerPhotoFile = input.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.ownerPhotoPreview = e.target?.result as string;
      };
      reader.readAsDataURL(this.ownerPhotoFile);
    }
  }

  onPetPhotoSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.petPhotoFile = input.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.petPhotoPreview = e.target?.result as string;
      };
      reader.readAsDataURL(this.petPhotoFile);
    }
  }

  removeOwnerPhoto(): void {
    this.ownerPhotoFile = null;
    this.ownerPhotoPreview = null;
  }

  removePetPhoto(): void {
    this.petPhotoFile = null;
    this.petPhotoPreview = null;
  }

  onSubmit(): void {
    if (!this.profile.owner_name?.trim()) return;

    this.isLoading = true;
    const token = localStorage.getItem('access_token');

    // Create form data for file upload
    const formData = new FormData();
    formData.append('user_id', this.userId || '');
    formData.append('owner_name', this.profile.owner_name);
    formData.append('owner_address', this.profile.owner_address);
    formData.append('owner_phone', this.profile.owner_phone);
    formData.append('owner_city', this.profile.owner_city);
    formData.append('owner_state', this.profile.owner_state);

    if (this.ownerPhotoFile) {
      formData.append('owner_photo', this.ownerPhotoFile);
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    const request$ = this.hasProfile
      ? this.http.patch(this.profileApi, formData, { headers })
      : this.http.post(this.profileApi, formData, { headers });

    request$.subscribe({
      next: () => {
        this.isLoading = false;
        this.isEditMode = false;
        this.hasProfile = true;
        this.loadProfile();
        this.showSnackbar('Profile saved successfully');
      },
      error: (error) => {
        this.isLoading = false;
        this.showSnackbar('Error saving profile');
      }
    });
  }

  cancelEdit(): void {
    if (this.hasProfile) {
      this.isEditMode = false;
      this.loadProfile();
    }
  }

  loadPets(): void {
    if (!this.userId) return;
    this.loadingPets = true;
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<Pet[]>(
      `${this.petsApi}?user_id=${this.userId}`,
      { headers }
    ).subscribe({
      next: (response) => {
        this.pets = response || [];
        this.allpets = response || [];
        this.loadingPets = false;

        // Initialize pet avatars if not already set
        response?.forEach(pet => {
          if (pet.pet_id && !this.petAvatars.has(pet.pet_id)) {
            this.petAvatars.set(pet.pet_id, this.getDefaultPetAvatar(pet.species));
          }
        });
      },
      error: (error) => {
        this.pets = [];
        this.allpets = [];
        this.loadingPets = false;
      }
    });
  }

  showOnlyDogs(): void {
    this.activePetFilter = 'dogs';
    this.pets = this.allpets.filter(
      pet => pet.species?.toLowerCase() === 'dog'
    );
  }

  showAllPets(): void {
    this.activePetFilter = 'all';
    this.pets = this.allpets;
  }

  showOnlyCats(): void {
    this.activePetFilter = 'cats';
    this.pets = this.allpets.filter(pet => pet.species?.toLowerCase() === 'cat')
  }

  showOtherPets(): void {
    this.activePetFilter = 'other';
    this.pets = this.allpets.filter(pet => pet.species?.toLowerCase() !== 'cat' && pet.species?.toLowerCase() !== 'dog')
  }

  startAddPet(): void {
    this.isPetFormVisible = true;
    this.editingPet = false;
    this.currentPet = {
      pet_id: null,
      pet_name: '',
      species: '',
      breed: '',
      age: 0,
      is_lost: false,
      pet_photo: null,
      alerts: []
    };
    this.petPhotoPreview = null;
    this.petPhotoFile = null;
    this.currentPetAvatar = 'pet1';
  }

  editPet(pet: Pet, event?: Event): void {
    if (event) event.stopPropagation();
    this.isPetFormVisible = true;
    this.editingPet = true;
    this.currentPet = { ...pet };
    this.petPhotoPreview = pet.pet_photo;
    this.currentPetAvatar = this.petAvatars.get(pet.pet_id!) || this.getDefaultPetAvatar(pet.species);
  }

  cancelPetForm(): void {
    this.isPetFormVisible = false;
    this.currentPet = {
      pet_id: null,
      pet_name: '',
      species: '',
      breed: '',
      age: 0,
      is_lost: false,
      pet_photo: null,
      alerts: []
    };
    this.petPhotoPreview = null;
    this.petPhotoFile = null;
    this.currentPetAvatar = 'pet1';
  }

  savePet(): void {
    const token = localStorage.getItem('access_token');

    // Create form data for pet with photo
    const formData = new FormData();
    formData.append('pet_name', this.currentPet.pet_name);
    formData.append('species', this.currentPet.species);
    formData.append('breed', this.currentPet.breed || '');
    formData.append('age', this.currentPet.age.toString());
    formData.append('is_lost', this.currentPet.is_lost.toString());
    formData.append('owner', this.userId || '');

    if (this.petPhotoFile) {
      formData.append('pet_photo', this.petPhotoFile);
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.loadingPets = true;

    let request$;
    if (this.editingPet && this.currentPet.pet_id) {
      formData.append('pet_id', this.currentPet.pet_id.toString());
      formData.append('user_id', this.userId || '');
      // For PUT request to update existing pet
      request$ = this.http.put(this.petsApi, formData, { headers });;
    } else {
      // For POST request to create new pet
      formData.append('user_id', this.userId || '');
      request$ = this.http.post(this.petsApi, formData, { headers });
    }

    request$.subscribe({
      next: (response: any) => {
        this.loadingPets = false;
        this.isPetFormVisible = false;

        // Save avatar locally if no photo uploaded
        if (response?.pet_id && !this.petPhotoFile) {
          this.petAvatars.set(response.pet_id, this.currentPetAvatar);
        }

        this.loadPets();
        this.showSnackbar(this.editingPet ? 'Pet updated successfully' : 'Pet added successfully');
      },
      error: (error) => {
        this.loadingPets = false;
        console.error('Save pet error:', error);
        this.showSnackbar('Error saving pet');
      }
    });
  }

  deletePet(pet: Pet, event: Event): void {
    event.stopPropagation();

    if (!pet.pet_id || !this.userId) return;

    if (!confirm(`Are you sure you want to delete ${pet.pet_name}?`)) {
      return;
    }

    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    // ⚠️ pet_id + user_id as QUERY PARAMS
    this.http.delete(
      `${this.petsApi}?user_id=${this.userId}&pet_id=${pet.pet_id}`,
      { headers }
    ).subscribe({
      next: () => {
        this.pets = this.pets.filter(p => p.pet_id !== pet.pet_id);
        this.allpets = this.allpets.filter(p => p.pet_id !== pet.pet_id);

        if (pet.pet_id) {
          this.petAvatars.delete(pet.pet_id);
        }

        this.showSnackbar('Pet deleted successfully');
      },
      error: (error) => {
        console.error('Delete pet error:', error);
        this.showSnackbar('Error deleting pet');
      }
    });
  }


  openAlertModal(pet: Pet, event: Event): void {
    event.stopPropagation();
    this.selectedPet = pet;
    this.isAlertModalOpen = true;
  }

  closeAlertModal(): void {
    this.isAlertModalOpen = false;
    this.selectedPet = null;
  }

  openPreviewModal(pet: Pet, event: Event): void {
    event.stopPropagation();
    this.selectedPet = pet;
    this.isPreviewModalOpen = true;
  }

  closePreviewModal(): void {
    this.isPreviewModalOpen = false;
    this.selectedPet = null;
  }

  viewOnMap(location: string): void {
    // Open Google Maps with the location
    const encodedLocation = encodeURIComponent(location);
    window.open(`https://www.google.com/maps/search/?api=1&query=${encodedLocation}`, '_blank');
  }

  markAsLost(pet: Pet, event: Event): void {
    const checkbox = event.target as HTMLInputElement;
    const newStatus = checkbox.checked;

    if (!pet.pet_id || !this.userId) return;

    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    const payload = {
      user_id: this.userId,
      pet_id: pet.pet_id,
      is_lost: newStatus
    };

    this.http.put(this.petsApi, payload, { headers }).subscribe({
      next: () => {
        pet.is_lost = newStatus;
        this.showSnackbar(`${pet.pet_name} status updated to ${newStatus ? 'Lost' : 'Safe'}`);
      },
      error: (error) => {
        console.error('Update status error:', error);
        checkbox.checked = !newStatus; // Revert checkbox on error
        this.showSnackbar('Error updating pet status');
      }
    });
  }

  formatLocation(location: any): string {
    if (!location) return 'Location not specified';
    if (Array.isArray(location)) {
      return location.filter(item => !!item).join(', ');
    }
    return location;
  }


  resolveAlert(alertId: number): void {
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    const payload = {
      alert_id: alertId,
      user_id: this.userId
    };

    this.http.put(this.resolveAlertApi, payload, { headers }).subscribe({
      next: () => {
        if (this.selectedPet) {
          this.selectedPet.alerts = this.selectedPet.alerts?.filter(alert => alert.id !== alertId) ?? [];
        }
        this.showSnackbar('Alert resolved successfully');
      },
      error: (error) => {
        console.error('Resolve alert error:', error);
        this.showSnackbar('Error resolving alert');
      }
    });
  }

  private showSnackbar(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top'
    });
  }

  // Select avatar for pet (frontend only)
  selectPetAvatar(avatar: string): void {
    this.currentPetAvatar = avatar;
  }

  // Get default avatar based on species
  private getDefaultPetAvatar(species: string): string {
    switch (species?.toLowerCase()) {
      case 'dog': return 'pet1';
      case 'cat': return 'cat-play';
      case 'bird': return 'bird';
      default: return 'pet1';
    }
  }

  getOwnerPhotoUrl(): string {
    if (!this.profile?.owner_photo) return 'assets/icons/avatar.svg';
    return 'http://127.0.0.1:8000' + (this.profile.owner_photo.startsWith('/') ? this.profile.owner_photo : '/' + this.profile.owner_photo);
  }


  // Get pet photo URL with fallback to avatar
  getPetPhotoUrl(pet: Pet): string {
    if (pet.pet_photo) {
      // If backend returns relative path, prefix backend URL
      if (pet.pet_photo.startsWith('/')) {
        return `http://127.0.0.1:8000${pet.pet_photo}`;
      }
      return pet.pet_photo;
    }

    if (pet.pet_id && this.petAvatars.has(pet.pet_id)) {
      return `assets/icons/${this.petAvatars.get(pet.pet_id)}.svg`;
    }

    return `assets/icons/${this.getDefaultPetAvatar(pet.species)}.svg`;
  }

}