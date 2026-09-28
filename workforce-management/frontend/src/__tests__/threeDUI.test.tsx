import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { WebGLFallback } from '../components/3d/WebGLFallback';
import { ThreeDMetricCard } from '../components/3d/ThreeDMetricCard';
import { ThemeProvider, useTheme } from '../context/ThemeContext';

describe('Phase 8 — 3D UI & Enterprise Components', () => {
  it('renders WebGLFallback gracefully with custom title and subtitle', () => {
    render(
      <WebGLFallback
        title="Custom 3D Fallback"
        subtitle="Standard 2D rendering mode active."
      />
    );
    expect(screen.getByText('Custom 3D Fallback')).toBeInTheDocument();
    expect(screen.getByText('Standard 2D rendering mode active.')).toBeInTheDocument();
  });

  it('renders ThreeDMetricCard with depth, values, and badge', () => {
    const handleClick = vi.fn();
    render(
      <ThemeProvider>
        <ThreeDMetricCard
          label="Total Headcount"
          value={200}
          subtext="Active corporate roster"
          badge="Verified"
          badgeVariant="success"
          onClick={handleClick}
        />
      </ThemeProvider>
    );

    expect(screen.getByText('Total Headcount')).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument();
    expect(screen.getByText('Active corporate roster')).toBeInTheDocument();
    expect(screen.getByText('Verified')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Total Headcount'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('ThemeContext toggles between dark and light modes', () => {
    const TestThemeComponent = () => {
      const { theme, toggleTheme } = useTheme();
      return (
        <div>
          <span data-testid="current-theme">{theme}</span>
          <button onClick={toggleTheme}>Toggle</button>
        </div>
      );
    };

    render(
      <ThemeProvider>
        <TestThemeComponent />
      </ThemeProvider>
    );

    const themeDisplay = screen.getByTestId('current-theme');
    const toggleBtn = screen.getByText('Toggle');

    expect(themeDisplay.textContent).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');

    fireEvent.click(toggleBtn);
    expect(themeDisplay.textContent).toBe('light');
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');

    fireEvent.click(toggleBtn);
    expect(themeDisplay.textContent).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });
});
