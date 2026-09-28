import { describe, it, expect } from 'vitest';

describe('Form Business Logic & Validations', () => {
  it('validates timesheet hours equality: billable + non_billable == total_hours', () => {
    const validateTimesheet = (total: number, billable: number, nonBillable: number) => {
      if (total <= 0 || total > 24) return false;
      return billable + nonBillable === total;
    };

    expect(validateTimesheet(8, 6, 2)).toBe(true);
    expect(validateTimesheet(8, 8, 0)).toBe(true);
    expect(validateTimesheet(8, 5, 2)).toBe(false); // 5 + 2 != 8
    expect(validateTimesheet(25, 20, 5)).toBe(false); // > 24
    expect(validateTimesheet(0, 0, 0)).toBe(false); // <= 0
  });

  it('validates leave application date order: start_date <= end_date', () => {
    const validateLeaveDates = (start: string, end: string) => {
      return new Date(start) <= new Date(end);
    };

    expect(validateLeaveDates('2026-04-01', '2026-04-05')).toBe(true);
    expect(validateLeaveDates('2026-04-05', '2026-04-05')).toBe(true); // single day
    expect(validateLeaveDates('2026-04-10', '2026-04-05')).toBe(false); // reversed
  });

  it('validates employee ID format starts with EMP and numbers', () => {
    const validateEmployeeId = (id: string) => {
      return /^EMP\d{3,}$/.test(id);
    };

    expect(validateEmployeeId('EMP001')).toBe(true);
    expect(validateEmployeeId('EMP201')).toBe(true);
    expect(validateEmployeeId('ABC001')).toBe(false);
    expect(validateEmployeeId('EMP')).toBe(false);
  });
});
