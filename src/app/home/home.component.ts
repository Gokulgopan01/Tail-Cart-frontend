import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  username: string | null = '';
  userId: string | null = '';
  hasProfile = false;
  cartItems = 3; // Example cart items count

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.username = localStorage.getItem('username');
    this.userId = localStorage.getItem('user_id');
    
    if (this.userId) {
    this.checkProfile();
  }
  }

  checkProfile(): void {
    this.http.get<any>(`http://13.60.65.166/api/user/profile/?user_id=${this.userId}`)
      .subscribe({
        next: (response) => {
          this.hasProfile = !!response.owner_name;
        },
        error: (error) => {
          this.hasProfile = false;
        }
      });
  }

  navigateToProfile(): void {
    this.router.navigate(['/profile']);
  }

  logout(): void {
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    this.router.navigate(['/auth']);
  }

  navigateTo(path: string): void {
    this.router.navigate([path]);
  }

  
}