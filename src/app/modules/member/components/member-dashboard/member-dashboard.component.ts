import { Component, OnInit, OnDestroy } from '@angular/core';
import { BookService } from '../../../../services/book.service';
import { AuthService } from '../../../../services/auth.service';
import { TransactionWithDetails, TransactionStatus } from '../../../../models/transaction.model';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-member-dashboard',
  templateUrl: './member-dashboard.component.html',
  styleUrls: ['./member-dashboard.component.scss']
})
export class MemberDashboardComponent implements OnInit, OnDestroy {
  totalBooksAvailable = 0;
  myActiveBooks = 0;
  overdueBooks = 0;
  recentTransactions: TransactionWithDetails[] = [];
  
  private destroy$ = new Subject<void>();

  constructor(
    private bookService: BookService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadDashboardData(): void {
    console.log('Loading dashboard data...');
    
    // Load available books
    this.bookService.getAllBooks().pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (books) => {
        console.log('Books loaded:', books);
        this.totalBooksAvailable = books.reduce((sum, book) => sum + book.availableCopies, 0);
      },
      error: (error) => {
        console.error('Error loading books:', error);
      }
    });

    // Load user's transactions
    const currentUser = this.authService.currentUser();
    console.log('Current user:', currentUser);
    
    if (currentUser) {
      console.log('Loading transactions for user:', currentUser.id);
      this.bookService.getUserTransactions(currentUser.id).pipe(
        takeUntil(this.destroy$)
      ).subscribe({
        next: (transactions) => {
          console.log('User transactions loaded:', transactions);
          this.myActiveBooks = transactions.filter(t => t.status === TransactionStatus.ACTIVE).length;
          this.overdueBooks = transactions.filter(t => 
            t.status === TransactionStatus.ACTIVE && 
            new Date() > new Date(t.dueDate)
          ).length;
          
          // Get recent transactions (last 5)
          this.recentTransactions = transactions
            .sort((a, b) => new Date(b.issueDate).getTime() - new Date(a.issueDate).getTime())
            .slice(0, 5);
          
          console.log('Dashboard stats updated:', {
            myActiveBooks: this.myActiveBooks,
            overdueBooks: this.overdueBooks,
            recentTransactions: this.recentTransactions.length
          });
        },
        error: (error) => {
          console.error('Error loading user transactions:', error);
        }
      });
    } else {
      console.warn('No current user found');
    }
  }
}
