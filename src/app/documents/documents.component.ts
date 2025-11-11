import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import Swal from 'sweetalert2';

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
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './documents.component.html',
  styleUrl: './documents.component.css'
})
export class DocumentsComponent implements OnInit  {
  documents: Document[] = [];
  uploadForm: FormGroup;
  selectedFile: File | null = null;
  isUploading = false;
  private apiUrl = 'https://tailcart.duckdns.org/api/user/documents/';
  private userId: string = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient
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
      Swal.fire('Error', 'Please log in to access documents.', 'error');
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
          Swal.fire('Error', 'Error loading documents. Please try again.', 'error');
        }
      });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        Swal.fire('Error', 'File size must be less than 10MB', 'error');
        return;
      }
      
      this.selectedFile = file;
      this.uploadForm.patchValue({
        document_file: file
      });
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
            Swal.fire('Success', 'Document uploaded successfully!', 'success');
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
            Swal.fire('Error', errorMessage, 'error');
          }
        });
    } else {
      Object.keys(this.uploadForm.controls).forEach(key => {
        this.uploadForm.get(key)?.markAsTouched();
      });
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
  }

  deleteDocument(documentId: number): void {
    Swal.fire({
      title: 'Are you sure?',
      text: 'Do you want to delete this document?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, delete it!',
      cancelButtonText: 'Cancel'
    }).then(result => {
      if (result.isConfirmed) {
        this.http.delete(`${this.apiUrl}/${documentId}/`)
          .subscribe({
            next: () => {
              this.documents = this.documents.filter(doc => doc.document_id !== documentId);
              Swal.fire('Deleted!', 'Document deleted successfully!', 'success');
            },
            error: (error) => {
              console.error('Error deleting document:', error);
              Swal.fire('Error', 'Error deleting document. Please try again.', 'error');
            }
          });
      }
    });
  }

  getTotalSize(): string {
    const totalSize = this.documents.length * 0.5; 
    return totalSize < 1 ? `${(totalSize * 1024).toFixed(0)} KB` : `${totalSize.toFixed(1)} MB`;
  }

  isLoggedIn(): boolean {
    return this.userId !== null;
  }
}
