import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './shared/components/navbar/navbar.component';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, NavbarComponent],
  template: `
    <div class="app-container">
      <app-navbar *ngIf="authService.isAuthenticated()"></app-navbar>
      <main class="main-content" [class.with-navbar]="authService.isAuthenticated()">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .app-container {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .main-content {
      flex: 1;
      padding: 0;
      transition: all 0.3s ease;
    }

    .main-content.with-navbar {
      padding-top: 64px; /* Height of navbar */
    }

    @media (max-width: 768px) {
      .main-content.with-navbar {
        padding-top: 56px;
      }
    }
  `]
})
export class AppComponent {
  title = 'library-management';

  constructor(public authService: AuthService) {}
}
