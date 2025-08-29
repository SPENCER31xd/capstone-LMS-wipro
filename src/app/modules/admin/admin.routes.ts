import { Routes } from '@angular/router';
import { AdminDashboardComponent } from './components/admin-dashboard/admin-dashboard.component';
import { BookManagementComponent } from './components/book-management/book-management.component';
import { MemberManagementComponent } from './components/member-management/member-management.component';
import { TransactionManagementComponent } from './components/transaction-management/transaction-management.component';

export const adminRoutes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    component: AdminDashboardComponent
  },
  {
    path: 'books',
    component: BookManagementComponent
  },
  {
    path: 'members',
    component: MemberManagementComponent
  },
  {
    path: 'transactions',
    component: TransactionManagementComponent
  }
];
