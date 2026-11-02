import { useEffect, useState } from 'react'

// Product themes. Each id maps to a token set in index.css under
// `.ff-product[data-theme='<id>']`; the swatches mirror those tokens.
export const THEMES = [
  { id: 'cobalt', label: 'Cobalt', swatch: ['#2f45ff', '#eef1f6'] },
  { id: 'midnight', label: 'Midnight', swatch: ['#7c8cff', '#0b1020'] },
  { id: 'mint', label: 'Mint', swatch: ['#0b7a57', '#eef4ef'] },
  { id: 'sunset', label: 'Sunset', swatch: ['#b8430f', '#f8efe6'] },
]

const STORAGE_KEY = 'focusflow-theme'
const IDS = new Set(THEMES.map((theme) => theme.id))

export function getStoredTheme() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return IDS.has(stored) ? stored : 'cobalt'
  } catch {
    return 'cobalt'
  }
}

export function useTheme() {
  const [theme, setTheme] = useState(getStoredTheme)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, theme)
    } catch {
      // Storage can be unavailable (private mode); the in-memory theme still works.
    }
  }, [theme])

  return [theme, setTheme]
}
