import type { AppProps } from 'next/app'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import Navbar from '../components/Navbar'
import '../styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        staleTime: 15_000,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-[#0b0f17] text-gray-200">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Component {...pageProps} />
        </main>
      </div>
    </QueryClientProvider>
  )
}
