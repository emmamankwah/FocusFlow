import { apiPost } from '@/lib/api'

// Older messages are dropped so the request stays small.
const MAX_HISTORY = 20
const MAX_CONTEXT = 4000

// The UI stores { role: 'user' | 'ai', text }; the API expects
// { role: 'user' | 'assistant', content }.
export function toApiMessages(messages) {
  return messages
    .filter(
      (message) =>
        !message.error &&
        typeof message.text === 'string' &&
        message.text.trim(),
    )
    .slice(-MAX_HISTORY)
    .map((message) => ({
      role: message.role === 'ai' ? 'assistant' : 'user',
      content: message.text.trim(),
    }))
}

export function buildPlannerContext({
  dateLabel,
  score,
  restPlanned,
  pendingTasks = [],
  risks = [],
}) {
  const lines = [`Today: ${dateLabel}`, `Burnout score: ${score}/100`]
  if (restPlanned) lines.push('A rest day is already planned this week.')

  if (pendingTasks.length) {
    lines.push('', 'Remaining tasks:')
    for (const task of pendingTasks.slice(0, 12)) {
      lines.push(`- ${task.t} ${task.title} (${task.type}, ${task.dur} min)`)
    }
  }

  if (risks.length) {
    lines.push('', 'Deadline risk:')
    for (const risk of risks.slice(0, 6)) {
      lines.push(`- ${risk.n}: due ${risk.due}, ${risk.p}% risk. ${risk.why}`)
    }
  }

  return lines.join('\n').slice(0, MAX_CONTEXT)
}

export async function sendPlannerMessage(messages, context) {
  const data = await apiPost('/ai/chat', {
    messages: toApiMessages(messages),
    context: context || null,
  })

  const reply = typeof data?.reply === 'string' ? data.reply.trim() : ''
  if (!reply) throw new Error('The assistant returned an empty reply.')
  return reply
}
