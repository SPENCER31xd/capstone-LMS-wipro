import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { SignupComponent } from './signup.component';
import { AuthService } from '../../../../services/auth.service';
import { UserRole } from '../../../../models/user.model';

describe('SignupComponent', () => {
  let component: SignupComponent;
  let fixture: ComponentFixture<SignupComponent>;
  let mockAuthService: jasmine.SpyObj<AuthService>;
  let mockRouter: jasmine.SpyObj<Router>;
  let mockSnackBar: jasmine.SpyObj<MatSnackBar>;

  beforeEach(async () => {
    mockAuthService = jasmine.createSpyObj('AuthService', ['signup', 'isAuthenticated', 'isLoading']);
    mockRouter = jasmine.createSpyObj('Router', ['navigate']);
    mockSnackBar = jasmine.createSpyObj('MatSnackBar', ['open']);

    mockAuthService.isAuthenticated.and.returnValue(false);
    mockAuthService.isLoading.and.returnValue(false);

    await TestBed.configureTestingModule({
      declarations: [SignupComponent],
      imports: [ReactiveFormsModule, NoopAnimationsModule],
      providers: [
        { provide: AuthService, useValue: mockAuthService },
        { provide: Router, useValue: mockRouter },
        { provide: MatSnackBar, useValue: mockSnackBar }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(SignupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize form with validators', () => {
    expect(component.signupForm).toBeDefined();
    expect(component.signupForm.get('firstName')?.hasError('required')).toBeTruthy();
    expect(component.signupForm.get('email')?.hasError('required')).toBeTruthy();
  });

  it('should validate password match', () => {
    component.signupForm.patchValue({
      password: 'password123',
      confirmPassword: 'different'
    });
    
    expect(component.signupForm.hasError('passwordMismatch')).toBeTruthy();
    
    component.signupForm.patchValue({
      confirmPassword: 'password123'
    });
    
    expect(component.signupForm.hasError('passwordMismatch')).toBeFalsy();
  });

  it('should call signup service on form submit', () => {
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

    mockAuthService.signup.and.returnValue(of(mockResponse));

    component.signupForm.patchValue({
      firstName: 'Test',
      lastName: 'User',
      email: 'test@test.com',
      password: 'password123',
      confirmPassword: 'password123',
      role: UserRole.MEMBER
    });

    component.onSubmit();

    expect(mockAuthService.signup).toHaveBeenCalledWith({
      firstName: 'Test',
      lastName: 'User',
      email: 'test@test.com',
      password: 'password123',
      role: UserRole.MEMBER
    });
  });
});
