import { Component, signal, ViewChild, ElementRef, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import lottie, { AnimationItem } from 'lottie-web';

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
}

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})
export class AuthComponent implements AfterViewInit, OnDestroy {

  isLoginMode = signal(true);
  isLoading = signal(false);
  errorMessage = signal('');
  successMessage = signal('');
  showPassword = false;

  loginData: LoginData = { email_address: '', password: '' };
  registerData: RegisterData = { username: '', email_address: '', password: '' };

  @ViewChild('lottieContainer', { static: true })
  lottieContainer!: ElementRef<HTMLDivElement>;

  private animation: AnimationItem | null = null;

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngAfterViewInit(): void {
    this.animation = lottie.loadAnimation({
      container: this.lottieContainer.nativeElement,
      renderer: 'svg',
      loop: true,
      autoplay: false,
      path: 'assets/Running_Cat.json'
    });
  }

  private startLoader(): void {
    console.log('START LOADER');
    this.isLoading.set(true);
    this.animation?.goToAndPlay(0, true);
  }

  private stopLoader(): void {
    this.animation?.stop();
    this.isLoading.set(false);
  }

  onSwitchMode(): void {
    this.isLoginMode.set(!this.isLoginMode());
    this.errorMessage.set('');
    this.successMessage.set('');
    this.loginData.password = '';
    this.registerData.password = '';
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
    const passwordField = document.getElementById('password') as HTMLInputElement;
    if (passwordField) {
      passwordField.type = this.showPassword ? 'text' : 'password';
    }
  }

  onSubmit(): void {
    this.startLoader();
    this.errorMessage.set('');
    this.successMessage.set('');

    if (this.isLoginMode()) {
      this.http
        .post<LoginResponse>('http://127.0.0.1:8000/api/user/login/', this.loginData)
        .subscribe({
          next: (response) => {
            if (response.message === 'Login successful') {
              localStorage.setItem('user_id', response.user_id.toString());
              localStorage.setItem('username', response.username);

              this.successMessage.set('Login successful! Redirecting...');

              // ✅ FORCE loader for 10 seconds
              setTimeout(() => {
                this.stopLoader();
                this.router.navigate(['/home']);
              }, 3000);
            } else {
              this.stopLoader();
              this.errorMessage.set('Login failed');
            }
          },
          error: (error) => {
            this.stopLoader();
            this.errorMessage.set(
              error.error?.message || 'Login failed. Please check your credentials.'
            );
          }
        });
    } else {
      this.http
        .post<RegisterResponse>('http://127.0.0.1:8000/api/user/register/', this.registerData)
        .subscribe({
          next: (response) => {
            this.stopLoader();
            if (response.message?.includes('successful')) {
              this.successMessage.set('Registration successful! You can now login.');
              setTimeout(() => this.isLoginMode.set(true), 3000);
            } else {
              this.errorMessage.set(response.message || 'Registration completed.');
            }
          },
          error: (error) => {
            this.stopLoader();
            this.errorMessage.set(
              error.error?.message || 'Registration failed. Please try again.'
            );
          }
        });
    }
  }

  ngOnDestroy(): void {
    this.animation?.destroy();
    this.animation = null;
  }
}
