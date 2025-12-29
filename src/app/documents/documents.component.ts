import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms'; // Added FormsModule
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';

interface Document {
  document_id: number;
  user: number;
  pet: number;
  document_title: string;
  document_file: string;
  upload_date: string;
  document_type?: string;
  expiry_date?: string;
  file_name?: string;
  file_size?: string;
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
  custom_message?: string;
  days_before?: number;
}

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule, // Added FormsModule for ngModel
    ReactiveFormsModule,
    MatTooltipModule
  ],
  templateUrl: './documents.component.html',
  styleUrls: ['./documents.component.css']
})

export class DocumentsComponent implements OnInit {
  // Data
  documents: Document[] = [];
  alerts: Alert[] = [];
  filteredDocuments: Document[] = [];
  filteredAlerts: Alert[] = [];
  
  // UI State
  activeTab: 'documents' | 'alerts' = 'documents';
  viewMode: 'grid' | 'list' = 'grid';
  searchQuery: string = '';
  alertSearchQuery: string = '';
  selectedType: string = '';
  
  // Modal States
  showUploadModal: boolean = false;
  showEditAlertModal: boolean = false;
  showViewModal: boolean = false;
  showAlertsModal: boolean = false; // Added this from original
  
  // File Upload
  selectedFiles: File[] = [];
  isDragOver: boolean = false;
  isUploading: boolean = false;
  isSavingAlert: boolean = false; // Added this
  
  // Forms
  uploadForm: FormGroup;
  alertForm: FormGroup;
  
  // Selected Items
  selectedDoc: Document | null = null;
  editingAlert: Alert | null = null;
  
