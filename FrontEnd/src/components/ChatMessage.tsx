export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isError?: boolean;
}

interface Props {
  message: Message;
}

export default function ChatMessage({ message }: Props) {
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


      </div>

      {isUser && (
        <div className="chat-message__avatar chat-message__avatar--user">
          <span>👤</span>
        </div>
      )}
    </div>
  );
}
