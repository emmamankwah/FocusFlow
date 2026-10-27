import { WEEKLY_GOAL_HOURS, riskLevel, riskStyles } from './data.js'
import {
  BTN_PRIMARY,
  BTN_QUIET,
  CheckIcon,
  Panel,
  SectionLabel,
  cx,
} from './ui.jsx'

export function SuggestionsSection({ suggestions, sugs, onSuggestion }) {
  const visible = suggestions.filter((s) => sugs[s.id] !== 'no')

  return (
    <Panel id="sec-ai" title="Suggestions" hint="AI planner">
      {visible.length === 0 ? (
        <p className="rounded-xl border border-dashed border-line bg-deck/40 px-3 py-6 text-center text-sm text-dim">
          You’re all caught up. New suggestions appear when your plan changes.
        </p>
      ) : (
        <div className="space-y-3">
          {visible.map((s) => {
            const isDone = sugs[s.id] === 'done'
            if (isDone) {
              return (
                <div
                  key={s.id}
                  className="rounded-xl border border-amber/20 bg-amber/[0.06] p-3.5"
                >
                  <div className="flex items-start gap-2.5">
                    <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-amber text-[#171205]">
                      <CheckIcon className="h-3 w-3" />
                    </span>
                    <div className="min-w-0">
                      <SectionLabel className="text-amber/85">Added to plan</SectionLabel>
                      <p className="mt-1 text-[0.82rem] leading-snug font-semibold text-ink">
                        {s.h}
                      </p>
                      <p className="mt-1 text-[0.72rem] leading-snug text-dim">{s.ok}</p>
                    </div>
                  </div>
                </div>
              )
            }

            return (
              <div
                key={s.id}
                className="relative overflow-hidden rounded-xl border border-line bg-deck/45 p-3.5 pl-4"
              >
                <span
                  aria-hidden="true"
                  className="absolute top-3 bottom-3 left-0 w-0.5 rounded-full bg-amber"
                />
                <SectionLabel>Suggested block</SectionLabel>
                <p className="mt-1.5 text-[0.82rem] leading-snug font-semibold text-ink">
                  {s.h}
                </p>
                <p className="mt-1 text-[0.72rem] leading-snug text-dim">{s.p}</p>
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    className={BTN_PRIMARY}
                    onClick={() => onSuggestion(s.id, 'done')}
                  >
                    {s.yes}
                  </button>
                  <button
                    type="button"
                    className={BTN_QUIET}
                    onClick={() => onSuggestion(s.id, 'no')}
                  >
                    Not now
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </Panel>
  )
}

export function DeadlinesSection({ risks }) {
  const orderedRisks = [...risks].sort((a, b) => b.p - a.p)

  return (
    <Panel id="sec-deadlines" title="Deadlines" hint="Ordered by risk">
      <ul>
        {orderedRisks.map((risk, index) => {
          const tone = riskStyles[risk.level]
          return (
            <li
              key={risk.n}
              className={cx(
                'border-t border-line/60 py-3 first:border-t-0 first:pt-0 last:pb-0',
                index === 0 && 'pt-0',
              )}
            >
              <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-1.5">
                <p className="min-w-0 text-[0.82rem] leading-snug font-semibold text-ink">
                  {risk.n}
                </p>
                <span
                  className={cx(
                    'inline-flex shrink-0 rounded-[3px] border px-1.5 py-0.5 font-mono text-[0.56rem] tracking-[0.08em] uppercase',
                    tone.pill,
                  )}
                >
                  {risk.label}
                </span>
              </div>
              <div className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[0.64rem] text-dim">
                <span>{risk.due}</span>
                <span aria-hidden="true">·</span>
                <span>{risk.p}% risk</span>
              </div>
              <div className="mt-2 h-1 overflow-hidden rounded-full bg-deck">
                <div
                  className={cx('h-full rounded-full', tone.bar)}
                  style={{ width: `${risk.p}%` }}
                />
              </div>
              <p className="mt-1.5 text-[0.68rem] leading-snug text-dim">{risk.why}</p>
            </li>
          )
        })}
      </ul>
    </Panel>
  )
}

const GAUGE_LEN = Math.PI * 100

export function WellbeingSection({ score, restPlanned }) {
  const level = riskLevel(score)
  const color = {
    high: 'var(--color-coral)',
    med: 'var(--color-amber)',
    low: 'var(--color-cyan)',
  }[level]
  const label = { high: 'High', med: 'Moderate', low: 'Low' }[level]
  const dash = (GAUGE_LEN * score) / 100

  return (
    <Panel id="sec-wellbeing" title="Wellbeing" hint="Lower is better">
      <div
        role="img"
        aria-label={`Burnout score ${score} out of 100, ${label.toLowerCase()}`}
        className="mx-auto w-full max-w-[250px]"
      >
        <div className="relative">
          <svg viewBox="0 0 240 132" className="h-auto w-full" aria-hidden="true">
            <path
              d="M20 120A100 100 0 0 1 220 120"
              fill="none"
              stroke="var(--color-line)"
              strokeWidth="12"
              strokeLinecap="round"
            />
            <path
              className="ffd-gauge-arc"
              d="M20 120A100 100 0 0 1 220 120"
              fill="none"
              stroke={color}
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${dash} ${GAUGE_LEN}`}
            />
          </svg>
          <div className="absolute inset-x-0 bottom-0 text-center">
            <div className="ffd-nums font-grotesk text-[2.35rem] leading-none font-bold tracking-[-0.04em] text-ink">
              {score}
            </div>
            <div
              className="mt-1 font-mono text-[0.56rem] font-medium tracking-[0.18em] uppercase"
              style={{ color }}
            >
              {label}
            </div>
          </div>
        </div>
      </div>

      <ul className="mt-4 space-y-2 border-t border-line/60 pt-4 text-[0.76rem] leading-snug text-dim">
        <li className="flex gap-2">
          <span
            aria-hidden="true"
            className={cx(
              'mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full',
              restPlanned ? 'bg-cyan' : 'bg-amber',
            )}
          />
          <span>
            {restPlanned
              ? 'Rest day planned after six study days'
              : 'No full rest day in the last six days'}
          </span>
        </li>
        <li className="flex gap-2">
          <span aria-hidden="true" className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber" />
          <span>Two late nights (after 23:00) this week</span>
        </li>
        <li className="flex gap-2">
          <span aria-hidden="true" className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan" />
          <span>7.5 h average sleep</span>
        </li>
      </ul>
    </Panel>
  )
}

const CHART_W = 400
const CHART_H = 190
const CHART_L = 26
const CHART_R = 8
const CHART_T = 16
const CHART_B = 28
const CHART_MAX = 5
const GOAL = 4
const PLOT_W = CHART_W - CHART_L - CHART_R
const PLOT_H = CHART_H - CHART_T - CHART_B
const SLOT = PLOT_W / 7
const BAR_W = 18

function chartY(value) {
  return CHART_T + PLOT_H * (1 - value / CHART_MAX)
}

export function ProgressSection({ chart, total, average }) {
  const weeklyPct = (total / WEEKLY_GOAL_HOURS) * 100
  const goalY = chartY(GOAL)

  return (
    <Panel id="sec-progress" title="Progress" hint="Past 7 days">
      <div className="flex flex-wrap items-end gap-x-8 gap-y-2">
        <div>
          <SectionLabel>Total focus</SectionLabel>
          <div className="mt-1 font-grotesk text-[1.65rem] leading-none font-bold tracking-[-0.02em] text-ink">
            {total.toFixed(1)} h
          </div>
        </div>
        <div>
          <SectionLabel>Daily average</SectionLabel>
          <div className="mt-1 font-grotesk text-[1.65rem] leading-none font-bold tracking-[-0.02em] text-ink">
            {average.toFixed(1)} h
          </div>
        </div>
      </div>

      <div className="ff-chart-wrap ffd-chart-wrap mt-4 overflow-x-auto pb-1">
        <svg
          viewBox={`0 0 ${CHART_W} ${CHART_H}`}
          className="ffd-chart h-auto w-full min-w-[300px]"
          role="img"
          aria-label={`Focus hours for the past seven days: ${chart
            .map((day) => `${day.label} ${day.hours} hours`)
            .join(', ')}`}
        >
          {[0, 1, 2, 3, 4, 5].map((value) => (
            <line
              key={value}
              className="ffd-chart-grid"
              x1={CHART_L}
              y1={chartY(value)}
              x2={CHART_W - CHART_R}
              y2={chartY(value)}
            />
          ))}
          {[0, 2, 4].map((value) => (
            <text
              key={value}
              className="ffd-chart-label"
              x={CHART_L - 7}
              y={chartY(value) + 3}
              textAnchor="end"
            >
              {value}
            </text>
          ))}

          <line
            className="ffd-chart-goal"
            x1={CHART_L}
            y1={goalY}
            x2={CHART_W - CHART_R}
            y2={goalY}
          />
          <text className="ffd-chart-goal-label" x={CHART_L + 2} y={goalY - 4}>
            GOAL 4H
          </text>

          {chart.map((day, index) => {
            const x = CHART_L + index * SLOT + (SLOT - BAR_W) / 2
            const y = chartY(day.hours)
            const height = CHART_T + PLOT_H - y
            const hitGoal = day.hours >= GOAL
            return (
              <g key={`${day.label}-${index}`}>
                <rect
                  x={x}
                  y={y}
                  width={BAR_W}
                  height={height}
                  rx="2"
                  fill="var(--color-amber)"
                  fillOpacity={hitGoal ? 1 : 0.18}
                  stroke="var(--color-amber)"
                  strokeWidth="1"
                />
                <text
                  className="ffd-chart-value"
                  x={x + BAR_W / 2}
                  y={y - 4}
                  textAnchor="middle"
                >
                  {day.hours}
                </text>
                <text
                  className="ffd-chart-label"
                  x={x + BAR_W / 2}
                  y={CHART_H - 8}
                  textAnchor="middle"
                >
                  {day.label}
                </text>
              </g>
            )
          })}
        </svg>
      </div>

      <div className="mt-3 border-t border-line/60 pt-3">
        <div className="flex items-baseline justify-between gap-3">
          <SectionLabel>Weekly focus goal</SectionLabel>
          <span className="font-mono text-[0.68rem] text-dim">
            {total.toFixed(1)} / {WEEKLY_GOAL_HOURS} h
          </span>
        </div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-deck">
          <div
            className="h-full rounded-full bg-amber"
            style={{ width: `${Math.min(100, weeklyPct)}%` }}
          />
        </div>
      </div>
    </Panel>
  )
}
