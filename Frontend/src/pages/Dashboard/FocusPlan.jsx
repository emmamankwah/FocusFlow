import { formatClock, typeName } from './data.js'
import { BTN, BTN_PRIMARY, CheckIcon, Panel, SectionLabel, cx } from './ui.jsx'

const RING_R = 66
const RING_C = 2 * Math.PI * RING_R

export function FocusSection({
  heroTask,
  durationMin,
  remainSec,
  running,
  onDuration,
  onStartPause,
  onReset,
}) {
  const totalSec = durationMin * 60
  const fresh = remainSec === totalSec
  const status = running ? 'Focusing' : remainSec === 0 ? 'Done' : fresh ? 'Ready' : 'Paused'
  const action = running ? 'Pause' : remainSec === 0 || fresh ? 'Start session' : 'Resume'
  const offset = RING_C * (1 - Math.max(0, Math.min(1, remainSec / totalSec)))
  const sub = heroTask
    ? heroTask.sub || (heroTask.meta ? `${heroTask.meta}.` : 'Notifications pause while the timer runs.')
    : 'Add a focus block to plan another session, or take the rest of the day off.'

  return (
    <section
      id="sec-focus"
      aria-label="Focus session"
      className="ffd-section relative overflow-hidden rounded-2xl border border-amber/20 bg-surface p-5 shadow-[0_30px_90px_-50px_rgba(242,184,75,0.35)]"
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-gradient-to-br from-amber/[0.11] via-transparent to-transparent"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-24 -right-16 h-56 w-56 rounded-full bg-amber/10 blur-3xl"
      />
      <span
        aria-hidden="true"
        className="absolute inset-x-10 top-0 h-px bg-gradient-to-r from-transparent via-amber/70 to-transparent"
      />

      <div className="relative grid gap-5 lg:grid-cols-[minmax(0,1fr)_168px] lg:items-center">
        <div className="min-w-0">
          <SectionLabel className="text-amber/85">
            {heroTask ? `Focus block · ${heroTask.t} · ${heroTask.dur} min` : 'Focus'}
          </SectionLabel>
          <h2 className="mt-2 font-grotesk text-[1.3rem] leading-tight font-bold tracking-[-0.02em] text-ink sm:text-[1.45rem]">
            {heroTask ? heroTask.title : 'No focus blocks left today'}
          </h2>
          <p className="mt-2 max-w-xl text-[0.83rem] leading-relaxed text-dim">{sub}</p>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            {[25, 45, 60].map((mins) => (
              <button
                key={mins}
                type="button"
                aria-pressed={durationMin === mins}
                onClick={() => onDuration(mins)}
                className={cx(
                  'min-h-[26px] rounded-full border px-3 py-1 text-[0.72rem] font-semibold transition',
                  durationMin === mins
                    ? 'border-amber bg-amber text-[#171205]'
                    : 'border-line bg-surface text-dim hover:border-dim hover:text-ink',
                )}
              >
                {mins} min
              </button>
            ))}
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            <button
              type="button"
              className={BTN_PRIMARY}
              onClick={onStartPause}
              disabled={!heroTask}
              aria-label={`${action} focus timer`}
            >
              {action}
            </button>
            <button type="button" className={BTN} onClick={onReset}>
              Reset
            </button>
            <span className="font-mono text-[0.62rem] tracking-[0.1em] text-dim uppercase">
              Notifications pause while the timer runs
            </span>
          </div>
        </div>

        <div className="order-first mx-auto h-[150px] w-[150px] lg:order-last lg:mx-0">
          <div className="relative h-full w-full">
            <svg
              viewBox="0 0 150 150"
              className="-rotate-90"
              width="150"
              height="150"
              aria-hidden="true"
            >
              <circle
                cx="75"
                cy="75"
                r={RING_R}
                fill="none"
                stroke="var(--color-line)"
                strokeWidth="10"
              />
              <circle
                className="ffd-ring-arc"
                cx="75"
                cy="75"
                r={RING_R}
                fill="none"
                stroke="var(--color-amber)"
                strokeWidth="10"
                strokeLinecap="round"
                strokeDasharray={RING_C}
                strokeDashoffset={offset}
              />
            </svg>
            <div
              role="timer"
              aria-live="off"
              className="absolute inset-0 grid place-items-center text-center"
            >
              <div>
                <span className="ffd-nums block font-mono text-[1.72rem] leading-none font-medium text-ink">
                  {formatClock(remainSec)}
                </span>
                <small className="mt-1.5 block font-mono text-[0.56rem] font-medium tracking-[0.2em] text-dim uppercase">
                  {status}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

const FIELD =
  'w-full rounded-xl border border-line bg-canvas/60 px-3 py-2 text-[0.84rem] text-ink placeholder:text-dim outline-none transition focus:border-amber/60 focus:ring-4 focus:ring-amber/10'

const LABEL = 'mb-1 block font-mono text-[0.58rem] tracking-[0.14em] text-dim uppercase'

export function PlanSection({
  tasks,
  done,
  nextId,
  addOpen,
  form,
  onFormChange,
  onAdd,
  formError,
  onToggle,
  onRemove,
  titleRef,
  sectionRef,
}) {
  return (
    <div ref={sectionRef}>
      <Panel
        id="sec-today"
        title="Today’s plan"
        hint="Tick a block when it’s done"
      >
        {tasks.length === 0 ? (
          <p className="rounded-xl border border-dashed border-line bg-deck/40 px-3 py-6 text-center text-sm text-dim">
            Nothing planned yet. Add a block to start shaping today.
          </p>
        ) : (
          <ul className="ff-sched">
            {tasks.map((task) => {
              const isDone = Boolean(done[task.id])
              const isNext = task.id === nextId
              const tag = isNext ? 'Up next' : typeName[task.type] || 'Task'
              return (
                <li
                  key={task.id}
                  data-task-id={task.id}
                  className={cx(
                    'grid grid-cols-[26px_minmax(0,1fr)_auto] items-center gap-x-3 gap-y-1 py-3 sm:grid-cols-[26px_52px_minmax(0,1fr)_auto]',
                    isNext
                      ? 'rounded-xl border-t-0 bg-amber/[0.07]'
                      : 'border-t border-line/60 first:border-t-0',
                  )}
                >
                  <button
                    type="button"
                    data-task-id={task.id}
                    aria-pressed={isDone}
                    aria-label={`${isDone ? 'Mark not done' : 'Mark done'}: ${task.title}`}
                    onClick={() => onToggle(task.id)}
                    className={cx(
                      'grid h-6 w-6 place-items-center rounded-md border-2 transition duration-150',
                      isDone
                        ? 'border-amber bg-amber text-[#171205]'
                        : 'border-line bg-surface text-transparent hover:border-amber hover:text-amber/40',
                    )}
                  >
                    <CheckIcon className="h-3 w-3" />
                  </button>

                  <span className="hidden font-mono text-[0.68rem] text-dim sm:block">
                    {task.t}
                  </span>

                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                      <p
                        className={cx(
                          'text-[0.86rem] leading-snug font-semibold',
                          isDone
                            ? 'text-dim line-through decoration-line'
                            : 'text-ink',
                        )}
                      >
                        {task.title}
                      </p>
                      <span
                        className={cx(
                          'inline-flex items-center rounded-[3px] border px-1.5 py-0.5 font-mono text-[0.56rem] tracking-[0.08em] uppercase',
                          isNext
                            ? 'border-amber/30 bg-amber text-[#171205]'
                            : 'border-line bg-deck text-dim',
                        )}
                      >
                        {tag}
                      </span>
                    </div>
                    <p className="mt-0.5 text-[0.68rem] leading-snug text-dim">
                      <span className="sm:hidden">{task.t} · </span>
                      {task.dur} min · {task.meta}
                    </p>
                  </div>

                  {task.custom ? (
                    <button
                      type="button"
                      onClick={() => onRemove(task.id)}
                      className="min-h-6 rounded border border-transparent px-1.5 py-0.5 font-mono text-[0.58rem] tracking-[0.08em] text-dim uppercase transition hover:border-coral/30 hover:text-coral"
                      aria-label={`Remove ${task.title}`}
                    >
                      Remove
                    </button>
                  ) : (
                    <span aria-hidden="true" />
                  )}
                </li>
              )
            })}
          </ul>
        )}

        {addOpen && (
          <form
            id="ff-addform"
            aria-label="Add a task"
            onSubmit={onAdd}
            className="ffd-addform ff-addform mt-4 grid gap-3 rounded-xl border border-amber/20 bg-amber/[0.04] p-3.5 sm:grid-cols-3"
          >
            <div className="sm:col-span-3">
              <label htmlFor="ffd-task-title" className={LABEL}>
                Task name
              </label>
              <input
                id="ffd-task-title"
                ref={titleRef}
                value={form.title}
                onChange={(e) => onFormChange('title', e.target.value)}
                maxLength={80}
                autoComplete="off"
                placeholder="e.g. Draft the CHEM 230 conclusion"
                className={FIELD}
              />
            </div>

            <div>
              <label htmlFor="ffd-task-time" className={LABEL}>
                Start time
              </label>
              <input
                id="ffd-task-time"
                type="time"
                value={form.time}
                onChange={(e) => onFormChange('time', e.target.value)}
                className={FIELD}
              />
            </div>

            <div>
              <label htmlFor="ffd-task-dur" className={LABEL}>
                Length
              </label>
              <select
                id="ffd-task-dur"
                value={form.duration}
                onChange={(e) => onFormChange('duration', e.target.value)}
                className={cx(FIELD, '[color-scheme:dark]')}
              >
                <option value="25">25 min</option>
                <option value="45">45 min</option>
                <option value="60">60 min</option>
                <option value="90">90 min</option>
                <option value="120">120 min</option>
              </select>
            </div>

            <div>
              <label htmlFor="ffd-task-type" className={LABEL}>
                Type
              </label>
              <select
                id="ffd-task-type"
                value={form.type}
                onChange={(e) => onFormChange('type', e.target.value)}
                className={cx(FIELD, '[color-scheme:dark]')}
              >
                <option value="focus">Focus</option>
                <option value="class">Class</option>
                <option value="rest">Rest</option>
              </select>
            </div>

            <div className="flex flex-wrap items-center gap-2 sm:col-span-3">
              <button type="submit" className={BTN_PRIMARY}>
                Add task
              </button>
              {formError && (
                <p role="alert" className="text-[0.72rem] font-medium text-coral">
                  {formError}
                </p>
              )}
            </div>
          </form>
        )}
      </Panel>
    </div>
  )
}
