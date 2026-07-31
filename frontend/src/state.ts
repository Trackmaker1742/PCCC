// ============================================================
// Global Application State
// ============================================================
import type { User, Tenant } from './types';

export let mockUsers: User[] = [];
export let mockTenants: Tenant[] = [];
export let currentUser: User | null = null;
export let activeTenant: Tenant | null = null;

export function setMockUsers(users: User[]): void {
  mockUsers = users;
}

export function setMockTenants(tenants: Tenant[]): void {
  mockTenants = tenants;
}

export function setCurrentUser(user: User | null): void {
  currentUser = user;
}

export function setActiveTenant(tenant: Tenant | null): void {
  activeTenant = tenant;
}

/**
 * Build request headers from the active simulated context.
 */
export function getHeaders(): Record<string, string> {
  if (!currentUser || !activeTenant) return {};
  return {
    'X-User-ID': currentUser.id,
    'X-Tenant-ID': activeTenant.id,
  };
}
