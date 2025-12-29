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
      min-height: calc(100vh - 200px);
      width: 100%;
      background: #f8fafc;
      padding-top: 0 !important; /* Remove any default padding */
      margin-top: 0 !important; /* Let navbar CSS handle this */
    }
    
    /* Ensure content doesn't get hidden behind navbar */
    .main-content > *:first-child {
      padding-top: 20px;
    }
    
    @media (min-width: 769px) {
      .main-content {
        width: 100%;
      }
    }
  `]
})
export class AppComponent {
  title = 'Tail Cart Frontend';
}