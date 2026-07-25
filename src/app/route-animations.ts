import {
  trigger,
  transition,
  style,
  query,
  animateChild,
  group,
  animate
} from '@angular/animations';

export const routeTransitionAnimations = trigger('routeAnimations', [
  transition('* <=> *', [
    // Ensure the container is relative so absolute children overlap correctly
    style({ position: 'relative' }),
    query(':enter, :leave', [
      style({
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%'
      })
    ], { optional: true }),
    query(':enter', [
      style({ opacity: 0, transform: 'translateY(20px)' })
    ], { optional: true }),
    query(':leave', animateChild(), { optional: true }),
    group([
      query(':leave', [
        animate('400ms cubic-bezier(0.22, 1, 0.36, 1)', style({ opacity: 0, transform: 'translateY(-20px)' }))
      ], { optional: true }),
      query(':enter', [
        animate('600ms cubic-bezier(0.22, 1, 0.36, 1)', style({ opacity: 1, transform: 'translateY(0)' }))
      ], { optional: true }),
    ]),
    query(':enter', animateChild(), { optional: true }),
  ])
]);
