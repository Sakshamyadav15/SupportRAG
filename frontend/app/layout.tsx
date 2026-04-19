import React from "react"
import type { Metadata } from 'next'
import { Geist, Geist_Mono, IBM_Plex_Sans } from 'next/font/google'
import { Courier_Prime } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });
const _courierPrime = Courier_Prime({ weight: ["400", "700"], subsets: ["latin"] });
const _ibmPlexSans = IBM_Plex_Sans({ weight: ["300", "400", "500", "600"], subsets: ["latin"] });

export const metadata: Metadata = {
  title: 'SupportRAG — Dual Vector Store RAG for Customer Support',
  description: 'Production-ready RAG system with dual vector stores, async processing, and FAISS IVF optimization. 4.2x throughput improvement with 337ms average latency across 15.5k+ documents.',
  keywords: ['RAG', 'customer support', 'vector store', 'FAISS', 'LangChain', 'Groq', 'AI support'],
  authors: [{ name: 'Saksham Yadav' }],
  openGraph: {
    title: 'SupportRAG — Dual Vector Store RAG for Customer Support',
    description: 'Production-ready RAG system with dual vector stores, async processing, and FAISS IVF optimization.',
    type: 'website',
    url: 'https://supportrag.dev',
    siteName: 'SupportRAG',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SupportRAG — Dual Vector Store RAG for Customer Support',
    description: 'Production-ready RAG system with dual vector stores, async processing, and FAISS IVF optimization.',
  },
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
