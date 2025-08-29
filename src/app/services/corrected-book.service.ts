import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { delay, map, catchError } from 'rxjs/operators';
import { Book, BookCategory, CreateBookRequest, UpdateBookRequest } from '../models/book.model';
import { Transaction, TransactionType, TransactionStatus, IssueBookRequest, ReturnBookRequest, TransactionWithDetails } from '../models/transaction.model';
import { environment } from '../../environments/environment';

// Backend response interfaces
interface BackendBook {
  id: string;
  title: string;
  author: string;
  isbn: string;
  category: string;
  publishedYear: number;
  description: string;
  totalCopies: number;
  availableCopies: number;
  imageUrl: string;
  createdAt: string;
  updatedAt: string;
}

interface BackendTransaction {
  id: string;
  bookId: string;
  userId: string;
  type: string;
  issueDate: string;
  dueDate: string;
  returnDate?: string;
  status: string;
  fine?: number;
  createdAt: string;
  updatedAt: string;
  book?: {
    title: string;
    author: string;
    isbn: string;
  };
  user?: {
    firstName: string;
    lastName: string;
    email: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class CorrectedBookService {
  private apiUrl = environment.apiUrl;
  private booksSignal = signal<Book[]>([]);
  private transactionsSignal = signal<Transaction[]>([]);
  private isLoadingSignal = signal(false);

  // Inject dependencies
  private http = inject(HttpClient);

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

  constructor() {
    this.getAllBooks().subscribe(); // Load initial data
  }

  // Helper method to get auth headers
  private getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  // Helper method to convert backend book to frontend book
  private convertBackendBook(backendBook: BackendBook): Book {
    return {
      id: backendBook.id,
      title: backendBook.title,
      author: backendBook.author,
      isbn: backendBook.isbn,
      category: backendBook.category as BookCategory,
      publishedYear: backendBook.publishedYear,
      description: backendBook.description,
      totalCopies: backendBook.totalCopies,
      availableCopies: backendBook.availableCopies,
      imageUrl: backendBook.imageUrl,
      createdAt: new Date(backendBook.createdAt),
      updatedAt: new Date(backendBook.updatedAt)
    };
  }

  // Helper method to convert backend transaction to frontend transaction
  private convertBackendTransaction(backendTransaction: BackendTransaction): Transaction {
    return {
      id: backendTransaction.id,
      bookId: backendTransaction.bookId,
      userId: backendTransaction.userId,
      type: backendTransaction.type as TransactionType,
      issueDate: new Date(backendTransaction.issueDate),
      dueDate: new Date(backendTransaction.dueDate),
      returnDate: backendTransaction.returnDate ? new Date(backendTransaction.returnDate) : undefined,
      status: backendTransaction.status as TransactionStatus,
      fine: backendTransaction.fine,
      createdAt: new Date(backendTransaction.createdAt),
      updatedAt: new Date(backendTransaction.updatedAt)
    };
  }

  // Book operations
  getAllBooks(): Observable<Book[]> {
    this.isLoadingSignal.set(true);
    return this.http.get<BackendBook[]>(`${this.apiUrl}/books`).pipe(
      map(backendBooks => {
        const books = backendBooks.map(book => this.convertBackendBook(book));
        this.booksSignal.set(books);
        this.isLoadingSignal.set(false);
        return books;
      }),
      catchError((error: any) => {
        this.isLoadingSignal.set(false);
        console.error('Error fetching books:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to fetch books'));
      })
    );
  }

  getBookById(id: string): Observable<Book | null> {
    return this.http.get<BackendBook>(`${this.apiUrl}/books/${id}`).pipe(
      map(backendBook => this.convertBackendBook(backendBook)),
      catchError((error: any) => {
        console.error('Error fetching book:', error);
        return of(null);
      })
    );
  }

  searchBooks(query: string, category?: BookCategory): Observable<Book[]> {
    this.isLoadingSignal.set(true);
    // For now, we'll fetch all books and filter client-side
    // In a real implementation, you'd add query parameters to the API
    return this.getAllBooks().pipe(
      map(books => {
        let filteredBooks = books;

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

        return filteredBooks;
      })
    );
  }

  createBook(bookRequest: CreateBookRequest): Observable<Book> {
    const headers = this.getAuthHeaders();
    return this.http.post<BackendBook>(`${this.apiUrl}/books`, bookRequest, { headers }).pipe(
      map(backendBook => {
        const newBook = this.convertBackendBook(backendBook);
        const currentBooks = this.booksSignal();
        this.booksSignal.set([newBook, ...currentBooks]);
        return newBook;
      }),
      catchError((error: any) => {
        console.error('Error creating book:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to create book'));
      })
    );
  }

