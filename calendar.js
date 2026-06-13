/**
 * Economic Calendar — ForexFactory JSON feed
 */
const URL = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json';

let cache = [], cacheTime = 0;

export async function fetchCalendar() {
  if (cache.length && Date.now() - cacheTime < 30 * 60 * 1000) return cache;
  try {
    const r = await fetch(URL);
    cache = await r.json();
    cacheTime = Date.now();
  } catch (e) { console.error('[Calendar]', e.message); }
  return cache;
}

export async function getUpcomingHigh(windowMin = 15) {
  const events = await fetchCalendar();
  const now = new Date(), limit = new Date(now.getTime() + windowMin * 60000);
  return events.filter(e => e.impact === 'High' && e.country === 'USD' && new Date(e.date) >= now && new Date(e.date) <= limit);
}

export async function isNewsTime() {
  const events = await fetchCalendar();
  const now = new Date();
  return events.some(e => e.impact === 'High' && e.country === 'USD' && Math.abs(now - new Date(e.date)) / 60000 <= 5);
}

export async function todaySummary() {
  const events = await fetchCalendar();
  const today = new Date().toDateString();
  const usd = events.filter(e => new Date(e.date).toDateString() === today && e.country === 'USD');
  if (!usd.length) return 'لا توجد أخبار USD اليوم ✅';
  return usd.sort((a, b) => new Date(a.date) - new Date(b.date)).map(e => {
    const t = new Date(e.date).toLocaleTimeString('ar', { hour: '2-digit', minute: '2-digit', timeZone: 'America/New_York' });
    return (e.impact === 'High' ? '🔴' : e.impact === 'Medium' ? '🟡' : '⚪') + ` ${t} — ${e.title}`;
  }).join('\n');
}
