import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import CatList from './CatList';

// Mock the cat service
const mockGetCats = jest.fn();
const mockAdoptCat = jest.fn();
const mockDeleteCat = jest.fn();

jest.mock('../../services/catService', () => ({
  getCats: () => mockGetCats(),
  adoptCat: (...args: any[]) => mockAdoptCat(...args),
  deleteCat: (...args: any[]) => mockDeleteCat(...args),
}));

describe('CatList Component', () => {
  const mockOnAddNew = jest.fn();
  const originalConsoleError = console.error;

  beforeEach(() => {
    jest.clearAllMocks();
    // Suppress console.error during tests
    console.error = jest.fn();
  });

  afterEach(() => {
    // Restore console.error after tests
    console.error = originalConsoleError;
  });

  test('renders loading state initially', () => {
    mockGetCats.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<CatList onAddNew={mockOnAddNew} />);
    expect(screen.getByText('Loading cats... 🐱')).toBeInTheDocument();
  });

  test('renders Add New Cat button', async () => {
    mockGetCats.mockResolvedValue({
      count: 0,
      results: []
    });

    await act(async () => {
      render(<CatList onAddNew={mockOnAddNew} />);
    });

    await waitFor(() => {
      expect(screen.getByText('+ Add New Cat')).toBeInTheDocument();
    });
  });

  test('handles error state correctly', async () => {
    mockGetCats.mockRejectedValue(new Error('Network error'));

    await act(async () => {
      render(<CatList onAddNew={mockOnAddNew} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch cats. Please try again.')).toBeInTheDocument();
    });
  });
});