  updateBook(bookRequest: UpdateBookRequest): Observable<Book> {
    const headers = this.getAuthHeaders();
    return this.http.put<BackendBook>(`${this.apiUrl}/books/${bookRequest.id}`, bookRequest, { headers }).pipe(
      map(backendBook => {
        const updatedBook = this.convertBackendBook(backendBook);
        const currentBooks = this.booksSignal();
        const bookIndex = currentBooks.findIndex(b => b.id === updatedBook.id);
        if (bookIndex !== -1) {
          const newBooks = [...currentBooks];
          newBooks[bookIndex] = updatedBook;
          this.booksSignal.set(newBooks);
        }
        return updatedBook;
      }),
      catchError((error: any) => {
        console.error('Error updating book:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to update book'));
      })
    );
  }

  deleteBook(id: string): Observable<boolean> {
    const headers = this.getAuthHeaders();
    return this.http.delete<boolean>(`${this.apiUrl}/books/${id}`, { headers }).pipe(
      map(result => {
        if (result) {
          const currentBooks = this.booksSignal();
          const newBooks = currentBooks.filter(book => book.id !== id);
          this.booksSignal.set(newBooks);
        }
        return result;
      }),
      catchError((error: any) => {
        console.error('Error deleting book:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to delete book'));
      })
    );
  }

  // Transaction operations
  getAllTransactions(): Observable<TransactionWithDetails[]> {
    this.isLoadingSignal.set(true);
    const headers = this.getAuthHeaders();
    return this.http.get<BackendTransaction[]>(`${this.apiUrl}/transactions`, { headers }).pipe(
      map(backendTransactions => {
        const transactionsWithDetails = backendTransactions.map(backendTransaction => {
          const transaction = this.convertBackendTransaction(backendTransaction);
          return {
            ...transaction,
            book: backendTransaction.book || { title: 'Unknown', author: 'Unknown', isbn: 'Unknown' },
            user: backendTransaction.user || { firstName: 'Unknown', lastName: 'User', email: 'unknown@example.com' }
          };
        });
        
        const transactions = backendTransactions.map(bt => this.convertBackendTransaction(bt));
        this.transactionsSignal.set(transactions);
        this.isLoadingSignal.set(false);
        return transactionsWithDetails;
      }),
      catchError((error: any) => {
        this.isLoadingSignal.set(false);
        console.error('Error fetching transactions:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to fetch transactions'));
      })
    );
  }

  getUserTransactions(userId: string): Observable<TransactionWithDetails[]> {
    return this.getAllTransactions().pipe(
      map(transactions => transactions.filter(t => t.userId === userId))
    );
  }

  issueBook(request: IssueBookRequest): Observable<Transaction> {
    const headers = this.getAuthHeaders();
    const body = {
      dueDate: request.dueDate.toISOString()
    };
    
    return this.http.post<BackendTransaction>(`${this.apiUrl}/borrow/${request.bookId}`, body, { headers }).pipe(
      map(backendTransaction => {
        const newTransaction = this.convertBackendTransaction(backendTransaction);
        
        // Update local book availability
        const currentBooks = this.booksSignal();
        const bookIndex = currentBooks.findIndex(b => b.id === request.bookId);
        if (bookIndex !== -1) {
          const newBooks = [...currentBooks];
          newBooks[bookIndex] = {
            ...newBooks[bookIndex],
            availableCopies: newBooks[bookIndex].availableCopies - 1
          };
          this.booksSignal.set(newBooks);
        }
        
        // Update local transactions
        const currentTransactions = this.transactionsSignal();
        this.transactionsSignal.set([newTransaction, ...currentTransactions]);
        
        return newTransaction;
      }),
      catchError((error: any) => {
        console.error('Error issuing book:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to issue book'));
      })
    );
  }

  returnBook(request: ReturnBookRequest): Observable<Transaction> {
    const headers = this.getAuthHeaders();
    const body = {
      returnDate: request.returnDate.toISOString()
    };
    
    return this.http.post<BackendTransaction>(`${this.apiUrl}/return/${request.transactionId}`, body, { headers }).pipe(
      map(backendTransaction => {
        const updatedTransaction = this.convertBackendTransaction(backendTransaction);
        
        // Update local book availability
        const currentBooks = this.booksSignal();
        const bookIndex = currentBooks.findIndex(b => b.id === updatedTransaction.bookId);
        if (bookIndex !== -1) {
          const newBooks = [...currentBooks];
          newBooks[bookIndex] = {
            ...newBooks[bookIndex],
            availableCopies: newBooks[bookIndex].availableCopies + 1
          };
          this.booksSignal.set(newBooks);
        }
        
        // Update local transactions
        const currentTransactions = this.transactionsSignal();
        const transactionIndex = currentTransactions.findIndex(t => t.id === updatedTransaction.id);
        if (transactionIndex !== -1) {
          const newTransactions = [...currentTransactions];
          newTransactions[transactionIndex] = updatedTransaction;
          this.transactionsSignal.set(newTransactions);
        }
        
        return updatedTransaction;
      }),
      catchError((error: any) => {
        console.error('Error returning book:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to return book'));
      })
    );
  }
}

