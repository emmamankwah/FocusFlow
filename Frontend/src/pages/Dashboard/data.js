export const STORAGE_KEY = 'focusflow-dashboard-v1'
export const FOCUS_GOAL_HOURS = 4
export const WEEKLY_GOAL_HOURS = 25

export const sections = [
  { id: 'sec-motivation', label: 'Motivation' },
  { id: 'sec-overview', label: 'Overview' },
  { id: 'sec-modules', label: 'Modules' },
  { id: 'sec-work', label: 'Work Inbox' },
  { id: 'sec-focus', label: 'Today' },
  { id: 'sec-ai', label: 'Suggestions' },
  { id: 'sec-deadlines', label: 'Deadlines' },
  { id: 'sec-wellbeing', label: 'Wellbeing' },
  { id: 'sec-progress', label: 'Progress' },
  { id: 'sec-chat', label: 'Planner chat' },
  { id: 'sec-notes', label: 'Notifications' },
]

export const baseTasks = [
  { id: 'b1', t: '08:30', dur: 90, title: 'MATH 201 Linear Algebra lecture', meta: 'Room B14', type: 'class' },
  { id: 'b2', t: '10:00', dur: 90, title: 'Write CHEM 230 lab report: results', meta: 'Best focus window', type: 'focus', sub: 'Your highest-risk deadline. This block lowers the risk the most.' },
  { id: 'b3', t: '12:30', dur: 60, title: 'Lunch and a walk', meta: 'Break', type: 'rest' },
  { id: 'b4', t: '14:00', dur: 120, title: 'CS 140 programming lab', meta: 'Lab 3', type: 'class' },
  { id: 'b5', t: '16:30', dur: 45, title: 'Read HIST 210 chapters 6 and 7', meta: 'Essay prep', type: 'focus', sub: 'Prepares you for the essay outline due next week.' },
  { id: 'b6', t: '19:30', dur: 60, title: 'Write CHEM 230 lab report: discussion', meta: 'Second block for the report', type: 'focus', sub: 'Finishing this section brings the report back on track.' },
  { id: 'b7', t: '21:00', dur: 30, title: 'Wind down, no study after this', meta: 'Protects your sleep', type: 'rest' },
]

export const typeName = { class: 'Class', focus: 'Focus', rest: 'Rest' }

const deadlinesSeed = [
  { n: 'CHEM 230 lab report', off: 2, p: 71, why: 'Needs about 5 h more and only 3 h of free time is left.' },
  { n: 'CS 140 project milestone 2', off: 3, p: 48, why: 'Starts after the lab report. A missed block pushes it into the weekend.' },
  { n: 'HIST 210 essay outline', off: 6, p: 44, why: 'Two of four chapters read. Today’s reading block covers the rest.' },
  { n: 'MATH 201 Problem Set 7', off: 8, p: 18, why: 'On track. Starts later this week.' },
]

const chartValues = [2.5, 4.2, 3.1, 1.6, 2.4, 3.2, 2.8]

export const riskStyles = {
  high: { pill: 'border-coral/25 bg-coral/15 text-coral', bar: 'bg-coral' },
  med: { pill: 'border-amber/25 bg-amber/15 text-amber', bar: 'bg-amber' },
  low: { pill: 'border-cyan/25 bg-cyan/15 text-cyan', bar: 'bg-cyan' },
}

export function addDays(date, n) {
  const d = new Date(date)
  d.setDate(d.getDate() + n)
  return d
}

export function dayKey(date = new Date()) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export function fmtDate(date) {
  return date.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' })
}

export function fmtLongDate(date) {
  return date.toLocaleDateString('en-GB', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export function fmtWeekday(date) {
  return date.toLocaleDateString('en-GB', { weekday: 'short' })
}

export function greeting(date = new Date()) {
  const h = date.getHours()
  return `${h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening'}, Ama`
}

export function formatClock(totalSeconds) {
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

export function riskLevel(p) {
  return p >= 60 ? 'high' : p >= 35 ? 'med' : 'low'
}

export function riskLabel(p) {
  return { high: 'High risk', med: 'Medium risk', low: 'Low risk' }[riskLevel(p)]
}

export function loadBoard(date = new Date()) {
  const fresh = { done: {}, custom: [], sugs: {}, read: {}, extraMin: 0, timed: {}, workQueue: [] }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return fresh
    const saved = JSON.parse(raw)
    if (!saved || typeof saved !== 'object') return fresh
    if (saved.day === dayKey(date)) {
      return {
        done: saved.done && typeof saved.done === 'object' ? saved.done : {},
        custom: Array.isArray(saved.custom) ? saved.custom : [],
        sugs: saved.sugs && typeof saved.sugs === 'object' ? saved.sugs : {},
        read: saved.read && typeof saved.read === 'object' ? saved.read : {},
        extraMin: Number.isFinite(saved.extraMin) ? saved.extraMin : 0,
        timed: saved.timed && typeof saved.timed === 'object' ? saved.timed : {},
        workQueue: Array.isArray(saved.workQueue) ? saved.workQueue : [],
      }
    }
    return {
      ...fresh,
      sugs: saved.sugs && typeof saved.sugs === 'object' ? saved.sugs : {},
      read: saved.read && typeof saved.read === 'object' ? saved.read : {},
      workQueue: Array.isArray(saved.workQueue) ? saved.workQueue : [],
    }
  } catch {
    return fresh
  }
}

export function saveBoard(board, date = new Date()) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ day: dayKey(date), ...board }))
  } catch {
    // Local-only demo data; storage can be unavailable.
  }
}

