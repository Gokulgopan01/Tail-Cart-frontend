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
  @ViewChild('fileInput') fileInput!: ElementRef;
  
  documents: Document[] = [];
  alerts: Alert[] = [];
  userPets: Pet[] = [];
  loadingPets = false;
  
  uploadForm: FormGroup;
  alertForm: FormGroup;
  
  selectedFile: File | null = null;
  isUploading = false;
  isCreatingAlert = false;
  loadingAlerts = false;
  
  showUploadModal = false;
  showCreateAlertModal = false;
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
    this.uploadForm = this.fb.group({
      document_title: ['', [Validators.required]],
      pet: ['', [Validators.required]]
    });

    this.alertForm = this.fb.group({
      title: ['', [Validators.required]],
      pet: ['', [Validators.required]],
      alert_type: ['', [Validators.required]],
      due_date: ['', [Validators.required]],
      frequency: ['One-time']
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
      this.showSnackbar('Please log in to access documents.', 'error');
    }
  }

  startAlertMonitoring(): void {
    setInterval(() => {
      this.checkCriticalAlerts();
    }, 30000);
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
      
      if (diffDays <= 2) {
        critical.push(alert);
        
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

  // Modal Methods
  openUploadModal(): void {
    this.showUploadModal = true;
    document.body.style.overflow = 'hidden';
  }

  closeUploadModal(): void {
    this.showUploadModal = false;
    this.uploadForm.reset();
    this.selectedFile = null;
    document.body.style.overflow = 'auto';
  }

  openCreateAlertModal(): void {
    this.showCreateAlertModal = true;
    document.body.style.overflow = 'hidden';
  }

  closeCreateAlertModal(): void {
    this.showCreateAlertModal = false;
    this.alertForm.reset({ frequency: 'One-time' });
    this.editingAlert = null;
    document.body.style.overflow = 'auto';
  }

  closeAllModals(): void {
    this.closeUploadModal();
    this.closeCreateAlertModal();
    this.showAlertsModal = false;
    document.body.style.overflow = 'auto';
  }

  // Document Methods
  loadDocuments(): void {
    this.http.get<Document[]>(`${this.documentsApi}?user_id=${this.userId}`)
      .subscribe({
        next: (docs) => {
          this.documents = docs;
        },
        error: (error) => {
          console.error('Error loading documents:', error);
          this.showSnackbar('Error loading documents.', 'error');
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
          this.showSnackbar('Error loading alerts.', 'error');
          this.loadingAlerts = false;
        }
      });
  }

  loadUserPets(): void {
    this.loadingPets = true;
    this.http.get<Pet[]>(`${this.petsApi}?user_id=${this.userId}`)
      .subscribe({
        next: (response) => {
          this.userPets = response;
          this.loadingPets = false;
        },
        error: (error) => {
          console.error('Error loading pets:', error);
          this.loadingPets = false;
        }
      });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        this.showSnackbar('File size must be less than 10MB', 'error');
        return;
      }
      
      this.selectedFile = file;
      this.showSnackbar(`Selected: ${file.name}`, 'success');
    }
  }

  clearFile(): void {
    this.selectedFile = null;
    if (this.fileInput) {
      this.fileInput.nativeElement.value = '';
    }
  }

  onSubmit(): void {
    if (this.uploadForm.valid && this.selectedFile) {
      this.isUploading = true;
      
      const formData = new FormData();
      formData.append('user', this.userId);
      formData.append('pet', this.uploadForm.get('pet')?.value);
      formData.append('document_title', this.uploadForm.get('document_title')?.value);
      formData.append('document_file', this.selectedFile);

      this.http.post(this.documentsApi, formData)
        .subscribe({
          next: () => {
            this.isUploading = false;
            this.closeUploadModal();
            this.loadDocuments();
            this.showSnackbar('Document uploaded successfully!', 'success');
          },
          error: (error) => {
            this.isUploading = false;
            console.error('Error uploading document:', error);
            this.showSnackbar('Error uploading document.', 'error');
          }
        });
    } else {
      Object.keys(this.uploadForm.controls).forEach(key => {
        this.uploadForm.get(key)?.markAsTouched();
      });
      if (!this.selectedFile) {
        this.showSnackbar('Please select a file', 'error');
      }
    }
  }

  downloadDocument(doc: Document): void {
    const fileUrl = ` http://127.0.0.1:8000${doc.document_file}`;
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = doc.document_title;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    this.showSnackbar(`Downloading ${doc.document_title}`, 'info');
  }

  previewDocument(doc: Document): void {
    const fileUrl = ` http://127.0.0.1:8000${doc.document_file}`;
    window.open(fileUrl, '_blank');
  }

  deleteDocument(documentId: number): void {
  const snackRef = this.snackBar.open(
    'Are you sure you want to delete this document?',
    'DELETE',
    {
      duration: 8000,
      panelClass: ['snackbar-warning'],
      horizontalPosition: 'right',
      verticalPosition: 'top'
    }
  );

  snackRef.onAction().subscribe(() => {
    const params = { document_id: documentId.toString() };

    this.http.delete(this.documentsApi, { params })
      .subscribe({
        next: () => {
          this.documents = this.documents.filter(
            doc => doc.document_id !== documentId
          );
          this.showSnackbar('Document deleted successfully', 'success');
        },
        error: (error) => {
          console.error('Error deleting document:', error);
          this.showSnackbar('Failed to delete document', 'error');
        }
      });
  });
}

  // Alert Methods
  createAlert(): void {
    if (this.alertForm.valid) {
      this.isCreatingAlert = true;
      
      const alertData = {
        user: this.userId,
        ...this.alertForm.value,
        is_active: true
      };

      const request$ = this.http.post(this.alertsApi, alertData);

      request$.subscribe({
        next: () => {
          this.isCreatingAlert = false;
          this.closeCreateAlertModal();
          this.loadAlerts();
          this.showSnackbar('Alert created successfully!', 'success');
        },
        error: (error) => {
          this.isCreatingAlert = false;
          console.error('Error saving alert:', error);
          this.showSnackbar('Error saving alert.', 'error');
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
      frequency: alert.frequency
    });
    this.openCreateAlertModal();
  }

  deleteAlert(alertId: number): void {
  const snackRef = this.snackBar.open(
    'Are you sure you want to delete this alert?',
    'DELETE',
    {
      duration: 8000,
      panelClass: ['snackbar-warning'],
      horizontalPosition: 'right',
      verticalPosition: 'top'
    }
  );

  snackRef.onAction().subscribe(() => {
    const params = { alert_id: alertId.toString() };

    this.http.delete(this.alertsApi, { params })
      .subscribe({
        next: () => {
          this.alerts = this.alerts.filter(
            alert => alert.alert_id !== alertId
          );
          this.showSnackbar('Alert deleted successfully', 'success');
        },
        error: (error) => {
          console.error('Error deleting alert:', error);
          this.showSnackbar('Failed to delete alert', 'error');
        }
      });
  });
}


  openAlertFormForDocument(doc: Document): void {
    this.alertForm.patchValue({
      title: `Reminder for ${doc.document_title}`,
      pet: doc.pet.toString(),
      alert_type: 'Vaccination',
      due_date: this.today
    });
    this.openCreateAlertModal();
  }

  // Helper Methods
  getPetNameById(petId: number): string {
    const pet = this.userPets.find(p => p.pet_id === petId);
    return pet ? pet.pet_name : '';
  }

  getUpcomingAlertsCount(): number {
    const today = new Date();
    return this.alerts.filter(alert => {
      const dueDate = new Date(alert.due_date);
      return dueDate >= today && alert.is_active;
    }).length;
  }

  getDaysRemaining(alert: Alert): string {
    const today = new Date();
    const dueDate = new Date(alert.due_date);
    const diffTime = dueDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return `Overdue`;
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    return `${diffDays}d`;
  }

  getDaysRemainingClass(alert: Alert): string {
    const today = new Date();
    const dueDate = new Date(alert.due_date);
    const diffTime = dueDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'bg-danger';
    if (diffDays === 0) return 'bg-warning text-dark';
    if (diffDays <= 2) return 'bg-warning';
    if (diffDays <= 7) return 'bg-info';
    return 'bg-secondary';
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
      'Vaccination': 'bg-primary',
      'Medication': 'bg-success',
      'Appointment': 'bg-warning text-dark',
      'Checkup': 'bg-info',
      'Other': 'bg-secondary'
    };
    return classes[alertType] || 'bg-secondary';
  }

  toggleAlertsModal(): void {
    this.showAlertsModal = !this.showAlertsModal;
    if (this.showAlertsModal) {
      this.loadAlerts();
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
  }

  showSnackbar(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
    const config: MatSnackBarConfig = {
      duration: type === 'error' || type === 'warning' ? 5000 : 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: [`snackbar-${type}`]
    };
    
    this.snackBar.open(message, 'Close', config);
  }
}