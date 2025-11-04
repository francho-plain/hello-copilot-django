import React from 'react';
import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import CatForm from './CatForm';

// Mock the cat service
const mockCreateCat = jest.fn();
jest.mock('../../services/catService', () => ({
  createCat: (...args: any[]) => mockCreateCat(...args),
}));

describe('CatForm Component', () => {
  const mockOnCancel = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form title and fields', async () => {
    await act(async () => {
      render(<CatForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    });

    expect(screen.getByText('Add New Cat')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter cat\'s name')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Create Cat')).toBeInTheDocument();
  });

  test('submit button is disabled when name is empty', async () => {
    await act(async () => {
      render(<CatForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    });
    
    const submitButton = screen.getByText('Create Cat');
    expect(submitButton).toBeDisabled();
  });

  test('shows required field indicators', async () => {
    await act(async () => {
      render(<CatForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    });
    
    expect(screen.getByText('*')).toBeInTheDocument(); // Required field indicator
  });
});