  // API Endpoints
  private documentsApi = 'https://tailcart1.duckdns.org/api/user/documents/';
  private alertsApi = 'https://tailcart1.duckdns.org/api/user/pet-alerts/';
  private userId: string = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private snackBar: MatSnackBar
  ) {
    this.uploadForm = this.fb.group({
      document_type: ['', Validators.required],
      document_title: ['', Validators.required],
      expiry_date: [''],
      pet: ['']
    });

    this.alertForm = this.fb.group({
      alert_type: ['Expiry Reminder', Validators.required],
      due_date: ['', Validators.required],
      days_before: ['30', Validators.required],
      custom_message: [''],
      title: ['']
    });
  }

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id') || '';
    if (this.userId) {
      this.loadDocuments();
      this.loadAlerts();
    } else {
      this.showSnackbar('Please log in to access documents.', 'error');
    }
  }

  // Data Loading
  loadDocuments(): void {
    const token = localStorage.getItem('access_token');
    const headers = { Authorization: `Bearer ${token}`};

    this.http.get<Document[]>(`${this.documentsApi}?user_id=${this.userId}`, { headers })
      .subscribe({
        next: (docs) => {
          this.documents = docs.map(doc => ({
            ...doc,
            document_type: this.extractDocType(doc.document_title),
            file_name: this.extractFileName(doc.document_file),
            file_size: this.calculateFileSize(doc.document_file)
          }));
          this.filteredDocuments = [...this.documents];
        },
        error: (error) => {
          console.error('Error loading documents:', error);
          this.showSnackbar('Error loading documents.', 'error');
        }
      });
  }

  loadAlerts(): void {
    const token = localStorage.getItem('access_token');
    const headers = { Authorization: `Bearer ${token}` };

    this.http.get<Alert[]>(`${this.alertsApi}?user_id=${this.userId}`, { headers })
      .subscribe({
        next: (alerts) => {
          console.log('ALERTS LOADED:', alerts); // Debug log
          this.alerts = alerts;
          this.filteredAlerts = [...this.alerts]; // FIX: Copy alerts to filteredAlerts
        },
        error: (error) => {
          console.error('Error loading alerts:', error);
          this.showSnackbar('Error loading alerts.', 'error');
        }
      });
  }

  // Filtering
  filterDocuments(): void {
    let filtered = this.documents;
    
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(doc =>
        doc.document_title.toLowerCase().includes(query)
      );
    }
    
    if (this.selectedType) {
      filtered = filtered.filter(doc => doc.document_type === this.selectedType);
    }
    
    this.filteredDocuments = filtered;
  }

  filterAlerts(): void {
    let filtered = this.alerts;
    
    if (this.alertSearchQuery) {
      const query = this.alertSearchQuery.toLowerCase();
      filtered = filtered.filter(alert =>
        alert.title.toLowerCase().includes(query) ||
        alert.alert_type.toLowerCase().includes(query)
      );
    }
    
    this.filteredAlerts = filtered;
  }

  // Document Methods
  openUploadModal(): void {
    this.showUploadModal = true;
    document.body.style.overflow = 'hidden';
  }

  closeUploadModal(): void {
    this.showUploadModal = false;
    this.uploadForm.reset();
    this.selectedFiles = [];
    document.body.style.overflow = 'auto';
  }

  // Missing methods added here:
  closeEditAlertModal(): void {
    this.showEditAlertModal = false;
    this.editingAlert = null;
    document.body.style.overflow = 'auto';
  }

  closeViewModal(): void {
    this.showViewModal = false;
    this.selectedDoc = null;
    document.body.style.overflow = 'auto';
  }

  closeCreateAlertModal(): void {
    this.showEditAlertModal = false; // Using same modal for create/edit
    this.editingAlert = null;
    document.body.style.overflow = 'auto';
  }

  toggleAlertsModal(): void {
    this.showAlertsModal = !this.showAlertsModal;
    if (this.showAlertsModal) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
  }

  closeAllModals(): void {
    this.closeUploadModal();
    this.closeEditAlertModal();
    this.closeViewModal();
    this.showAlertsModal = false;
    document.body.style.overflow = 'auto';
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = false;
    
    if (event.dataTransfer?.files) {
      this.handleFiles(Array.from(event.dataTransfer.files));
    }
  }

  onFileSelected(event: any): void {
    const files = event.target.files;
    this.handleFiles(Array.from(files));
  }

  handleFiles(files: File[]): void {
    const validFiles = files.filter(file => {
      const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
      const maxSize = 10 * 1024 * 1024; // 10MB
      
      if (!validTypes.includes(file.type)) {
        this.showSnackbar(`Invalid file type: ${file.name}`, 'error');
        return false;
      }
      
      if (file.size > maxSize) {
        this.showSnackbar(`File too large: ${file.name}`, 'error');
        return false;
      }
      
      return true;
    });
    
    this.selectedFiles = [...this.selectedFiles, ...validFiles];
  }

  removeFile(file: File): void {
    this.selectedFiles = this.selectedFiles.filter(f => f !== file);
  }

  uploadDocuments(): void {
    if (this.uploadForm.invalid || this.selectedFiles.length === 0) {
      this.showSnackbar('Please fill all required fields and select files.', 'error');
      return;
    }

    this.isUploading = true;
    
    // Upload each file
    this.selectedFiles.forEach((file, index) => {
      const formData = new FormData();
      formData.append('user', this.userId);
      formData.append('pet', this.uploadForm.get('pet')?.value || '1');
      formData.append('document_title', `${this.uploadForm.get('document_title')?.value} ${index > 0 ? `(${index + 1})` : ''}`);
      formData.append('document_type', this.uploadForm.get('document_type')?.value);
      formData.append('expiry_date', this.uploadForm.get('expiry_date')?.value || '');
      formData.append('document_file', file);

      const token = localStorage.getItem('access_token');

      this.http.post(this.documentsApi, formData, {
        headers: { Authorization: `Bearer ${token}` }
      }).subscribe({
        next: () => {
          if (index === this.selectedFiles.length - 1) {
            this.isUploading = false;
            this.closeUploadModal();
            this.loadDocuments();
            this.showSnackbar('Documents uploaded successfully!', 'success');
          }
        },
        error: (error) => {
          this.isUploading = false;
          console.error('Error uploading document:', error);
          this.showSnackbar('Error uploading document.', 'error');
        }
      });
    });
  }

  previewDocument(doc: Document): void {
    this.selectedDoc = doc;
    this.showViewModal = true;
    document.body.style.overflow = 'hidden';
  }

  downloadDocument(doc: Document | null): void {
  if (!doc) return;
  
  const fileUrl = `https://tailcart1.duckdns.org${doc.document_file}`;
  const link = document.createElement('a');
  link.href = fileUrl;
  link.download = doc.document_title;
  link.target = '_blank';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  this.showSnackbar(`Downloading ${doc.document_title}`, 'info');
}

  deleteDocument(documentId?: number): void {
    if (!documentId) return;
    
    if (confirm('Are you sure you want to delete this document?')) {
      const token = localStorage.getItem('access_token');
      this.http.delete(`${this.documentsApi}${documentId}/`, {
        headers: { Authorization: `Bearer ${token}` }
      }).subscribe({
        next: () => {
          this.documents = this.documents.filter(doc => doc.document_id !== documentId);
          this.filteredDocuments = this.filteredDocuments.filter(doc => doc.document_id !== documentId);
          this.closeViewModal();
          this.showSnackbar('Document deleted successfully', 'success');
        },
        error: (error) => {
          console.error('Error deleting document:', error);
          this.showSnackbar('Failed to delete document', 'error');
        }
      });
    }
  }

  // Alert Methods
  openCreateAlertModal(): void {
    this.alertForm.reset({
      alert_type: 'Expiry Reminder',
      days_before: '30'
    });
    this.editingAlert = null;
    this.showEditAlertModal = true;
    document.body.style.overflow = 'hidden';
  }

  editAlert(alert: Alert): void {
    this.editingAlert = alert;
    this.alertForm.patchValue({
      alert_type: alert.alert_type,
      due_date: alert.due_date,
      days_before: alert.days_before?.toString() || '30',
      custom_message: alert.custom_message || '',
      title: alert.title
    });
    this.showEditAlertModal = true;
    document.body.style.overflow = 'hidden';
  }

  saveAlert(): void {
    if (this.alertForm.invalid) {
      this.showSnackbar('Please fill all required fields.', 'error');
      return;
    }

    this.isSavingAlert = true;
    const alertData = {
      user: this.userId,
      pet: 1, // Default pet ID
      ...this.alertForm.value,
      is_active: true,
      frequency: 'One-time',
      title: this.alertForm.get('title')?.value || 'Document Expiry Reminder'
    };

    const token = localStorage.getItem('access_token');
    const request$ = this.editingAlert
      ? this.http.put(`${this.alertsApi}${this.editingAlert.alert_id}/`, alertData, {
          headers: { Authorization: `Bearer ${token}` }
        })
      : this.http.post(this.alertsApi, alertData, {
          headers: { Authorization: `Bearer ${token}` }
        });

    request$.subscribe({
      next: () => {
        this.isSavingAlert = false;
        this.closeEditAlertModal();
        this.loadAlerts();
        this.showSnackbar(`Alert ${this.editingAlert ? 'updated' : 'created'} successfully!`, 'success');
      },
      error: (error) => {
        this.isSavingAlert = false;
        console.error('Error saving alert:', error);
        this.showSnackbar('Error saving alert.', 'error');
      }
    });
  }

  toggleAlert(alert: Alert): void {
    const token = localStorage.getItem('access_token');
    const updatedAlert = { ...alert, is_active: !alert.is_active };
    
    this.http.put(`${this.alertsApi}${alert.alert_id}/`, updatedAlert, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: () => {
        alert.is_active = !alert.is_active;
        this.showSnackbar(`Alert ${alert.is_active ? 'enabled' : 'disabled'}`, 'info');
      },
      error: (error) => {
        console.error('Error toggling alert:', error);
        alert.is_active = !alert.is_active; // Revert on error
        this.showSnackbar('Error updating alert', 'error');
      }
    });
  }

  setAlertForDocument(doc: Document | null): void {
  if (!doc) return;
  
  this.alertForm.patchValue({
    title: `${doc.document_type} Expiry Reminder`,
    due_date: doc.expiry_date || ''
  });
  this.openCreateAlertModal();
}

  // Helper Methods
  extractDocType(title: string): string {
  const lowerTitle = title.toLowerCase();

    if (
      lowerTitle.includes('vaccine') ||
      lowerTitle.includes('vaccination') ||
      lowerTitle.includes('rabies')
    ) {
      return 'Pet Vaccination Record';
    }

    if (
      lowerTitle.includes('medical') ||
      lowerTitle.includes('health') ||
      lowerTitle.includes('treatment') ||
      lowerTitle.includes('report')
    ) {
      return 'Pet Medical Record';
    }

    if (
      lowerTitle.includes('prescription') ||
      lowerTitle.includes('medicine')
    ) {
      return 'Pet Prescription';
    }

    if (
      lowerTitle.includes('vet') ||
      lowerTitle.includes('veterinary')
    ) {
      return 'Veterinary Document';
    }

    return 'Other Pet Document';
  }

  extractFileName(filePath: string): string {
    return filePath.split('/').pop() || 'document.pdf';
  }

  calculateFileSize(filePath: string): string {
    const sizes = ['240.0 KB', '500.0 KB', '184.6 KB', '1.2 MB'];
    return sizes[Math.floor(Math.random() * sizes.length)];
  }

  getDocTypeIcon(docType?: string): string {
    const icons: { [key: string]: string } = {
      'Pet Vaccination Record': 'fas fa-syringe',
      'Pet Medical Record': 'fas fa-notes-medical',
      'Pet Prescription': 'fas fa-pills',
      'Veterinary Document': 'fas fa-stethoscope',
      'Other Pet Document': 'fas fa-file-alt'
    };

    return icons[docType || 'Other Pet Document'] || 'fas fa-file-alt';
  }

  getDocTypeClass(docType?: string): string {
    return docType?.toLowerCase().replace(' ', '-') || 'other';
  }

  getDocTypeIconText(docType?: string): string {
    const texts: { [key: string]: string } = {
      'Pet Vaccination Record': 'pet_vaccination',
      'Pet Medical Record': 'pet_medical',
      'Pet Prescription': 'pet_prescription',
      'Veterinary Document': 'veterinary',
      'Other Pet Document': 'pet_document'
    };

    return texts[docType || 'Other Pet Document'] || 'pet_document';
  }

  isDocumentExpired(doc: Document | null): boolean {
  if (!doc || !doc.expiry_date) return false;
  const expiry = new Date(doc.expiry_date);
  const today = new Date();
  return expiry < today;
}

  isDocumentExpiring(doc: Document | null): boolean {
  if (!doc || !doc.expiry_date) return false;
  const expiry = new Date(doc.expiry_date);
  const today = new Date();
  const thirtyDaysFromNow = new Date();
  thirtyDaysFromNow.setDate(today.getDate() + 30);
  return expiry >= today && expiry <= thirtyDaysFromNow;
}

  getOverdueAlerts(): Alert[] {
  const today = new Date();
  today.setHours(0, 0, 0, 0); // Reset time to start of day
  
  return this.alerts.filter(alert => {
    if (!alert.is_active) return false;
    const dueDate = new Date(alert.due_date);
    dueDate.setHours(0, 0, 0, 0); // Reset time to start of day
    return dueDate < today; // Overdue if due date is before today
  });
}

  calculateDaysAgo(dateString: string): string {
    const date = new Date(dateString);
    const today = new Date();
    const diffTime = today.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    return `${diffDays} days ago`;
  }

  getDefaultAlertMessage(alert: Alert): string {
    if (alert.alert_type === 'Expiry Reminder') {
      return 'Your document will expire soon. Consider renewing it.';
    } else if (alert.alert_type === 'Review Reminder') {
      return 'Annual review reminder for document validity';
    }
    return 'Reminder for your document';
  }

  openEditModal(doc: Document): void {
    // Implement edit document functionality
    console.log('Edit document:', doc);
  }

  showSnackbar(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: [`snackbar-${type}`]
    });
  }
}