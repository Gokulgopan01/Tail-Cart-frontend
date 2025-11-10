import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import Swal from 'sweetalert2';

interface LoginData {
  email_address: string;
  password: string;
}

interface RegisterData {
  username: string;
  email_address: string;
  password: string;
}

interface LoginResponse {
  message: string;
  user_id: number;
  username: string;
}

interface RegisterResponse {
  message?: string;
  user_id?: number;
  username?: string;
}

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})
export class AuthComponent {
  isLoginMode = signal(true);
  isLoading = signal(false);
  errorMessage = signal('');
  successMessage = signal('');

  // Separate form models for login and register
  loginData: LoginData = {
    email_address: '',
    password: ''
  };

  registerData: RegisterData = {
    username: '',
    email_address: '',
    password: ''
  };

  constructor(private http: HttpClient, private router: Router) {}

  onSwitchMode(): void {
    this.isLoginMode.set(!this.isLoginMode());
    this.errorMessage.set('');
    this.successMessage.set('');
    
    // Clear password when switching modes
    this.loginData.password = '';
    this.registerData.password = '';
  }

  onSubmit(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    if (this.isLoginMode()) {
      this.http.post<LoginResponse>('https://bulbous-unaesthetical-albert.ngrok-free.dev/api/user/login/', this.loginData)
        .subscribe({
          next: (response) => {
            this.isLoading.set(false);
            if (response.message === "Login successful") {
              // Store user data in localStorage
              localStorage.setItem('user_id', response.user_id.toString());
              localStorage.setItem('username', response.username);
              
              // Show success alert
              Swal.fire('Success', 'Login successful!', 'success').then(() => {
                // Navigate to home page after successful login
                this.router.navigate(['/home']);
              });
            }
          },
          error: (error) => {
            this.isLoading.set(false);
            const msg = error.error?.message || 'Login failed. Please check your credentials.';
            this.errorMessage.set(msg);
            Swal.fire('Error', msg, 'error');
          }
        });
    } else {
      this.http.post<RegisterResponse>('https://bulbous-unaesthetical-albert.ngrok-free.dev/api/user/register/', this.registerData)
        .subscribe({
          next: (response) => {
            this.isLoading.set(false);
            if (response.message && response.message.includes('successful')) {
              // Switch to login mode after successful registration
              this.isLoginMode.set(true);
              this.successMessage.set('Registration successful! Please login with your credentials.');
              Swal.fire('Success', 'Registration successful! Please login with your credentials.', 'success');
            } else {
              const msg = response.message || 'Registration completed. Please login.';
              this.errorMessage.set(msg);
              Swal.fire('Info', msg, 'info');
            }
          },
          error: (error) => {
            this.isLoading.set(false);
            const msg = error.error?.message || 'Registration failed. Please try again.';
            this.errorMessage.set(msg);
            Swal.fire('Error', msg, 'error');
          }
        });
    }
  }
}
