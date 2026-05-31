import { useState } from 'react';
import type { SourceItem } from '../api/chat';
import SourceCard from './SourceCard';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceItem[];
  isError?: boolean;
}

interface Props {
  message: Message;
}

export default function ChatMessage({ message }: Props) {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === 'user';

  return (
    <div className={`chat-message chat-message--${isUser ? 'user' : 'assistant'}`}>
      {!isUser && (
        <div className="chat-message__avatar">
          <span>💊</span>
        </div>
      )}

      <div className="chat-message__bubble-wrap">
        <div
          className={`chat-message__bubble ${message.isError ? 'chat-message__bubble--error' : ''}`}
        >
          {message.content.split('\n').map((line, i) => (
            <span key={i}>
              {line}
              {i < message.content.split('\n').length - 1 && <br />}
            </span>
          ))}
        </div>

        {/* 출처 토글 */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="chat-message__sources">
            <button
              className="sources-toggle"
              onClick={() => setShowSources((v) => !v)}
            >
              <span className="sources-toggle__icon">{showSources ? '▲' : '▼'}</span>
              참고 영양제 {message.sources.length}개
            </button>

            {showSources && (
              <div className="sources-list">
                {message.sources.map((src, i) => (
                  <SourceCard key={i} source={src} index={i} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="chat-message__avatar chat-message__avatar--user">
          <span>👤</span>
        </div>
      )}
    </div>
  );
}
