import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { signal } from '@angular/core';
import { NavbarComponent } from './navbar.component';
import { AuthService } from '../../../services/auth.service';
import { UserRole } from '../../../models/user.model';

describe('NavbarComponent', () => {
  let component: NavbarComponent;
  let fixture: ComponentFixture<NavbarComponent>;
  let mockAuthService: jasmine.SpyObj<AuthService>;
  let mockRouter: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    mockAuthService = jasmine.createSpyObj('AuthService', ['logout'], {
      isAuthenticated: signal(true),
      isAdmin: signal(false),
      isMember: signal(true),
      currentUser: signal({
        id: '1',
        firstName: 'John',
        lastName: 'Doe',
        email: 'john@library.com',
        role: UserRole.MEMBER,
        password: '',
        createdAt: new Date(),
        isActive: true
      })
    });

    mockRouter = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      imports: [NavbarComponent, NoopAnimationsModule],
      providers: [
        { provide: AuthService, useValue: mockAuthService },
        { provide: Router, useValue: mockRouter }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(NavbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display app name', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Library Management');
  });

  it('should call logout when logout button is clicked', () => {
    component.logout();
    expect(mockAuthService.logout).toHaveBeenCalled();
  });

  it('should show member navigation items for member role', () => {
    mockAuthService.isMember = signal(true);
    mockAuthService.isAdmin = signal(false);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Books');
    expect(compiled.textContent).toContain('My Books');
    expect(compiled.textContent).not.toContain('Manage Books');
  });
});
