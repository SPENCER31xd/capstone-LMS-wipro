import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';
import { of, signal } from 'rxjs';

import { BookManagementComponent } from './book-management.component';
import { BookService } from '../../../../services/book.service';
import { BookCategory } from '../../../../models/book.model';

describe('BookManagementComponent', () => {
  let component: BookManagementComponent;
  let fixture: ComponentFixture<BookManagementComponent>;
  let mockBookService: jasmine.SpyObj<BookService>;
  let mockDialog: jasmine.SpyObj<MatDialog>;
  let mockSnackBar: jasmine.SpyObj<MatSnackBar>;

  const mockBooks = [
    {
      id: '1',
      title: 'Test Book',
      author: 'Test Author',
      isbn: '123456789',
      category: BookCategory.FICTION,
      publishedYear: 2023,
      description: 'Test description',
      totalCopies: 5,
      availableCopies: 3,
      createdAt: new Date(),
      updatedAt: new Date()
    }
  ];

  beforeEach(async () => {
    mockBookService = jasmine.createSpyObj('BookService', ['getAllBooks', 'deleteBook'], {
      isLoading: signal(false)
    });
    mockDialog = jasmine.createSpyObj('MatDialog', ['open']);
    mockSnackBar = jasmine.createSpyObj('MatSnackBar', ['open']);

    mockBookService.getAllBooks.and.returnValue(of(mockBooks));

    await TestBed.configureTestingModule({
      declarations: [BookManagementComponent],
      imports: [NoopAnimationsModule, FormsModule],
      providers: [
        { provide: BookService, useValue: mockBookService },
        { provide: MatDialog, useValue: mockDialog },
        { provide: MatSnackBar, useValue: mockSnackBar }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(BookManagementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load books on init', () => {
    expect(mockBookService.getAllBooks).toHaveBeenCalled();
    expect(component.books).toEqual(mockBooks);
  });

  it('should filter books by search term', () => {
    component.books = mockBooks;
    component.searchTerm = 'Test Book';
    component.applyFilters();
    
    expect(component.filteredBooks.length).toBe(1);
    expect(component.filteredBooks[0].title).toBe('Test Book');
  });

  it('should filter books by category', () => {
    component.books = mockBooks;
    component.selectedCategory = BookCategory.FICTION;
    component.applyFilters();
    
    expect(component.filteredBooks.length).toBe(1);
    expect(component.filteredBooks[0].category).toBe(BookCategory.FICTION);
  });
});
