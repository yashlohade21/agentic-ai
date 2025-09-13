import React, { useState } from 'react';
import { User, Bot, Copy, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { toast } from 'react-hot-toast';

const MessageRenderer = ({ message }) => {
  const [isHovered, setIsHovered] = useState(false);

  // Ensure content is properly displayed without truncation
  React.useEffect(() => {
    // Component mounted, message content will be fully rendered
  }, [message]);

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
      <div className="message-wrapper" style={{
        width: '100%',
        marginBottom: '20px',
        display: 'flex',
        justifyContent: 'flex-end'
      }}>
        <div className="user-message" style={{
          background: isDark
            ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '12px 16px',
          borderRadius: '16px',
          maxWidth: '80%',
          minWidth: '0',
          fontSize: '15px',
          lineHeight: '1.6',
          boxShadow: '0 2px 12px rgba(102, 126, 234, 0.3)',
          wordWrap: 'break-word',
          overflowWrap: 'anywhere'
        }}>
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
      style={{
        width: '100%',
        marginBottom: '20px',
        padding: '0'
      }}
    >
      <div className="assistant-message" style={{
        display: 'flex',
        gap: '12px',
        alignItems: 'flex-start',
        width: '100%',
        maxWidth: '100%'
      }}>
        <div
          className="message-avatar"
          style={{
            width: '36px',
            height: '36px',
            minWidth: '36px',
            minHeight: '36px',
            borderRadius: '8px',
            background: isDark
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)',
            flexShrink: 0
          }}
        >
          <Bot size={20} />
        </div>
        <div className="message-content" style={{
          maxHeight: 'none',
          overflow: 'visible',
          display: 'block',
          whiteSpace: 'normal'
        }}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const codeString = String(children).replace(/\n$/, '');

                // Handle both specified language and unspecified code blocks
                if (!inline && (match || codeString.includes('\n'))) {
                  // Auto-detect language if not specified
                  let language = match ? match[1] : 'plaintext';

                  // Language detection patterns
                  if (!match) {
                    // Try to detect JSON
                    if (codeString.trim().startsWith('{') || codeString.trim().startsWith('[')) {
                      try {
                        JSON.parse(codeString);
                        language = 'json';
                      } catch {
                        // Check for JavaScript
                        if (codeString.includes('function') || codeString.includes('const') ||
                            codeString.includes('let') || codeString.includes('var') ||
                            codeString.includes('=>')) {
                          language = 'javascript';
                        }
                      }
                    }
                    // Detect Java
                    else if (codeString.includes('public class') || codeString.includes('public static') ||
                             codeString.includes('System.out') || codeString.includes('import java') ||
                             codeString.includes('package ')) {
                      language = 'java';
                    }
                    // Detect Python
                    else if (codeString.includes('def ') || codeString.includes('import ') ||
                             codeString.includes('from ') || codeString.includes('print(')) {
                      language = 'python';
                    }
                    // Detect HTML
                    else if (codeString.includes('<!DOCTYPE') || codeString.includes('<html') ||
                             codeString.includes('<div') || codeString.includes('<body')) {
                      language = 'html';
                    }
                    // Detect CSS
                    else if (codeString.includes('{') && (codeString.includes('color:') ||
                             codeString.includes('background:') || codeString.includes('margin:') ||
                             codeString.includes('padding:'))) {
                      language = 'css';
                    }
                    // Detect SQL
                    else if (codeString.toUpperCase().includes('SELECT') ||
                             codeString.toUpperCase().includes('INSERT') ||
                             codeString.toUpperCase().includes('UPDATE')) {
                      language = 'sql';
                    }
                  }

                  return (
                    <div className={`code-block-wrapper ${isDark ? 'dark' : 'light'}`} style={{
                      margin: '20px 0',
                      borderRadius: '12px',
                      overflow: 'hidden',
                      background: isDark ? '#1e1e1e' : '#f6f8fa',
                      border: `1px solid ${isDark ? '#2d2d30' : '#d1d5db'}`,
                      position: 'relative'
                    }}>
                      {/* Language Label */}
                      <div className="code-language-label" style={{
                        position: 'absolute',
                        top: '12px',
                        left: '16px',
                        zIndex: 2,
                        background: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)',
                        color: isDark ? '#858585' : '#6e6e6e',
                        padding: '3px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: '500',
                        textTransform: 'lowercase',
                        letterSpacing: '0.5px',
                        fontFamily: 'system-ui, -apple-system, sans-serif'
                      }}>
                        {language}
                      </div>

                      {/* Copy Button */}
                      <button
                        className="code-copy-button"
                        onClick={() => {
                          navigator.clipboard.writeText(codeString);
                          toast.success('Copied!', { duration: 1500 });
                        }}
                        style={{
                          position: 'absolute',
                          top: '12px',
                          right: '16px',
                          zIndex: 2,
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          padding: '5px 10px',
                          background: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)',
                          border: 'none',
                          borderRadius: '6px',
                          color: isDark ? '#cccccc' : '#424242',
                          fontSize: '12px',
                          fontWeight: '500',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          fontFamily: 'system-ui, -apple-system, sans-serif'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.background = isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.1)';
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.background = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)';
                        }}
                        title="Copy code"
                      >
                        <Copy size={12} />
                        <span>Copy code</span>
                      </button>

                      <div className="code-content-area" style={{
                        padding: '48px 20px 20px 20px',
                        overflow: 'auto',
                        maxHeight: '600px'
                      }}>
                        <SyntaxHighlighter
                          style={isDark ? vscDarkPlus : oneLight}
                          language={language}
                          PreTag="pre"
                          showLineNumbers={false}
                          customStyle={{
                            margin: 0,
                            padding: '16px',
                            background: isDark ? '#1e1e1e' : '#f6f8fa',
                            fontSize: '14px',
                            lineHeight: '1.6',
                            fontFamily: "'JetBrains Mono', 'Cascadia Code', 'Fira Code', Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace",
                            borderRadius: '0',
                            border: 'none',
                            overflow: 'visible'
                          }}
                          codeTagProps={{
                            style: {
                              fontFamily: "'JetBrains Mono', 'Cascadia Code', 'Fira Code', Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace",
                              fontSize: '14px',
                              lineHeight: '1.6'
                            }
                          }}
                          {...props}
                        >
                          {codeString}
                        </SyntaxHighlighter>
                      </div>
                    </div>
                  );
                }
                return (
                  <code
                    style={{
                      background: isDark ? 'rgba(110, 118, 129, 0.4)' : 'rgba(175, 184, 193, 0.2)',
                      color: isDark ? '#e5e5e5' : '#1f2937',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      fontSize: '0.875em',
                      fontFamily: "'JetBrains Mono', 'Cascadia Code', 'Fira Code', Consolas, Monaco, 'Liberation Mono', 'Courier New', monospace",
                      fontWeight: '500',
                      border: `1px solid ${isDark ? 'rgba(110, 118, 129, 0.3)' : 'rgba(175, 184, 193, 0.3)'}`,
                      whiteSpace: 'nowrap'
                    }}
                    {...props}
                  >
                    {children}
                  </code>
                );
              },
              p: ({ children }) => (
                <p style={{
                  margin: '12px 0',
                  lineHeight: '1.7',
                  color: isDark ? '#e5e5e5' : '#374151',
                  fontSize: '15px'
                }}>{children}</p>
              ),
              h1: ({ children }) => (
                <h1 style={{
                  margin: '24px 0 16px 0',
                  fontSize: '1.6em',
                  fontWeight: '700',
                  color: isDark ? '#ffffff' : '#111827',
                  lineHeight: '1.3',
                  borderBottom: `2px solid ${isDark ? '#444654' : '#e5e7eb'}`,
                  paddingBottom: '8px'
                }}>{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 style={{
                  margin: '20px 0 12px 0',
                  fontSize: '1.4em',
                  fontWeight: '600',
                  color: isDark ? '#f3f4f6' : '#1f2937',
                  lineHeight: '1.4'
                }}>{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 style={{
                  margin: '16px 0 8px 0',
                  fontSize: '1.2em',
                  fontWeight: '600',
                  color: isDark ? '#e5e7eb' : '#374151',
                  lineHeight: '1.5'
                }}>{children}</h3>
              ),
              ul: ({ children }) => (
                <ul style={{
                  margin: '12px 0',
                  paddingLeft: '24px',
                  listStyleType: 'disc'
                }}>{children}</ul>
              ),
              ol: ({ children }) => (
                <ol style={{
                  margin: '12px 0',
                  paddingLeft: '24px',
                  listStyleType: 'decimal'
                }}>{children}</ol>
              ),
              li: ({ children }) => (
                <li style={{
                  margin: '6px 0',
                  lineHeight: '1.6',
                  color: isDark ? '#e5e5e5' : '#374151'
                }}>{children}</li>
              ),
              blockquote: ({ children }) => (
                <blockquote style={{
                  borderLeft: `4px solid ${isDark ? '#667eea' : '#3b82f6'}`,
                  paddingLeft: '20px',
                  paddingTop: '12px',
                  paddingBottom: '12px',
                  margin: '16px 0',
                  fontStyle: 'italic',
                  background: isDark ? 'rgba(102, 126, 234, 0.05)' : 'rgba(59, 130, 246, 0.05)',
                  color: isDark ? '#c5c5d2' : '#4b5563',
                  borderRadius: '0 6px 6px 0',
                  fontSize: '0.95em'
                }}>
                  {children}
                </blockquote>
              ),
              table: ({ children }) => (
                <div style={{
                  overflowX: 'auto',
                  margin: '16px 0',
                  borderRadius: '8px',
                  border: `1px solid ${isDark ? '#444654' : '#e5e7eb'}`,
                  boxShadow: isDark ? '0 2px 4px rgba(0,0,0,0.2)' : '0 2px 4px rgba(0,0,0,0.05)'
                }}>
                  <table style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    background: isDark ? '#343541' : '#ffffff'
                  }}>
                    {children}
                  </table>
                </div>
              ),
              th: ({ children }) => (
                <th style={{
                  padding: '12px 16px',
                  textAlign: 'left',
                  borderBottom: `2px solid ${isDark ? '#565869' : '#d1d5db'}`,
                  background: isDark ? '#404040' : '#f9fafb',
                  fontWeight: '600',
                  fontSize: '14px',
                  color: isDark ? '#e5e5e5' : '#374151'
                }}>
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td style={{
                  padding: '12px 16px',
                  borderBottom: `1px solid ${isDark ? '#444654' : '#e5e7eb'}`,
                  fontSize: '14px',
                  color: isDark ? '#e5e5e5' : '#374151'
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
              marginTop: '16px',
              paddingTop: '12px',
              borderTop: `1px solid ${isDark ? '#444654' : '#e5e7eb'}`,
              display: 'flex',
              justifyContent: 'flex-end'
            }}>
              <button
                onClick={handleCopy}
                style={{
                  background: isDark ? '#404040' : '#f8f9fa',
                  border: `1px solid ${isDark ? '#565869' : '#d1d5db'}`,
                  color: isDark ? '#e5e5e5' : '#374151',
                  cursor: 'pointer',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  fontSize: '13px',
                  fontWeight: '500',
                  transition: 'all 0.2s ease',
                  boxShadow: isDark ? '0 1px 3px rgba(0,0,0,0.2)' : '0 1px 3px rgba(0,0,0,0.1)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = isDark ? '#4a5568' : '#e2e8f0';
                  e.target.style.transform = 'translateY(-1px)';
                  e.target.style.boxShadow = isDark ? '0 2px 6px rgba(0,0,0,0.3)' : '0 2px 6px rgba(0,0,0,0.15)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = isDark ? '#404040' : '#f8f9fa';
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = isDark ? '0 1px 3px rgba(0,0,0,0.2)' : '0 1px 3px rgba(0,0,0,0.1)';
                }}
                title="Copy message"
              >
                <Copy size={14} />
                <span>Copy</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageRenderer;