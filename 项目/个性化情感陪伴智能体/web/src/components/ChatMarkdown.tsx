import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/**
 * 助手气泡内 Markdown（GFM：列表、表格、任务列表、删除线等）。
 * react-markdown 默认不执行 HTML，适合展示模型输出。
 */
export function ChatMarkdown({ content }: { content: string }) {
  return (
    <div className="chat-md text-[var(--text)]">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          ul: ({ children }) => <ul className="mb-2 list-disc pl-5 last:mb-0">{children}</ul>,
          ol: ({ children }) => <ol className="mb-2 list-decimal pl-5 last:mb-0">{children}</ol>,
          li: ({ children }) => <li className="mb-0.5">{children}</li>,
          h1: ({ children }) => <h3 className="mb-2 mt-3 text-base font-semibold first:mt-0">{children}</h3>,
          h2: ({ children }) => <h3 className="mb-2 mt-3 text-base font-semibold first:mt-0">{children}</h3>,
          h3: ({ children }) => <h4 className="mb-1 mt-2 text-sm font-semibold first:mt-0">{children}</h4>,
          blockquote: ({ children }) => (
            <blockquote className="my-2 border-l-2 border-[var(--accent)]/50 pl-3 text-[var(--text-muted)]">
              {children}
            </blockquote>
          ),
          code: ({ className, children, ...props }) => {
            const inline = !className
            if (inline) {
              return (
                <code className="rounded bg-[color-mix(in_oklab,var(--border)_40%,var(--surface))] px-1 py-0.5 font-mono text-[0.9em]" {...props}>
                  {children}
                </code>
              )
            }
            return (
              <code className={className} {...props}>
                {children}
              </code>
            )
          },
          pre: ({ children }) => (
            <pre className="my-2 max-h-64 overflow-auto rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3 font-mono text-[12px] leading-relaxed">
              {children}
            </pre>
          ),
          a: ({ href, children }) => (
            <a href={href} className="text-[var(--accent)] underline underline-offset-2 hover:opacity-90" target="_blank" rel="noreferrer noopener">
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="my-2 max-w-full overflow-x-auto">
              <table className="min-w-full border-collapse border border-[var(--border)] text-xs">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border border-[var(--border)] bg-[var(--surface)] px-2 py-1 text-left font-medium">{children}</th>
          ),
          td: ({ children }) => <td className="border border-[var(--border)] px-2 py-1">{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
