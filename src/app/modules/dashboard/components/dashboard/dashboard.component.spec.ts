import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { signal } from '@angular/core';

import { DashboardComponent } from './dashboard.component';
import { AuthService } from '../../../../services/auth.service';
import { UserRole } from '../../../../models/user.model';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;
  let mockAuthService: jasmine.SpyObj<AuthService>;
  let mockRouter: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    mockAuthService = jasmine.createSpyObj('AuthService', [], {
      currentUser: signal({
        id: '1',
        firstName: 'Test',
        lastName: 'User',
        email: 'test@test.com',
        role: UserRole.MEMBER,
        password: '',
        createdAt: new Date(),
        isActive: true
      })
    });

    mockRouter = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      declarations: [DashboardComponent],
      imports: [NoopAnimationsModule],
      providers: [
        { provide: AuthService, useValue: mockAuthService },
        { provide: Router, useValue: mockRouter }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should redirect admin to admin dashboard', () => {
    mockAuthService.currentUser = signal({
      id: '1',
      firstName: 'Admin',
      lastName: 'User',
      email: 'admin@test.com',
      role: UserRole.ADMIN,
      password: '',
      createdAt: new Date(),
      isActive: true
    });

    component.ngOnInit();

    expect(mockRouter.navigate).toHaveBeenCalledWith(['/admin/dashboard']);
  });

  it('should redirect member to member dashboard', () => {
    mockAuthService.currentUser = signal({
      id: '1',
      firstName: 'Member',
      lastName: 'User',
      email: 'member@test.com',
      role: UserRole.MEMBER,
      password: '',
      createdAt: new Date(),
      isActive: true
    });

    component.ngOnInit();

    expect(mockRouter.navigate).toHaveBeenCalledWith(['/member/dashboard']);
  });
});
