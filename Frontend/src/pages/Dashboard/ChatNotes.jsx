import { useEffect, useMemo, useRef, useState } from 'react'
import {
  BTN_PRIMARY,
  BTN_QUIET,
  Panel,
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

const CAPABILITIES = [
  'Plan your day and week around deadlines',
  'Explain risks and suggest fixes',
  'Balance workload and burnout',
  'Suggest free slots and focus blocks',
  'Answer questions about your current plan',
]

function PaperclipIcon({ className = '' }) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" className={className} fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6">
      <path d="M11.2 7.3 6.9 11.6a2 2 0 0 1-2.8-2.8L8.4 4.5a3 3 0 0 1 4.2 4.2L8.1 13a4 4 0 0 1-5.7-5.7l4.7-4.7" />
    </svg>
  )
}

function MicIcon({ className = '' }) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" className={className} fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6">
      <rect x="6" y="2" width="4" height="7" rx="2" />
      <path d="M4 7a4 4 0 0 0 8 0M8 11v3" />
    </svg>
  )
}

function ImageIcon({ className = '' }) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" className={className} fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6">
      <rect x="2.5" y="3" width="11" height="10" rx="1.6" />
      <circle cx="6" cy="6.5" r="1" />
      <path d="m2.5 11 3-3 2.2 2.2 2.8-2.8 3 3" />
    </svg>
  )
}

function FileIcon({ className = '' }) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" className={className} fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6">
      <path d="M9 2H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V5Z" />
      <path d="M9 2v3h3" />
    </svg>
  )
}

function PlusIcon({ className = '' }) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" className={className} fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8">
      <path d="M8 3v10M3 8h10" />
    </svg>
  )
}

function SearchIcon({ className = '' }) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" className={className} fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6">
      <circle cx="7" cy="7" r="4" />
      <path d="m10.5 10.5 3 3" />
    </svg>
  )
}

function GlobeIcon({ className = '' }) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" className={className} fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6">
      <circle cx="8" cy="8" r="5.5" />
      <path d="M2.5 8h11M8 2.5a12 12 0 0 1 0 11M8 2.5a12 12 0 0 0 0 11" />
    </svg>
  )
}

function ListIcon({ className = '' }) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" className={className} fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.6">
      <path d="M5 4h8M5 8h8M5 12h8M3 4h.01M3 8h.01M3 12h.01" />
    </svg>
  )
}

function TypingBubble() {
  return (
    <div
      role="status"
      aria-label="Assistant is thinking"
      className="mr-auto flex w-fit items-center gap-1.5 rounded-xl rounded-tl-sm border border-line bg-deck px-3.5 py-2.5"
    >
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-dim" />
      <span
        className="h-1.5 w-1.5 animate-bounce rounded-full bg-dim"
        style={{ animationDelay: '120ms' }}
      />
      <span
        className="h-1.5 w-1.5 animate-bounce rounded-full bg-dim"
        style={{ animationDelay: '240ms' }}
      />
    </div>
  )
}

