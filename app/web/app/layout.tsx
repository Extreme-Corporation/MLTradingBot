import './globals.css';
import type { ReactNode } from 'react';

export const metadata = {
  title: 'IQ Option Bot Dashboard',
  description: 'Painel de controle do robô IQ Option'
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
