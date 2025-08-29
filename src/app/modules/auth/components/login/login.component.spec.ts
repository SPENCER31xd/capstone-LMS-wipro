import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { LoginComponent } from './login.component';
import { AuthService } from '../../../../services/auth.service';
import { UserRole } from '../../../../models/user.model';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let mockAuthService: jasmine.SpyObj<AuthService>;
  let mockRouter: jasmine.SpyObj<Router>;
  let mockSnackBar: jasmine.SpyObj<MatSnackBar>;

  beforeEach(async () => {
    mockAuthService = jasmine.createSpyObj('AuthService', ['login', 'isAuthenticated', 'isLoading']);
    mockRouter = jasmine.createSpyObj('Router', ['navigate']);
    mockSnackBar = jasmine.createSpyObj('MatSnackBar', ['open']);

    mockAuthService.isAuthenticated.and.returnValue(false);
    mockAuthService.isLoading.and.returnValue(false);

    await TestBed.configureTestingModule({
      declarations: [LoginComponent],
      imports: [ReactiveFormsModule, NoopAnimationsModule],
      providers: [
        { provide: AuthService, useValue: mockAuthService },
        { provide: Router, useValue: mockRouter },
        { provide: MatSnackBar, useValue: mockSnackBar }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize form with validators', () => {
    expect(component.loginForm).toBeDefined();
    expect(component.loginForm.get('email')?.hasError('required')).toBeTruthy();
    expect(component.loginForm.get('password')?.hasError('required')).toBeTruthy();
  });

  it('should navigate to dashboard if already authenticated', () => {
    mockAuthService.isAuthenticated.and.returnValue(true);
    component.ngOnInit();
    expect(mockRouter.navigate).toHaveBeenCalledWith(['/dashboard']);
  });

  it('should call login service on form submit', () => {
    const mockResponse = {
      user: {
        id: '1',
        email: 'test@test.com',
        role: UserRole.MEMBER,
        firstName: 'Test',
        lastName: 'User',
        password: 'password',
        createdAt: new Date(),
        isActive: true
      },
      token: 'mock-token'
    };

    mockAuthService.login.and.returnValue(of(mockResponse));

    component.loginForm.patchValue({
      email: 'test@test.com',
      password: 'password123'
    });

    component.onSubmit();

    expect(mockAuthService.login).toHaveBeenCalledWith({
      email: 'test@test.com',
      password: 'password123'
    });
  });

  it('should display error message on login failure', () => {
    mockAuthService.login.and.returnValue(throwError(() => new Error('Invalid credentials')));

    component.loginForm.patchValue({
      email: 'test@test.com',
      password: 'password123'
    });

    component.onSubmit();

    expect(mockSnackBar.open).toHaveBeenCalledWith('Invalid credentials', 'Close', { duration: 5000 });
  });
});
