import { Component, ElementRef, ViewChild, AfterViewChecked, OnInit, HostListener } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface ChatMessage {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface ExamplePrompt {
  id: number;
  title: string;
  subtitle: string;
  category: string;
}

@Component({
  selector: 'app-doctor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './doctor.component.html',
  styleUrls: ['./doctor.component.css']
})
export class DoctorComponent implements OnInit, AfterViewChecked {
  // Chat state
  messages: ChatMessage[] = [];
  userInput: string = '';
  isAiTyping: boolean = false;
  showWelcomeScreen: boolean = true;
  showWelcomeInChat: boolean = true;
  showIncompleteNotice: boolean = false;
  errorMessage: string | null = null;
  isMobileView: boolean = false;
  isScrolledUp: boolean = false;
  
  // Example prompts (exact from screenshot)
  examplePrompts: ExamplePrompt[] = [
    { id: 1, title: 'My dog is scratching a lot', subtitle: 'Skin & allergy concerns', category: 'health' },
    { id: 2, title: 'Cat not eating properly', subtitle: 'Appetite & nutrition help', category: 'nutrition' },
    { id: 3, title: 'Signs of pet anxiety', subtitle: 'Behavior & mental health', category: 'behavior' },
    { id: 4, title: 'Vaccination schedule', subtitle: 'Preventive care guide', category: 'prevention' },
    { id: 5, title: 'Best diet for puppies', subtitle: 'Nutrition advice', category: 'nutrition' },
    { id: 6, title: 'Exercise needs for pets', subtitle: 'Activity recommendations', category: 'activity' }
  ];

  @ViewChild('chatContainer') private chatContainer!: ElementRef;
  @ViewChild('chatInput') private chatInput!: ElementRef;

  // Gemini AI API configuration
  private geminiApiKey = 'AIzaSyD_DUMMY_API_KEY_REPLACE_ME'; // Replace with your actual API key
  private geminiApiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    // Check if mobile view
    this.checkIfMobile();
    // Initialize with welcome state
    this.showWelcomeScreen = true;
    this.showWelcomeInChat = true;
  }

  @HostListener('window:resize')
  onResize() {
    this.checkIfMobile();
  }

  private checkIfMobile() {
    this.isMobileView = window.innerWidth < 768;
  }

  ngAfterViewChecked() {
    // Only auto-scroll if not manually scrolled up
    if (!this.isScrolledUp) {
      this.scrollToBottom();
    }
  }

  // Handle chat scroll
  onChatScroll() {
    if (this.chatContainer?.nativeElement) {
      const container = this.chatContainer.nativeElement;
      const scrollTop = container.scrollTop;
      const scrollHeight = container.scrollHeight;
      const clientHeight = container.clientHeight;
      
      // User is scrolled up if not near bottom
      this.isScrolledUp = scrollTop + clientHeight < scrollHeight - 100;
    }
  }

  // Main function to handle user questions
  askDoctor(): void {
    if (!this.userInput.trim()) {
      return;
    }

    // Hide welcome screen and switch to chat interface
    this.showWelcomeScreen = false;
    
    // Add user message
    const userMessage: ChatMessage = {
      id: this.messages.length + 1,
      text: this.userInput,
      sender: 'user',
      timestamp: new Date()
    };
    this.messages.push(userMessage);

    // Clear input
    const userText = this.userInput;
    this.userInput = '';
    this.errorMessage = null;
    this.showIncompleteNotice = false;

    // Reset scroll position for new messages
    this.isScrolledUp = false;

    // Show typing indicator
    this.isAiTyping = true;
    
    // Scroll to bottom immediately for new message
    setTimeout(() => {
      this.scrollToBottom(true);
    }, 50);

    // Call Gemini API
    this.callGeminiAPI(userText);
  }

  callGeminiAPI(userInput: string): void {
    // Check for incomplete messages (like "sfsfsfsfsf" from your example)
    if (userInput.length < 3 || /^[a-z]{3,}$/i.test(userInput) && !/\s/.test(userInput)) {
      setTimeout(() => {
        this.isAiTyping = false;
        this.showIncompleteNotice = true;
        this.isScrolledUp = false;
        setTimeout(() => {
          this.scrollToBottom(true);
        }, 100);
      }, 1000);
      return;
    }

    const systemPrompt = `You are Pet AI Doctor, an AI veterinary assistant. You help pet owners with their furry, feathery, or scaly friends. 
    
    Your role:
    1. Provide helpful, accurate pet health information
    2. Be empathetic and understanding
    3. Always recommend consulting a real veterinarian for serious concerns
    4. Use clear, easy-to-understand language
    5. Structure responses with bullet points or numbered lists when appropriate
    6. Always include a disclaimer about not being a substitute for professional veterinary care
    
    Format your responses in a clean, readable way. Use markdown-style formatting for lists and emphasis.`;

    const requestBody = {
      contents: [{
        parts: [{
          text: `${systemPrompt}\n\nUser question: ${userInput}\n\nPlease provide a helpful response as Pet AI Doctor:`
        }]
      }],
      generationConfig: {
        temperature: 0.7,
        topK: 40,
        topP: 0.95,
        maxOutputTokens: 1024,
      }
    };

    const url = `${this.geminiApiUrl}?key=${this.geminiApiKey}`;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    this.http.post<any>(url, requestBody, { headers })
      .subscribe({
        next: (response) => {
          this.handleAPIResponse(response, userInput);
        },
        error: (error) => {
          console.error('API Error:', error);
          this.handleAPIError(error, userInput);
        }
      });
  }

  handleAPIResponse(response: any, userInput: string): void {
    this.isAiTyping = false;
    this.isScrolledUp = false;
    
    let aiText = '';
    
    // Handle Gemini API response
    if (response.candidates && response.candidates.length > 0 && 
        response.candidates[0].content.parts.length > 0) {
      aiText = response.candidates[0].content.parts[0].text;
    } else {
      // Fallback response
      aiText = this.getFallbackResponse(userInput);
    }
    
    // Add AI response to messages
    this.messages.push({
      id: this.messages.length + 1,
      text: aiText,
      sender: 'ai',
      timestamp: new Date()
    });
    
    // Hide welcome message in chat after first interaction
    if (this.showWelcomeInChat) {
      this.showWelcomeInChat = false;
    }
    
    // Scroll to show new message
    setTimeout(() => {
      this.scrollToBottom(true);
    }, 100);
  }

  handleAPIError(error: any, userInput: string): void {
    this.isAiTyping = false;
    this.isScrolledUp = false;
    
    // Add fallback AI response
    const aiText = this.getFallbackResponse(userInput);
    
    this.messages.push({
      id: this.messages.length + 1,
      text: aiText,
      sender: 'ai',
      timestamp: new Date()
    });
    
    // Hide welcome message in chat after first interaction
    if (this.showWelcomeInChat) {
      this.showWelcomeInChat = false;
    }
    
    // Scroll to show new message
    setTimeout(() => {
      this.scrollToBottom(true);
    }, 100);
  }

  getFallbackResponse(userInput: string): string {
    const lowerInput = userInput.toLowerCase();
    
    if (lowerInput.includes('scratch') || lowerInput.includes('itch') || lowerInput.includes('skin')) {
      return `For scratching or skin issues:\n\n• Check for fleas or parasites regularly\n• Consider allergies (food or environmental)\n• Try an oatmeal bath for temporary relief\n• Keep your pet's bedding clean\n• Consult your veterinarian for proper diagnosis\n\n*Note: This is general advice. Always consult a professional veterinarian for specific concerns.*`;
    } else if (lowerInput.includes('vaccin') || lowerInput.includes('shot')) {
      return `**Vaccination Schedule Guide:**\n\n• **Core Vaccines**: Rabies, DHPP (dogs), FVRCP (cats)\n• **Timing**: Usually start at 6-8 weeks, boosters every 3-4 weeks\n• **Adult Pets**: Annual or triennial boosters based on vaccine type\n• **Lifestyle Vaccines**: Based on exposure risk (kennel cough, Lyme, etc.)\n\n*Please consult your veterinarian for a personalized vaccination schedule.*`;
    } else if (lowerInput.includes('eat') || lowerInput.includes('food') || lowerInput.includes('diet') || lowerInput.includes('appetite')) {
      return `**Appetite & Nutrition Help:**\n\n• Ensure fresh water is always available\n• Try different food textures (wet, dry, mixed)\n• Monitor for dental issues or mouth pain\n• Maintain consistent feeding schedule\n• Avoid sudden food changes\n• Consult your vet for dietary recommendations\n\n*Sudden appetite changes should be evaluated by a veterinarian.*`;
    } else if (lowerInput.includes('anxiety') || lowerInput.includes('stress') || lowerInput.includes('nervous')) {
      return `**Signs of Pet Anxiety:**\n\n• Excessive vocalization (barking/meowing)\n• Destructive behavior\n• House soiling\n• Pacing or restlessness\n• Hiding or avoidance\n• Excessive grooming or licking\n• Changes in appetite\n\n**Management Tips:**\n1. Create a safe, quiet space\n2. Use calming pheromone diffusers\n3. Establish consistent daily routine\n4. Provide mental stimulation (puzzle toys)\n5. Gradual desensitization to triggers\n6. Consider calming supplements (consult vet first)\n\n*For severe anxiety, consult a veterinarian about behavioral therapy options.*`;
    } else if (lowerInput.includes('pupp') && lowerInput.includes('diet')) {
      return `**Best Diet for Puppies:**\n\n• **Age-appropriate food**: Puppy formula until 12-24 months\n• **Frequency**: 3-4 meals daily for young puppies\n• **Protein-rich**: High-quality animal protein sources\n• **Essential nutrients**: DHA for brain development, calcium for bones\n• **Portion control**: Follow package guidelines based on expected adult weight\n• **Treats**: Limited to 10% of daily calories\n\n*Consult your veterinarian for breed-specific recommendations.*`;
    } else if (lowerInput.includes('exercise') || lowerInput.includes('activity')) {
      return `**Exercise Needs by Pet Type:**\n\n**Dogs:**\n• 30 minutes to 2 hours daily based on breed/age\n• Mix of walking, playing, and mental stimulation\n• Adjust for age and health conditions\n\n**Cats:**\n• 15-30 minutes of active play daily\n• Interactive toys and climbing structures\n• Food puzzles for mental stimulation\n\n**General Guidelines:**\n• Start slow with new routines\n• Watch for overheating in warm weather\n• Provide plenty of fresh water\n• Adjust based on individual pet's energy level\n\n*Always consult your vet before starting new exercise routines.*`;
    }
    
    return "Hello! I'm your AI veterinary assistant. I'm here to help with questions about your pet's health, behavior, nutrition, or general care. Could you tell me more about what you're concerned about? I'll do my best to provide helpful information and guidance. Remember, for serious or emergency situations, please contact your veterinarian immediately.";
  }

  // Use example prompt
  useExamplePrompt(prompt: ExamplePrompt): void {
    this.userInput = prompt.title;
    // Auto-focus the textarea
    setTimeout(() => {
      if (this.chatInput) {
        this.chatInput.nativeElement.focus();
        this.chatInput.nativeElement.setSelectionRange(
          this.userInput.length, 
          this.userInput.length
        );
      }
    }, 100);
  }

  clearChat(): void {
    this.messages = [];
    this.userInput = '';
    this.showWelcomeScreen = true;
    this.showWelcomeInChat = true;
    this.errorMessage = null;
    this.showIncompleteNotice = false;
    this.isScrolledUp = false;
  }

  formatMessage(text: string): string {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>')
      .replace(/\•/g, '•')
      .replace(/\*/g, '•')
      .replace(/^•\s*/gm, '• ');
  }

  // Keyboard support
  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.askDoctor();
    }
  }

  scrollToBottom(force: boolean = false): void {
    try {
      if (this.chatContainer?.nativeElement && (force || !this.isScrolledUp)) {
        const container = this.chatContainer.nativeElement;
        setTimeout(() => {
          container.scrollTop = container.scrollHeight;
        }, 50);
      }
    } catch (err) {
      console.error('Scroll error:', err);
    }
  }

  // Auto-resize textarea
  adjustTextareaHeight(): void {
    if (this.chatInput) {
      const textarea = this.chatInput.nativeElement;
      textarea.style.height = 'auto';
      const maxHeight = 120;
      const newHeight = Math.min(textarea.scrollHeight, maxHeight);
      textarea.style.height = newHeight + 'px';
      textarea.style.overflowY = newHeight >= maxHeight ? 'auto' : 'hidden';
    }
  }
}