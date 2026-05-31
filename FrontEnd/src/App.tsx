import ChatWindow from './components/ChatWindow';
import './App.css';

export default function App() {
  return (
    <div className="app">
      {/* 헤더 */}
      <header className="app__header">
        <div className="app__header-inner">
          <div className="app__logo">
            <span className="app__logo-icon">💊</span>
            <span className="app__logo-text">
              I <strong>Pill</strong> Good
            </span>
          </div>
          <p className="app__tagline">식약처 공인 데이터 기반 영양제 AI 어시스턴트</p>
        </div>
      </header>

      {/* 채팅 본문 */}
      <main className="app__main">
        <ChatWindow />
      </main>

      {/* 푸터 */}
      <footer className="app__footer">
        <p>본 서비스는 식품의약품안전처 공공데이터를 기반으로 합니다. 의료적 진단·처방을 대체하지 않습니다.</p>
      </footer>
    </div>
  );
}