export function ChatSection({
  messages,
  chatInput,
  onChatInput,
  onSend,
  onAsk,
  logRef,
  variant = 'panel',
  pending = false,
  onAttach,
  onVoice,
  onDeepSearch,
  onWebSearch,
  onSearchPriorities,
}) {
  const recent = useMemo(() => messages.slice(-6), [messages])
  const [attachMenuOpen, setAttachMenuOpen] = useState(false)
  const attachMenuRef = useRef(null)
  const attachButtonRef = useRef(null)

  useEffect(() => {
    if (typeof document === 'undefined') return undefined
    const onKeyDown = (event) => {
      if (event.key === 'Escape') {
        setAttachMenuOpen(false)
      }
    }
    const onPointerDown = (event) => {
      if (
        attachMenuRef.current &&
        !attachMenuRef.current.contains(event.target) &&
        attachButtonRef.current &&
        !attachButtonRef.current.contains(event.target)
      ) {
        setAttachMenuOpen(false)
      }
    }
    document.addEventListener('keydown', onKeyDown)
    document.addEventListener('pointerdown', onPointerDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.removeEventListener('pointerdown', onPointerDown)
    }
  }, [])

  if (variant === 'full') {
    return (
      <div className="flex min-h-0 flex-1 flex-col">
        <div className="grid min-h-0 flex-1 gap-4 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
          <Panel title="Conversation" hint="Planner chat" className="flex min-h-0 flex-col">
            <div
              ref={logRef}
              role="log"
              aria-live="polite"
              aria-label="Planner conversation"
              className="ffd-chat-log min-h-0 flex-1 space-y-2.5 overflow-y-auto pr-1"
            >
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={cx(
                    'max-w-[92%] rounded-xl px-3.5 py-2.5 text-[0.84rem] leading-relaxed sm:max-w-[78%]',
                    message.role === 'user'
                      ? 'ml-auto rounded-tr-sm bg-amber text-[#171205]'
                      : 'mr-auto rounded-tl-sm border border-line bg-deck text-ink',
                  )}
                >
                  {message.text}
                </div>
              ))}
              {pending && <TypingBubble />}
            </div>

            <form className="mt-3 flex shrink-0 flex-wrap items-center gap-2" onSubmit={onSend} aria-label="Ask the planner">
              <div className="flex min-w-0 flex-1 items-center gap-1 rounded-xl border border-line bg-canvas/60 px-1.5 py-1">
                <div className="relative">
                  <button
                    ref={attachButtonRef}
                    type="button"
                    onClick={() => setAttachMenuOpen((o) => !o)}
                    aria-expanded={attachMenuOpen}
                    aria-haspopup="menu"
                    aria-label="Add files, images, documents, or search"
                    className="grid h-8 w-8 place-items-center rounded-lg text-dim transition hover:bg-deck/60 hover:text-ink"
                  >
                    <PlusIcon className="h-4 w-4" />
                  </button>
                  {attachMenuOpen && (
                    <div
                      ref={attachMenuRef}
                      role="menu"
                      aria-label="Add options"
                      className="absolute bottom-full left-0 z-40 mb-2 w-56 rounded-xl border border-line/80 bg-surface p-1 shadow-[0_24px_70px_-30px_rgba(0,0,0,0.95)]"
                    >
                      <button
                        type="button"
                        role="menuitem"
                        onClick={() => {
                          setAttachMenuOpen(false)
                          onAttach?.('image')
                        }}
                        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-[0.8rem] text-ink transition hover:bg-deck/60"
                      >
                        <ImageIcon className="h-4 w-4 text-amber" />
                        Add photos
                      </button>
                      <button
                        type="button"
                        role="menuitem"
                        onClick={() => {
                          setAttachMenuOpen(false)
                          onAttach?.('image')
                        }}
                        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-[0.8rem] text-ink transition hover:bg-deck/60"
                      >
                        <ImageIcon className="h-4 w-4 text-amber" />
                        Add images
                      </button>
                      <button
                        type="button"
                        role="menuitem"
                        onClick={() => {
                          setAttachMenuOpen(false)
                          onAttach?.('file')
                        }}
                        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-[0.8rem] text-ink transition hover:bg-deck/60"
                      >
                        <FileIcon className="h-4 w-4 text-amber" />
                        Add files
                      </button>
                      <button
                        type="button"
                        role="menuitem"
                        onClick={() => {
                          setAttachMenuOpen(false)
                          onAttach?.('document')
                        }}
                        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-[0.8rem] text-ink transition hover:bg-deck/60"
                      >
                        <PaperclipIcon className="h-4 w-4 text-amber" />
                        Add documents
                      </button>
                      <div className="my-1 border-t border-line/60" />
                      <button
                        type="button"
                        role="menuitem"
                        onClick={() => {
                          setAttachMenuOpen(false)
                          onDeepSearch?.()
                        }}
                        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-[0.8rem] text-ink transition hover:bg-deck/60"
                      >
                        <SearchIcon className="h-4 w-4 text-amber" />
                        Deep search
                      </button>
                      <button
                        type="button"
                        role="menuitem"
                        onClick={() => {
                          setAttachMenuOpen(false)
                          onWebSearch?.()
                        }}
                        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-[0.8rem] text-ink transition hover:bg-deck/60"
                      >
                        <GlobeIcon className="h-4 w-4 text-amber" />
                        Web search
                      </button>
                      <button
                        type="button"
                        role="menuitem"
                        onClick={() => {
                          setAttachMenuOpen(false)
                          onSearchPriorities?.()
                        }}
                        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-[0.8rem] text-ink transition hover:bg-deck/60"
                      >
                        <ListIcon className="h-4 w-4 text-amber" />
                        Search priorities
                      </button>
                    </div>
                  )}
                </div>
                <label htmlFor="ffd-chat-input-full" className="sr-only">
                  Message the planner
                </label>
                <input
                  id="ffd-chat-input-full"
                  value={chatInput}
                  onChange={(e) => onChatInput(e.target.value)}
                  placeholder={pending ? 'Thinking…' : 'Ask about your week, deadlines, or workload...'}
                  autoComplete="off"
                  maxLength={220}
                  disabled={pending}
                  className="min-w-0 flex-1 border-0 bg-transparent px-2 py-1 text-[0.84rem] text-ink placeholder:text-dim outline-none disabled:cursor-not-allowed"
                />
                <button
                  type="button"
                  onClick={() => onVoice?.()}
                  aria-label="Use voice input"
                  className="grid h-8 w-8 place-items-center rounded-lg text-dim transition hover:bg-deck/60 hover:text-ink"
                >
                  <MicIcon className="h-4 w-4" />
                </button>
              </div>
              <button type="submit" className={BTN_PRIMARY} aria-label="Send message" disabled={pending}>
                <SendIcon className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </form>
            <p className="mt-1.5 shrink-0 font-mono text-[0.54rem] tracking-[0.1em] text-dim uppercase">
              Attach · Photos · Files · Documents · Deep search · Web search · Priorities · Voice (demo)
            </p>
          </Panel>

          <div className="hidden min-h-0 flex-col gap-4 lg:flex">
            <Panel title="Quick prompts" hint="Get started" className="shrink-0">
              <div className="flex flex-wrap gap-1.5">
                {quickPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => onAsk(prompt)}
                    disabled={pending}
                    className="min-h-[28px] rounded-full border border-line px-3 py-1 text-[0.72rem] font-semibold text-dim transition hover:border-amber/50 hover:text-amber disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </Panel>

            <Panel title="What it can do" hint="Capabilities" className="shrink-0">
              <ul className="space-y-2">
                {CAPABILITIES.map((item) => (
                  <li key={item} className="flex items-start gap-2 text-[0.8rem] text-ink">
                    <span className="mt-1 h-1.5 w-1.5 rounded-full bg-amber" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </Panel>

            <Panel title="Recent" hint="Latest messages" className="flex min-h-0 flex-1 flex-col">
              <div className="ffd-chat-log min-h-0 flex-1 space-y-2 overflow-y-auto pr-1">
                {recent.length === 0 && <p className="text-[0.8rem] text-dim">No messages yet.</p>}
                {recent.map((message, index) => (
                  <div
                    key={`recent-${index}`}
                    className={cx(
                      'rounded-xl px-3 py-2 text-[0.76rem] leading-relaxed',
                      message.role === 'user'
                        ? 'border border-amber/30 bg-amber/10 text-ink'
                        : 'border border-line bg-deck/40 text-ink',
                    )}
                  >
                    <div className="mb-1 font-mono text-[0.54rem] tracking-[0.12em] uppercase text-dim">
                      {message.role === 'user' ? 'You' : 'FocusFlow AI'}
                    </div>
                    <div className="truncate">{message.text}</div>
                  </div>
                ))}
              </div>
            </Panel>
          </div>
        </div>
      </div>
    )
  }

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
        {pending && <TypingBubble />}
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5">
        {quickPrompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onAsk(prompt)}
            disabled={pending}
            className="min-h-[26px] rounded-full border border-line px-3 py-1 text-[0.68rem] font-semibold text-dim transition hover:border-amber/50 hover:text-amber disabled:cursor-not-allowed disabled:opacity-50"
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
          placeholder={pending ? 'Thinking…' : 'Ask about your week...'}
          autoComplete="off"
          maxLength={160}
          disabled={pending}
          className={`${CHAT_FIELD} disabled:cursor-not-allowed`}
        />
        <button type="submit" className={BTN_PRIMARY} aria-label="Send message" disabled={pending}>
          <SendIcon className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Send</span>
        </button>
      </form>

      <p className="mt-2 font-mono text-[0.56rem] tracking-[0.1em] text-dim uppercase">
        Replies use your planner context
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
