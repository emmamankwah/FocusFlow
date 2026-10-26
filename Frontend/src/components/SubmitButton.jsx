export default function SubmitButton({ loading, loadingText, disabled, children }) {
  return (
    <button
      type="submit"
      disabled={loading || disabled}
      className="group btn btn-primary w-full justify-center gap-2 rounded-xl px-5 py-3.5 shadow-[0_16px_38px_-18px_rgba(242,184,75,0.7)] transition-all duration-200 hover:shadow-[0_20px_44px_-18px_rgba(242,184,75,0.8)] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0"
    >
      {loading && (
        <span
          aria-hidden
          className="h-4 w-4 animate-spin rounded-full border-2 border-[#171205]/25 border-t-[#171205]"
        />
      )}
      {loading ? loadingText : children}
      {!loading && (
        <svg
          viewBox="0 0 16 16"
          className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M2.5 8h11M9 3.5 13.5 8 9 12.5" />
        </svg>
      )}
    </button>
  )
}
