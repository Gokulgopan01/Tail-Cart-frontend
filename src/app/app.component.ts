// app.component.ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './navbar/navbar.component';
import { FooterComponent } from './footer/footer.component';
import { routeTransitionAnimations } from './route-animations';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, FooterComponent],
  animations: [routeTransitionAnimations],
  template: `
  <app-navbar></app-navbar>
  
  <main class="main-content page-content-wrapper" [@routeAnimations]="outlet.isActivated ? outlet.activatedRoute : ''">
    <router-outlet #outlet="outlet"></router-outlet>
  </main>

  <app-footer></app-footer>
`,
  styles: [`
    .main-content {
      min-height: 100vh;
      width: 100%;
      max-width: 100vw;
      overflow-x: hidden;
      background: var(--bg-light);
      position: relative;
    }
  `]
})
export class AppComponent {
  title = 'Tail Cart Frontend';
}