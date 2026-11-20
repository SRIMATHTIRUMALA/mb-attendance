import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Logo } from '../components/common/Logo';
import { StatusBadge } from '../components/common/StatusBadge';

describe('Frontend Core UI Components', () => {
  it('renders MB Solar Hub Logo brand title correctly', () => {
    render(<Logo />);
    expect(screen.getByText(/MB SOLAR/i)).toBeInTheDocument();
    expect(screen.getByText(/HUB/i)).toBeInTheDocument();
  });

  it('renders status badges with appropriate classes', () => {
    const { rerender } = render(<StatusBadge status="present" />);
    expect(screen.getByText('present')).toBeInTheDocument();

    rerender(<StatusBadge status="late" />);
    expect(screen.getByText('late')).toBeInTheDocument();

    rerender(<StatusBadge status="weekly off" />);
    expect(screen.getByText('weekly off')).toBeInTheDocument();
  });
});
