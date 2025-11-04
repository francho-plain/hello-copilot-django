import React from 'react';
import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock all the services
jest.mock('./services/catService');

test('renders app header', async () => {
  await act(async () => {
    render(<App />);
  });
  
  const headerElement = screen.getByText('🐱 Cat Adoption Center');
  expect(headerElement).toBeInTheDocument();
});

test('renders navigation buttons', async () => {
  await act(async () => {
    render(<App />);
  });
  
  expect(screen.getByText('All Cats')).toBeInTheDocument();
  expect(screen.getByText('Add Cat')).toBeInTheDocument();
  expect(screen.getByText('Statistics')).toBeInTheDocument();
});
