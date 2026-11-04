import categoriesData from '../data/categories.json';
import home from '../data/home.json';
import jobsData from '../data/jobs.json';

const postModules = import.meta.glob('../data/posts/*.json', { eager: true });
const pageModules = import.meta.glob('../data/pages/*.json', { eager: true });
let tagModules = import.meta.glob('../data/tags.json', { eager: true });

export const posts = Object.values(postModules).map((m) => m.default)
  .sort((a, b) => b.date.localeCompare(a.date));
export const pages = Object.values(pageModules).map((m) => m.default);
export const categories = categoriesData;
export const tags = Object.values(tagModules)[0]?.default || [];
export { home, jobsData };

export const postUrl = (p) => {
  const [y, m, d] = p.date.slice(0, 10).split('-');
  return `/${y}/${m}/${d}/${p.slug}/`;
};
export const bySlug = (slug) => posts.find((p) => p.slug === slug);
export const catName = (slug) => categories.find((c) => c.slug === slug)?.name || slug.replace(/-/g, ' ');
export const tagName = (slug) => tags.find((t) => t.slug === slug)?.name || slug.replace(/-/g, ' ');

export const fmtDate = (iso) =>
  new Date(iso.slice(0, 10) + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
export const fmtShort = (iso) =>
  new Date(iso + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });

// "Today" in Dhaka at build time. The browser recalculates this on every visit.
export const dhakaToday = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Dhaka' }).format(new Date());
export const daysBetween = (a, b) => Math.round((Date.parse(b) - Date.parse(a)) / 86400000);

export function jobLabel(deadline, today) {
  if (!deadline) return { text: 'OPEN', color: '#6b6f76', soon: false };
  const n = daysBetween(today, deadline);
  if (n <= 0) return { text: 'CLOSES TODAY', color: '#c2410c', soon: true };
  if (n === 1) return { text: 'CLOSES TOMORROW', color: '#c2410c', soon: true };
  if (n <= 7) return { text: 'CLOSES THIS WEEK', color: '#b45309', soon: true };
  return { text: 'DEADLINE', color: '#0b8f68', soon: false };
}
export function openJobs(today = dhakaToday()) {
  return jobsData.jobs.filter((j) => !j.deadline || j.deadline >= today);
}
export const firstImage = (html = '') => /<img\s/i.test(html);
