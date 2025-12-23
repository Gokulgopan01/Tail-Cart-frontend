import { CanActivateFn } from '@angular/router';

export const adminGuard: CanActivateFn = (route, state) => {
  const role = localStorage.getItem('access_role');
  return role === 'ADMIN';
};
