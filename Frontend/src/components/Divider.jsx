export default function Divider({ children }) {
  return (
    <div className="flex items-center gap-3 text-[0.78rem] text-inkwell/55">
      <span className="h-px flex-1 bg-inkwell/15" />
      {children}
      <span className="h-px flex-1 bg-inkwell/15" />
    </div>
  )
}
