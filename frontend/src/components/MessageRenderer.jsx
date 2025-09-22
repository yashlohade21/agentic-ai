import React, { useState } from 'react';
import { User, Bot, Copy, AlertCircle, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { toast } from 'react-hot-toast';
import './CodeBlock.css';

const MessageRenderer = ({ message }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [copiedStates, setCopiedStates] = useState({});

  const isDark = document.documentElement.classList.contains('theme-dark') || 
                document.body.classList.contains('theme-dark');

  const handleCopy = async (text, id = 'message') => {
    try {
      await navigator.clipboard.writeText(text);
      
      // Update copy state for specific code block or message
      setCopiedStates(prev => ({ ...prev, [id]: true }));
      
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [id]: false }));
      }, 2000);
      
      toast.success('Copied!', { duration: 2000 });
    } catch (error) {
      toast.error('Failed to copy');
    }
  };

  if (message.type === 'user') {
    return (
      <div className="message-wrapper user-wrapper">
        <div className="user-message">
          <div className="message-content">
            {message.content}
          </div>
        </div>
      </div>
    );
  }

  if (message.type === 'error') {
    return (
      <div className="message-wrapper error">
        <div className="error-message">
          <div className="message-avatar">
            <AlertCircle size={20} />
          </div>
          <div className="message-content">
            <div className="error-content">
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
      className="message-wrapper assistant-wrapper"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="assistant-message">
        <div className="message-avatar assistant-avatar">
          <Bot size={20} />
        </div>
        <div className="message-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                let codeString = '';

                if (typeof children === 'string') {
                  codeString = children;
                } else if (Array.isArray(children)) {
                  codeString = children.map(child => {
                    if (typeof child === 'string') return child;
                    if (child?.props?.children) return child.props.children;
                    return '';
                  }).join('');
                } else if (children?.props?.children) {
                  codeString = String(children.props.children);
                } else {
                  codeString = String(children || '');
                }

                codeString = codeString.replace(/\n$/, '');

                if (!inline && (match || codeString.includes('\n'))) {
                  let language = match ? match[1] : 'plaintext';
                  const codeId = `code-${Math.random().toString(36).substr(2, 9)}`;
                  const isCopied = copiedStates[codeId];

                  // Language detection logic remains the same
                  if (!match) {
                    if (codeString.trim().startsWith('{') || codeString.trim().startsWith('[')) {
                      try {
                        JSON.parse(codeString);
                        language = 'json';
                      } catch {
                        if (codeString.includes('function') || codeString.includes('const') ||
                            codeString.includes('let') || codeString.includes('var') ||
                            codeString.includes('=>')) {
                          language = 'javascript';
                        }
                      }
                    } else if (codeString.includes('public class') || codeString.includes('public static') ||
                             codeString.includes('System.out') || codeString.includes('import java') ||
                             codeString.includes('package ')) {
                      language = 'java';
                    } else if (codeString.includes('def ') || codeString.includes('import ') ||
                             codeString.includes('from ') || codeString.includes('print(')) {
                      language = 'python';
                    } else if (codeString.includes('<!DOCTYPE') || codeString.includes('<html') ||
                             codeString.includes('<div') || codeString.includes('<body')) {
                      language = 'html';
                    } else if (codeString.includes('{') && (codeString.includes('color:') ||
                             codeString.includes('background:') || codeString.includes('margin:') ||
                             codeString.includes('padding:'))) {
                      language = 'css';
                    } else if (codeString.toUpperCase().includes('SELECT') ||
                             codeString.toUpperCase().includes('INSERT') ||
                             codeString.toUpperCase().includes('UPDATE')) {
                      language = 'sql';
                    }
                  }

                  return (
                    <div className={`code-block ${isDark ? 'dark' : 'light'}`}>
                      <div className="code-header">
                        <div className="code-language">
                          {language}
                        </div>
                        <button
                          className="code-copy-btn"
                          onClick={() => handleCopy(codeString, codeId)}
                          title=""
                        >
                          {isCopied ? <Check size={14} /> : <Copy size={14} />}
                          <span>{isCopied ? 'Copied!' : ''}</span>
                        </button>
                      </div>
                      <div className="code-content">
                        <SyntaxHighlighter
                          style={isDark ? vscDarkPlus : oneLight}
                          language={language}
                          PreTag="pre"
                          showLineNumbers={true}
                          lineNumberStyle={{
                            color: isDark ? '#6e7681' : '#8b949e',
                            paddingRight: '16px',
                            marginRight: '16px',
                            borderRight: `1px solid ${isDark ? '#30363d' : '#d8dee4'}`,
                            textAlign: 'right',
                            minWidth: '3em',
                            userSelect: 'none'
                          }}
                          customStyle={{
                            margin: 0,
                            padding: '16px',
                            background: 'transparent',
                            fontSize: '14px',
                            lineHeight: '1.6',
                            fontFamily: "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace",
                            borderRadius: '0',
                            border: 'none',
                            overflow: 'auto',
                            whiteSpace: 'pre',
                            wordSpacing: 'normal',
                            wordBreak: 'normal',
                            wordWrap: 'normal',
                            tabSize: 4
                          }}
                          codeTagProps={{
                            style: {
                              fontFamily: "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace",
                              fontSize: '14px',
                              lineHeight: '1.6',
                              whiteSpace: 'pre',
                              display: 'block'
                            }
                          }}
                          wrapLines={true}
                          wrapLongLines={false}
                          {...props}
                        >
                          {codeString}
                        </SyntaxHighlighter>
                      </div>
                    </div>
                  );
                }
                return (
                  <code className="inline-code" {...props}>
                    {children}
                  </code>
                );
              },
              p: ({ children }) => <p className="markdown-p">{children}</p>,
              h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
              h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
              h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
              ul: ({ children }) => <ul className="markdown-ul">{children}</ul>,
              ol: ({ children }) => <ol className="markdown-ol">{children}</ol>,
              li: ({ children }) => <li className="markdown-li">{children}</li>,
              blockquote: ({ children }) => <blockquote className="markdown-blockquote">{children}</blockquote>,
              table: ({ children }) => (
                <div className="markdown-table-container">
                  <table className="markdown-table">{children}</table>
                </div>
              ),
              th: ({ children }) => <th className="markdown-th">{children}</th>,
              td: ({ children }) => <td className="markdown-td">{children}</td>,
            }}
          >
            {message.content}
          </ReactMarkdown>

        </div>
        {isHovered && (
          <div className="message-actions">
            <button
              onClick={() => handleCopy(message.content)}
              className="copy-message-btn"
              title="Copy message"
            >
              <Copy size={14} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageRenderer;