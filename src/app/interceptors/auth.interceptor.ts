import { HttpRequest, HttpHandlerFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

export function authInterceptor(request: HttpRequest<unknown>, next: HttpHandlerFn) {
  const router = inject(Router);
  
  // Get token from localStorage
  const token = localStorage.getItem('auth_token');
  
  // Validate token before using it
  if (token && token !== 'null' && token !== 'undefined' && token.trim() !== '') {
    console.log('Adding Authorization header with token:', token.substring(0, 20) + '...');
    request = request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  } else {
    console.warn('No valid token found in localStorage for request:', request.url);
  }

  // Handle the request and catch any errors
  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      // If we get a 401 Unauthorized, redirect to login
      if (error.status === 401) {
        console.log('Unauthorized request, redirecting to login');
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        router.navigate(['/auth/login']);
      }
      return throwError(() => error);
    })
  );
}

