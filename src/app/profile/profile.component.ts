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
  // EXACT API DATA
  profile: UserProfile = {
    owner_name: '',
    owner_address: '',
    owner_phone: '',
    owner_city: '',
    owner_state: ''
  };

  pets: Pet[] = [];
  allpets: Pet[] = [];
  
  // UI states
  activeTab: 'owner' | 'pets' = 'owner';
  isEditMode = false;
  isLoading = false;
  hasProfile = false;
  userId: string | null = '';
  loadingPets = false;
  isPetFormVisible = false;
  editingPet = false;
  currentPet: Pet = { pet_id: null, pet_name: '', species: '', breed: '' };
  
  // ONLY ADDITION: Avatar (frontend only)
  ownerAvatar: string = 'male';
  currentPetAvatar: string = 'pet1';
  petAvatars: Map<number, string> = new Map();

  private profileApi = 'https://tailcart1.duckdns.org/api/user/profile/';
  private petsApi = 'https://tailcart1.duckdns.org/api/user/pets/';

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
        }
      }
    });
  }

  toggleEditMode(): void {
    this.isEditMode = !this.isEditMode;
  }

  selectOwnerAvatar(avatar: 'male' | 'female'): void {
  this.ownerAvatar = avatar;
}

  selectPetAvatar(avatar: string): void {
    this.currentPetAvatar = avatar;
  }

  onSubmit(): void {
    if (!this.profile.owner_name?.trim()) return;

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
        this.loadProfile();
      },
      error: (error) => {
        this.isLoading = false;
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

    this.http.get<Pet[]>(
      `${this.petsApi}?user_id=${this.userId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: (response) => {
        this.pets = response || [];
        this.allpets = response || [];
        this.loadingPets = false;
      },
      error: (error) => {
        this.pets = [];
        this.loadingPets = false;
      }
    });
  }

  showOnlyDogs(): void {
    this.pets = this.allpets.filter(
      pet => pet.species?.toLowerCase() === 'dog'
    );
  }

  showAllPets(): void {
    this.pets = this.allpets;
  }

  showOnlyCats(): void {
    this.pets = this.allpets.filter(pets => pets.species?.toLowerCase() === 'cat')
  }

  showOtherPets(): void {
    this.pets = this.allpets.filter(pets => pets.species?.toLowerCase() !== 'cat' && pets.species?.toLowerCase() !== 'dog')
  }

  startAddPet(): void {
    this.isPetFormVisible = true;
    this.editingPet = false;
    this.currentPet = { pet_id: null, pet_name: '', species: '', breed: '' };
    this.currentPetAvatar = 'pet1';
  }

  editPet(pet: Pet): void {
    this.isPetFormVisible = true;
    this.editingPet = true;
    this.currentPet = { ...pet };
    this.currentPetAvatar = this.petAvatars.get(pet.pet_id!) || 'pet1';
  }

  cancelPetForm(): void {
    this.isPetFormVisible = false;
    this.currentPet = { pet_id: null, pet_name: '', species: '', breed: '' };
    this.currentPetAvatar = 'pet1';
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
          { ...payload, user_id: this.userId }, 
          { headers })
      : this.http.post(`${this.petsApi}`, payload, { headers });

    request$.subscribe({
      next: (response: any) => {
        this.loadingPets = false;
        this.isPetFormVisible = false;
        
        // Save avatar locally
        if (response && response.pet_id) {
          this.petAvatars.set(response.pet_id, this.currentPetAvatar);
        }
        
        this.loadPets();
      },
      error: (error) => {
        this.loadingPets = false;
      }
    });
  }

  deletePet(pet: Pet): void {
    const token = localStorage.getItem('access_token');

    this.http.delete(
      `${this.petsApi}?user_id=${this.userId}&pet_id=${pet.pet_id}`,
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: () => {
        this.pets = this.pets.filter(p => p.pet_id !== pet.pet_id);
        this.petAvatars.delete(pet.pet_id!);
      },
      error: (error) => {
        console.error('Delete pet error:', error);
      }
    });
  }

  getPetAvatar(petId: number | null): string {
    if (!petId) return 'pet1';
    return this.petAvatars.get(petId) || 'pet1';
  }
}