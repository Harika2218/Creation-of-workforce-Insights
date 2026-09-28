import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Card } from '../components/common/Card';
import { StatCard } from '../components/common/StatCard';
import { EmptyState } from '../components/common/EmptyState';
import { Modal } from '../components/common/Modal';
import { Table, Column } from '../components/common/Table';

describe('Reusable UI Components Tests', () => {
  it('renders Button with variants and triggers onClick', () => {
    const handleClick = vi.fn();
    render(
      <Button variant="primary" onClick={handleClick}>
        Click Me
      </Button>
    );

    const btn = screen.getByRole('button', { name: /Click Me/i });
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('renders Badge with correct status classes', () => {
    const { container } = render(<Badge variant="Present">Present</Badge>);
    expect(container.querySelector('.badge-present')).toBeInTheDocument();
    expect(screen.getByText('Present')).toBeInTheDocument();
  });

  it('renders StatCard with value and label', () => {
    render(
      <StatCard
        label="Total Employees"
        value={200}
        icon={<span>Icon</span>}
      />
    );

    expect(screen.getByText('Total Employees')).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument();
  });

  it('renders Card with title, subtitle, and action', () => {
    render(
      <Card title="Card Title" subtitle="Card Subtitle" action={<button>Action</button>}>
        <div>Card Content</div>
      </Card>
    );

    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card Subtitle')).toBeInTheDocument();
    expect(screen.getByText('Card Content')).toBeInTheDocument();
    expect(screen.getByText('Action')).toBeInTheDocument();
  });

  it('renders Modal and calls onClose when close button clicked', () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} title="Test Modal">
        <div>Modal Body Text</div>
      </Modal>
    );

    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Modal Body Text')).toBeInTheDocument();

    const closeBtn = screen.getByRole('button', { name: /Close modal/i });
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('renders Table data rows properly', () => {
    const cols: Column<{ id: string; name: string }>[] = [
      { key: 'id', header: 'ID' },
      { key: 'name', header: 'Name' },
    ];
    const data = [
      { id: '1', name: 'Alpha' },
      { id: '2', name: 'Beta' },
    ];

    render(<Table columns={cols} data={data} />);

    expect(screen.getByText('Alpha')).toBeInTheDocument();
    expect(screen.getByText('Beta')).toBeInTheDocument();
  });

  it('renders EmptyState when Table data is empty', () => {
    const cols: Column<any>[] = [{ key: 'id', header: 'ID' }];
    render(<Table columns={cols} data={[]} emptyTitle="No Data Found" />);

    expect(screen.getByText('No Data Found')).toBeInTheDocument();
  });
});
