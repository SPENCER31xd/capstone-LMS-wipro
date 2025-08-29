import { Injectable, signal, computed } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { delay, map } from 'rxjs/operators';
import { Book, BookCategory, CreateBookRequest, UpdateBookRequest } from '../models/book.model';
import { Transaction, TransactionType, TransactionStatus, IssueBookRequest, ReturnBookRequest, TransactionWithDetails } from '../models/transaction.model';

@Injectable({
  providedIn: 'root'
})
export class BookService {
  private booksSignal = signal<Book[]>([]);
  private transactionsSignal = signal<Transaction[]>([]);
  private isLoadingSignal = signal(false);

  // Computed signals
  public readonly books = this.booksSignal.asReadonly();
  public readonly transactions = this.transactionsSignal.asReadonly();
  public readonly isLoading = this.isLoadingSignal.asReadonly();

  public readonly availableBooks = computed(() => 
    this.booksSignal().filter(book => book.availableCopies > 0)
  );

  public readonly categorizedBooks = computed(() => {
    const books = this.booksSignal();
    const categories = Object.values(BookCategory);
    return categories.reduce((acc, category) => {
      acc[category] = books.filter(book => book.category === category);
      return acc;
    }, {} as Record<BookCategory, Book[]>);
  });

  // Mock data
  private mockBooks: Book[] = [
    {
      id: '1',
      title: 'The Great Gatsby',
      author: 'F. Scott Fitzgerald',
      isbn: '978-0-7432-7356-5',
      category: BookCategory.FICTION,
      publishedYear: 1925,
      description: 'A classic American novel set in the Jazz Age.',
      totalCopies: 5,
      availableCopies: 3,
      imageUrl: 'https://via.placeholder.com/150x200',
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-01-01')
    },
    {
      id: '2',
      title: 'To Kill a Mockingbird',
      author: 'Harper Lee',
      isbn: '978-0-06-112008-4',
      category: BookCategory.FICTION,
      publishedYear: 1960,
      description: 'A gripping tale of racial injustice and childhood innocence.',
      totalCopies: 4,
      availableCopies: 2,
      imageUrl: 'https://via.placeholder.com/150x200',
      createdAt: new Date('2024-01-02'),
      updatedAt: new Date('2024-01-02')
    },
    {
      id: '3',
      title: 'Clean Code',
      author: 'Robert C. Martin',
      isbn: '978-0-13-235088-4',
      category: BookCategory.TECHNOLOGY,
      publishedYear: 2008,
      description: 'A handbook of agile software craftsmanship.',
      totalCopies: 6,
      availableCopies: 4,
      imageUrl: 'https://via.placeholder.com/150x200',
      createdAt: new Date('2024-01-03'),
      updatedAt: new Date('2024-01-03')
    },
    {
      id: '4',
      title: 'Sapiens',
      author: 'Yuval Noah Harari',
      isbn: '978-0-06-231609-7',
      category: BookCategory.HISTORY,
      publishedYear: 2011,
      description: 'A brief history of humankind.',
      totalCopies: 3,
      availableCopies: 1,
      imageUrl: 'https://via.placeholder.com/150x200',
      createdAt: new Date('2024-01-04'),
      updatedAt: new Date('2024-01-04')
    },
    {
      id: '5',
      title: 'The Lean Startup',
      author: 'Eric Ries',
      isbn: '978-0-307-88789-4',
      category: BookCategory.NON_FICTION,
      publishedYear: 2011,
      description: 'How constant innovation creates radically successful businesses.',
      totalCopies: 4,
      availableCopies: 3,
      imageUrl: 'https://via.placeholder.com/150x200',
      createdAt: new Date('2024-01-05'),
      updatedAt: new Date('2024-01-05')
    }
  ];

  private mockTransactions: Transaction[] = [
    {
      id: '1',
      bookId: '1',
      userId: '2',
      type: TransactionType.ISSUE,
      issueDate: new Date('2024-01-10'),
      dueDate: new Date('2024-02-10'),
      status: TransactionStatus.ACTIVE,
      createdAt: new Date('2024-01-10'),
      updatedAt: new Date('2024-01-10')
    },
    {
      id: '2',
      bookId: '2',
      userId: '3',
      type: TransactionType.ISSUE,
      issueDate: new Date('2024-01-15'),
      dueDate: new Date('2024-02-15'),
      returnDate: new Date('2024-02-01'),
      status: TransactionStatus.RETURNED,
      createdAt: new Date('2024-01-15'),
      updatedAt: new Date('2024-02-01')
    }
  ];

  constructor() {
    this.initializeData();
  }

  // Book operations
  getAllBooks(): Observable<Book[]> {
    this.isLoadingSignal.set(true);
    return of(this.mockBooks).pipe(
      delay(500),
      map(books => {
        this.booksSignal.set(books);
        this.isLoadingSignal.set(false);
        return books;
      })
    );
  }

  getBookById(id: string): Observable<Book | null> {
    const book = this.mockBooks.find(b => b.id === id);
    return of(book || null).pipe(delay(300));
  }

  searchBooks(query: string, category?: BookCategory): Observable<Book[]> {
    this.isLoadingSignal.set(true);
    let filteredBooks = this.mockBooks;

    if (query) {
      const searchQuery = query.toLowerCase();
      filteredBooks = filteredBooks.filter(book => 
        book.title.toLowerCase().includes(searchQuery) ||
        book.author.toLowerCase().includes(searchQuery) ||
        book.isbn.includes(searchQuery)
      );
    }

    if (category) {
      filteredBooks = filteredBooks.filter(book => book.category === category);
    }

    return of(filteredBooks).pipe(
      delay(500),
      map(books => {
        this.booksSignal.set(books);
        this.isLoadingSignal.set(false);
        return books;
      })
    );
  }

