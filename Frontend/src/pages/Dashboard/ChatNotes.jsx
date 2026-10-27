import {
  BTN_PRIMARY,
  BTN_QUIET,
  Panel,
  SectionLabel,
  SendIcon,
  cx,
} from './ui.jsx'

const CHAT_FIELD =
  'min-w-0 flex-1 rounded-xl border border-line bg-canvas/60 px-3 py-2 text-[0.84rem] text-ink placeholder:text-dim outline-none transition focus:border-amber/60 focus:ring-4 focus:ring-amber/10'

const quickPrompts = [
  'What should I focus on next?',
  'Why is the lab report at risk?',
  'Is my workload too heavy?',
  'Re-plan my week',
]

export function ChatSection({
  messages,
  chatInput,
  onChatInput,
  onSend,
  onAsk,
  logRef,
}) {
  return (
    <Panel id="sec-chat" title="Planner chat" hint="AI helper">
      <div
        ref={logRef}
        role="log"
        aria-live="polite"
        aria-label="Planner conversation"
        className="ffd-chat-log h-[250px] space-y-2.5 overflow-y-auto pr-1"
      >
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={cx(
              'max-w-[92%] rounded-xl px-3.5 py-2.5 text-[0.8rem] leading-relaxed',
              message.role === 'user'
                ? 'ml-auto rounded-tr-sm bg-amber text-[#171205]'
                : 'mr-auto rounded-tl-sm border border-line bg-deck text-ink',
            )}
          >
            {message.text}
          </div>
        ))}
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5">
        {quickPrompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onAsk(prompt)}
            className="min-h-[26px] rounded-full border border-line px-3 py-1 text-[0.68rem] font-semibold text-dim transition hover:border-amber/50 hover:text-amber"
          >
            {prompt}
          </button>
        ))}
      </div>

      <form className="mt-3 flex gap-2" onSubmit={onSend} aria-label="Ask the planner">
        <label htmlFor="ffd-chat-input" className="sr-only">
          Message the planner
        </label>
        <input
          id="ffd-chat-input"
          value={chatInput}
          onChange={(e) => onChatInput(e.target.value)}
          placeholder="Ask about your week..."
          autoComplete="off"
          maxLength={160}
          className={CHAT_FIELD}
        />
        <button type="submit" className={BTN_PRIMARY} aria-label="Send message">
          <SendIcon className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Send</span>
        </button>
      </form>

      <p className="mt-2 font-mono text-[0.56rem] tracking-[0.1em] text-dim uppercase">
        Local demo · replies are rule-based
      </p>
    </Panel>
  )
}

export function NotificationsSection({ notes, read, unread, onRead, onMarkAll }) {
  return (
    <Panel
      id="sec-notes"
      title="Notifications"
      hint={unread === 0 ? 'All read' : `${unread} unread`}
      action={
        <button
          type="button"
          className={BTN_QUIET}
          onClick={onMarkAll}
          disabled={unread === 0}
        >
          Mark all read
        </button>
      }
    >
      <ul>
        {notes.map((note) => {
          const isRead = Boolean(read[note.id])
          const label = `${note.lead ? `${note.lead} ` : ''}${note.text}`
          return (
            <li
              key={note.id}
              className="border-t border-line/60 py-1 first:border-t-0 first:pt-0 last:pb-0"
            >
              <button
                type="button"
                onClick={() => onRead(note.id)}
                aria-label={`${isRead ? 'Read' : 'Unread, mark as read'}: ${label}`}
                className="grid min-h-6 w-full grid-cols-[8px_minmax(0,1fr)] items-start gap-2.5 rounded py-1 text-left transition hover:bg-deck/35"
              >
                <span
                  aria-hidden="true"
                  className={cx(
                    'mt-1.5 h-2 w-2 rounded-full',
                    isRead ? 'border border-line bg-transparent' : 'bg-amber',
                  )}
                />
                <span className="min-w-0">
                  <span
                    className={cx(
                      'block text-[0.76rem] leading-snug',
                      isRead ? 'text-dim' : 'text-ink',
                    )}
                  >
                    {note.lead && (
                      <b className={cx('font-semibold', isRead ? 'text-dim' : 'text-ink')}>
                        {note.lead}{' '}
                      </b>
                    )}
                    {note.text}
                  </span>
                  <span className="mt-1 block font-mono text-[0.58rem] tracking-[0.1em] text-dim uppercase">
                    {note.when}
                  </span>
                </span>
              </button>
            </li>
          )
        })}
      </ul>
    </Panel>
  )
}
