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
  access: string;
  refresh: string;
  role: string;
}

interface RegisterResponse {
  message?: string;
  user_id?: number;
  username?: string;
  access?: string;
  refresh?: string;
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
  rememberMe = false;

  // running cat
  @ViewChild('lottieContainer', { static: true })
  lottieContainer!: ElementRef<HTMLDivElement>;
  private animation: AnimationItem | null = null;

  // login lottie
  @ViewChild('bannerLottie', { static: true })
  bannerLottie!: ElementRef<HTMLDivElement>;
  private bannerAnimation: AnimationItem | null = null;

  constructor(
    private http: HttpClient,
    private router: Router
  ) { }

  ngAfterViewInit(): void {
    this.bannerAnimation = lottie.loadAnimation({
      container: this.bannerLottie.nativeElement,
      renderer: 'svg',
      loop: true,
      autoplay: true,
      path: 'assets/Login_banner.json',
      rendererSettings: {
        preserveAspectRatio: 'xMidYMid slice'
      }
    });

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
    this.loginData = { email_address: '', password: '' };
    this.registerData = { username: '', email_address: '', password: '' };
    this.showPassword = false;
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
              localStorage.setItem('access_token', response.access);
              localStorage.setItem('refresh_token', response.refresh);
              localStorage.setItem('access_role', response.role.toLowerCase());

              this.successMessage.set('Login successful! Redirecting...');

              setTimeout(() => {
                this.stopLoader();
                this.router.navigate(['/home']);
              }, 500);

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
      // Validate username before registration
      if (!this.registerData.username || this.registerData.username.trim().length === 0) {
        this.stopLoader();
        this.errorMessage.set('Username is required');
        return;
      }

      this.http
        .post<RegisterResponse>('http://127.0.0.1:8000/api/user/register/', this.registerData)
        .subscribe({
          next: (response) => {
            this.stopLoader();
            if (response.message?.includes('successful')) {
              if (response.access && response.refresh) {
                localStorage.setItem('user_id', response.user_id!.toString());
                localStorage.setItem('username', response.username!);
                localStorage.setItem('access_token', response.access);
                localStorage.setItem('refresh_token', response.refresh);
              }

              this.successMessage.set('Registration successful! You can now login.');
              setTimeout(() => {
                this.isLoginMode.set(true);
                this.loginData.email_address = this.registerData.email_address;
                this.registerData = { username: '', email_address: '', password: '' };
              }, 2000);
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
    this.bannerAnimation?.destroy();
    this.animation = null;
  }
}