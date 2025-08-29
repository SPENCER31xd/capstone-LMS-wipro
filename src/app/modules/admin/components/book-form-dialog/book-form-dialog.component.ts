import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { BookService } from '../../../../services/book.service';
import { Book, BookCategory, CreateBookRequest, UpdateBookRequest } from '../../../../models/book.model';

export interface BookDialogData {
  mode: 'add' | 'edit';
  book?: Book;
}

@Component({
  selector: 'app-book-form-dialog',
  templateUrl: './book-form-dialog.component.html',
  styleUrls: ['./book-form-dialog.component.scss']
})
export class BookFormDialogComponent implements OnInit {
  bookForm!: FormGroup;
  categories = Object.values(BookCategory);
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private bookService: BookService,
    private dialogRef: MatDialogRef<BookFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: BookDialogData
  ) {}

  ngOnInit(): void {
    this.initializeForm();
  }

  private initializeForm(): void {
    const book = this.data.book;
    
    this.bookForm = this.fb.group({
      title: [book?.title || '', [Validators.required, Validators.minLength(2)]],
      author: [book?.author || '', [Validators.required, Validators.minLength(2)]],
      isbn: [book?.isbn || '', [Validators.required, Validators.pattern(/^(?:\d{9}[\dX]|\d{13})$/)]],
      category: [book?.category || BookCategory.FICTION, [Validators.required]],
      publishedYear: [book?.publishedYear || new Date().getFullYear(), 
        [Validators.required, Validators.min(1000), Validators.max(new Date().getFullYear())]],
      description: [book?.description || '', [Validators.required, Validators.minLength(10)]],
      totalCopies: [book?.totalCopies || 1, [Validators.required, Validators.min(1)]],
      imageUrl: [book?.imageUrl || '']
    });
  }

  onSubmit(): void {
    if (this.bookForm.valid) {
      this.isLoading = true;
      const formValue = this.bookForm.value;
      console.log('Form submitted with values:', formValue);

      if (this.data.mode === 'add') {
        const createRequest: CreateBookRequest = {
          ...formValue
        };
        console.log('Creating book with request:', createRequest);

        this.bookService.createBook(createRequest).subscribe({
          next: (book) => {
            console.log('Book created successfully:', book);
            this.isLoading = false;
            this.dialogRef.close(book);
          },
          error: (error) => {
            console.error('Error creating book:', error);
            this.isLoading = false;
            // You might want to show an error message to the user here
          }
        });
      } else {
        const updateRequest: UpdateBookRequest = {
          id: this.data.book!.id,
          ...formValue
        };
        console.log('Updating book with request:', updateRequest);

        this.bookService.updateBook(updateRequest).subscribe({
          next: (book) => {
            console.log('Book updated successfully:', book);
            this.isLoading = false;
            this.dialogRef.close(book);
          },
          error: (error) => {
            console.error('Error updating book:', error);
            this.isLoading = false;
            // You might want to show an error message to the user here
          }
        });
      }
    } else {
      console.log('Form is invalid:', this.bookForm.errors);
      // Mark all fields as touched to show validation errors
      Object.keys(this.bookForm.controls).forEach(key => {
        const control = this.bookForm.get(key);
        control?.markAsTouched();
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  getErrorMessage(field: string): string {
    const control = this.bookForm.get(field);
    
    if (control?.hasError('required')) {
      return `${this.getFieldDisplayName(field)} is required`;
    }
    
    if (control?.hasError('minlength')) {
      const minLength = control.getError('minlength').requiredLength;
      return `${this.getFieldDisplayName(field)} must be at least ${minLength} characters`;
    }

    if (control?.hasError('min')) {
      const min = control.getError('min').min;
      return `${this.getFieldDisplayName(field)} must be at least ${min}`;
    }

    if (control?.hasError('max')) {
      const max = control.getError('max').max;
      return `${this.getFieldDisplayName(field)} cannot exceed ${max}`;
    }

    if (control?.hasError('pattern')) {
      return 'Please enter a valid ISBN (10 or 13 digits)';
    }
    
    return '';
  }

  private getFieldDisplayName(field: string): string {
    switch (field) {
      case 'publishedYear': return 'Published year';
      case 'totalCopies': return 'Total copies';
      case 'imageUrl': return 'Image URL';
      default: return field.charAt(0).toUpperCase() + field.slice(1);
    }
  }
}
