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
  uploadForm: FormGroup;
  selectedFile: File | null = null;
  isUploading = false;
  private apiUrl = 'https://tailcart.duckdns.org/api/user/documents/';
  private userId: string = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) {
    this.uploadForm = this.fb.group({
      document_title: ['', [Validators.required, Validators.minLength(1)]],
      pet: ['', [Validators.required, Validators.min(1)]],
      document_file: [null, [Validators.required]],
    });
  }

  ngOnInit(): void {
    this.userId = localStorage.getItem('user_id') || '';
    if (this.userId) {
      this.loadDocuments();
    } else {
      console.error('User ID not found in localStorage');
      this.showSnackbar('Please log in to access documents.', 'error');
    }
  }

  loadDocuments(): void {
    this.http.get<Document[]>(`${this.apiUrl}?user_id=${this.userId}`)
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
    
    // Reset the file input
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

      this.http.post(this.apiUrl, formData)
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
    const confirmed = window.confirm('Are you sure you want to delete this document? This action cannot be undone.');
    
    if (confirmed) {
      this.http.delete(`${this.apiUrl}/${documentId}/`)
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

  getTotalSize(): string {
    const totalSize = this.documents.length * 0.5; 
    return totalSize < 1 ? `${(totalSize * 1024).toFixed(0)} KB` : `${totalSize.toFixed(1)} MB`;
  }

  scrollToUpload(): void {
    if (this.uploadSection) {
      this.uploadSection.nativeElement.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
      });
    }
  }

  showSnackbar(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
  const config: MatSnackBarConfig = {
    duration: type === 'error' || type === 'warning' ? 5000 : 3000,
    horizontalPosition: 'right',
    verticalPosition: 'top',  // Change from bottom to top
    panelClass: [`snackbar-${type}`],
    politeness: 'polite'
  };
  
  this.snackBar.open(message, 'Close', config);
}
}