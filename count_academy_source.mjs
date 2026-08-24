import fs from 'node:fs';

const items = JSON.parse(fs.readFileSync('./items.json', 'utf8'));
const matching = items.filter((item) =>
  String(item.source || '').includes('أكاديمية المحاماة'),
);

const sourceBreakdown = Object.entries(
  matching.reduce((accumulator, item) => {
    const source = item.source || 'غير محدد';
    accumulator[source] = (accumulator[source] || 0) + 1;
    return accumulator;
  }, {}),
).sort(([, left], [, right]) => right - left);

console.log(
  JSON.stringify(
    {
      total_items: items.length,
      academy_items: matching.length,
      source_breakdown: sourceBreakdown,
    },
    null,
    2,
  ),
);
