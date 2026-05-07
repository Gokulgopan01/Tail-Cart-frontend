import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  imports: [],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {
  scrollToSaveTheDate() {
    const element = document.getElementById('save-the-date');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  }
}
 