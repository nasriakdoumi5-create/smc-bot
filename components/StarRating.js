export default function StarRating({ rating, count, size = 'sm' }) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5;
  const sizeClass = size === 'sm' ? 'text-sm' : size === 'lg' ? 'text-xl' : 'text-base';
  return (
    <div className={`flex items-center gap-1.5 ${sizeClass}`}>
      <div className="flex text-yellow-400">
        {Array(5).fill(0).map((_, i) => (
          <span key={i}>{i < full ? '★' : (i === full && half ? '½' : '☆')}</span>
        ))}
      </div>
      {count !== undefined && (
        <span className="text-gray-500 text-xs">({count.toLocaleString()} reviews)</span>
      )}
    </div>
  );
}