export function makeSuggestions(date = new Date()) {
  return [
    {
      id: 's1',
      h: `Add a 90 min block on ${fmtDate(addDays(date, 1))} at 10:00 for the CHEM 230 lab report`,
      p: 'Lowers the deadline risk from 71% to about 38%.',
      yes: 'Add to my plan',
      ok: 'Block added. Lab report risk is now about 38%.',
    },
    {
      id: 's2',
      h: `Keep ${fmtDate(addDays(date, 5))} free of study`,
      p: 'You have studied every day for the last six days. A rest day lowers your burnout score from 41 to about 33.',
      yes: 'Keep it free',
      ok: 'Rest day saved. Burnout score is now about 33.',
    },
  ]
}

export function getRisks(date = new Date(), sugs = {}) {
  return deadlinesSeed.map((d, i) => {
    let p = d.p
    let why = d.why
    if (i === 0 && sugs.s1 === 'done') {
      p = 38
      why = 'Extra block added. You now have enough time before the deadline.'
    }
    return {
      ...d,
      p,
      why,
      due: fmtDate(addDays(date, d.off)),
      level: riskLevel(p),
      label: riskLabel(p),
    }
  })
}

function lastSunday(date) {
  const d = new Date(date)
  const day = d.getDay()
  d.setDate(d.getDate() - (day === 0 ? 7 : day))
  return d
}

export function makeNotes(date = new Date()) {
  return [
    { id: 'n1', lead: 'CHEM 230 lab report is now high risk.', text: 'Open suggestions to add an extra block.', when: 'Yesterday' },
    { id: 'n2', text: 'Your best focus window is 10:00 to 12:00. Hard tasks are placed there.', when: 'Yesterday' },
    { id: 'n3', text: 'You are 5.2 h away from 25 focus hours this week.', when: 'Yesterday' },
    { id: 'n4', text: 'MATH 201 Problem Set 6 was submitted on time.', when: fmtWeekday(lastSunday(date)) },
  ]
}

export function getChartData(date = new Date()) {
  return chartValues.map((hours, i) => {
    const d = addDays(date, i - 7)
    return { hours, label: fmtWeekday(d) }
  })
}

export function chatReply(question, { firstFocus, score, labRisk, restPlanned }) {
  const q = question.toLowerCase()

  if (/next|first|focus on|start/.test(q)) {
    return firstFocus
      ? `${firstFocus.title} at ${firstFocus.t} (${firstFocus.dur} min). It is the next focus block in your plan.`
      : 'Your focus blocks are done for today. A short rest will help tomorrow’s sessions.'
  }

  if (/risk|lab|chem|behind|deadline/.test(q)) {
    if (labRisk?.p <= 40) {
      return 'The extra block is already in your plan. Lab report risk is now about 38%, so you are back on track.'
    }
    return 'The lab report needs about 5 h and only 3 h are free before it is due. Accepting the suggested 90 min block lowers the risk from 71% to about 38%.'
  }

  if (/heavy|too much|burn|tired|rest|sleep|workload/.test(q)) {
    const level = score >= 65 ? 'high' : score >= 35 ? 'moderate' : 'low'
    return `Your burnout score is ${score}, which is ${level}. ${
      restPlanned ? 'A rest day is already on your plan.' : 'A free rest day would help.'
    } You have also worked past 23:00 twice this week.`
  }

  if (/re-?plan/.test(q)) {
    return 'I rebalanced your week around the lab report and kept evenings light. Check the suggestions and accept what suits you.'
  }

  return 'I can help with your plan, deadlines and workload. Try asking what to focus on next.'
}
