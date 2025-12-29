import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';

export interface UserProfile {
  owner_name: string;
  owner_address: string;
  owner_phone: string;
  owner_city: string;
  owner_state: string;
  pets?: any[];
}

export interface Pet {
  pet_id: number | null;
  pet_name: string;
  species: string;
  breed: string;
  owner?: string;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
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

  activeTab: 'owner' | 'pets' = 'owner';
  isEditMode = false;
  isLoading = false;
  hasProfile = false;
  userId: string | null = '';
  pets: Pet[] = [];
  loadingPets = false;
  isPetFormVisible = false;
  editingPet = false;
  currentPet: Pet = { pet_id: null, pet_name: '', species: '', breed: '' };

  private profileApi = 'https://tailcart1.duckdns.org/api/user/profile/';
  private petsApi = 'https://tailcart1.duckdns.org/api/user/pets/';

  private showSnackbar(
    message: string,
    type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: [`snackbar-${type}`],
      horizontalPosition: 'right',
      verticalPosition: 'top'
    });
  }

  constructor(
    private http: HttpClient, 
    private router: Router,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id');
    if (!this.userId) {
      this.router.navigate(['/auth']);
      return;
    }
    this.loadProfile();
    this.loadPets();
  }

  switchTab(tab: 'owner' | 'pets'): void {
    this.activeTab = tab;
  }

  loadProfile(): void {
    this.isLoading = true;
    const token = localStorage.getItem('access_token');
    this.http.get<UserProfile>(
      `${this.profileApi}?user_id=${this.userId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: (response) => {
        this.isLoading = false;
        if (response && response.owner_name) {
          this.profile = response;
          this.hasProfile = true;
          this.isEditMode = false;
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
        } else {
          console.error('Load profile error:', error);
        }
      }
    });
  }

  toggleEditMode(): void {
    this.isEditMode = !this.isEditMode;
  }

  onSubmit(): void {
    if (!this.validateProfile()) {
      return;
    }

    this.isLoading = true;
    const profileData = { 
      ...this.profile, 
      user_id: this.userId 
    };
    
    const token = localStorage.getItem('access_token');
    const headers = { 
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    const request$ = this.hasProfile
      ? this.http.patch(this.profileApi, profileData, { headers })
      : this.http.post(this.profileApi, profileData, { headers });

    request$.subscribe({
      next: () => {
        this.isLoading = false;
        this.isEditMode = false;
        this.hasProfile = true;
        this.showSnackbar('Profile saved successfully!', 'success');
        this.loadProfile();
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Save profile error:', error);
        this.showSnackbar('Failed to save profile', 'error');
      }
    });
  }

  private validateProfile(): boolean {
    return !!(this.profile.owner_name?.trim() && 
              this.profile.owner_phone?.trim() && 
              this.profile.owner_address?.trim() && 
              this.profile.owner_city?.trim() && 
              this.profile.owner_state?.trim());
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

    this.http.get<Pet[]>(
      `${this.petsApi}?user_id=${this.userId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: (response) => {
        this.pets = response || [];
        this.loadingPets = false;
      },
      error: (error) => {
        this.pets = [];
        this.loadingPets = false;
        console.error('Load pets error:', error);
      }
    });
  }

  startAddPet(): void {
    this.isPetFormVisible = true;
    this.editingPet = false;
    this.currentPet = { pet_id: null, pet_name: '', species: '', breed: '' };
  }

  editPet(pet: Pet): void {
    this.isPetFormVisible = true;
    this.editingPet = true;
    this.currentPet = { ...pet };
  }

  cancelPetForm(): void {
    this.isPetFormVisible = false;
    this.currentPet = { pet_id: null, pet_name: '', species: '', breed: '' };
  }

  savePet(): void {
    const token = localStorage.getItem('access_token');
    const payload = { 
      ...this.currentPet, 
      owner: this.userId 
    };
    
    this.loadingPets = true;

    const headers = { 
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    const request$ = this.editingPet && this.currentPet.pet_id
      ? this.http.put(`${this.petsApi}`, 
          { ...payload, pet_id: this.currentPet.pet_id, user_id: this.userId }, 
          { headers })
      : this.http.post(`${this.petsApi}`, payload, { headers });

    request$.subscribe({
      next: () => {
        this.loadingPets = false;
        this.isPetFormVisible = false;
        this.showSnackbar('Pet saved successfully!', 'success');
        this.loadPets();
      },
      error: (error) => {
        this.loadingPets = false;
        console.error('Save pet error:', error);
        this.showSnackbar('Failed to save pet', 'error');
      }
    });
  }

  deletePet(pet: Pet): void {
    const snackRef = this.snackBar.open(
      `Delete ${pet.pet_name}?`,
      'DELETE',
      {
        duration: 5000,
        panelClass: ['snackbar-warning'],
        horizontalPosition: 'right',
        verticalPosition: 'top'
      }
    );

    snackRef.onAction().subscribe(() => {
      const token = localStorage.getItem('access_token');

      this.http.delete(
        `${this.petsApi}?user_id=${this.userId}&pet_id=${pet.pet_id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      ).subscribe({
        next: () => {
          this.pets = this.pets.filter(p => p.pet_id !== pet.pet_id);
          this.showSnackbar(`${pet.pet_name} deleted`, 'success');
        },
        error: (error) => {
          console.error('Delete pet error:', error);
          this.showSnackbar('Failed to delete pet', 'error');
        }
      });
    });
  }

}