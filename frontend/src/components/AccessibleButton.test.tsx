import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AccessibleButton } from './AccessibleButton';

vi.mock('../utils/logger', () => ({
  trackEvent: vi.fn(async () => {}),
}));

describe('AccessibleButton', () => {
  it('renders with title and subtitle and is accessible', () => {
    render(
      <AccessibleButton
        id="btn-quality"
        variant="quality-metrics"
        title="Quality Metrics"
        subtitle="Performance tracking"
        ariaLabel="Quality metrics"
      />
    );

    const button = screen.getByRole('button', { name: /quality metrics/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute('id', 'btn-quality');
  });

  it('fires onClick and logs event on click', async () => {
    const onClick = vi.fn();
    const { trackEvent } = await import('../utils/logger');

    render(
      <AccessibleButton
        id="btn-recurring"
        variant="recurring-defects"
        title="Recurring Defects"
        onClick={onClick}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /recurring defects/i }));
    await waitFor(() => expect(onClick).toHaveBeenCalledTimes(1));
    expect(trackEvent).toHaveBeenCalled();
  });

  it('does not trigger click when disabled', async () => {
    const onClick = vi.fn();

    render(
      <AccessibleButton
        id="btn-disabled"
        title="Disabled Button"
        onClick={onClick}
        disabled
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /disabled button/i }));
    expect(onClick).not.toHaveBeenCalled();
  });
});
