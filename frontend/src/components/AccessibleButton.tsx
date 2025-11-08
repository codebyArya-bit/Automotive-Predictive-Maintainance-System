import React from 'react';
import clsx from 'clsx';
import { trackEvent } from '../utils/logger';

type Variant = 'recurring-defects' | 'quality-metrics' | 'primary';

export interface AccessibleButtonProps {
  variant?: Variant;
  title: string;
  subtitle?: string;
  icon?: React.ReactNode; // Prefer simple emoji or lightweight icon
  onClick?: () => void;
  ariaLabel?: string;
  disabled?: boolean;
  className?: string;
  id?: string;
}

const variantClasses: Record<Variant, string> = {
  'recurring-defects': 'from-orange-500 to-orange-600 text-white',
  'quality-metrics': 'from-blue-500 to-blue-600 text-white',
  primary: 'from-purple-500 to-purple-600 text-white',
};

export const AccessibleButton: React.FC<AccessibleButtonProps> = ({
  variant = 'primary',
  title,
  subtitle,
  icon,
  onClick,
  ariaLabel,
  disabled,
  className,
  id,
}) => {
  const handleClick = async () => {
    try {
      await trackEvent('ui_interaction', 'button_click', {
        id,
        title,
        variant,
      });
      onClick?.();
    } catch (err) {
      // Interaction tracking should never break button use
    }
  };

  return (
    <>
      <button
        id={id}
        type="button"
        aria-label={ariaLabel || title}
        aria-disabled={disabled ? 'true' : undefined}
        disabled={disabled}
        title={title}
        className={clsx(
          'bg-gradient-to-r p-6 rounded-xl hover:opacity-90 transition-opacity shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white/70 flex flex-col items-start',
          variantClasses[variant],
          disabled && 'opacity-60 cursor-not-allowed',
          className
        )}
        onClick={handleClick}
      >
        {icon && <div className="text-4xl mb-3" aria-hidden="true">{icon}</div>}
        <div className="text-lg font-bold mb-1">{title}</div>
        {subtitle && (
          <div className={clsx('text-sm', variant === 'recurring-defects' ? 'text-orange-100' : variant === 'quality-metrics' ? 'text-blue-100' : 'text-purple-100')}>
            {subtitle}
          </div>
        )}
      </button>
      <noscript>
        <div className="p-4 rounded-xl bg-white/10 text-white" role="note">
          {title}
        </div>
      </noscript>
    </>
  );
};

export default AccessibleButton;