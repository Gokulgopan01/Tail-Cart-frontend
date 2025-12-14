import { Component, AfterViewInit } from '@angular/core';
import { Router } from '@angular/router';

declare var bootstrap: any;

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements AfterViewInit {

  hasProfile = false;
  private observer!: IntersectionObserver;

  constructor(private router: Router) {}

  ngAfterViewInit(): void {
    this.initAnimations();
    this.initCarousel();
  }

  initCarousel() {
    const el = document.getElementById('featuresCarousel');
    if (el) {
      new bootstrap.Carousel(el, {
        interval: 4500,
        pause: false,
        touch: true
      });
    }
  }

  initAnimations() {
    this.observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          this.observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    document.querySelectorAll('.reveal')
      .forEach(el => this.observer.observe(el));
  }

  navigateTo(path: string) {
    this.router.navigate([path]);
  }

  navigateToProfile() {
    this.router.navigate(['/profile']);
  }
}
