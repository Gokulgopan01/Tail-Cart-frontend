// app.component.ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './navbar/navbar.component'; 
import { FooterComponent } from './footer/footer.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, FooterComponent],
  template: `
    <app-navbar></app-navbar>
    
    <main class="main-content">
      <router-outlet></router-outlet>
    </main>
    
    <app-footer></app-footer>
  `,
  styles: [`
    .main-content {
      min-height: calc(100vh - 200px); /* Adjust for navbar & footer */
      width: 100%;
      background: #f8fafc; /* Light background for content area */
    }
    
    /* Add more spacing for desktop */
    @media (min-width: 769px) {
      .main-content {
        width: 100%;
      }
    }
    
    /* Container for all page content */
    .main-content > * {
      width: 100%;
    }
  `]
})
export class AppComponent {
  title = 'Tail Cart Frontend';
}