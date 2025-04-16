import './globals.css';

export const metadata = {
  title: 'EGG Monitor',
  description: 'A tool for monitoring EGG (electrogastrogram) data',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        {children}
      </body>
    </html>
  );
}
