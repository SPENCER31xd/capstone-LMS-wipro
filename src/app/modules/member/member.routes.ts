import { Routes } from '@angular/router';
import { MemberDashboardComponent } from './components/member-dashboard/member-dashboard.component';
import { BookListComponent } from './components/book-list/book-list.component';
import { MyTransactionsComponent } from './components/my-transactions/my-transactions.component';

export const memberRoutes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    component: MemberDashboardComponent
  },
  {
    path: 'books',
    component: BookListComponent
  },
  {
    path: 'transactions',
    component: MyTransactionsComponent
  }
];
