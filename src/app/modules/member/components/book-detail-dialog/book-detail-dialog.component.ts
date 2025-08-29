import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BookService } from '../../../../services/book.service';
import { AuthService } from '../../../../services/auth.service';
import { Book } from '../../../../models/book.model';

export interface BookDetailDialogData {
  book: Book;
}

@Component({
  selector: 'app-book-detail-dialog',
  templateUrl: './book-detail-dialog.component.html',
  styleUrls: ['./book-detail-dialog.component.scss']
})
export class BookDetailDialogComponent {
  isLoading = false;

  constructor(
    private bookService: BookService,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private dialogRef: MatDialogRef<BookDetailDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: BookDetailDialogData
  ) {}

  borrowBook(): void {
    const currentUser = this.authService.currentUser();
    if (!currentUser) {
      this.snackBar.open('Please log in to borrow books', 'Close', { duration: 3000 });
      return;
    }

    if (this.data.book.availableCopies <= 0) {
      this.snackBar.open('This book is currently not available', 'Close', { duration: 3000 });
      return;
    }

    this.isLoading = true;
    
    // Set due date to 14 days from now
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 14);

    this.bookService.issueBook({
      bookId: this.data.book.id,
      userId: currentUser.id,
      dueDate: dueDate
    }).subscribe({
      next: () => {
        this.isLoading = false;
        this.dialogRef.close('borrowed');
      },
      error: (error) => {
        this.isLoading = false;
        this.snackBar.open(error.message || 'Failed to borrow book', 'Close', { duration: 3000 });
      }
    });
  }

  onClose(): void {
    this.dialogRef.close();
  }
}
