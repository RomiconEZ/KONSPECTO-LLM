// frontend/src/__tests__/GoogleDocViewer.test.jsx

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import GoogleDocViewer from '../components/GoogleDocViewer';
import { getConfig } from '../config';

// Мокаем config.js
jest.mock('../config');

describe('GoogleDocViewer Component', () => {
  const mockOnClose = jest.fn();

  it('renders iframe when fileId is provided', () => {
    const fileId = '12345';

    render(<GoogleDocViewer fileId={fileId} onClose={mockOnClose} />);

    const iframe = screen.getByTitle(/Просмотр документа Google/i);
    expect(iframe).toBeInTheDocument();
    expect(iframe).toHaveAttribute('src', `https://drive.google.com/file/d/${fileId}/preview`);
  });

  it('does not render when fileId is not provided', () => {
    render(<GoogleDocViewer fileId="" onClose={mockOnClose} />);

    expect(screen.queryByTitle(/Просмотр документа Google/i)).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const fileId = '12345';

    render(<GoogleDocViewer fileId={fileId} onClose={mockOnClose} />);

    const closeButton = screen.getByText(/Закрыть/i);
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
});