import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { 
  MatSnackBar, 
  MatSnackBarModule, 
  MatSnackBarConfig 
} from '@angular/material/snack-bar';

// Define profile type with string keys only
export interface UserProfile {
  user_id?: string;
  owner_name: string;
  owner_address: string;
  owner_phone: string;
  owner_city: string;
  owner_state: string;
  pets?: any[];
  [key: string]: any; // Keep index signature for flexibility
}

// Define profile keys as string literal types
type ProfileKey = 'owner_name' | 'owner_address' | 'owner_phone' | 'owner_city' | 'owner_state' | 'user_id';

export interface ProfileResponse {
  message: string;
  profile_id?: number;
}

export interface Pet {
  pet_id: number | null;
  pet_name: string;
  species: string;
  breed: string;
  owner?: string;
}

// Define typed field interfaces
interface ProfileField {
  key: ProfileKey; // Use specific string literal type
  label: string;
  icon: string;
}

interface FormField {
  key: ProfileKey; // Use specific string literal type
  label: string;
  icon: string;
  type: string;
  required: boolean;
  placeholder: string;
  error: string;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSnackBarModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  profile: UserProfile = {
    owner_name: '',
    owner_address: '',
    owner_phone: '',
    owner_city: '',
    owner_state: ''
  };

  // Profile fields for display - typed with specific keys
  profileFields: ProfileField[] = [
    { key: 'owner_name', label: 'Full Name', icon: 'fas fa-user' },
    { key: 'owner_phone', label: 'Phone Number', icon: 'fas fa-phone' },
    { key: 'owner_address', label: 'Address', icon: 'fas fa-map-marker-alt' },
    { key: 'owner_city', label: 'City', icon: 'fas fa-city' },
    { key: 'owner_state', label: 'State', icon: 'fas fa-map' }
  ];

  // Form fields for editing - typed with specific keys
  formFields: FormField[] = [
    { 
      key: 'owner_name', 
      label: 'Full Name', 
      icon: 'fas fa-user',
      type: 'text',
      required: true,
      placeholder: 'Enter your full name',
      error: 'Name is required'
    },
    { 
      key: 'owner_phone', 
      label: 'Phone Number', 
      icon: 'fas fa-phone',
      type: 'tel',
      required: true,
      placeholder: 'Enter your phone number',
      error: 'Phone number is required'
    },
    { 
      key: 'owner_address', 
      label: 'Address', 
      icon: 'fas fa-map-marker-alt',
      type: 'text',
      required: true,
      placeholder: 'Enter your full address',
      error: 'Address is required'
    },
    { 
      key: 'owner_city', 
      label: 'City', 
      icon: 'fas fa-city',
      type: 'text',
      required: true,
      placeholder: 'Enter your city',
      error: 'City is required'
    },
    { 
      key: 'owner_state', 
      label: 'State', 
      icon: 'fas fa-map',
      type: 'text',
      required: true,
      placeholder: 'Enter your state',
      error: 'State is required'
    }
  ];

  isEditMode = false;
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  hasProfile = false;
  userId: string | null = '';
  pets: Pet[] = [];
  loadingPets = false;
  isPetFormVisible = false;
  editingPet = false;
  currentPet: Pet = { pet_id: null, pet_name: '', species: '', breed: '' };

  // API URLs - Update these with your actual endpoints
  private profileApi = 'http://127.0.0.1:8000/api/user/profile/';
  private petsApi = 'http://127.0.0.1:8000/api/user/pets/';

  constructor(
    private http: HttpClient, 
    private router: Router,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id');
    if (!this.userId) {
      this.showSnackbar('Please log in to access your profile', 'error');
      this.router.navigate(['/auth']);
      return;
    }
    this.loadProfile();
    this.loadPets();
  }

  // Helper method to safely get profile field value
  getProfileValue(key: ProfileKey): string {
    return this.profile[key] || '';
  }

  // Snackbar notification using global styles
  private showSnackbar(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
    const config: MatSnackBarConfig = {
      duration: type === 'error' || type === 'warning' ? 5000 : 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: [`snackbar-${type}`],
      politeness: 'polite'
    };
    
    this.snackBar.open(message, 'Close', config);
  }

  deletePet(pet: Pet): void {
    if (window.confirm(`Are you sure you want to delete ${pet.pet_name}?`)) {
      this.http.delete(`${this.petsApi}${pet.pet_id}/`).subscribe({
        next: () => {
          this.pets = this.pets.filter(p => p.pet_id !== pet.pet_id);
          this.showSnackbar(`${pet.pet_name} has been deleted`, 'success');
        },
        error: (error) => {
          console.error('Delete pet error:', error);
          this.showSnackbar('Failed to delete pet. Please try again.', 'error');
        }
      });
    }
  }

