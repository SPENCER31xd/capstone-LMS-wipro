import { Component, OnInit, OnDestroy } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BookService } from '../../../../services/book.service';
import { Book, BookCategory } from '../../../../models/book.model';
import { BookFormDialogComponent } from '../book-form-dialog/book-form-dialog.component';
import { ConfirmDialogComponent } from '../confirm-dialog/confirm-dialog.component';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-book-management',
  templateUrl: './book-management.component.html',
  styleUrls: ['./book-management.component.scss']
})
export class BookManagementComponent implements OnInit, OnDestroy {
  displayedColumns: string[] = ['title', 'author', 'category', 'isbn', 'totalCopies', 'availableCopies', 'actions'];
  books: Book[] = [];
  filteredBooks: Book[] = [];
  searchTerm = '';
  selectedCategory: BookCategory | 'all' = 'all';
  categories = Object.values(BookCategory);
  
  private destroy$ = new Subject<void>();

  constructor(
    public bookService: BookService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadBooks();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadBooks(): void {
    console.log('Loading books...');
    this.bookService.getAllBooks().pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (books) => {
        console.log('Books loaded successfully:', books);
        this.books = books;
        this.applyFilters();
      },
      error: (error) => {
        console.error('Failed to load books:', error);
        this.snackBar.open('Failed to load books: ' + (error.message || 'Unknown error'), 'Close', { duration: 5000 });
      }
    });
  }

  applyFilters(): void {
    let filtered = [...this.books];

    if (this.searchTerm) {
      const search = this.searchTerm.toLowerCase();
      filtered = filtered.filter(book => 
        book.title.toLowerCase().includes(search) ||
        book.author.toLowerCase().includes(search) ||
        book.isbn.includes(search)
      );
    }

    if (this.selectedCategory !== 'all') {
      filtered = filtered.filter(book => book.category === this.selectedCategory);
    }

    this.filteredBooks = filtered;
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  onCategoryChange(): void {
    this.applyFilters();
  }

  openAddBookDialog(): void {
    console.log('Opening add book dialog...');
    const dialogRef = this.dialog.open(BookFormDialogComponent, {
      width: '500px',
      data: { mode: 'add' }
    });

    dialogRef.afterClosed().pipe(
      takeUntil(this.destroy$)
    ).subscribe(result => {
      if (result) {
        console.log('Book added successfully:', result);
        this.loadBooks();
        this.snackBar.open('Book added successfully', 'Close', { duration: 3000 });
      } else {
        console.log('Add book dialog was cancelled');
      }
    });
  }

  openEditBookDialog(book: Book): void {
    console.log('Opening edit book dialog for book:', book);
    const dialogRef = this.dialog.open(BookFormDialogComponent, {
      width: '500px',
      data: { mode: 'edit', book: { ...book } }
    });

    dialogRef.afterClosed().pipe(
      takeUntil(this.destroy$)
    ).subscribe(result => {
      if (result) {
        console.log('Book updated successfully:', result);
        this.loadBooks();
        this.snackBar.open('Book updated successfully', 'Close', { duration: 3000 });
      } else {
        console.log('Edit book dialog was cancelled');
      }
    });
  }

  deleteBook(book: Book): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Delete Book',
        message: `Are you sure you want to delete "${book.title}"? This action cannot be undone.`,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().pipe(
      takeUntil(this.destroy$)
    ).subscribe(result => {
      if (result) {
        this.bookService.deleteBook(book.id).pipe(
          takeUntil(this.destroy$)
        ).subscribe({
          next: () => {
            this.loadBooks();
            this.snackBar.open('Book deleted successfully', 'Close', { duration: 3000 });
          },
          error: (error) => {
            this.snackBar.open(error.message || 'Failed to delete book', 'Close', { duration: 3000 });
          }
        });
      }
    });
  }
}
