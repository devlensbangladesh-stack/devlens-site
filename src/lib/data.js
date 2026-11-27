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
// A post with a future `publishAt` (ISO time, Dhaka) stays out of the build until a build after that time.
const builtAt = process.env.BUILD_TIME ? Date.parse(process.env.BUILD_TIME) : Date.now();
const isLive = (p) => !p.publishAt || Date.parse(p.publishAt.length <= 19 ? p.publishAt + '+06:00' : p.publishAt) <= builtAt;
export const posts = Object.values(postModules).map((m) => m.default)
  .filter(isLive)
  .map((p) => (p.image ? p : { ...p, image: imgFromContent(p.content) }))
  .sort((a, b) => b.date.localeCompare(a.date));
export const pages = Object.values(pageModules).map((m) => m.default);
export const categories = categoriesData;
export const tags = Object.values(tagModules)[0]?.default || [];
// `home.scheduledLead` ({from, slug, label, headline, summary, special}) takes over the lead at the first build after `from`.
// The previous lead then becomes the main "Also today" item, and the old main item moves to the front of `plus`.
const sl = home.scheduledLead;
const slLive = sl && Date.parse(sl.from.length <= 19 ? sl.from + '+06:00' : sl.from) <= builtAt && posts.some((p) => p.slug === sl.slug);
const homeLive = slLive ? {
  ...home,
  lead: { slug: sl.slug, label: sl.label, headline: sl.headline, summary: sl.summary },
  alsoToday: { ...home.lead, plus: [home.alsoToday.slug, ...(home.alsoToday.plus || [])].filter((x, i, a) => x && x !== sl.slug && x !== home.lead.slug && a.indexOf(x) === i) },
  special: sl.special ? { slug: sl.slug, label: sl.label, headline: sl.headline, summary: sl.summary, published: sl.from.slice(0, 10) } : home.special,
} : home;
export { homeLive as home, jobsData };

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

// ---- Jobs: divisions, own pages and Google for Jobs ----
// Division for each job, from the place names in its location (a job can sit in more than one).
export const DIVISIONS = [
  ['dhaka', 'Dhaka', ['dhaka','gazipur','narayanganj','narsingdi','manikganj','munshiganj','tangail','kishoreganj','faridpur','gopalganj','madaripur','rajbari','shariatpur']],
  ['chattogram', 'Chattogram', ['chattogram','chittagong',"cox's bazar",'coxs bazar','ukhiya','ukhia','teknaf','kutupalong','bhasan char','camp ','cumilla','comilla','feni','chandpur','lakshmipur','noakhali','brahmanbaria','rangamati','khagrachhari','khagrachari','bandarban']],
  ['khulna', 'Khulna', ['khulna','paikgachha','satkhira','bagerhat','jashore','jessore','jhenaidah','magura','narail','kushtia','chuadanga','meherpur']],
  ['rajshahi', 'Rajshahi', ['rajshahi','bogura','bogra','pabna','sirajganj','natore','naogaon','chapainawabganj','joypurhat']],
  ['rangpur', 'Rangpur', ['rangpur','gaibandha','saghata','kurigram','lalmonirhat','nilphamari','dinajpur','thakurgaon','panchagarh']],
  ['barishal', 'Barishal', ['barishal','barisal','laharhat','bhola','patuakhali','pirojpur','barguna','jhalokathi']],
  ['sylhet', 'Sylhet', ['sylhet','sunamganj','habiganj','moulvibazar']],
  ['mymensingh', 'Mymensingh', ['mymensingh','jamalpur','netrokona','sherpur']],
];
export const divisionsOf = (loc) => {
  const l = ` ${(loc || '').toLowerCase()} `;
  const found = DIVISIONS.filter(([, , words]) => words.some((w) => l.includes(w))).map(([id]) => id);
  return found.length ? found : ['nationwide'];
};

const slugify = (s) => s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
// Short, stable fingerprint of the advert link, so two jobs with the same title never share a page.
const fingerprint = (s) => { let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return (h >>> 0).toString(36).slice(0, 5); };
export const jobSlug = (j) => j.id || `${slugify(`${j.title} ${j.badge || j.org}`).slice(0, 70).replace(/-+$/, '')}-${fingerprint(j.url)}`;
export const jobPath = (j) => `/jobs/${jobSlug(j)}/`;
// A job gets its own page only when we hold the advert's full description (Google for Jobs needs it).
export const hasJobPage = (j) => typeof j.description === 'string' && j.description.replace(/<[^>]+>/g, ' ').trim().split(/\s+/).length >= 60;

