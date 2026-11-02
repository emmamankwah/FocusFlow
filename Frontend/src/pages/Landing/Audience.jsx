const groups = ['Students', 'Developers', 'Freelancers', 'Researchers', 'Teams']

export default function Audience() {
  return (
    <section id="audience" className="border-t border-line py-10">
      <div className="mx-auto flex max-w-[1180px] flex-col gap-5 px-7 sm:flex-row sm:items-center sm:justify-between">
        <p className="max-w-[52ch] text-[0.9rem] leading-relaxed text-dim">
          <span className="font-semibold text-ink">Students first.</span> The same engine works for
          anyone whose week is a mix of deadlines, meetings, and time that is not really theirs.
        </p>

        <ul className="flex flex-wrap gap-2">
          {groups.map((group) => (
            <li key={group} className="chip">
              {group}
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
