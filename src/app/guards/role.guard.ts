import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { UserRole } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const requiredRoles: UserRole[] = route.data?.['roles'] || [];
    const currentUser = this.authService.currentUser();
    
    if (!currentUser) {
      this.router.navigate(['/auth/login']);
      return false;
    }

    if (requiredRoles.length === 0 || requiredRoles.includes(currentUser.role)) {
      return true;
    } else {
      this.router.navigate(['/dashboard']);
      return false;
    }
  }
}
