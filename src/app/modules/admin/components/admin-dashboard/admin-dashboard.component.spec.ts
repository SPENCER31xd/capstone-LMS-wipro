import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { RouterTestingModule } from '@angular/router/testing';
import { of, signal } from 'rxjs';

import { AdminDashboardComponent } from './admin-dashboard.component';
import { BookService } from '../../../../services/book.service';
import { AuthService } from '../../../../services/auth.service';
import { UserRole } from '../../../../models/user.model';

describe('AdminDashboardComponent', () => {
  let component: AdminDashboardComponent;
  let fixture: ComponentFixture<AdminDashboardComponent>;
  let mockBookService: jasmine.SpyObj<BookService>;
  let mockAuthService: jasmine.SpyObj<AuthService>;

  beforeEach(async () => {
    mockBookService = jasmine.createSpyObj('BookService', ['getAllBooks', 'getAllTransactions']);
    mockAuthService = jasmine.createSpyObj('AuthService', ['getAllMembers'], {
      currentUser: signal({
        id: '1',
        firstName: 'Admin',
        lastName: 'User',
        email: 'admin@test.com',
        role: UserRole.ADMIN,
        password: '',
        createdAt: new Date(),
        isActive: true
      })
    });

    mockBookService.getAllBooks.and.returnValue(of([]));
    mockBookService.getAllTransactions.and.returnValue(of([]));
    mockAuthService.getAllMembers.and.returnValue(of([]));

    await TestBed.configureTestingModule({
      declarations: [AdminDashboardComponent],
      imports: [NoopAnimationsModule, RouterTestingModule],
      providers: [
        { provide: BookService, useValue: mockBookService },
        { provide: AuthService, useValue: mockAuthService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AdminDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load dashboard data on init', () => {
    expect(mockBookService.getAllBooks).toHaveBeenCalled();
    expect(mockAuthService.getAllMembers).toHaveBeenCalled();
    expect(mockBookService.getAllTransactions).toHaveBeenCalled();
  });
});
