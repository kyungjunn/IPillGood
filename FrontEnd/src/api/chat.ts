export interface ChatResponse {
  answer: string;
}

export async function sendMessage(message: string): Promise<ChatResponse> {
  const response = await fetch('/api/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: message }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error?.detail ?? `서버 오류 (${response.status})`);
  }

  return response.json();
}
