import { useState, useRef, useEffect } from 'react';
import { sendMessage } from '../api/chat';
import ChatMessage, { type Message } from './ChatMessage';

const SUGGESTED_QUESTIONS = [
  '피로회복에 좋은 영양제 추천해줘',
  '비타민C 영양제 어떤 제품이 있어?',
  '프로바이오틱스 복용 방법 알려줘',
  '오메가3 고르는 기준이 뭐야?',
];

let idCounter = 0;
const genId = () => `msg-${++idCounter}`;

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: genId(),
      role: 'assistant',
      content:
        '안녕하세요! 저는 영양제 전문 AI 어시스턴트 IPillGood입니다 💊\n궁금한 영양제 성분, 효능, 복용 방법 등 무엇이든 물어보세요!',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = async (text?: string) => {
    const question = (text ?? input).trim();
    if (!question || loading) return;

    setInput('');
    setMessages((prev) => [
      ...prev,
      { id: genId(), role: 'user', content: question },
    ]);
    setLoading(true);

    try {
      const data = await sendMessage(question);
      setMessages((prev) => [
        ...prev,
        {
          id: genId(),
          role: 'assistant',
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
      setMessages((prev) => [
        ...prev,
        {
          id: genId(),
          role: 'assistant',
          content: `⚠️ 오류가 발생했습니다: ${message}`,
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const isOnlyGreeting = messages.length === 1;

  return (
    <div className="chat-window">
      {/* 메시지 영역 */}
      <div className="chat-window__messages">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {/* 로딩 버블 */}
        {loading && (
          <div className="chat-message chat-message--assistant">
            <div className="chat-message__avatar">
              <span>💊</span>
            </div>
            <div className="chat-message__bubble-wrap">
              <div className="chat-message__bubble chat-message__bubble--loading">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            </div>
          </div>
        )}

        {/* 추천 질문 (최초 화면) */}
        {isOnlyGreeting && !loading && (
          <div className="suggested-questions">
            <p className="suggested-questions__label">이런 질문을 해보세요</p>
            <div className="suggested-questions__list">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  className="suggested-questions__item"
                  onClick={() => handleSubmit(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* 입력 영역 */}
      <div className="chat-window__input-area">
        <textarea
          ref={inputRef}
          className="chat-window__input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="영양제에 대해 궁금한 것을 물어보세요... (Enter로 전송)"
          rows={1}
          disabled={loading}
        />
        <button
          className="chat-window__send"
          onClick={() => handleSubmit()}
          disabled={loading || !input.trim()}
          aria-label="전송"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
    </div>
  );
}
