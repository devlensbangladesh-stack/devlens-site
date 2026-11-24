import categoriesData from '../data/categories.json';
import home from '../data/home.json';
import jobsData from '../data/jobs.json';

const postModules = import.meta.glob('../data/posts/*.json', { eager: true });
const pageModules = import.meta.glob('../data/pages/*.json', { eager: true });
let tagModules = import.meta.glob('../data/tags.json', { eager: true });

const imgFromContent = (html = '') => {
  const m = html.match(/<img[^>]*?src=\\?"([^"\\]+)\\?"[^>]*>/i);
  if (!m) return null;
  const alt = (m[0].match(/alt=\\?"([^"\\]*)/i) || [])[1] || '';
  return { src: m[1].replace(/\?.*$/, ''), alt };
};
export const posts = Object.values(postModules).map((m) => m.default)
  .map((p) => (p.image ? p : { ...p, image: imgFromContent(p.content) }))
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

// ---- Development sectors (built from the Sectors page, NGOAB list) ----
const sectorsPage = pages.find((p) => p.slug === 'sectors')?.content || '';
const decode = (s) => s.replace(/&amp;/g, '&').replace(/&#8217;/g, '’');
export const sectorList = [];
const tagToSector = {};
{
  let cur = null;
  const re = /<h3[^>]*>([^<]*)<a href="\/tag\/([^/]+)\/">([^<]+)<\/a>|<li><a href="\/tag\/([^/]+)\/">/g;
  let m;
  while ((m = re.exec(sectorsPage))) {
    if (m[2]) { cur = m[2]; sectorList.push({ slug: cur, name: decode(m[3]), icon: m[1].trim() }); tagToSector[cur] = cur; }
    else if (cur && !tagToSector[m[4]]) tagToSector[m[4]] = cur;
  }
}
// Cross-cutting themes NGOs follow that are not NGOAB sectors.
sectorList.unshift(
  { slug: 'humanitarian-rohingya-response', name: 'Humanitarian & Rohingya', icon: '🆘' },
  { slug: 'aid-financing', name: 'Aid, funding & NGOs', icon: '💰' },
);
const aliases = {
  'humanitarian-rohingya-response': 'humanitarian-rohingya-response', 'rohingya-response': 'humanitarian-rohingya-response',
  'coxs-bazar': 'humanitarian-rohingya-response', 'humanitarian-response': 'humanitarian-rohingya-response',
  'aid-financing': 'aid-financing', localisation: 'aid-financing', 'development-cooperation': 'aid-financing', safeguarding: 'aid-financing',
  'health-nutrition': 'health', 'climate-disaster-resilience': 'climate-change', 'disaster-risk-reduction': 'disaster-management',
  'food-security-agriculture': 'agriculture', 'gender-equality': 'women-empowerment', education: 'education-and-human-resource-development',
  'governance-human-rights': 'public-order-and-safety', 'digital-development': 'innovation-science-and-information-technology',
  'livelihoods-economic-empowerment': 'poverty-reduction-decent-employment', poverty: 'poverty-reduction-decent-employment',
  migration: 'poverty-reduction-decent-employment',
};
export const postSectors = (p) => {
  const out = [];
  for (const t of p.tags || []) {
    const s = aliases[t] || tagToSector[t];
    if (s && !out.includes(s)) out.push(s);
  }
  const rank = (x) => sectorList.findIndex((q) => q.slug === x);
  return out.sort((a, b) => rank(a) - rank(b));
};
export const sectorInfo = (slug) => sectorList.find((s) => s.slug === slug);
if (tagToSector['child-protection'] && !aliases['child-rights-protection']) aliases['child-rights-protection'] = tagToSector['child-protection'];

// First sentence of the story's "Why it matters" section.
const stripHtml = (h) => h.replace(/<[^>]+>/g, ' ').replace(/&amp;/g, '&').replace(/&#8217;/g, '’').replace(/\s+/g, ' ').trim();
export const whyItMatters = (p) => {
  const m = (p.content || '').match(/<h3[^>]*>\s*Why it matters[^<]*<\/h3>\s*<p[^>]*>([\s\S]*?)<\/p>/i);
  if (!m) return '';
  const text = stripHtml(m[1]);
  const sents = text.match(/[^.!?]+[.!?]+(?=\s+[A-Z“"]|$)/g) || [text];
  let s = sents[0].trim();
  for (let i = 1; i < sents.length && (s + ' ' + sents[i].trim()).length <= 300; i++) s += ' ' + sents[i].trim();
  return s.length > 320 ? s.slice(0, 317).replace(/\s+\S*$/, '') + '…' : s;
};
