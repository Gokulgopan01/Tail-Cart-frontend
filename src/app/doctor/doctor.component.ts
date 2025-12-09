import { Component, ElementRef, ViewChild, AfterViewChecked, OnInit, inject } from '@angular/core';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSnackBarConfig } from '@angular/material/snack-bar';

interface ChatMessage {
  type: 'user' | 'ai' | 'error' | 'welcome';
  content: string;
  timestamp: Date;
}

@Component({
  selector: 'app-doctor',
  standalone: true,
  imports: [CommonModule, HttpClientModule, FormsModule, MatSnackBarModule],
  templateUrl: './doctor.component.html',
  styleUrls: ['./doctor.component.css']
})
export class DoctorComponent implements OnInit, AfterViewChecked {
  userInput = "";
  response = "";
  error = "";
  loading = false;
  
  @ViewChild('chatMessages') private chatMessages!: ElementRef;
  
  private snackBar = inject(MatSnackBar);
  
  // Sample quick questions for suggestions
  quickQuestions = [
    'My dog is vomiting, what should I do?',
    'What foods are toxic to cats?',
    'My pet is not eating, what could be wrong?',
    'How often should I vaccinate my puppy?',
    'What are signs of dehydration in pets?',
    'How to treat minor cuts on my cat?'
  ];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    // Show welcome snackbar
    setTimeout(() => {
      this.showSnackBar('Welcome to Dr. PetAI! Ask any pet health questions.', 'info');
    }, 1000);
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      if (this.chatMessages?.nativeElement) {
        this.chatMessages.nativeElement.scrollTop = this.chatMessages.nativeElement.scrollHeight;
      }
    } catch (err) {
      console.error('Scroll error:', err);
    }
  }

  setQuickQuestion(question: string): void {
    this.userInput = question;
    
    // Auto-focus the textarea
    setTimeout(() => {
      const textarea = document.querySelector('.form-control') as HTMLTextAreaElement;
      if (textarea) {
        textarea.focus();
        textarea.setSelectionRange(textarea.value.length, textarea.value.length);
      }
    }, 100);
    
    this.showSnackBar('Question added. Click "Ask Doctor" to send.', 'info');
  }

  askDoctor() {
    if (!this.userInput.trim()) {
      this.showSnackBar('Please enter a question first.', 'warning');
      return;
    }

    this.loading = true;
    this.error = '';
    this.showSnackBar('Analyzing your pet\'s symptoms...', 'info');

    this.http.post<{response: string}>('https://tailcart.duckdns.org/api/ai-doctor/', {
      question: this.userInput
    }).subscribe({
      next: (res) => {
        this.response = res.response;
        this.loading = false;
        this.userInput = "";
        this.showSnackBar('Dr. PetAI has responded!', 'success');
      },
      error: (err) => {
        this.error = err.error?.message || 'Unable to connect to AI Doctor. Please try again later.';
        this.loading = false;
        console.error('AI Doctor Error:', err);
        this.showSnackBar('Failed to get response. Please try again.', 'error');
      }
    });
  }

  clearChat(): void {
    if (this.userInput || this.response || this.error) {
      this.showSnackBar('Chat cleared successfully.', 'info');
    }
    this.userInput = "";
    this.response = "";
    this.error = "";
  }

  private showSnackBar(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
    const config: MatSnackBarConfig = {
      duration: 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: [`snackbar-${type}`]
    };
    
    this.snackBar.open(message, 'Close', config);
  }

  // Helper method to format responses
  formatResponse(response: string): string {
    // Add line breaks for better readability
    return response.replace(/\n/g, '<br>');
  }

  // Get random quick question (for future enhancement)
  getRandomQuestion(): string {
    return this.quickQuestions[Math.floor(Math.random() * this.quickQuestions.length)];
  }
}