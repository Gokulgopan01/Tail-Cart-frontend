import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-pet-public',
    standalone: true,
    imports: [CommonModule, HttpClientModule, RouterModule, FormsModule],
    templateUrl: './pet-public.component.html',
    styleUrls: ['./pet-public.component.css']
})
export class PetPublicComponent implements OnInit {
    userId: string | null = null;
    petId: string | null = null;
    uuid: string | null = null;
    profileData: any = null;
    selectedPet: any = null;
    loading: boolean = true;
    error: string | null = null;

    // Modal & Form State
    isLocationModalOpen: boolean = false;
    isSubmitting: boolean = false;
    finderName: string = '';
    finderPhone: string = '';

    // Customization variables (can be fetched from API later)
    themeColor: string = '#D4AF37'; // Default Gold
    fontFamily: string = "'Montserrat', sans-serif";

    private profileApi = 'http://127.0.0.1:8000/api/user/profile/';
    private publicPetApi = 'http://127.0.0.1:8000/api/public/pet/qr/';
    private alertsApi = 'https://tailcart.duckdns.org/api/alerts/'; // External Alert API

    constructor(private route: ActivatedRoute, private http: HttpClient) { }

    ngOnInit(): void {
        // Check for path param 'uuid'
        this.uuid = this.route.snapshot.paramMap.get('uuid');

        if (this.uuid) {
            this.fetchPublicPet(this.uuid);
        } else {
            // Fallback to query params mode
            this.route.queryParams.subscribe(params => {
                this.userId = params['user_id'];
                this.petId = params['pet_id'];
                if (this.userId && this.petId) {
                    this.fetchProfile();
                } else {
                    this.error = 'Invalid Profile or Pet ID';
                    this.loading = false;
                }
            });
        }
    }

    fetchPublicPet(uuid: string): void {
        this.http.get(`${this.publicPetApi}${uuid}`).subscribe({
            next: (data: any) => {
                // Map the flat data to the expected structure
                this.profileData = {
                    owner_name: data.owner_name,
                    owner_phone: data.owner_phone,
                    owner_address: data.owner_address,
                    owner_city: data.owner_city,
                    owner_state: data.owner_state,
                    owner_photo: data.owner_photo || '/media/owners/default.jpg' // Fallback
                };
                this.selectedPet = {
                    pet_name: data.pet_name,
                    species: data.species,
                    breed: data.breed,
                    age: data.age,
                    pet_photo: data.pet_photo,
                    is_lost: data.is_lost
                };
                this.loading = false;
            },
            error: (err) => {
                console.error('Error fetching public pet:', err);
                this.error = 'Failed to load pet details.';
                this.loading = false;
            }
        });
    }

    fetchProfile(): void {
        const token = localStorage.getItem('access_token');
        const headers = new HttpHeaders({
            'Authorization': `Bearer ${token}`
        });
        this.http.get(`${this.profileApi}?user_id=${this.userId}`, { headers }).subscribe({
            next: (data: any) => {
                this.profileData = data;
                if (data.pets && data.pets.length > 0) {
                    this.selectedPet = data.pets.find((p: any) => p.pet_id.toString() === this.petId);
                    if (!this.selectedPet) {
                        this.error = 'Pet not found in this profile.';
                    }
                } else {
                    this.error = 'No pets found for this user.';
                }
                this.loading = false;
            },
            error: (err) => {
                console.error('Error fetching profile:', err);
                this.error = 'Failed to load profile details.';
                this.loading = false;
            }
        });
    }

    callOwner(phone: string): void {
        window.location.href = `tel:${phone}`;
    }

    openLocationModal(): void {
        this.isLocationModalOpen = true;
    }

    closeLocationModal(): void {
        this.isLocationModalOpen = false;
        this.finderName = '';
        this.finderPhone = '';
    }

    submitLocationShare(): void {
        if (!this.finderName) {
            alert('Please enter your name.');
            return;
        }

        if (navigator.geolocation) {
            this.isSubmitting = true;
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const payload = {
                        user_id: this.userId,
                        pet_id: this.petId,
                        finder_name: this.finderName,
                        finder_phone: this.finderPhone,
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        timestamp: new Date().toISOString()
                    };

                    this.http.post(this.alertsApi, payload).subscribe({
                        next: () => {
                            alert('Location shared successfully! The owner has been notified.');
                            this.closeLocationModal();
                            this.isSubmitting = false;
                        },
                        error: (err) => {
                            console.error('API Error:', err);
                            // Fallback to WhatsApp if API fails
                            const mapsUrl = `https://www.google.com/maps?q=${position.coords.latitude},${position.coords.longitude}`;
                            window.open(`https://wa.me/${this.profileData.owner_phone}?text=I found ${this.selectedPet.pet_name}! My name is ${this.finderName}. My location: ${mapsUrl}`, '_blank');
                            this.isSubmitting = false;
                            this.closeLocationModal();
                        }
                    });
                },
                (error) => {
                    alert('Could not get your location. Please ensure GPS is enabled.');
                    this.isSubmitting = false;
                }
            );
        } else {
            alert('Geolocation is not supported by this browser.');
        }
    }
}
