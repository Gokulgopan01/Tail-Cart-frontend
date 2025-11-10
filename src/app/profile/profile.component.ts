import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import Swal from 'sweetalert2';

export interface UserProfile {
  user_id?: string;
  owner_name: string;
  owner_address: string;
  owner_phone: string;
  owner_city: string;
  owner_state: string;
  pets?: any[];
}

export interface ProfileResponse {
  message: string;
  profile_id?: number;
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

  isEditMode = false;
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  hasProfile = false;
  userId: string | null = '';
  pets: any[] = [];
  loadingPets = false;
  isPetFormVisible = false;
  editingPet = false;
  currentPet = { pet_id: null, pet_name: '', species: '', breed: '' };

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id');
    if (!this.userId) {
      this.router.navigate(['/auth']);
      return;
    }
    this.loadProfile();
    this.loadPets();
  }

  deletePet(pet: any): void {
    Swal.fire({
      title: 'Are you sure?',
      text: `Do you want to delete pet ${pet.pet_name}?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, delete it!',
      cancelButtonText: 'Cancel'
    }).then(result => {
      if (result.isConfirmed) {
        this.http.delete(`https://bulbous-unaesthetical-albert.ngrok-free.dev/api/user/pets/${pet.pet_id}/`)
          .subscribe({
            next: () => {
              Swal.fire('Deleted!', `${pet.pet_name} has been deleted.`, 'success');
              this.loadPets();
            },
            error: () => {
              Swal.fire('Error', 'Failed to delete pet', 'error');
            }
          });
      }
    });
  }

  loadProfile(): void {
    this.isLoading = true;
    this.http.get<UserProfile>(`https://bulbous-unaesthetical-albert.ngrok-free.dev/api/user/profile/?user_id=${this.userId}`)
      .subscribe({
        next: (response) => {
          this.isLoading = false;
          if (response.owner_name) {
            this.profile = response;
            this.hasProfile = true;
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
            Swal.fire('Error', 'Failed to load profile. Please try again.', 'error');
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

    const profileData = { ...this.profile, user_id: this.userId };

    const request$ = this.hasProfile
      ? this.http.patch<ProfileResponse>('https://bulbous-unaesthetical-albert.ngrok-free.dev/api/user/profile/', profileData)
      : this.http.post<ProfileResponse>('https://bulbous-unaesthetical-albert.ngrok-free.dev/api/user/profile/', profileData);

    request$.subscribe({
      next: (response) => {
        this.isLoading = false;
        Swal.fire('Success', response.message || (this.hasProfile ? 'Profile updated!' : 'Profile created!'), 'success');
        this.isEditMode = false;
        this.hasProfile = true;
        this.loadProfile();
      },
      error: (error) => {
        this.isLoading = false;
        let message = error.error?.message || 'Failed to save profile. Please try again.';
        Swal.fire('Error', message, 'error');
      }
    });
  }

  cancelEdit(): void {
    if (this.hasProfile) {
      this.isEditMode = false;
      this.loadProfile();
    } else {
      this.router.navigate(['/home']);
    }
  }

  loadPets(): void {
    if (!this.userId) return;
    this.loadingPets = true;
    this.http.get<any[]>(`https://bulbous-unaesthetical-albert.ngrok-free.dev/api/user/pets/?user_id=${this.userId}`)
      .subscribe({
        next: (response) => {
          this.pets = response;
          this.loadingPets = false;
        },
        error: () => {
          this.pets = [];
          this.loadingPets = false;
        }
      });
  }

  startAddPet(): void {
    this.isPetFormVisible = true;
    this.editingPet = false;
    this.currentPet = { pet_id: null, pet_name: '', species: '', breed: '' };
  }

  editPet(pet: any): void {
    this.isPetFormVisible = true;
    this.editingPet = true;
    this.currentPet = { ...pet };
  }

  cancelPetForm(): void {
    this.isPetFormVisible = false;
    this.currentPet = { pet_id: null, pet_name: '', species: '', breed: '' };
  }

  savePet(): void {
    const payload = { ...this.currentPet, owner: this.userId };
    this.loadingPets = true;

    const request$ = this.editingPet
      ? this.http.put('https://bulbous-unaesthetical-albert.ngrok-free.dev/api/user/pets/', { ...payload, pet_id: this.currentPet.pet_id, user_id: this.userId })
      : this.http.post('https://bulbous-unaesthetical-albert.ngrok-free.dev/api/user/pets/', payload);

    request$.subscribe({
      next: () => {
        this.loadingPets = false;
        this.isPetFormVisible = false;
        Swal.fire('Success', this.editingPet ? 'Pet updated successfully!' : 'Pet added successfully!', 'success');
        this.loadPets();
      },
      error: () => {
        this.loadingPets = false;
        Swal.fire('Error', this.editingPet ? 'Failed to update pet' : 'Failed to add pet', 'error');
      }
    });
  }
}
