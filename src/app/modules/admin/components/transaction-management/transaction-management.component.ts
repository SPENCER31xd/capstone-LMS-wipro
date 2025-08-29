import { Component, OnInit, OnDestroy } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BookService } from '../../../../services/book.service';
import { TransactionWithDetails, TransactionStatus } from '../../../../models/transaction.model';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-transaction-management',
  templateUrl: './transaction-management.component.html',
  styleUrls: ['./transaction-management.component.scss']
})
export class TransactionManagementComponent implements OnInit, OnDestroy {
  displayedColumns: string[] = ['book', 'member', 'issueDate', 'dueDate', 'returnDate', 'status', 'fine', 'actions'];
  transactions: TransactionWithDetails[] = [];
  filteredTransactions: TransactionWithDetails[] = [];
  selectedStatus: TransactionStatus | 'all' = 'all';
  statusOptions = Object.values(TransactionStatus);
  
  private destroy$ = new Subject<void>();

  constructor(
    public bookService: BookService,
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
    this.bookService.getAllTransactions().pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (transactions) => {
        this.transactions = transactions;
        this.applyFilters();
      },
      error: (error) => {
        this.snackBar.open('Failed to load transactions', 'Close', { duration: 3000 });
      }
    });
  }

  applyFilters(): void {
    let filtered = [...this.transactions];

    if (this.selectedStatus !== 'all') {
      filtered = filtered.filter(transaction => transaction.status === this.selectedStatus);
    }

    this.filteredTransactions = filtered;
  }

  onStatusFilterChange(): void {
    this.applyFilters();
  }

  returnBook(transaction: TransactionWithDetails): void {
    this.bookService.returnBook({
      transactionId: transaction.id,
      returnDate: new Date()
    }).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: () => {
        this.loadTransactions();
        this.snackBar.open('Book returned successfully', 'Close', { duration: 3000 });
      },
      error: (error) => {
        this.snackBar.open(error.message || 'Failed to return book', 'Close', { duration: 3000 });
      }
    });
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
