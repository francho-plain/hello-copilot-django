import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import Statistics from './Statistics';

// Mock the cat service
const mockGetStatistics = jest.fn();
jest.mock('../../services/catService', () => ({
  getStatistics: () => mockGetStatistics(),
}));

const mockStatistics = {
  total_cats: 25,
  adopted_cats: 12,
  available_cats: 13,
  adoption_rate: 48.0,
  average_age: 3.5,
  youngest_age: 1,
  oldest_age: 8,
  neutered_cats: 18,
  breeds_count: 8,
  recent_adoptions: 3
};

describe('Statistics Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    mockGetStatistics.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<Statistics />);
    expect(screen.getByText('Loading statistics... 📊')).toBeInTheDocument();
  });

  test('renders title and displays statistics after loading', async () => {
    mockGetStatistics.mockResolvedValue(mockStatistics);

    await act(async () => {
      render(<Statistics />);
    });

    await waitFor(() => {
      expect(screen.getByText('Cat Statistics 📈')).toBeInTheDocument();
    });

    // Check that statistics are displayed
    await waitFor(() => {
      expect(screen.getByText('25')).toBeInTheDocument(); // Total cats
      expect(screen.getByText('Total Cats')).toBeInTheDocument();
    });
  });

  test('handles error state correctly', async () => {
    mockGetStatistics.mockRejectedValue(new Error('Network error'));

    await act(async () => {
      render(<Statistics />);
    });

    await waitFor(() => {
      expect(screen.getByText('Error Loading Statistics')).toBeInTheDocument();
    });
  });
});