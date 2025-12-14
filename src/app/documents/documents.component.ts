import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBarConfig } from '@angular/material/snack-bar';

interface Document {
  document_id: number;
  user: number;
  pet: number;
  document_title: string;
  document_file: string;
  upload_date: string;
}

interface Alert {
  alert_id: number;
  user: number;
  pet: number;
  alert_type: string;
  title: string;
  due_date: string;
  frequency: string;
  is_active: boolean;
}

interface Pet {
  pet_id: number;
  pet_name: string;
  species: string;
  breed: string;
  owner: number;
}

interface UserProfile {
  owner_name: string;
  owner_address: string;
  owner_phone: string;
  owner_city: string;
  owner_state: string;
  pets: Pet[];
}

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatSnackBarModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  templateUrl: './documents.component.html',
  styleUrls: ['./documents.component.css']
})
export class DocumentsComponent implements OnInit {
  @ViewChild('uploadSection') uploadSection!: ElementRef;
  @ViewChild('fileInput') fileInput!: ElementRef;
  
  documents: Document[] = [];
  alerts: Alert[] = [];
  userProfile: UserProfile | null = null;
  userPets: Pet[] = [];
  loadingPets = false;
  
  uploadForm: FormGroup;
  alertForm: FormGroup;
  
  selectedFile: File | null = null;
  isUploading = false;
  isCreatingAlert = false;
  loadingAlerts = false;
  showAlertsModal = false;
  editingAlert: Alert | null = null;
  
  today = new Date().toISOString().split('T')[0];
  criticalAlerts: Alert[] = [];
  
