import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface PetAlert {
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
    owner: number | null;
    is_lost: boolean;
    alerts: PetAlert[];
    pet_photo: string | null;
    about: string | null;
    gender: string | null;
}

interface OwnerProfile {
    owner_name: string;
    owner_address: string;
    owner_phone: string;
    owner_email: string;
    owner_city: string;
    owner_state: string;
    owner_photo: string | null;
    emergency_contact_name: string;
    emergency_contact_phone: string;
    created_at: string;
    pets: Pet[];
}

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
    profileData: OwnerProfile | null = null;
    selectedPet: Pet | null = null;
    loading: boolean = true;
    error: string | null = null;

    // Modal & Form State
    isLocationModalOpen: boolean = false;
    isSubmitting: boolean = false;
    finderName: string = '';
    finderPhone: string = '';
    finderMessage: string = '';

    // Customization variables
    themeColor: string = '#D4AF37'; // Default Gold
    fontFamily: string = "'Montserrat', sans-serif";

    private profileApi = 'http://127.0.0.1:8000/api/user/profile/';
    private publicPetApi = 'http://127.0.0.1:8000/api/public/pet/';
    private alertsApi = 'http://127.0.0.1:8000/api/alerts/create/';

    constructor(private route: ActivatedRoute, private http: HttpClient) { }

    ngOnInit(): void {
        this.uuid = this.route.snapshot.paramMap.get('uuid');

        if (this.uuid) {
            this.fetchPublicPet(this.uuid);
        } else {
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
        this.http.get<any>(`${this.publicPetApi}${uuid}`).subscribe({
            next: (data: any) => {
                // The public pet endpoint may return a flat structure
                // Map it to our full OwnerProfile shape
                this.profileData = {
                    owner_name: data.owner_name || '',
                    owner_address: data.owner_address || '',
                    owner_phone: data.owner_phone || '',
                    owner_email: data.owner_email || '',
                    owner_city: data.owner_city || '',
                    owner_state: data.owner_state || '',
                    owner_photo: data.owner_photo || null,
                    emergency_contact_name: data.emergency_contact_name || '',
                    emergency_contact_phone: data.emergency_contact_phone || '',
                    created_at: data.created_at || '',
                    pets: data.pets || []
                };

                // If pets array is present, pick the right one; else build from flat fields
                if (data.pets && data.pets.length > 0) {
                    this.selectedPet = data.pets[0];
                } else {
                    this.selectedPet = {
                        pet_id: data.pet_id || null,
                        pet_name: data.pet_name || '',
                        species: data.species || '',
                        breed: data.breed || '',
                        age: data.age || 0,
                        owner: null,
                        is_lost: data.is_lost || false,
                        alerts: data.alerts || [],
                        pet_photo: data.pet_photo || null,
                        about: data.about || null,
                        gender: data.gender || null
                    };
                }
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
        const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });

        this.http.get<OwnerProfile>(`${this.profileApi}?user_id=${this.userId}`, { headers }).subscribe({
            next: (data: OwnerProfile) => {
                this.profileData = data;
                if (data.pets && data.pets.length > 0) {
                    this.selectedPet = data.pets.find((p: Pet) => p.pet_id?.toString() === this.petId) || null;
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

    getOwnerPhoto(): string {
        if (this.profileData?.owner_photo) {
            return this.profileData.owner_photo.startsWith('http')
                ? this.profileData.owner_photo
                : `http://127.0.0.1:8000${this.profileData.owner_photo}`;
        }
        return '';
    }

    getPetPhoto(): string {
        if (this.selectedPet?.pet_photo) {
            return this.selectedPet.pet_photo.startsWith('http')
                ? this.selectedPet.pet_photo
                : `http://127.0.0.1:8000${this.selectedPet.pet_photo}`;
        }
        return 'assets/icons/pet1.svg';
    }

    callOwner(phone: string): void {
        window.location.href = `tel:${phone}`;
    }

    callEmergency(phone: string): void {
        window.location.href = `tel:${phone}`;
    }

    openLocationModal(): void {
        this.isLocationModalOpen = true;
    }

    closeLocationModal(): void {
        this.isLocationModalOpen = false;
        this.finderName = '';
        this.finderPhone = '';
        this.finderMessage = '';
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
                    const mapsUrl = `https://www.google.com/maps?q=${position.coords.latitude},${position.coords.longitude}`;
                    const payload = {
                        pet_id: this.selectedPet?.pet_id || Number(this.petId),
                        sender_name: this.finderName,
                        phone: this.finderPhone,
                        message: this.finderMessage,
                        location: mapsUrl, // Sending the live location link as requested
                    };

                    this.http.post(this.alertsApi, payload).subscribe({
                        next: () => {
                            alert('Location shared successfully! The owner has been notified.');
                            this.closeLocationModal();
                            this.isSubmitting = false;
                        },
                        error: (err) => {
                            console.error('API Error:', err);
                            const waMessage = `I found ${this.selectedPet?.pet_name}! My name is ${this.finderName}. ${this.finderMessage ? 'Message: ' + this.finderMessage : ''} My location: ${mapsUrl}`;
                            window.open(`https://wa.me/${this.profileData?.owner_phone}?text=${encodeURIComponent(waMessage)}`, '_blank');
                            this.isSubmitting = false;
                            this.closeLocationModal();
                        }
                    });
                },
                (error) => {
                    console.error('Geolocation error:', error);
                    alert('Could not get your location. Please ensure GPS is enabled and permissions are granted.');
                    this.isSubmitting = false;
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        } else {
            alert('Geolocation is not supported by this browser.');
        }
    }
}
