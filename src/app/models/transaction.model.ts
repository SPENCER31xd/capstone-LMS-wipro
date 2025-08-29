export interface Transaction {
  id: string;
  bookId: string;
  userId: string;
  type: TransactionType;
  issueDate: Date;
  dueDate: Date;
  returnDate?: Date;
  status: TransactionStatus;
  fine?: number;
  createdAt: Date;
  updatedAt: Date;
}

export enum TransactionType {
  ISSUE = 'issue',
  RETURN = 'return'
}

export enum TransactionStatus {
  ACTIVE = 'active',
  RETURNED = 'returned',
  OVERDUE = 'overdue'
}

export interface IssueBookRequest {
  bookId: string;
  userId: string;
  dueDate: Date;
}

export interface ReturnBookRequest {
  transactionId: string;
  returnDate: Date;
}

export interface TransactionWithDetails extends Transaction {
  book: {
    title: string;
    author: string;
    isbn: string;
  };
  user: {
    firstName: string;
    lastName: string;
    email: string;
  };
}
