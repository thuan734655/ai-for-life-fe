import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/react-query';

/**
 * @param {object} props
 * @param {React.ReactNode} props.children
 */
export const AppProvider = ({ children }) => {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
};
