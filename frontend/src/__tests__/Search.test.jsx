// frontend/src/__tests__/Search.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Search from '../pages/Search';

test('renders search page and performs search', async () => {
  render(
    <BrowserRouter>
      <Search />
    </BrowserRouter>
  );

  const input = screen.getByPlaceholderText(/Enter your query/i);
  fireEvent.change(input, { target: { value: 'test query' } });

  const button = screen.getByText(/Search/i);
  fireEvent.click(button);

  const results = await screen.findByText(/Results/i);
  expect(results).toBeInTheDocument();
});