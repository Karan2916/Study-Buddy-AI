import { createRoot } from 'react-dom/client'
import { ThemeProvider } from '@/components/ThemesProvider'
import App from './App.tsx'
import './index.css'

createRoot(document.getElementById("root")!).render(
  <ThemeProvider
    attribute="class"
    defaultTheme="system"
    enableSystem
    disableTransitionOnChange
  >
    <App />
  </ThemeProvider>
);
