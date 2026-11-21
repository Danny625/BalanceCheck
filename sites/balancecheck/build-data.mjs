import {readFileSync, readdirSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';

function readCsv(path) {
  const csv = readFileSync(path, 'utf8').replace(/^\uFEFF/, '').trimEnd();
  const rows = [[]];
  let value = '';
  let quoted = false;
  for (let index = 0; index < csv.length; index++) {
    const char = csv[index];
    if (char === '"') {
      if (quoted && csv[index + 1] === '"') {
        value += '"';
        index++;
      } else {
        quoted = !quoted;
      }
    } else if (!quoted && (char === ',' || char === '\n')) {
      rows.at(-1).push(value);
      value = '';
      if (char === '\n') rows.push([]);
    } else if (quoted || char !== '\r') {
      value += char;
    }
  }
  rows.at(-1).push(value);
  const headers = rows.shift();
  return rows.map(row => {
    if (row.length !== headers.length) throw new Error('Invalid CSV row in ' + path);
    return Object.fromEntries(headers.map((header, index) => [header, row[index]]));
  });
}

const source = process.argv[2] ?? '../../data';
const shared = name => readCsv(join(source, 'shared', name + '.csv'));
const roster = shared('characters');
const shares = Object.fromEntries(shared('skill_groups').map(row => [row.skill_group, Number(row.share_of_players)]));
const thresholds = Object.fromEntries(shared('review_thresholds').map(row => [row.parameter, Number(row.value)]));
const dataset = readdirSync(join(source, 'scenarios'), {withFileTypes: true})
  .filter(entry => entry.isDirectory())
  .sort((a, b) => a.name.localeCompare(b.name))
  .map(({name}) => {
    const directory = join(source, 'scenarios', name);
    return {
      name,
      roster: readdirSync(directory).includes('characters.csv') ? readCsv(join(directory, 'characters.csv')) : roster,
      stats: readCsv(join(directory, 'stats.csv')),
      feedback: readCsv(join(directory, 'feedback.csv'))
    };
  });
writeFileSync(new URL('./dist/dataset.js', import.meta.url),
  'const balanceData = ' + JSON.stringify({dataset, shares, thresholds}) + ';\n');
