import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { trigger, transition, style, animate } from '@angular/animations';

interface Alert {
  id: number;
  sender_name: string;
  phone: string;
  location: string;
  message: string;
  created_at: string;
  resolved?: boolean;
}

interface Pet {
  pet_id: number | null;
  pet_name: string;
  species: string;
  breed: string;
  age: number;
  is_lost: boolean;
  pet_photo: string | null;
  about?: string | null;
  alerts?: Alert[];
  owner?: number;
}

@Component({
  selector: 'app-pet-profile',
  standalone: true,
  imports: [CommonModule, RouterModule, MatSnackBarModule],
  templateUrl: './pet-profile.component.html',
  styleUrls: ['./pet-profile.component.css'],
  animations: [
    trigger('fadeUp', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(20px)' }),
        animate('500ms cubic-bezier(0.16, 1, 0.3, 1)', style({ opacity: 1, transform: 'translateY(0)' }))
      ])
    ])
  ]
})
export class PetProfileComponent implements OnInit {
  petId: string | null = null;
  userId: string | null = null;
  pet: Pet | null = null;
  isLoading = true;

  private petsApi = 'http://127.0.0.1:8000/api/user/pets/';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id');
    this.petId = this.route.snapshot.paramMap.get('petId');

    if (!this.userId || !this.petId) {
      this.router.navigate(['/profile']);
      return;
    }

    this.loadPet();
  }

  loadPet(): void {
    this.isLoading = true;
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<Pet[]>(
      `${this.petsApi}?user_id=${this.userId}`,
      { headers }
    ).subscribe({
      next: (pets) => {
        this.isLoading = false;
        this.pet = pets.find(p => p.pet_id === Number(this.petId)) || null;
        if (!this.pet) {
          this.showSnackbar('Pet not found');
          this.router.navigate(['/profile']);
        }
      },
      error: (err) => {
        this.isLoading = false;
        this.showSnackbar('Error loading pet details');
        console.error(err);
      }
    });
  }

  toggleLostStatus(): void {
    if (!this.pet || !this.pet.pet_id || !this.userId) return;

    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    const newStatus = !this.pet.is_lost;
    const payload = {
      user_id: this.userId,
      pet_id: this.pet.pet_id,
      is_lost: newStatus
    };

    this.http.put(this.petsApi, payload, { headers }).subscribe({
      next: () => {
        this.pet!.is_lost = newStatus;
        this.showSnackbar(`${this.pet!.pet_name} is now ${newStatus ? 'Reported Lost' : 'Marked Safe'}`);
      },
      error: () => this.showSnackbar('Failed to update status')
    });
  }

  deletePet(): void {
    if (!this.pet || !this.pet.pet_id || !this.userId) return;

    if (!confirm(`Are you sure you want to remove ${this.pet.pet_name}? This cannot be undone.`)) {
      return;
    }

    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.delete(
      `${this.petsApi}?user_id=${this.userId}&pet_id=${this.pet.pet_id}`,
      { headers }
    ).subscribe({
      next: () => {
        this.showSnackbar('Pet removed successfully');
        this.router.navigate(['/profile']);
      },
      error: () => this.showSnackbar('Failed to delete pet')
    });
  }

  editPet(): void {
    // Navigate to profile with edit query param or just open modal (for now redirecting to profile with tab)
    this.router.navigate(['/profile'], { queryParams: { editPet: this.petId } });
  }

  getPetPhoto(): string {
    if (this.pet?.pet_photo) {
      return this.pet.pet_photo.startsWith('http') 
        ? this.pet.pet_photo 
        : `http://127.0.0.1:8000${this.pet.pet_photo}`;
    }
    return 'assets/icons/pet1.svg';
  }

  private showSnackbar(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top'
    });
  }
}
