import { Injectable, signal, computed, inject } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { delay, map, catchError } from 'rxjs/operators';
import { User, UserRole, LoginRequest, SignupRequest, AuthResponse } from '../models/user.model';
import { environment } from '../../environments/environment';

// Backend response interfaces
interface BackendUser {
  id: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: string;
  createdAt: string;
  isActive: boolean;
}

interface LoginResponse {
  user: BackendUser;
  token: string;
}

interface SignupResponse {
  user: BackendUser;
  token: string;
}

interface MemberResponse {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  createdAt: string;
  isActive: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSignal = signal<User | null>(null);
  private isLoadingSignal = signal(false);

  // Inject dependencies
  private router = inject(Router);
  private http = inject(HttpClient);

  // Computed signals
  public readonly currentUser = this.currentUserSignal.asReadonly();
  public readonly isAuthenticated = computed(() => !!this.currentUserSignal());
  public readonly isAdmin = computed(() => this.currentUserSignal()?.role === UserRole.ADMIN);
  public readonly isMember = computed(() => this.currentUserSignal()?.role === UserRole.MEMBER);
  public readonly isLoading = this.isLoadingSignal.asReadonly();

  constructor() {
    this.loadUserFromStorage();
  }

  login(loginRequest: LoginRequest): Observable<AuthResponse> {
    this.isLoadingSignal.set(true);
    
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, {
      email: loginRequest.email,
      password: loginRequest.password
    }).pipe(
      map(backendResponse => {
        const user: User = {
          id: backendResponse.user.id,
          email: backendResponse.user.email,
          password: backendResponse.user.password,
          firstName: backendResponse.user.firstName,
          lastName: backendResponse.user.lastName,
          role: backendResponse.user.role === 'admin' ? UserRole.ADMIN : UserRole.MEMBER,
          createdAt: new Date(backendResponse.user.createdAt),
          isActive: backendResponse.user.isActive
        };

        const response: AuthResponse = {
          user: user,
          token: backendResponse.token
        };

        this.setCurrentUser(response.user, response.token);
        this.isLoadingSignal.set(false);
        return response;
      }),
      catchError((error: any) => {
        this.isLoadingSignal.set(false);
        return throwError(() => new Error(error.error?.error || 'Login failed'));
      })
    );
  }

  signup(signupRequest: SignupRequest): Observable<AuthResponse> {
    this.isLoadingSignal.set(true);

    return this.http.post<SignupResponse>(`${this.apiUrl}/signup`, {
      email: signupRequest.email,
      password: signupRequest.password,
      firstName: signupRequest.firstName,
      lastName: signupRequest.lastName,
      role: signupRequest.role === UserRole.ADMIN ? 'admin' : 'member'
    }).pipe(
      map(backendResponse => {
        const user: User = {
          id: backendResponse.user.id,
          email: backendResponse.user.email,
          password: backendResponse.user.password,
          firstName: backendResponse.user.firstName,
          lastName: backendResponse.user.lastName,
          role: signupRequest.role || UserRole.MEMBER,
          createdAt: new Date(backendResponse.user.createdAt),
          isActive: backendResponse.user.isActive
        };

        const response: AuthResponse = {
          user: user,
          token: backendResponse.token
        };

        this.setCurrentUser(response.user, response.token);
        this.isLoadingSignal.set(false);
        return response;
      }),
      catchError((error: any) => {
        this.isLoadingSignal.set(false);
        return throwError(() => new Error(error.error?.error || 'Signup failed'));
      })
    );
  }

  logout(): void {
    this.currentUserSignal.set(null);
    localStorage.removeItem('auth_user');
    localStorage.removeItem('auth_token');
    this.router.navigate(['/auth/login']);
  }

  getAllMembers(): Observable<User[]> {
    const token = this.getValidToken();
    if (!token) {
      return throwError(() => new Error('No valid authentication token'));
    }
    
    console.log('Fetching members with manual token handling');
    
    return this.http.get<MemberResponse[]>(`${this.apiUrl}/members`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }).pipe(
      map(backendUsers => {
        console.log('Backend members response:', backendUsers);
        const users = backendUsers.map(backendUser => ({
          id: backendUser.id,
          email: backendUser.email,
          password: '',
          firstName: backendUser.firstName,
          lastName: backendUser.lastName,
          role: UserRole.MEMBER,
          createdAt: new Date(backendUser.createdAt),
          isActive: backendUser.isActive
        }));
        console.log('Mapped users:', users);
        return users;
      }),
      catchError((error: any) => {
        console.error('Error fetching members:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to fetch members'));
      })
    );
  }

  updateMemberStatus(userId: string, isActive: boolean): Observable<User> {
    const token = this.getValidToken();
    if (!token) {
      return throwError(() => new Error('No valid authentication token'));
    }
    
    console.log('Updating member status with manual token handling');
    return this.http.put<MemberResponse>(`${this.apiUrl}/members/${userId}`, {
      isActive: isActive
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }).pipe(
      map(backendUser => ({
        id: backendUser.id,
        email: backendUser.email,
        password: '',
        firstName: backendUser.firstName,
        lastName: backendUser.lastName,
        role: UserRole.MEMBER,
        createdAt: new Date(backendUser.createdAt),
        isActive: backendUser.isActive
      })),
      catchError((error: any) => {
        return throwError(() => new Error(error.error?.error || 'Failed to update member status'));
      })
    );
  }

  private setCurrentUser(user: User, token: string): void {
    if (!token || token === 'null' || token === 'undefined') {
      console.error('Invalid token received:', token);
      throw new Error('Invalid token received from server');
    }
    
    console.log('Setting current user with token:', token.substring(0, 20) + '...');
    this.currentUserSignal.set(user);
    localStorage.setItem('auth_user', JSON.stringify(user));
    localStorage.setItem('auth_token', token);
  }

  private loadUserFromStorage(): void {
    const storedUser = localStorage.getItem('auth_user');
    const storedToken = localStorage.getItem('auth_token');
    
    if (storedUser && storedToken) {
      try {
        const user = JSON.parse(storedUser);
        this.currentUserSignal.set(user);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        this.logout();
      }
    }
  }

  private getValidToken(): string | null {
    const token = localStorage.getItem('auth_token');
    if (token && token !== 'null' && token !== 'undefined' && token.trim() !== '') {
      console.log('Valid token found:', token.substring(0, 20) + '...');
      return token;
    } else {
      console.warn('No valid token found in localStorage');
      return null;
    }
  }
}