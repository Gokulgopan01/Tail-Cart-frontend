import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
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

interface Remainder {
  alert_id: number;
  user: number;
  pet: number;
  alert_type: string;
  alert_subtype: string;
  title: string;
  reminder_time: string;
  remainder_date: string;
  frequency: string;
  notes?: string;
  is_active: boolean;
  completed_at?: string | null;
  created_at?: string;
  statusInfo?: { text: string, type: string };
}

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTooltipModule
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './documents.component.html',
  styleUrls: ['./documents.component.css']
})

export class DocumentsComponent implements OnInit {
  // Data
  documents: Document[] = [];
  remainders: Remainder[] = [];
  filteredDocuments: Document[] = [];
  filteredRemainders: Remainder[] = [];
  userPets: { id: number, name: string }[] = [];

  overdueCount: number = 0;
  upcomingCount: number = 0;

  // UI State
  activeTab: 'documents' | 'remainders' = 'documents';
  docsViewMode: 'grid' | 'list' = 'grid';
  remainderViewMode: 'list' | 'calendar' = 'list';
  searchQuery: string = '';
  remainderSearchQuery: string = '';
  selectedType: string = '';
  selectedPet: string = '';
  selectedStatus: string = '';
  dateFilter: string = 'all';

  // Modal States
  showUploadModal: boolean = false;
  showEditRemainderModal: boolean = false;
  showViewModal: boolean = false;
  showRemaindersModal: boolean = false; // Added this from original

  // File Upload
  selectedFiles: File[] = [];
  isDragOver: boolean = false;
  isUploading: boolean = false;
  isSavingRemainder: boolean = false; // Added this

  // Forms
  uploadForm: FormGroup;
  remainderForm: FormGroup;

  // Selected Items
  selectedDoc: Document | null = null;
  editingRemainder: Remainder | null = null;