  private documentsApi = 'http://127.0.0.1:8000/api/user/documents/';
  private alertsApi = 'http://127.0.0.1:8000/api/user/pet-alerts/';
  private petsApi = 'http://127.0.0.1:8000/api/user/pets/';
  private userId: string = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) {
    // Upload Form
    this.uploadForm = this.fb.group({
      document_title: ['', [Validators.required, Validators.minLength(1)]],
      pet: ['', [Validators.required, Validators.min(1)]],
      document_file: [null, [Validators.required]],
    });

    // Alert Form
    this.alertForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      pet: ['', [Validators.required]],
      alert_type: ['', [Validators.required]],
      due_date: ['', [Validators.required]],
      frequency: ['One-time'],
      is_active: [true]
    });
  }

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id') || '';
    if (this.userId) {
      this.loadDocuments();
      this.loadAlerts();
      this.loadUserPets();
      this.startAlertMonitoring();
    } else {
      console.error('User ID not found in localStorage');
      this.showSnackbar('Please log in to access documents.', 'error');
    }
  }

  startAlertMonitoring(): void {
    // Check alerts every 30 seconds
    setInterval(() => {
      this.checkCriticalAlerts();
    }, 30000);
    
    // Initial check
    this.checkCriticalAlerts();
  }

  checkCriticalAlerts(): void {
    const critical: Alert[] = [];
    const today = new Date();
    
    this.alerts.forEach(alert => {
      if (!alert.is_active) return;
      
      const dueDate = new Date(alert.due_date);
      const diffTime = dueDate.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      // If overdue or due today/tomorrow
      if (diffDays <= 2) {
        critical.push(alert);
        
        // Show snackbar for urgent alerts
        if (diffDays === 0) {
          this.showSnackbar(`CRUCIAL: ${alert.title} is due TODAY!`, 'error');
        } else if (diffDays === 1) {
          this.showSnackbar(`Urgent: ${alert.title} is due TOMORROW!`, 'warning');
        } else if (diffDays < 0) {
          this.showSnackbar(`OVERDUE: ${alert.title} by ${Math.abs(diffDays)} days!`, 'error');
        }
      }
    });
    
    this.criticalAlerts = critical;
  }

  getDaysRemaining(alert: Alert): string {
    const today = new Date();
    const dueDate = new Date(alert.due_date);
    const diffTime = dueDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      return `Overdue by ${Math.abs(diffDays)} days`;
    } else if (diffDays === 0) {
      return 'Due today!';
    } else if (diffDays === 1) {
      return 'Due tomorrow';
    } else {
      return `${diffDays} days left`;
    }
  }

  getDaysRemainingClass(alert: Alert): string {
    const today = new Date();
    const dueDate = new Date(alert.due_date);
    const diffTime = dueDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'days-overdue';
    if (diffDays === 0) return 'days-today';
    if (diffDays <= 2) return 'days-tomorrow';
    if (diffDays <= 7) return 'days-soon';
    return 'days-normal';
  }

  loadDocuments(): void {
    this.http.get<Document[]>(`${this.documentsApi}?user_id=${this.userId}`)
      .subscribe({
        next: (docs) => {
          this.documents = docs;
        },
        error: (error) => {
          console.error('Error loading documents:', error);
          this.showSnackbar('Error loading documents. Please try again.', 'error');
        }
      });
  }

  loadAlerts(): void {
    this.loadingAlerts = true;
    this.http.get<Alert[]>(`${this.alertsApi}?user_id=${this.userId}`)
      .subscribe({
        next: (alerts) => {
          this.alerts = alerts;
          this.loadingAlerts = false;
          this.checkCriticalAlerts();
        },
        error: (error) => {
          console.error('Error loading alerts:', error);
          this.showSnackbar('Error loading alerts. Please try again.', 'error');
          this.loadingAlerts = false;
        }
      });
  }

  loadUserPets(): void {
    this.loadingPets = true;
    
    this.http.get<Pet[]>(`${this.petsApi}?user_id=${this.userId}`)
      .subscribe({
        next: (response) => {
          console.log('Pets API response:', response);
          this.userPets = response;
          this.loadingPets = false;
          
          if (response.length > 0 && !this.userProfile) {
            this.userProfile = {
              owner_name: '',
              owner_address: '',
              owner_phone: '',
              owner_city: '',
              owner_state: '',
              pets: response
            };
          }
        },
        error: (error) => {
          console.error('Error loading pets:', error);
          this.loadingPets = false;
          this.showSnackbar('Failed to load pet information', 'error');
        }
      });
  }

  getPetNameById(petId: number): string {
    if (!this.userPets || this.userPets.length === 0) {
      return '';
    }
    const pet = this.userPets.find(p => p.pet_id === petId);
    return pet ? pet.pet_name : '';
  }

  // Document Methods
  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        this.showSnackbar('File size must be less than 10MB', 'error');
        return;
      }
      
      this.selectedFile = file;
      this.uploadForm.patchValue({
        document_file: file
      });
      this.uploadForm.get('document_file')?.markAsTouched();
      this.showSnackbar(`Selected: ${file.name}`, 'success');
    }
  }

  clearFile(): void {
    this.selectedFile = null;
    this.uploadForm.patchValue({
      document_file: null
    });
    this.uploadForm.get('document_file')?.markAsUntouched();
    
    if (this.fileInput) {
      this.fileInput.nativeElement.value = '';
    }
  }

  onSubmit(): void {
    if (this.uploadForm.valid && this.selectedFile) {
      this.isUploading = true;
      
      const formData = new FormData();
      formData.append('user', this.userId.toString());
      formData.append('pet', this.uploadForm.get('pet')?.value);
      formData.append('document_title', this.uploadForm.get('document_title')?.value);
      formData.append('document_file', this.selectedFile);

      this.http.post(this.documentsApi, formData)
        .subscribe({
          next: (response: any) => {
            this.isUploading = false;
            this.uploadForm.reset();
            this.selectedFile = null;
            this.loadDocuments();
            this.showSnackbar('Document uploaded successfully!', 'success');
          },
          error: (error) => {
            this.isUploading = false;
            console.error('Error uploading document:', error);

            let errorMessage = 'Error uploading document. Please try again';
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
        });
    } else {
      Object.keys(this.uploadForm.controls).forEach(key => {
        this.uploadForm.get(key)?.markAsTouched();
      });
      this.showSnackbar('Please fill in all required fields', 'error');
    }
  }

  downloadDocument(doc: Document): void {
    const fileUrl = `https://tailcart.duckdns.org${doc.document_file}`;
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = doc.document_title;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    this.showSnackbar(`Downloading ${doc.document_title}`, 'info');
  }

  deleteDocument(documentId: number): void {
    if (confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      this.http.delete(`${this.documentsApi}/${documentId}/`)
        .subscribe({
          next: () => {
            this.documents = this.documents.filter(doc => doc.document_id !== documentId);
            this.showSnackbar('Document deleted successfully!', 'success');
          },
          error: (error) => {
            console.error('Error deleting document:', error);
            this.showSnackbar('Error deleting document. Please try again.', 'error');
          }
        });
    }
  }

  // Alert Methods
  createAlert(): void {
    if (this.alertForm.valid) {
      this.isCreatingAlert = true;
      
      const alertData = {
        user: this.userId,
        ...this.alertForm.value
      };

      const url = this.editingAlert 
        ? `${this.alertsApi}?user_id=${this.userId}&alert_id=${this.editingAlert.alert_id}`
        : this.alertsApi;

      const request$ = this.editingAlert
        ? this.http.put(url, alertData)
        : this.http.post(url, alertData);

      request$.subscribe({
        next: (response: any) => {
          this.isCreatingAlert = false;
          this.alertForm.reset({ frequency: 'One-time', is_active: true });
          this.editingAlert = null;
          this.loadAlerts();
          this.showSnackbar(
            this.editingAlert ? 'Alert updated successfully!' : 'Alert created successfully!',
            'success'
          );
        },
        error: (error) => {
          this.isCreatingAlert = false;
          console.error('Error saving alert:', error);
          this.showSnackbar('Error saving alert. Please try again.', 'error');
        }
      });
    } else {
      Object.keys(this.alertForm.controls).forEach(key => {
        this.alertForm.get(key)?.markAsTouched();
      });
    }
  }

  editAlert(alert: Alert): void {
    this.editingAlert = alert;
    this.alertForm.patchValue({
      title: alert.title,
      pet: alert.pet.toString(),
      alert_type: alert.alert_type,
      due_date: alert.due_date,
      frequency: alert.frequency,
      is_active: alert.is_active
    });
    
    // Scroll to alert form
    this.scrollToAlertForm();
    this.showSnackbar('Editing alert: ' + alert.title, 'info');
  }

  deleteAlert(alertId: number): void {
    if (confirm('Are you sure you want to delete this alert?')) {
      this.http.delete(`${this.alertsApi}?alert_id=${alertId}`)
        .subscribe({
          next: () => {
            this.alerts = this.alerts.filter(alert => alert.alert_id !== alertId);
            this.showSnackbar('Alert deleted successfully!', 'success');
          },
          error: (error) => {
            console.error('Error deleting alert:', error);
            this.showSnackbar('Error deleting alert. Please try again.', 'error');
          }
        });
    }
  }

  openAlertFormForDocument(doc: Document): void {
    this.alertForm.patchValue({
      title: `Reminder for ${doc.document_title}`,
      pet: doc.pet.toString(),
      alert_type: 'Vaccination', // Default for documents
      due_date: this.today
    });
    
    this.scrollToAlertForm();
    this.showSnackbar('Set an alert for this document', 'info');
  }

  // Helper Methods
  getUpcomingAlertsCount(): number {
    const today = new Date();
    return this.alerts.filter(alert => {
      const dueDate = new Date(alert.due_date);
      return dueDate >= today && alert.is_active;
    }).length;
  }

  isAlertDueSoon(alert: Alert): boolean {
    const today = new Date();
    const dueDate = new Date(alert.due_date);
    const diffTime = dueDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 7 && diffDays > 0 && alert.is_active;
  }

  isAlertOverdue(alert: Alert): boolean {
    const today = new Date();
    const dueDate = new Date(alert.due_date);
    return dueDate < today && alert.is_active;
  }

  isAlertActive(alert: Alert): boolean {
    return alert.is_active;
  }

  getAlertIcon(alertType: string): string {
    const icons: { [key: string]: string } = {
      'Vaccination': 'fas fa-syringe',
      'Medication': 'fas fa-pills',
      'Appointment': 'fas fa-calendar-check',
      'Checkup': 'fas fa-stethoscope',
      'Other': 'fas fa-bell'
    };
    return icons[alertType] || 'fas fa-bell';
  }

  getAlertIconClass(alertType: string): string {
    return alertType.toLowerCase();
  }

  getAlertBadgeClass(alertType: string): string {
    const classes: { [key: string]: string } = {
      'Vaccination': 'bg-primary bg-opacity-20 text-primary',
      'Medication': 'bg-success bg-opacity-20 text-success',
      'Appointment': 'bg-warning bg-opacity-20 text-warning',
      'Checkup': 'bg-info bg-opacity-20 text-info',
      'Other': 'bg-secondary bg-opacity-20 text-secondary'
    };
    return classes[alertType] || 'bg-secondary bg-opacity-20 text-secondary';
  }

  getDueDateTextClass(alert: Alert): string {
    if (this.isAlertOverdue(alert)) return 'text-danger';
    if (this.isAlertDueSoon(alert)) return 'text-warning';
    return 'text-muted';
  }

  getTotalSize(): string {
    const totalSize = this.documents.length * 0.5;
    return totalSize < 1 ? `${(totalSize * 1024).toFixed(0)} KB` : `${totalSize.toFixed(1)} MB`;
  }

  // UI Methods
  toggleAlertsModal(): void {
    this.showAlertsModal = !this.showAlertsModal;
    if (this.showAlertsModal) {
      this.loadAlerts();
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
  }

  scrollToUpload(): void {
    if (this.uploadSection) {
      this.uploadSection.nativeElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  }

  scrollToAlertForm(): void {
    this.toggleAlertsModal(); // Close modal first
    setTimeout(() => {
      const alertCard = document.querySelector('.alert-create-card');
      if (alertCard) {
        alertCard.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    }, 300);
  }

  showSnackbar(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', duration?: number): void {
    const config: MatSnackBarConfig = {
      duration: duration || (type === 'error' || type === 'warning' ? 5000 : 3000),
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: [`snackbar-${type}`],
      politeness: 'polite'
    };
    
    this.snackBar.open(message, 'Close', config);
  }
  showCriticalNotification(): void {
    if (this.criticalAlerts.length > 0) {
      const criticalAlert = this.criticalAlerts[0];
      const message = `⚠️ CRITICAL: ${criticalAlert.title} - ${this.getDaysRemaining(criticalAlert)}`;
      this.showSnackbar(message, 'error', 10000); // Show for 10 seconds
    }
  }
}