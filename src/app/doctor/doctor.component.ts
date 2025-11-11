import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface ChatMessage {
  type: 'user' | 'ai' | 'error' | 'welcome';
  content: string;
  timestamp: Date;
}

@Component({
  selector: 'app-doctor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './doctor.component.html',
  styleUrls: ['./doctor.component.css']
})
export class DoctorComponent implements AfterViewChecked {
  userInput = "";
  response = "";
  error = "";
  loading = false;
  
  @ViewChild('chatMessages') private chatMessages!: ElementRef;

  constructor(private http: HttpClient) {}

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      this.chatMessages.nativeElement.scrollTop = this.chatMessages.nativeElement.scrollHeight;
    } catch (err) {
      console.error('Scroll error:', err);
    }
  }

  setQuickQuestion(question: string): void {
    this.userInput = question;
    // Auto-focus the input area
    setTimeout(() => {
      const textarea = document.querySelector('.input-area') as HTMLTextAreaElement;
      if (textarea) {
        textarea.focus();
      }
    }, 100);
  }

  askDoctor() {
    if (!this.userInput.trim()) return;

    this.loading = true;
    this.error = '';
    // Don't clear response immediately to show previous conversation

    this.http.post<{response: string}>('https://tailcart.duckdns.org/api/ai-doctor/', {
      question: this.userInput
    }).subscribe({
      next: (res) => {
        this.response = res.response;
        this.loading = false;
        // Clear input after successful response
        this.userInput = "";
      },
      error: (err) => {
        this.error = 'Please try again later. If the problem persists, contact support.';
        this.loading = false;
        console.error('AI Doctor Error:', err);
      }
    });
  }

  clearChat(): void {
    this.userInput = "";
    this.response = "";
    this.error = "";
  }
}