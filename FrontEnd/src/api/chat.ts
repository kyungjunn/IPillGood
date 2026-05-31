export interface SourceItem {
  product_name: string;
  representative_ingredient: string;
  manufacturer: string;
  serving_size: string;
  origin_country: string;
  source_name: string;
}

export interface ChatResponse {
  answer: string;
  sources: SourceItem[];
}

export async function sendMessage(message: string): Promise<ChatResponse> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error?.detail ?? `서버 오류 (${response.status})`);
  }

  return response.json();
}
