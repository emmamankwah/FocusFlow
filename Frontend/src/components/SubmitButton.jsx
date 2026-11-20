export default function SubmitButton({ loading, loadingText, disabled, children }) {
  return (
    <button
      type="submit"
      disabled={loading || disabled}
      aria-busy={loading}
      className="group inline-flex h-12 w-full items-center justify-center gap-2.5 rounded-xl bg-cobalt px-5 text-[0.95rem] font-semibold text-white shadow-[0_18px_36px_-20px_rgba(47,69,255,0.85)] transition-all duration-200 hover:-translate-y-px hover:bg-[#2438e6] disabled:translate-y-0 disabled:cursor-not-allowed disabled:opacity-55"
    >
      {loading && (
        <span
          aria-hidden
          className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"
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
