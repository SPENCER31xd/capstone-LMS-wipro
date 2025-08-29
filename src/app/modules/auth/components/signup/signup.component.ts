import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../../../services/auth.service';
import { UserRole } from '../../../../models/user.model';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.scss']
})
export class SignupComponent implements OnInit {
  signupForm!: FormGroup;
  hidePassword = true;
  hideConfirmPassword = true;
  userRoles = Object.values(UserRole);

  constructor(
    private fb: FormBuilder,
    public authService: AuthService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/dashboard']);
      return;
    }

    this.signupForm = this.fb.group({
      firstName: ['', [Validators.required, Validators.minLength(2)]],
      lastName: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]],
      role: [UserRole.MEMBER, [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password')?.value;
    const confirmPassword = form.get('confirmPassword')?.value;
    
    if (password && confirmPassword && password !== confirmPassword) {
      return { passwordMismatch: true };
    }
    
    return null;
  }

  onSubmit(): void {
    if (this.signupForm.valid) {
      const { confirmPassword, ...signupData } = this.signupForm.value;
      
      this.authService.signup(signupData).subscribe({
        next: (response) => {
          this.snackBar.open('Account created successfully!', 'Close', { duration: 3000 });
          
          // Redirect based on role
          if (response.user.role === UserRole.ADMIN) {
            this.router.navigate(['/admin/dashboard']);
          } else {
            this.router.navigate(['/member/dashboard']);
          }
        },
        error: (error) => {
          this.snackBar.open(error.message, 'Close', { duration: 5000 });
        }
      });
    }
  }

  getErrorMessage(field: string): string {
    const control = this.signupForm.get(field);
    
    if (control?.hasError('required')) {
      return `${this.getFieldDisplayName(field)} is required`;
    }
    
    if (control?.hasError('email')) {
      return 'Please enter a valid email';
    }
    
    if (control?.hasError('minlength')) {
      const minLength = control.getError('minlength').requiredLength;
      return `${this.getFieldDisplayName(field)} must be at least ${minLength} characters`;
    }
    
    if (field === 'confirmPassword' && this.signupForm.hasError('passwordMismatch')) {
      return 'Passwords do not match';
    }
    
    return '';
  }

  private getFieldDisplayName(field: string): string {
    switch (field) {
      case 'firstName': return 'First name';
      case 'lastName': return 'Last name';
      case 'confirmPassword': return 'Confirm password';
      default: return field.charAt(0).toUpperCase() + field.slice(1);
    }
  }
}