  createBook(bookRequest: CreateBookRequest): Observable<Book> {
    const newBook: Book = {
      id: (this.mockBooks.length + 1).toString(),
      ...bookRequest,
      availableCopies: bookRequest.totalCopies,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.mockBooks.push(newBook);
    this.booksSignal.set([...this.mockBooks]);
    
    return of(newBook).pipe(delay(500));
  }

  updateBook(bookRequest: UpdateBookRequest): Observable<Book> {
    const bookIndex = this.mockBooks.findIndex(b => b.id === bookRequest.id);
    if (bookIndex === -1) {
      return throwError(() => new Error('Book not found'));
    }

    const updatedBook: Book = {
      ...this.mockBooks[bookIndex],
      ...bookRequest,
      updatedAt: new Date()
    };

    // Adjust available copies if total copies changed
    if (bookRequest.totalCopies !== undefined) {
      const difference = bookRequest.totalCopies - this.mockBooks[bookIndex].totalCopies;
      updatedBook.availableCopies = Math.max(0, updatedBook.availableCopies + difference);
    }

    this.mockBooks[bookIndex] = updatedBook;
    this.booksSignal.set([...this.mockBooks]);
    
    return of(updatedBook).pipe(delay(500));
  }

  deleteBook(id: string): Observable<boolean> {
    const bookIndex = this.mockBooks.findIndex(b => b.id === id);
    if (bookIndex === -1) {
      return throwError(() => new Error('Book not found'));
    }

    // Check if book has active transactions
    const hasActiveTransactions = this.mockTransactions.some(
      t => t.bookId === id && t.status === TransactionStatus.ACTIVE
    );

    if (hasActiveTransactions) {
      return throwError(() => new Error('Cannot delete book with active transactions'));
    }

    this.mockBooks.splice(bookIndex, 1);
    this.booksSignal.set([...this.mockBooks]);
    
    return of(true).pipe(delay(500));
  }

  // Transaction operations
  getAllTransactions(): Observable<TransactionWithDetails[]> {
    this.isLoadingSignal.set(true);
    return of(this.mockTransactions).pipe(
      delay(500),
      map(transactions => {
        const transactionsWithDetails = transactions.map(transaction => {
          const book = this.mockBooks.find(b => b.id === transaction.bookId);
          // In a real app, you'd get user data from UserService
          const user = {
            firstName: transaction.userId === '2' ? 'John' : 'Jane',
            lastName: transaction.userId === '2' ? 'Doe' : 'Smith',
            email: transaction.userId === '2' ? 'john@library.com' : 'jane@library.com'
          };
          
          return {
            ...transaction,
            book: book ? {
              title: book.title,
              author: book.author,
              isbn: book.isbn
            } : { title: 'Unknown', author: 'Unknown', isbn: 'Unknown' },
            user
          };
        });
        
        this.transactionsSignal.set(transactions);
        this.isLoadingSignal.set(false);
        return transactionsWithDetails;
      })
    );
  }

  getUserTransactions(userId: string): Observable<TransactionWithDetails[]> {
    return this.getAllTransactions().pipe(
      map(transactions => transactions.filter(t => t.userId === userId))
    );
  }

  issueBook(request: IssueBookRequest): Observable<Transaction> {
    const book = this.mockBooks.find(b => b.id === request.bookId);
    if (!book || book.availableCopies <= 0) {
      return throwError(() => new Error('Book not available'));
    }

    // Check if user already has this book
    const existingTransaction = this.mockTransactions.find(
      t => t.bookId === request.bookId && 
           t.userId === request.userId && 
           t.status === TransactionStatus.ACTIVE
    );

    if (existingTransaction) {
      return throwError(() => new Error('User already has this book'));
    }

    const newTransaction: Transaction = {
      id: (this.mockTransactions.length + 1).toString(),
      bookId: request.bookId,
      userId: request.userId,
      type: TransactionType.ISSUE,
      issueDate: new Date(),
      dueDate: request.dueDate,
      status: TransactionStatus.ACTIVE,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.mockTransactions.push(newTransaction);
    
    // Update book availability
    book.availableCopies--;
    this.booksSignal.set([...this.mockBooks]);
    this.transactionsSignal.set([...this.mockTransactions]);

    return of(newTransaction).pipe(delay(500));
  }

  returnBook(request: ReturnBookRequest): Observable<Transaction> {
    const transactionIndex = this.mockTransactions.findIndex(t => t.id === request.transactionId);
    if (transactionIndex === -1) {
      return throwError(() => new Error('Transaction not found'));
    }

    const transaction = this.mockTransactions[transactionIndex];
    if (transaction.status !== TransactionStatus.ACTIVE) {
      return throwError(() => new Error('Book is not currently issued'));
    }

    // Update transaction
    transaction.returnDate = request.returnDate;
    transaction.status = TransactionStatus.RETURNED;
    transaction.updatedAt = new Date();

    // Calculate fine if overdue
    if (request.returnDate > transaction.dueDate) {
      const overdueDays = Math.ceil(
        (request.returnDate.getTime() - transaction.dueDate.getTime()) / (1000 * 60 * 60 * 24)
      );
      transaction.fine = overdueDays * 1; // $1 per day fine
    }

    // Update book availability
    const book = this.mockBooks.find(b => b.id === transaction.bookId);
    if (book) {
      book.availableCopies++;
    }

    this.booksSignal.set([...this.mockBooks]);
    this.transactionsSignal.set([...this.mockTransactions]);

    return of(transaction).pipe(delay(500));
  }

  private initializeData(): void {
    this.booksSignal.set(this.mockBooks);
    this.transactionsSignal.set(this.mockTransactions);
  }
}
