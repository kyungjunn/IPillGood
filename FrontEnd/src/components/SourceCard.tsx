import type { SourceItem } from '../api/chat';

interface Props {
  source: SourceItem;
  index: number;
}

export default function SourceCard({ source, index }: Props) {
  return (
    <div className="source-card">
      <div className="source-card__badge">{index + 1}</div>
      <div className="source-card__body">
        <p className="source-card__name">{source.product_name}</p>
        <p className="source-card__ingredient">{source.representative_ingredient}</p>
        <div className="source-card__meta">
          {source.manufacturer && (
            <span className="source-card__tag">🏭 {source.manufacturer}</span>
          )}
          {source.origin_country && (
            <span className="source-card__tag">🌏 {source.origin_country}</span>
          )}
          {source.serving_size && (
            <span className="source-card__tag">💊 {source.serving_size}</span>
          )}
        </div>
        <p className="source-card__provider">출처: {source.source_name}</p>
      </div>
    </div>
  );
}