  // API Endpoints
  private documentsApi = 'http://127.0.0.1:8000/api/user/documents/';
  private remaindersApi = 'http://127.0.0.1:8000/api/user/pet-remainder/';
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
      pet: ['', Validators.required]
    });

    this.remainderForm = this.fb.group({
      pet: ['', Validators.required],
      alert_type: ['Health', Validators.required],
      alert_subtype: ['', Validators.required],
      title: ['', Validators.required],
      remainder_date: ['', Validators.required],
      reminder_time: ['', Validators.required],
      frequency: ['One-time', Validators.required],
      notes: [''],
      is_active: [true]
    });
  }

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id') || '';
    if (this.userId) {
      this.loadDocuments();
      this.loadRemainders();
      this.loadUserPets(); // <-- ADD THIS
    } else {
      this.showSnackbar('Please log in to access documents.', 'error');
    }
  }

  loadUserPets(): void {
    const token = localStorage.getItem('access_token');
    if (!this.userId) return;

    this.http.get<any[]>(`http://127.0.0.1:8000/api/user/pets/?user_id=${this.userId}`, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (pets) => {
        this.userPets = pets.map(p => ({ id: p.pet_id, name: p.pet_name }));
        console.log('Processed Pets:', this.userPets);
        // If creating a new remainder, preselect the first pet
        if (!this.editingRemainder && this.userPets.length > 0) {
          this.remainderForm.patchValue({ pet: this.userPets[0].id });
        }
      },
      error: (err) => {
        console.error('Error loading pets:', err);
        this.showSnackbar('Failed to load pets', 'error');
      }
    });
  }

  scrollToRemainders(): void {
    setTimeout(() => {
      document.getElementById('remainders-section')?.scrollIntoView({
        behavior: 'smooth'
      });
    }, 50);
  }

  // Data Loading
  loadDocuments(): void {
    const token = localStorage.getItem('access_token');
    const headers = { Authorization: `Bearer ${token}` };

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

  loadRemainders(): void {
    const token = localStorage.getItem('access_token');
    const headers = { Authorization: `Bearer ${token}` };

    this.http.get<Remainder[]>(`${this.remaindersApi}?user_id=${this.userId}`, { headers })
      .subscribe({
        next: (remainders) => {
          this.remainders = remainders.map(rem => ({
            ...rem,
            statusInfo: this.calculateStatus(rem)
          }));
          this.filterRemainders();
        },
        error: (error) => {
          console.error('Error loading remainders:', error);
          this.showSnackbar('Error loading remainders.', 'error');
        }
      });
  }

  calculateStatus(remainder: Remainder): { text: string, type: string } {
    if (remainder.completed_at || !remainder.is_active) {
      return { text: 'Completed', type: 'completed' };
    }

    if (!remainder.remainder_date) return { text: 'Scheduled', type: 'scheduled' };

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const remDate = new Date(remainder.remainder_date);
    remDate.setHours(0, 0, 0, 0);

    if (remDate.getTime() < today.getTime()) {
      return { text: 'Overdue', type: 'overdue' };
    }

    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (remDate.getTime() <= tomorrow.getTime()) {
      return { text: 'Upcoming', type: 'upcoming' };
    }

    return { text: 'Scheduled', type: 'scheduled' };
  }

  getPetName(petId: number): string {
    const pet = this.userPets.find(p => p.id === petId);
    return pet ? pet.name : `Pet ${petId}`;
  }

  updateBannerCounts(): void {
    this.overdueCount = this.remainders.filter(r => r.statusInfo?.type === 'overdue').length;
    this.upcomingCount = this.remainders.filter(r => r.statusInfo?.type === 'upcoming').length;
  }

  // Filtering
  filterDocuments(): void {
    let filtered = this.documents;

    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(doc =>
        doc.document_title.toLowerCase().includes(query) ||
        (doc.file_name && doc.file_name.toLowerCase().includes(query))
      );
    }

    if (this.selectedType) {
      filtered = filtered.filter(doc => doc.document_type === this.selectedType);
    }

    if (this.selectedPet) {
      filtered = filtered.filter(doc => doc.pet.toString() === this.selectedPet.toString());
    }

    if (this.dateFilter === 'recent') {
      const recentThreshold = new Date();
      recentThreshold.setDate(recentThreshold.getDate() - 30);
      filtered = filtered.filter(doc => {
        if (!doc.upload_date) return false;
        return new Date(doc.upload_date) >= recentThreshold;
      });
    }

    this.filteredDocuments = filtered;
  }

  filterRemainders(): void {
    let filtered = this.remainders;

    if (this.remainderSearchQuery) {
      const query = this.remainderSearchQuery.toLowerCase();
      filtered = filtered.filter(remainder =>
        remainder.title.toLowerCase().includes(query) ||
        remainder.alert_type.toLowerCase().includes(query)
      );
    }

    if (this.selectedPet) {
      filtered = filtered.filter(remainder => remainder.pet.toString() === this.selectedPet.toString());
    }

    if (this.selectedStatus) {
      filtered = filtered.filter(remainder => remainder.statusInfo?.type === this.selectedStatus);
    }

    // Sort by status priority: overdue first, then upcoming, scheduled, and completed last
    const statusPriority: { [key: string]: number } = {
      'overdue': 0,
      'upcoming': 1,
      'scheduled': 2,
      'completed': 3
    };

    filtered.sort((a, b) => {
      const priorityA = statusPriority[a.statusInfo?.type || 'scheduled'] ?? 2;
      const priorityB = statusPriority[b.statusInfo?.type || 'scheduled'] ?? 2;
      if (priorityA !== priorityB) {
        return priorityA - priorityB;
      }
      // Within the same status, sort by date (earliest first)
      return new Date(a.remainder_date).getTime() - new Date(b.remainder_date).getTime();
    });

    this.filteredRemainders = filtered;
    this.updateBannerCounts();
  }

  // Document Methods
  openUploadModal(): void {
    this.showUploadModal = true;
    document.body.style.overflow = 'hidden';
  }

  closeUploadModal(): void {
    this.showUploadModal = false;
    this.uploadForm.reset({ document_type: '', pet: '' });
    this.selectedFiles = [];
    document.body.style.overflow = 'auto';
  }

  // Missing methods added here:
  closeEditRemainderModal(): void {
    this.showEditRemainderModal = false;
    this.editingRemainder = null;
    document.body.style.overflow = 'auto';
  }

  closeViewModal(): void {
    this.showViewModal = false;
    this.selectedDoc = null;
    document.body.style.overflow = 'auto';
  }

  closeCreateRemainderModal(): void {
    this.showEditRemainderModal = false; // Using same modal for create/edit
    this.editingRemainder = null;
    document.body.style.overflow = 'auto';
  }

  toggleRemaindersModal(): void {
    this.showRemaindersModal = !this.showRemaindersModal;
    if (this.showRemaindersModal) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
  }

  closeAllModals(): void {
    this.closeUploadModal();
    this.closeEditRemainderModal();
    this.closeViewModal();
    this.showRemaindersModal = false;
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

    const fileUrl = `http://127.0.0.1:8000${doc.document_file}`;
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

  // Remainder Methods
  openCreateRemainderModal(): void {
    const todayStr = new Date().toISOString().split('T')[0];
    this.remainderForm.reset({
      alert_type: 'Health',
      alert_subtype: 'Vaccination',
      remainder_date: todayStr,
      reminder_time: '09:00',
      frequency: 'One-time',
      is_active: true,
      pet: this.userPets.length > 0 ? this.userPets[0].id : ''
    });

    this.editingRemainder = null;
    this.showEditRemainderModal = true;
    document.body.style.overflow = 'hidden';
  }

  editRemainder(remainder: Remainder): void {
    this.editingRemainder = remainder;
    this.remainderForm.patchValue({
      pet: remainder.pet,
      alert_type: remainder.alert_type || 'Health',
      alert_subtype: remainder.alert_subtype || '',
      title: remainder.title,
      remainder_date: remainder.remainder_date,
      reminder_time: remainder.reminder_time,
      frequency: remainder.frequency,
      notes: remainder.notes || '',
      is_active: remainder.is_active
    });
    this.showEditRemainderModal = true;
    document.body.style.overflow = 'hidden';
  }

  saveRemainder(): void {
    if (this.remainderForm.invalid) {
      this.showSnackbar('Please fill all required fields.', 'error');
      return;
    }

    this.isSavingRemainder = true;
    const remainderData = {
      user: this.userId,
      pet: this.remainderForm.value.pet,
      alert_type: this.remainderForm.value.alert_type,
      alert_subtype: this.remainderForm.value.alert_subtype,
      title: this.remainderForm.value.title,
      remainder_date: this.remainderForm.value.remainder_date,
      reminder_time: this.remainderForm.value.reminder_time,
      frequency: this.remainderForm.value.frequency,
      notes: this.remainderForm.value.notes,
      is_active: this.remainderForm.value.is_active ?? true
    };

    const token = localStorage.getItem('access_token');
    const request$ = this.editingRemainder
      ? this.http.put(this.remaindersApi, {
        ...remainderData,
        alert_id: this.editingRemainder.alert_id,
        user_id: this.userId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      : this.http.post(this.remaindersApi, remainderData, {
        headers: { Authorization: `Bearer ${token}` }
      });

    request$.subscribe({
      next: () => {
        this.isSavingRemainder = false;
        this.closeEditRemainderModal();
        this.loadRemainders();
        this.showSnackbar(`Remainder ${this.editingRemainder ? 'updated' : 'created'} successfully!`, 'success');
      },
      error: (error) => {
        this.isSavingRemainder = false;
        console.error('Error saving remainder:', error);
        this.showSnackbar('Error saving remainder.', 'error');
      }
    });
  }

  markAsCompleted(remainder: Remainder): void {
    const token = localStorage.getItem('access_token');
    const headers = { Authorization: `Bearer ${token}` };
    const now = new Date().toISOString();

    this.http.put(`${this.remaindersApi}`, {
      user_id: this.userId,
      alert_id: remainder.alert_id,
      completed_at: now,
      is_active: false
    }, { headers }).subscribe({
      next: () => {
        this.showSnackbar('Reminder marked as completed', 'success');
        this.loadRemainders();
      },
      error: (err) => {
        console.error('Error marking as completed:', err);
        this.showSnackbar('Failed to update status', 'error');
      }
    });
  }

  deleteRemainder(remainderId: number): void {
    if (!confirm('Are you sure you want to delete this reminder?')) return;

    const token = localStorage.getItem('access_token');
    const headers = { Authorization: `Bearer ${token}` };

    this.http.delete(`${this.remaindersApi}${remainderId}/`, { headers }).subscribe({
      next: () => {
        this.showSnackbar('Reminder deleted permanently', 'success');
        this.loadRemainders();
      },
      error: (err) => {
        console.error('Error deleting reminder:', err);
        this.showSnackbar('Failed to delete reminder', 'error');
      }
    });
  }

  setRemainderForDocument(doc: Document | null): void {
    if (!doc) return;

    this.remainderForm.patchValue({
      title: `${doc.document_type} Remainder`,
      alert_type: 'Vaccination'
    });
    this.openCreateRemainderModal();
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

  getReminderStatus(remainder: Remainder): { text: string, type: string } {
    return remainder.statusInfo || this.calculateStatus(remainder);
  }

  getRemindersByStatus(status: 'overdue' | 'today'): Remainder[] {
    return this.remainders.filter(r => this.getReminderStatus(r).type === status);
  }

  getOverdueRemainders(): Remainder[] {
    return this.getRemindersByStatus('overdue');
  }

  getUpcomingRemainders(): Remainder[] {
    return this.getRemindersByStatus('today');
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

  getDefaultRemainderMessage(remainder: Remainder): string {
    if (remainder.alert_type === 'Expiry Reminder') {
      return 'Your document will expire soon. Consider renewing it.';
    } else if (remainder.alert_type === 'Review Reminder') {
      return 'Annual review reminder for document validity';
    }
    return 'Reminder for your document';
  }

  openEditModal(doc: Document): void {

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