import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../../../services/auth.service';
import { UserRole } from '../../../../models/user.model';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {

  constructor(
    public authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Redirect to role-specific dashboard
    const user = this.authService.currentUser();
    if (user) {
      if (user.role === UserRole.ADMIN) {
        this.router.navigate(['/admin/dashboard']);
      } else if (user.role === UserRole.MEMBER) {
        this.router.navigate(['/member/dashboard']);
      }
    }
  }
}