// Keep advert HTML to plain structure: no scripts, styles, images, forms or inline handlers.
const ALLOWED = new Set(['p', 'br', 'ul', 'ol', 'li', 'strong', 'b', 'em', 'i', 'h2', 'h3', 'h4', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td']);
export const cleanJobHtml = (html = '') => html
  .replace(/<(script|style|iframe|object|form|svg|noscript)[\s\S]*?<\/\1>/gi, '')
  .replace(/<!--[\s\S]*?-->/g, '')
  .replace(/<\/?([a-z0-9]+)\b([^>]*)>/gi, (m, tag, attrs) => {
    const t = tag.toLowerCase();
    if (!ALLOWED.has(t)) return t === 'div' || t === 'section' ? (m[1] === '/' ? '</p>' : '<p>') : ' ';
    if (m[1] === '/') return `</${t}>`;
    if (t === 'a') {
      const href = (attrs.match(/href\s*=\s*"([^"]*)"/i) || attrs.match(/href\s*=\s*'([^']*)'/i) || [])[1] || '';
      return /^(https?:|mailto:)/i.test(href) ? `<a href="${href.replace(/"/g, '&quot;')}" rel="noopener nofollow" target="_blank">` : '<a>';
    }
    return `<${t}>`;
  })
  .replace(/<p>\s*(?:&nbsp;|\s)*<\/p>/gi, '')
  .trim();

const EMPLOYMENT = ['FULL_TIME', 'PART_TIME', 'CONTRACTOR', 'TEMPORARY', 'INTERN', 'VOLUNTEER', 'PER_DIEM', 'OTHER'];
const DIVISION_NAMES = Object.fromEntries(DIVISIONS.map(([id, name]) => [id, name + ' Division']));
// schema.org JobPosting for one job, following Google's job posting guidelines. Only facts we hold go in.
export function jobPostingLd(j, site) {
  const types = [].concat(j.employmentType || (j.consultancy ? 'CONTRACTOR' : [])).filter((t) => EMPLOYMENT.includes(t));
  const divs = divisionsOf(j.location).filter((d) => d !== 'nationwide');
  // Town: an explicit `city`, else the first known place name in the location text, in its original spelling.
  const town = (() => {
    if (j.city) return j.city;
    if (divs.length !== 1) return null;
    const loc = j.location || '', low = loc.toLowerCase();
    const hits = DIVISIONS.flatMap(([, , words]) => words).map((w) => [low.indexOf(w.trim()), w.trim()]).filter(([i]) => i > -1).sort((a, b) => a[0] - b[0]);
    return hits.length ? loc.substr(hits[0][0], hits[0][1].length).replace(/^\w/, (c) => c.toUpperCase()) : null;
  })();
  const place = (region) => ({ '@type': 'Place', address: { '@type': 'PostalAddress', ...(town ? { addressLocality: town } : {}), ...(region ? { addressRegion: region } : {}), addressCountry: 'BD' } });
  const ld = {
    '@context': 'https://schema.org', '@type': 'JobPosting',
    title: j.title,
    description: cleanJobHtml(j.description),
    datePosted: j.posted || j.added,
    hiringOrganization: { '@type': 'Organization', name: j.org, ...(j.orgUrl ? { sameAs: j.orgUrl } : {}) },
    url: new URL(jobPath(j), site).href,
    directApply: false,
  };
  if (j.deadline) ld.validThrough = `${j.deadline}T23:59:00+06:00`;
  if (types.length) ld.employmentType = types.length === 1 ? types[0] : types;
  if (j.remote) {
    ld.jobLocationType = 'TELECOMMUTE';
    ld.applicantLocationRequirements = { '@type': 'Country', name: 'Bangladesh' };
  } else {
    ld.jobLocation = divs.length ? divs.map((d) => place(DIVISION_NAMES[d])) : [place()];
    if (ld.jobLocation.length === 1) ld.jobLocation = ld.jobLocation[0];
  }
  const refNo = (j.ref || '').replace(/^Ref:\s*/i, '').split('·')[0].trim();
  if (refNo) ld.identifier = { '@type': 'PropertyValue', name: j.org, value: refNo };
  if (j.salary && j.salary.currency && (j.salary.min || j.salary.max)) {
    ld.baseSalary = { '@type': 'MonetaryAmount', currency: j.salary.currency, value: { '@type': 'QuantitativeValue', ...(j.salary.min ? { minValue: j.salary.min } : {}), ...(j.salary.max ? { maxValue: j.salary.max } : {}), unitText: j.salary.unit || 'MONTH' } };
  }
  return ld;
}
