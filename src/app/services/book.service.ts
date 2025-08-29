import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { delay, map, catchError } from 'rxjs/operators';
import { Book, BookCategory, CreateBookRequest, UpdateBookRequest } from '../models/book.model';
import { Transaction, TransactionType, TransactionStatus, IssueBookRequest, ReturnBookRequest, TransactionWithDetails } from '../models/transaction.model';
import { environment } from '../../environments/environment';

// Backend response interfaces
interface BackendBook {
  id: number | string;
  title: string;
  author: string;
  isbn?: string;
  category: string;
  publishedYear?: number;
  description?: string;
  totalCopies: number;
  availableCopies: number;
  imageUrl?: string;
  createdAt: string;
  updatedAt: string;
}

interface BackendTransaction {
  id: number | string;
  bookId: number | string;
  userId: number | string;
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
export class BookService {
  private apiUrl = environment.apiUrl;
  private booksSignal = signal<Book[]>([]);
  private transactionsSignal = signal<Transaction[]>([]);
  private isLoadingSignal = signal(false);

  // Inject HttpClient
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

  constructor() {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('auth_token');
    if (!token || token === 'null' || token === 'undefined' || token.trim() === '') {
      console.error('No valid token found in localStorage');
      throw new Error('No valid authentication token');
    }
    
    console.log('Using valid token for request:', token.substring(0, 20) + '...');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  private mapBackendCategoryToEnum(category: string): BookCategory {
    switch (category.toLowerCase()) {
      case 'fiction': return BookCategory.FICTION;
      case 'technology': return BookCategory.TECHNOLOGY;
      case 'history': return BookCategory.HISTORY;
      case 'science': return BookCategory.SCIENCE;
      case 'biography': return BookCategory.BIOGRAPHY;
      case 'mystery': return BookCategory.MYSTERY;
      case 'romance': return BookCategory.ROMANCE;
      case 'fantasy': return BookCategory.FANTASY;
      case 'children': return BookCategory.CHILDREN;
      case 'non-fiction':
      case 'business':
      case 'psychology':
      case 'self-help':
      default: return BookCategory.NON_FICTION;
    }
  }

  private mapBackendBookToBook(backendBook: BackendBook): Book {
    return {
      id: backendBook.id.toString(),
      title: backendBook.title,
      author: backendBook.author,
      isbn: backendBook.isbn || '',
      category: this.mapBackendCategoryToEnum(backendBook.category),
      publishedYear: backendBook.publishedYear || new Date().getFullYear(),
      description: backendBook.description || `${backendBook.title} by ${backendBook.author}`,
      totalCopies: backendBook.totalCopies,
      availableCopies: backendBook.availableCopies,
      imageUrl: backendBook.imageUrl || 'https://via.placeholder.com/150x200',
      createdAt: new Date(backendBook.createdAt),
      updatedAt: new Date(backendBook.updatedAt)
    };
  }

  private mapBackendTransactionToTransaction(bt: BackendTransaction): TransactionWithDetails {
    return {
      id: bt.id.toString(),
      bookId: bt.bookId.toString(),
      userId: bt.userId.toString(),
      type: bt.type === 'issue' ? TransactionType.ISSUE : TransactionType.RETURN,
      issueDate: new Date(bt.issueDate),
      dueDate: new Date(bt.dueDate),
      returnDate: bt.returnDate ? new Date(bt.returnDate) : undefined,
      status: bt.status === 'active' ? TransactionStatus.ACTIVE : TransactionStatus.RETURNED,
      fine: bt.fine || 0,
      createdAt: new Date(bt.createdAt),
      updatedAt: new Date(bt.updatedAt),
      book: bt.book || { title: 'Unknown', author: 'Unknown', isbn: 'Unknown' },
      user: bt.user || { firstName: 'Unknown', lastName: 'Unknown', email: 'unknown@example.com' }
    };
  }

  // Book operations
  getAllBooks(): Observable<Book[]> {
    this.isLoadingSignal.set(true);
    return this.http.get<BackendBook[]>(`${this.apiUrl}/books`, { headers: this.getAuthHeaders() }).pipe(
      map(backendBooks => {
        const books = backendBooks.map(backendBook => this.mapBackendBookToBook(backendBook));
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
    return this.http.get<BackendBook>(`${this.apiUrl}/books/${id}`, { headers: this.getAuthHeaders() }).pipe(
      map(backendBook => {
        if (!backendBook) return null;
        return this.mapBackendBookToBook(backendBook);
      }),
      catchError((error: any) => {
        console.error('Error fetching book:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to fetch book'));
      })
    );
  }

  searchBooks(query: string, category?: BookCategory): Observable<Book[]> {
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
    console.log('Creating book with request:', bookRequest);
    return this.http.post<BackendBook>(`${this.apiUrl}/books`, {
      title: bookRequest.title,
      author: bookRequest.author,
      isbn: bookRequest.isbn,
      category: bookRequest.category,
      publishedYear: bookRequest.publishedYear,
      description: bookRequest.description,
      totalCopies: bookRequest.totalCopies,
      imageUrl: bookRequest.imageUrl
    }, { headers: this.getAuthHeaders() }).pipe(
      map(backendBook => {
        console.log('Backend response for create book:', backendBook);
        const newBook = this.mapBackendBookToBook(backendBook);
        
        // Refresh the books list
        this.getAllBooks().subscribe();
        
        return newBook;
      }),
      catchError((error: any) => {
        console.error('Error creating book:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to create book'));
      })
    );
  }

  updateBook(bookRequest: UpdateBookRequest): Observable<Book> {
    console.log('Updating book with request:', bookRequest);
    return this.http.put<BackendBook>(`${this.apiUrl}/books/${bookRequest.id}`, {
      title: bookRequest.title,
      author: bookRequest.author,
      isbn: bookRequest.isbn,
      category: bookRequest.category,
      publishedYear: bookRequest.publishedYear,
      description: bookRequest.description,
      totalCopies: bookRequest.totalCopies,
      imageUrl: bookRequest.imageUrl
    }, { headers: this.getAuthHeaders() }).pipe(
      map(backendBook => {
        console.log('Backend response for update book:', backendBook);
        const updatedBook = this.mapBackendBookToBook(backendBook);
        
        // Refresh the books list
        this.getAllBooks().subscribe();
        
        return updatedBook;
      }),
      catchError((error: any) => {
        console.error('Error updating book:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to update book'));
      })
    );
  }

  deleteBook(id: string): Observable<boolean> {
    return this.http.delete<boolean>(`${this.apiUrl}/books/${id}`, { headers: this.getAuthHeaders() }).pipe(
      map(result => {
        // Refresh the books list
        this.getAllBooks().subscribe();
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
    return this.http.get<BackendTransaction[]>(`${this.apiUrl}/transactions`, { headers: this.getAuthHeaders() }).pipe(
      map(backendTransactions => {
        console.log('Backend transactions response:', backendTransactions);
        const transactions = backendTransactions.map(bt => this.mapBackendTransactionToTransaction(bt));
        
        this.transactionsSignal.set(transactions);
        this.isLoadingSignal.set(false);
        return transactions;
      }),
      catchError((error: any) => {
        this.isLoadingSignal.set(false);
        console.error('Error fetching transactions:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to fetch transactions'));
      })
    );
  }

  getUserTransactions(userId: string): Observable<TransactionWithDetails[]> {
    // For members, the backend automatically filters by user ID
    // For admins, we can filter client-side if needed
    return this.getAllTransactions().pipe(
      map(transactions => {
        // If it's a member, the backend already filtered by user ID
        // If it's an admin, we can optionally filter by specific user
        return transactions;
      }),
      catchError((error: any) => {
        console.error('Error fetching user transactions:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to fetch user transactions'));
      })
    );
  }

  issueBook(request: IssueBookRequest): Observable<Transaction> {
    console.log('Issuing book with request:', request);
    return this.http.post<BackendTransaction>(`${this.apiUrl}/borrow/${request.bookId}`, {
      dueDate: request.dueDate.toISOString()
    }, { headers: this.getAuthHeaders() }).pipe(
      map(response => {
        console.log('Backend response for issue book:', response);
        const transaction: Transaction = {
          id: response.id.toString(),
          bookId: response.bookId.toString(),
          userId: response.userId.toString(),
          type: TransactionType.ISSUE,
          issueDate: new Date(response.issueDate),
          dueDate: new Date(response.dueDate),
          status: TransactionStatus.ACTIVE,
          createdAt: new Date(response.createdAt),
          updatedAt: new Date(response.updatedAt)
        };
        
        // Refresh the books list and transactions
        this.getAllBooks().subscribe();
        this.getAllTransactions().subscribe();
        
        return transaction;
      }),
      catchError((error: any) => {
        console.error('Error issuing book:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to issue book'));
      })
    );
  }

  returnBook(request: ReturnBookRequest): Observable<Transaction> {
    console.log('Returning book with request:', request);
    return this.http.post<BackendTransaction>(`${this.apiUrl}/return/${request.transactionId}`, {
      returnDate: request.returnDate.toISOString()
    }, { headers: this.getAuthHeaders() }).pipe(
      map(response => {
        console.log('Backend response for return book:', response);
        const transaction: Transaction = {
          id: response.id.toString(),
          bookId: response.bookId.toString(),
          userId: response.userId.toString(),
          type: TransactionType.RETURN,
          issueDate: new Date(response.issueDate),
          dueDate: new Date(response.dueDate),
          returnDate: new Date(response.returnDate!),
          status: TransactionStatus.RETURNED,
          fine: response.fine || 0,
          createdAt: new Date(response.createdAt),
          updatedAt: new Date(response.updatedAt)
        };
        
        // Refresh the books list and transactions
        this.getAllBooks().subscribe();
        this.getAllTransactions().subscribe();
        
        return transaction;
      }),
      catchError((error: any) => {
        console.error('Error returning book:', error);
        return throwError(() => new Error(error.error?.error || 'Failed to return book'));
      })
    );
  }
}