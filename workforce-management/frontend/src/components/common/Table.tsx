import React, { ReactNode } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { LoadingSkeleton } from './LoadingSkeleton';
import { EmptyState } from './EmptyState';
import { Button } from './Button';

export interface Column<T> {
  key: string;
  header: ReactNode;
  render?: (item: T, index: number) => ReactNode;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  isLoading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  page?: number;
  totalPages?: number;
  totalRecords?: number;
  pageSize?: number;
  onPageChange?: (newPage: number) => void;
  keyExtractor?: (item: T, index: number) => string | number;
}

export function Table<T>({
  columns,
  data,
  isLoading = false,
  emptyTitle,
  emptyDescription,
  page,
  totalPages,
  totalRecords,
  pageSize,
  onPageChange,
  keyExtractor,
}: TableProps<T>) {
  if (isLoading) {
    return (
      <div className="table-container" style={{ padding: '1.5rem' }}>
        <LoadingSkeleton lines={6} height="36px" />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="table-container">
        <EmptyState title={emptyTitle} description={emptyDescription} />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  style={{
                    width: col.width,
                    textAlign: col.align || 'left',
                  }}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((item, rowIndex) => {
              const rowKey = keyExtractor ? keyExtractor(item, rowIndex) : rowIndex;
              return (
                <tr key={rowKey}>
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      style={{
                        textAlign: col.align || 'left',
                      }}
                    >
                      {col.render ? col.render(item, rowIndex) : (item as any)[col.key]}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {page !== undefined && totalPages !== undefined && totalPages > 1 && (
        <div className="pagination">
          <div>
            Showing {((page - 1) * (pageSize || 10)) + 1} to{' '}
            {Math.min(page * (pageSize || 10), totalRecords || 0)} of {totalRecords} records
          </div>
          <div className="pagination-pages">
            <Button
              variant="secondary"
              size="sm"
              icon={<ChevronLeft size={16} />}
              disabled={page <= 1}
              onClick={() => onPageChange && onPageChange(page - 1)}
            >
              Prev
            </Button>
            <span style={{ margin: '0 0.5rem', fontWeight: 600, color: '#FFF' }}>
              Page {page} of {totalPages}
            </span>
            <Button
              variant="secondary"
              size="sm"
              icon={<ChevronRight size={16} />}
              disabled={page >= totalPages}
              onClick={() => onPageChange && onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
