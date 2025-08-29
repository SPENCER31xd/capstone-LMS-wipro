import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatBadgeModule } from '@angular/material/badge';
import { MatDividerModule } from '@angular/material/divider';
import { AuthService } from '../../../services/auth.service';
import { UserRole } from '../../../models/user.model';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatBadgeModule,
    MatDividerModule
  ],
  template: `
    <mat-toolbar color="primary" class="navbar">
      <div class="navbar-content">
        <div class="navbar-left">
          <mat-icon class="logo-icon">local_library</mat-icon>
          <span class="app-name">Library Management</span>
        </div>

        <nav class="navbar-center" *ngIf="authService.isAuthenticated()">
          <a mat-button routerLink="/dashboard" routerLinkActive="active">
            <mat-icon>dashboard</mat-icon>
            Dashboard
          </a>

          <a mat-button routerLink="/member/books" routerLinkActive="active" *ngIf="authService.isMember()">
            <mat-icon>book</mat-icon>
            Books
          </a>

          <a mat-button routerLink="/member/transactions" routerLinkActive="active" *ngIf="authService.isMember()">
            <mat-icon>receipt</mat-icon>
            My Books
          </a>

          <a mat-button routerLink="/admin/books" routerLinkActive="active" *ngIf="authService.isAdmin()">
            <mat-icon>library_books</mat-icon>
            Manage Books
          </a>

          <a mat-button routerLink="/admin/members" routerLinkActive="active" *ngIf="authService.isAdmin()">
            <mat-icon>people</mat-icon>
            Members
          </a>

          <a mat-button routerLink="/admin/transactions" routerLinkActive="active" *ngIf="authService.isAdmin()">
            <mat-icon>assignment</mat-icon>
            All Transactions
          </a>
        </nav>

        <div class="navbar-right" *ngIf="authService.isAuthenticated()">
          <button mat-icon-button [matMenuTriggerFor]="userMenu">
            <mat-icon>account_circle</mat-icon>
          </button>
          <mat-menu #userMenu="matMenu">
            <div class="user-info">
              <div class="user-name">
                {{ authService.currentUser()?.firstName }} {{ authService.currentUser()?.lastName }}
              </div>
              <div class="user-role">{{ authService.currentUser()?.role | titlecase }}</div>
            </div>
            <mat-divider></mat-divider>
            <button mat-menu-item routerLink="/profile">
              <mat-icon>person</mat-icon>
              Profile
            </button>
            <button mat-menu-item (click)="logout()">
              <mat-icon>logout</mat-icon>
              Logout
            </button>
          </mat-menu>
        </div>
      </div>
    </mat-toolbar>
  `,
  styles: [`
    .navbar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 1000;
      height: 64px;
    }

    .navbar-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      height: 100%;
    }

    .navbar-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .logo-icon {
      font-size: 28px;
      height: 28px;
      width: 28px;
    }

    .app-name {
      font-size: 20px;
      font-weight: 500;
      white-space: nowrap;
    }

    .navbar-center {
      display: flex;
      align-items: center;
      gap: 4px;
      flex: 1;
      justify-content: center;
    }

    .navbar-center a {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
      border-radius: 8px;
      transition: all 0.3s ease;
    }

    .navbar-center a.active {
      background-color: rgba(255, 255, 255, 0.2);
    }

    .navbar-center a mat-icon {
      font-size: 20px;
      height: 20px;
      width: 20px;
    }

    .navbar-right {
      display: flex;
      align-items: center;
    }

    .user-info {
      padding: 12px 16px;
      text-align: center;
    }

    .user-name {
      font-weight: 500;
      font-size: 14px;
    }

    .user-role {
      font-size: 12px;
      color: rgba(0, 0, 0, 0.6);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    @media (max-width: 768px) {
      .navbar {
        height: 56px;
      }

      .app-name {
        font-size: 16px;
      }

      .navbar-center {
        display: none;
      }

      .navbar-center a {
        padding: 8px 12px;
      }

      .navbar-center a span {
        display: none;
      }
    }

    @media (max-width: 480px) {
      .app-name {
        display: none;
      }
    }
  `]
})
export class NavbarComponent {
  constructor(
    public authService: AuthService,
    private router: Router
  ) {}

  logout(): void {
    this.authService.logout();
  }
}
