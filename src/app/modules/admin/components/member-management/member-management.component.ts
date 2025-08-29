import { Component, OnInit, OnDestroy } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../../../services/auth.service';
import { User } from '../../../../models/user.model';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-member-management',
  templateUrl: './member-management.component.html',
  styleUrls: ['./member-management.component.scss']
})
export class MemberManagementComponent implements OnInit, OnDestroy {
  displayedColumns: string[] = ['name', 'email', 'joinDate', 'status', 'actions'];
  members: User[] = [];
  filteredMembers: User[] = [];
  searchTerm = '';
  
  private destroy$ = new Subject<void>();

  constructor(
    public authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadMembers();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadMembers(): void {
    console.log('Loading members...');
    this.authService.getAllMembers().pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (members) => {
        console.log('Members loaded successfully:', members);
        this.members = members;
        this.applyFilters();
      },
      error: (error) => {
        console.error('Failed to load members:', error);
        this.snackBar.open('Failed to load members: ' + (error.message || 'Unknown error'), 'Close', { duration: 5000 });
        this.members = [];
        this.applyFilters();
      }
    });
  }

  applyFilters(): void {
    let filtered = [...this.members];

    if (this.searchTerm) {
      const search = this.searchTerm.toLowerCase();
      filtered = filtered.filter(member => 
        member.firstName.toLowerCase().includes(search) ||
        member.lastName.toLowerCase().includes(search) ||
        member.email.toLowerCase().includes(search)
      );
    }

    this.filteredMembers = filtered;
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  toggleMemberStatus(member: User): void {
    const newStatus = !member.isActive;
    const action = newStatus ? 'activate' : 'deactivate';

    this.authService.updateMemberStatus(member.id, newStatus).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (updatedMember) => {
        const memberIndex = this.members.findIndex(m => m.id === member.id);
        if (memberIndex !== -1) {
          this.members[memberIndex] = updatedMember;
          this.applyFilters();
        }
        this.snackBar.open(`Member ${action}d successfully`, 'Close', { duration: 3000 });
      },
      error: (error) => {
        this.snackBar.open(`Failed to ${action} member`, 'Close', { duration: 3000 });
      }
    });
  }

  getFullName(member: User): string {
    return `${member.firstName} ${member.lastName}`;
  }
}
