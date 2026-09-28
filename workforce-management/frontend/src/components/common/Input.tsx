import React, { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes, ReactNode } from 'react';

interface BaseInputProps {
  label?: ReactNode;
  error?: string;
  helperText?: string;
  icon?: ReactNode;
  containerStyle?: React.CSSProperties;
}

export interface TextInputProps extends InputHTMLAttributes<HTMLInputElement>, BaseInputProps {
  as?: 'input';
}

export interface SelectInputProps extends SelectHTMLAttributes<HTMLSelectElement>, BaseInputProps {
  as: 'select';
  options?: Array<{ value: string | number; label: string }>;
  children?: ReactNode;
}

export interface TextareaInputProps extends TextareaHTMLAttributes<HTMLTextAreaElement>, BaseInputProps {
  as: 'textarea';
}

export type InputProps = TextInputProps | SelectInputProps | TextareaInputProps;

export const Input: React.FC<InputProps> = (props) => {
  const { label, error, helperText, icon, containerStyle, className = '', ...rest } = props;

  return (
    <div className="form-group" style={containerStyle}>
      {label && <label className="form-label">{label}</label>}

      {props.as === 'select' ? (
        <select
          className={`form-control ${error ? 'border-danger' : ''} ${className}`.trim()}
          {...(rest as SelectHTMLAttributes<HTMLSelectElement>)}
        >
          {props.options
            ? props.options.map((opt) => (
                <option key={opt.value} value={opt.value} style={{ background: '#161E31', color: '#FFF' }}>
                  {opt.label}
                </option>
              ))
            : props.children}
        </select>
      ) : props.as === 'textarea' ? (
        <textarea
          className={`form-control ${error ? 'border-danger' : ''} ${className}`.trim()}
          {...(rest as TextareaHTMLAttributes<HTMLTextAreaElement>)}
        />
      ) : (
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          {icon && (
            <span style={{ position: 'absolute', left: '0.85rem', color: 'var(--text-dim)', pointerEvents: 'none' }}>
              {icon}
            </span>
          )}
          <input
            className={`form-control ${error ? 'border-danger' : ''} ${className}`.trim()}
            style={icon ? { paddingLeft: '2.5rem', width: '100%' } : { width: '100%' }}
            {...(rest as InputHTMLAttributes<HTMLInputElement>)}
          />
        </div>
      )}

      {error && <span className="form-error">{error}</span>}
      {helperText && !error && <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.35rem' }}>{helperText}</span>}
    </div>
  );
};
