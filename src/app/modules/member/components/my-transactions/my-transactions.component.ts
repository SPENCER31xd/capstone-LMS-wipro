import { Component, OnInit, OnDestroy } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BookService } from '../../../../services/book.service';
import { AuthService } from '../../../../services/auth.service';
import { TransactionWithDetails, TransactionStatus } from '../../../../models/transaction.model';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-my-transactions',
  templateUrl: './my-transactions.component.html',
  styleUrls: ['./my-transactions.component.scss']
})
export class MyTransactionsComponent implements OnInit, OnDestroy {
  displayedColumns: string[] = ['book', 'issueDate', 'dueDate', 'returnDate', 'status', 'fine'];
  transactions: TransactionWithDetails[] = [];
  filteredTransactions: TransactionWithDetails[] = [];
  selectedStatus: TransactionStatus | 'all' = 'all';
  statusOptions = Object.values(TransactionStatus);
  
  private destroy$ = new Subject<void>();

  constructor(
    public bookService: BookService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadTransactions();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadTransactions(): void {
    const currentUser = this.authService.currentUser();
    console.log('Loading transactions for user:', currentUser);
    
    if (!currentUser) {
      console.warn('No current user found');
      return;
    }

    console.log('Calling getUserTransactions for user ID:', currentUser.id);
    this.bookService.getUserTransactions(currentUser.id).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (transactions) => {
        console.log('Transactions loaded successfully:', transactions);
        this.transactions = transactions;
        this.applyFilters();
      },
      error: (error) => {
        console.error('Failed to load transactions:', error);
        this.snackBar.open('Failed to load transactions: ' + (error.message || 'Unknown error'), 'Close', { duration: 5000 });
      }
    });
  }

  applyFilters(): void {
    let filtered = [...this.transactions];

    if (this.selectedStatus !== 'all') {
      filtered = filtered.filter(transaction => transaction.status === this.selectedStatus);
    }

    // Sort by issue date (newest first)
    filtered.sort((a, b) => new Date(b.issueDate).getTime() - new Date(a.issueDate).getTime());

    this.filteredTransactions = filtered;
  }

  onStatusFilterChange(): void {
    this.applyFilters();
  }

  getStatusClass(status: TransactionStatus): string {
    switch (status) {
      case TransactionStatus.ACTIVE:
        return 'status-active';
      case TransactionStatus.RETURNED:
        return 'status-returned';
      case TransactionStatus.OVERDUE:
        return 'status-overdue';
      default:
        return '';
    }
  }

  isOverdue(transaction: TransactionWithDetails): boolean {
    return transaction.status === TransactionStatus.ACTIVE && 
           new Date() > new Date(transaction.dueDate);
  }
}
