export default function FormError({ message }) {
  if (!message) return null

  return (
    <p
      role="alert"
      className="rounded-xl border border-[#b42318]/25 bg-[#fef3f2] px-3.5 py-2.5 text-[0.82rem] font-medium text-[#b42318]"
    >
      {message}
    </p>
  )
}
