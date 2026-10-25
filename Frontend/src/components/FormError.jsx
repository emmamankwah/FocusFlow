export default function FormError({ message }) {
  if (!message) return null

  return (
    <p
      role="alert"
      className="rounded-[3px] border border-coral/30 bg-coral/10 px-3.5 py-2.5 text-[0.8rem] text-coral"
    >
      {message}
    </p>
  )
}