  loadProfile(): void {
    this.isLoading = true;
    this.http.get<UserProfile>(`${this.profileApi}?user_id=${this.userId}`)
      .subscribe({
        next: (response) => {
          this.isLoading = false;
          if (response.owner_name) {
            this.profile = response;
            this.hasProfile = true;
            this.showSnackbar('Profile loaded successfully', 'success');
          } else {
            this.isEditMode = true;
            this.hasProfile = false;
            this.showSnackbar('Create your profile to get started', 'info');
          }
        },
        error: (error) => {
          this.isLoading = false;
          if (error.status === 404) {
            this.isEditMode = true;
            this.hasProfile = false;
            this.showSnackbar('No profile found. Create one now!', 'info');
          } else {
            this.showSnackbar('Failed to load profile. Please try again.', 'error');
          }
        }
      });
  }

  toggleEditMode(): void {
    this.isEditMode = !this.isEditMode;
    if (this.isEditMode && this.hasProfile) {
      this.loadProfile();
    }
  }

  onSubmit(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const profileData = { ...this.profile, user_id: this.userId };

    const request$ = this.hasProfile
      ? this.http.patch<ProfileResponse>(this.profileApi, profileData)
      : this.http.post<ProfileResponse>(this.profileApi, profileData);

    request$.subscribe({
      next: (response) => {
        this.isLoading = false;
        this.successMessage = response.message || (this.hasProfile ? 'Profile updated successfully!' : 'Profile created successfully!');
        this.showSnackbar(this.successMessage, 'success');
        this.isEditMode = false;
        this.hasProfile = true;
        this.loadProfile();
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = error.error?.message || 'Failed to save profile. Please try again.';
        this.showSnackbar(this.errorMessage, 'error');
      }
    });
  }

  cancelEdit(): void {
    if (this.hasProfile) {
      this.isEditMode = false;
      this.loadProfile();
      this.showSnackbar('Edit cancelled', 'info');
    } else {
      this.showSnackbar('Profile creation cancelled', 'info');
      this.router.navigate(['/home']);
    }
  }

  loadPets(): void {
    if (!this.userId) return;
    this.loadingPets = true;
    this.http.get<Pet[]>(`${this.petsApi}?user_id=${this.userId}`)
      .subscribe({
        next: (response) => {
          this.pets = response;
          this.loadingPets = false;
          if (response.length > 0) {
            this.showSnackbar(`Loaded ${response.length} pets`, 'success');
          }
        },
        error: (error) => {
          this.pets = [];
          this.loadingPets = false;
          console.error('Load pets error:', error);
          this.showSnackbar('Failed to load pets', 'error');
        }
      });
  }

  startAddPet(): void {
    this.isPetFormVisible = true;
    this.editingPet = false;
    this.currentPet = { pet_id: null, pet_name: '', species: '', breed: '' };
    this.showSnackbar('Add a new furry friend!', 'info');
  }

  editPet(pet: Pet): void {
    this.isPetFormVisible = true;
    this.editingPet = true;
    this.currentPet = { ...pet };
    this.showSnackbar(`Editing ${pet.pet_name}`, 'info');
  }

  cancelPetForm(): void {
    this.isPetFormVisible = false;
    this.currentPet = { pet_id: null, pet_name: '', species: '', breed: '' };
    this.showSnackbar('Pet form closed', 'info');
  }

  savePet(): void {
    const payload = { ...this.currentPet, owner: this.userId };
    this.loadingPets = true;

    const request$ = this.editingPet && this.currentPet.pet_id
      ? this.http.put(`${this.petsApi}`, { ...payload, pet_id: this.currentPet.pet_id, user_id: this.userId })
      : this.http.post(`${this.petsApi}`, payload);

    request$.subscribe({
      next: () => {
        this.loadingPets = false;
        this.isPetFormVisible = false;
        const message = this.editingPet ? `${this.currentPet.pet_name} updated successfully!` : 'Pet added successfully!';
        this.showSnackbar(message, 'success');
        this.loadPets();
      },
      error: (error) => {
        this.loadingPets = false;
        console.error('Save pet error:', error);
        const message = this.editingPet ? 'Failed to update pet' : 'Failed to add pet';
        this.showSnackbar(message, 'error');
      }
    });
  }
}