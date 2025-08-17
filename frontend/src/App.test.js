import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock fetch globally
global.fetch = jest.fn();

// Helper function to setup mock response
function mockFetchResponse(data, ok = true) {
  global.fetch.mockImplementationOnce(() => 
    Promise.resolve({
      ok,
      json: () => Promise.resolve(data)
    })
  );
}

beforeEach(() => {
  // Clear mock between tests
  global.fetch.mockClear();
});

test('renders Dynasty League Analyzer title', () => {
  render(<App />);
  expect(screen.getByText('Dynasty League Analyzer')).toBeInTheDocument();
});

test('renders username input and find leagues button', () => {
  render(<App />);
  expect(screen.getByLabelText('Sleeper Username')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /find leagues/i })).toBeInTheDocument();
});

test('button is disabled when username is empty', () => {
  render(<App />);
  const button = screen.getByRole('button', { name: /find leagues/i });
  expect(button).toBeDisabled();
});

test('button is enabled when username is entered', () => {
  render(<App />);
  const input = screen.getByLabelText('Sleeper Username');
  fireEvent.change(input, { target: { value: 'testuser' } });
  const button = screen.getByRole('button', { name: /find leagues/i });
  expect(button).toBeEnabled();
});

test('displays leagues when API call is successful', async () => {
  const mockLeagues = [
    { league_id: '1', name: 'Test League 1' },
    { league_id: '2', name: 'Test League 2' }
  ];
  
  mockFetchResponse(mockLeagues);
  
  render(<App />);
  
  // Enter username and submit
  const input = screen.getByLabelText('Sleeper Username');
  fireEvent.change(input, { target: { value: 'testuser' } });
  fireEvent.click(screen.getByRole('button', { name: /find leagues/i }));
  
  // Wait for leagues to be displayed
  await waitFor(() => {
    expect(screen.getByText('Select a league to analyze')).toBeInTheDocument();
  });
  
  // Check if leagues are displayed
  expect(screen.getByText('Test League 1')).toBeInTheDocument();
  expect(screen.getByText('Test League 2')).toBeInTheDocument();
  
  // Verify API was called correctly
  expect(fetch).toHaveBeenCalledWith('http://localhost:8000/leagues/user/testuser');
});

test('displays error message when API call fails', async () => {
  mockFetchResponse(null, false);
  
  render(<App />);
  
  // Enter username and submit
  const input = screen.getByLabelText('Sleeper Username');
  fireEvent.change(input, { target: { value: 'nonexistentuser' } });
  fireEvent.click(screen.getByRole('button', { name: /find leagues/i }));
  
  // Wait for error message
  await waitFor(() => {
    expect(screen.getByText('User not found')).toBeInTheDocument();
  });
  
  // Verify no leagues are displayed
  expect(screen.queryByText('Select a league to analyze')).not.toBeInTheDocument();
});
