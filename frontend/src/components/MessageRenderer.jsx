import React, { useState } from 'react';
import { User, Bot, Copy, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { toast } from 'react-hot-toast';

const MessageRenderer = ({ message }) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      toast.success('Copied!', { duration: 2000 });
    } catch (error) {
      toast.error('Failed to copy');
    }
  };

  const isDark = document.documentElement.classList.contains('theme-dark') || 
                document.body.classList.contains('theme-dark');

  if (message.type === 'user') {
    return (
      <div className="message-wrapper">
        <div className="user-message">
          {message.content}
        </div>
      </div>
    );
  }

  if (message.type === 'error') {
    return (
      <div className="message-wrapper">
        <div className="assistant-message">
          <div className="message-avatar">
            <AlertCircle size={20} />
          </div>
          <div className="message-content">
            <div style={{ color: '#ef4444', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={16} />
              {message.content}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="message-wrapper"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="assistant-message">
        <div className="message-avatar">
          <Bot size={20} />
        </div>
        <div className="message-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                if (!inline && match) {
                  return (
                    <div style={{ margin: '16px 0' }}>
                      <div className="message-content code-block-header">
                        <span>{match[1]}</span>
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(String(children).replace(/\n$/, ''));
                            toast.success('Copied!', { duration: 2000 });
                          }}
                          className="copy-btn"
                        >
                          <Copy size={16} />
                        </button>
                      </div>
                      <SyntaxHighlighter
                        style={isDark ? oneDark : oneLight}
                        language={match[1]}
                        PreTag="div"
                        customStyle={{
                          margin: 0,
                          borderTopLeftRadius: 0,
                          borderTopRightRadius: 0,
                          borderBottomLeftRadius: '8px',
                          borderBottomRightRadius: '8px'
                        }}
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    </div>
                  );
                }
                return (
                  <code className="inline-code" {...props}>
                    {children}
                  </code>
                );
              },
              p: ({ children }) => (
                <p style={{ margin: '8px 0', lineHeight: '1.6' }}>{children}</p>
              ),
              h1: ({ children }) => (
                <h1 style={{ margin: '16px 0 12px 0', fontSize: '1.5em', fontWeight: '600' }}>{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 style={{ margin: '16px 0 12px 0', fontSize: '1.3em', fontWeight: '600' }}>{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 style={{ margin: '16px 0 12px 0', fontSize: '1.1em', fontWeight: '600' }}>{children}</h3>
              ),
              ul: ({ children }) => (
                <ul style={{ margin: '8px 0', paddingLeft: '24px' }}>{children}</ul>
              ),
              ol: ({ children }) => (
                <ol style={{ margin: '8px 0', paddingLeft: '24px' }}>{children}</ol>
              ),
              li: ({ children }) => (
                <li style={{ margin: '4px 0' }}>{children}</li>
              ),
              blockquote: ({ children }) => (
                <blockquote style={{
                  borderLeft: '3px solid #10a37f',
                  paddingLeft: '16px',
                  margin: '12px 0',
                  fontStyle: 'italic',
                  color: isDark ? '#9ca3af' : '#6b7280'
                }}>
                  {children}
                </blockquote>
              ),
              table: ({ children }) => (
                <div style={{ overflowX: 'auto', margin: '16px 0' }}>
                  <table style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    border: `1px solid ${isDark ? '#444654' : '#e5e5e5'}`
                  }}>
                    {children}
                  </table>
                </div>
              ),
              th: ({ children }) => (
                <th style={{
                  padding: '8px 12px',
                  textAlign: 'left',
                  borderBottom: `1px solid ${isDark ? '#444654' : '#e5e5e5'}`,
                  background: isDark ? '#2a2b32' : '#f8f8f8',
                  fontWeight: '600'
                }}>
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td style={{
                  padding: '8px 12px',
                  borderBottom: `1px solid ${isDark ? '#444654' : '#e5e5e5'}`
                }}>
                  {children}
                </td>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>

          {isHovered && (
            <div style={{
              marginTop: '12px',
              paddingTop: '12px',
              borderTop: `1px solid ${isDark ? '#444654' : '#e5e5e5'}`,
              display: 'flex',
              justifyContent: 'flex-end'
            }}>
              <button
                onClick={handleCopy}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: isDark ? '#c5c5d2' : '#565869',
                  cursor: 'pointer',
                  padding: '4px',
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.1s ease'
                }}
                onMouseEnter={(e) => e.target.style.background = isDark ? '#2a2b32' : '#f0f0f0'}
                onMouseLeave={(e) => e.target.style.background = 'transparent'}
                title="Copy message"
              >
                <Copy size={16} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageRenderer;