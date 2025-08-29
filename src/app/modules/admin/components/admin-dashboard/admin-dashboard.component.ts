import { Component, OnInit, OnDestroy } from '@angular/core';
import { BookService } from '../../../../services/book.service';
import { AuthService } from '../../../../services/auth.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent implements OnInit, OnDestroy {
  totalBooks = 0;
  availableBooks = 0;
  totalMembers = 0;
  activeTransactions = 0;
  
  private destroy$ = new Subject<void>();

  constructor(
    private bookService: BookService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    // Check if user is authenticated before loading data
    if (this.authService.isAuthenticated()) {
      this.loadDashboardData();
    } else {
      console.warn('User not authenticated, skipping dashboard data load');
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadDashboardData(): void {
    console.log('Loading admin dashboard data...');
    
    // Load books data
    this.bookService.getAllBooks().pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (books) => {
        console.log('Books loaded for admin dashboard:', books);
        this.totalBooks = books.length;
        this.availableBooks = books.reduce((sum, book) => sum + book.availableCopies, 0);
      },
      error: (error) => {
        console.error('Error loading books for admin dashboard:', error);
        // Set default values on error to prevent infinite loops
        this.totalBooks = 0;
        this.availableBooks = 0;
      }
    });

    // Load members data
    console.log('Loading members for admin dashboard...');
    this.authService.getAllMembers().pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (members) => {
        console.log('Members loaded for admin dashboard:', members);
        this.totalMembers = members.filter(m => m.isActive).length;
        console.log('Total active members:', this.totalMembers);
      },
      error: (error) => {
        console.error('Error loading members for admin dashboard:', error);
        this.totalMembers = 0;
      }
    });

    // Load transactions data
    this.bookService.getAllTransactions().pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (transactions) => {
        console.log('Transactions loaded for admin dashboard:', transactions);
        this.activeTransactions = transactions.filter(t => t.status === 'active').length;
      },
      error: (error) => {
        console.error('Error loading transactions for admin dashboard:', error);
        // Set default values on error to prevent infinite loops
        this.activeTransactions = 0;
      }
    });
  }
}
