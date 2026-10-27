import { useEffect } from 'react'

// The app has no <title> of its own, so every route would otherwise inherit the
// landing page title in the browser tab, history and bookmarks.
export default function usePageTitle(title) {
  useEffect(() => {
    if (title) document.title = title
  }, [title])
}
