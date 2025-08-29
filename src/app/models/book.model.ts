export interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string;
  category: BookCategory;
  publishedYear: number;
  description: string;
  totalCopies: number;
  availableCopies: number;
  imageUrl?: string;
  createdAt: Date;
  updatedAt: Date;
}

export enum BookCategory {
  FICTION = 'Fiction',
  NON_FICTION = 'Non-Fiction',
  SCIENCE = 'Science',
  TECHNOLOGY = 'Technology',
  HISTORY = 'History',
  BIOGRAPHY = 'Biography',
  MYSTERY = 'Mystery',
  ROMANCE = 'Romance',
  FANTASY = 'Fantasy',
  CHILDREN = 'Children'
}

export interface CreateBookRequest {
  title: string;
  author: string;
  isbn: string;
  category: BookCategory;
  publishedYear: number;
  description: string;
  totalCopies: number;
  imageUrl?: string;
}

export interface UpdateBookRequest extends Partial<CreateBookRequest> {
  id: string;
}
