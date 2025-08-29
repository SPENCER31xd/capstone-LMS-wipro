import { Component, OnInit, OnDestroy } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BookService } from '../../../../services/book.service';
import { AuthService } from '../../../../services/auth.service';
import { Book, BookCategory } from '../../../../models/book.model';
import { BookDetailDialogComponent } from '../book-detail-dialog/book-detail-dialog.component';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-book-list',
  templateUrl: './book-list.component.html',
  styleUrls: ['./book-list.component.scss']
})
export class BookListComponent implements OnInit, OnDestroy {
  books: Book[] = [];
  filteredBooks: Book[] = [];
  searchTerm = '';
  selectedCategory: BookCategory | 'all' = 'all';
  categories = Object.values(BookCategory);
  
  private destroy$ = new Subject<void>();

  constructor(
    public bookService: BookService,
    private authService: AuthService,
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
    this.bookService.getAllBooks().pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (books) => {
        this.books = books;
        this.applyFilters();
      },
      error: (error) => {
        this.snackBar.open('Failed to load books', 'Close', { duration: 3000 });
      }
    });
  }

  applyFilters(): void {
    let filtered = [...this.books];

    if (this.searchTerm) {
      const search = this.searchTerm.toLowerCase();
      filtered = filtered.filter(book => 
        book.title.toLowerCase().includes(search) ||
        book.author.toLowerCase().includes(search)
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

  viewBookDetails(book: Book): void {
    const dialogRef = this.dialog.open(BookDetailDialogComponent, {
      width: '600px',
      data: { book }
    });

    dialogRef.afterClosed().pipe(
      takeUntil(this.destroy$)
    ).subscribe(result => {
      if (result === 'borrowed') {
        this.loadBooks(); // Refresh to update availability
        this.snackBar.open('Book borrowed successfully!', 'Close', { duration: 3000 });
      }
    });
  }
}
