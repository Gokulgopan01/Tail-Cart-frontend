import { Component, signal, ViewChild, ElementRef, AfterViewInit, OnDestroy, OnInit } from '@angular/core';
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
export class AuthComponent implements OnInit, AfterViewInit, OnDestroy {

  isLoginMode = signal(true);
  isLoading = signal(false);
  errorMessage = signal('');
  successMessage = signal('');
  showPassword = false;
  isScrolled = signal(false);
  isDarkMode = signal(false);

  showSuccessAnimation = signal(false);
  forgotMode = signal(false);
  forgotStep = signal(1); // 1: Email, 2: OTP & New Password

  loginData: LoginData = { email_address: '', password: '' };
  registerData: RegisterData = { username: '', email_address: '', password: '' };
  forgotData = { email_address: '', otp: '', new_password: '' };
  rememberMe = false;

  // running cat
  @ViewChild('lottieContainer', { static: true })
  lottieContainer!: ElementRef<HTMLDivElement>;
  private animation: AnimationItem | null = null;

  // login lottie
  @ViewChild('bannerLottie', { static: true })
  bannerLottie!: ElementRef<HTMLDivElement>;
  private bannerAnimation: AnimationItem | null = null;

  // success lottie
  @ViewChild('successLottie')
  successLottieElement!: ElementRef<HTMLDivElement>;
  private successAnimation: AnimationItem | null = null;

  constructor(
    private http: HttpClient,
    private router: Router
  ) { }

  ngOnInit(): void {
    const savedEmail = localStorage.getItem('remembered_email');
    if (savedEmail) {
      this.loginData.email_address = savedEmail;
      this.rememberMe = true;
    }

    const savedTheme = localStorage.getItem('auth_theme');
    const isDark = savedTheme === 'dark';

    this.isDarkMode.set(isDark);
    document.body.classList.toggle('dark', isDark);

    window.addEventListener('scroll', this.checkScroll.bind(this));
  }

  private checkScroll(): void {
    this.isScrolled.set(window.scrollY > 300);
  }

  scrollToTop(): void {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  private getErrorMessage(error: any): string {
    if (!error) return 'An unknown error occurred.';

    // If it's a simple string error from our own logic
    if (typeof error === 'string') return error;

    // Check for backend error object
    const errorData = error.error;
    if (!errorData) return error.message || 'An unknown error occurred.';

    // Case 1: errorData is a string
    if (typeof errorData === 'string') return errorData;

    // Case 2: errorData has a 'message' or 'detail' field (common in DRF)
    if (errorData.message) return errorData.message;
    if (errorData.detail) return errorData.detail;

    // Case 3: errorData is an object with field-specific errors (e.g., {"email_address": ["..."]})
    if (typeof errorData === 'object') {
      const messages: string[] = [];
      for (const key in errorData) {
        if (Array.isArray(errorData[key])) {
          messages.push(`${key}: ${errorData[key].join(', ')}`);
        } else if (typeof errorData[key] === 'string') {
          messages.push(`${key}: ${errorData[key]}`);
        }
      }
      if (messages.length > 0) return messages.join(' | ');
    }

    return error.message || 'An unknown error occurred.';
  }

  ngAfterViewInit(): void {
    this.bannerAnimation = lottie.loadAnimation({
      container: this.bannerLottie.nativeElement,
      renderer: 'svg',
      loop: true,
      autoplay: true,
      path: 'assets/Lottie/Login_banner.json',
      rendererSettings: {
        preserveAspectRatio: 'xMidYMid slice'
      }
    });
  }

  private initSuccessAnimation(): void {
    if (this.successLottieElement) {
      this.successAnimation = lottie.loadAnimation({
        container: this.successLottieElement.nativeElement,
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: 'assets/Lottie/Welcome.json'
      });
    }
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

  toggleTheme(): void {
    const isDark = !this.isDarkMode();

    this.isDarkMode.set(isDark);
    localStorage.setItem('auth_theme', isDark ? 'dark' : 'light');

    document.body.classList.toggle('dark', isDark);
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

              // Handle Remember Me
              if (this.rememberMe) {
                localStorage.setItem('remembered_email', this.loginData.email_address);
              } else {
                localStorage.removeItem('remembered_email');
              }

              localStorage.setItem('user_id', response.user_id.toString());
              localStorage.setItem('username', response.username);
              localStorage.setItem('access_token', response.access);
              localStorage.setItem('refresh_token', response.refresh);
              localStorage.setItem('access_role', response.role.toLowerCase());

              this.stopLoader();
              this.showSuccessAnimation.set(true);

              // Wait for view update then init lottie
              setTimeout(() => {
                this.initSuccessAnimation();
              }, 0);

              setTimeout(() => {
                this.router.navigate(['/home']);
              }, 2000);

            } else {
              this.stopLoader();
              this.errorMessage.set('Login failed');
            }
          },
          error: (error) => {
            this.stopLoader();
            this.errorMessage.set(this.getErrorMessage(error));
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
            this.errorMessage.set(this.getErrorMessage(error));
          }
        });
    }
  }

  onForgotPassword(): void {
    if (!this.forgotData.email_address) {
      this.errorMessage.set('Please enter your email address');
      return;
    }

    this.startLoader();
    this.errorMessage.set('');

    this.http.post<any>('http://127.0.0.1:8000/api/user/forgot-password/', {
      email_address: this.forgotData.email_address
    }).subscribe({
      next: (response) => {
        this.stopLoader();
        if (response.message === 'OTP sent to email') {
          this.successMessage.set('OTP sent to your email.');
          this.forgotStep.set(2);
        } else {
          this.errorMessage.set(response.message || 'Failed to send OTP');
        }
      },
      error: (error) => {
        this.stopLoader();
        this.errorMessage.set(this.getErrorMessage(error));
      }
    });
  }

  onResetPassword(): void {
    if (!this.forgotData.otp || !this.forgotData.new_password) {
      this.errorMessage.set('OTP and New Password are required');
      return;
    }

    this.startLoader();
    this.errorMessage.set('');

    this.http.post<any>('http://127.0.0.1:8000/api/user/reset-password/', {
      email_address: this.forgotData.email_address,
      otp: this.forgotData.otp,
      new_password: this.forgotData.new_password
    }).subscribe({
      next: (response) => {
        this.stopLoader();
        if (response.message === 'Password reset successfully') {
          this.successMessage.set('Password reset successful! You can now login.');
          setTimeout(() => {
            this.forgotMode.set(false);
            this.forgotStep.set(1);
            this.loginData.email_address = this.forgotData.email_address;
            this.successMessage.set('');
          }, 2000);
        } else {
          this.errorMessage.set(response.message || 'Reset failed');
        }
      },
      error: (error) => {
        this.stopLoader();
        this.errorMessage.set(this.getErrorMessage(error));
      }
    });
  }

  ngOnDestroy(): void {
    this.animation?.destroy();
    this.bannerAnimation?.destroy();
    this.successAnimation?.destroy();
    this.animation = null;
  }
}