const {dataset, shares, thresholds} = balanceData;
const byId = id => document.getElementById(id);
const scenarioSelect = byId('scenario');
const skillSelect = byId('skill');
const currentUpdate = '3.2';
const percent = value => value === null ? 'Unavailable' : (100 * value).toFixed(1) + '%';
const count = value => value === null ? 'Unavailable' : value.toLocaleString();
const numeric = value => value === '' ? null : Number(value);

function node(tag, value, className) {
  const element = document.createElement(tag);
  if (value !== undefined) element.textContent = value;
  if (className) element.className = className;
  return element;
}

function rate(numerator, denominator) {
  return numerator !== null && denominator > 0 ? numerator / denominator : null;
}

function prepare(row) {
  const wins = numeric(row.wins);
  const appearances = numeric(row.appearances);
  const win = rate(wins, appearances);
  const pick = rate(numeric(row.picks), numeric(row.eligible_selections));
  const sufficient = appearances >= thresholds.min_appearances && wins !== null;
  const deviation = win === null ? 0 : Math.max(0, win - thresholds.win_rate_max, thresholds.win_rate_min - win);
  return {...row, wins, appearances, win, pick, sufficient, deviation,
    id: ['stats', row.update, row.character, row.skill_group].join(':')};
}

function baseline(rows, roster) {
  const items = [];
  for (const {character, role} of roster) {
    const records = rows.filter(row => row.character === character);
    const flagged = records.filter(row => row.sufficient && row.deviation > 0);
    const collect = records.filter(row => !row.sufficient || row.pick === null);
    const monitor = records.filter(row => row.sufficient && row.pick !== null &&
      (row.pick < thresholds.pick_rate_min || row.pick > thresholds.pick_rate_max));
    const quality = [flagged, collect, monitor].findIndex(group => group.length);
    if (quality < 0) continue;
    const selected = [flagged, collect, monitor][quality];
    const affected = selected.map(row => row.skill_group);
    items.push({
      quality, role, deviation: Math.max(0, ...flagged.map(row => row.deviation)),
      impact: affected.reduce((sum, skill) => sum + shares[skill], 0),
      report: {character, action: ['Investigate', 'Collect data', 'Monitor'][quality],
        affected_skill_groups: affected, metric_refs: selected.map(row => row.id)},
      selected
    });
  }
  return items.sort((a, b) => a.quality - b.quality || b.impact - a.impact ||
    b.deviation - a.deviation || a.role.localeCompare(b.role)).slice(0, thresholds.max_priorities);
}

function tableRow(values) {
  const row = node('tr');
  row.append(...values.map(value => node('td', value)));
  return row;
}

function updatePerformance() {
  const skill = skillSelect.value;
  const shown = current.rows.filter(row => skill === 'All groups' || row.skill_group === skill);
  const names = current.scenario.roster.map(row => row.character);
  const plotted = names.map(name => {
    const records = shown.filter(row => row.character === name && row.win !== null);
    const appearances = records.reduce((sum, row) => sum + row.appearances, 0);
    return {name, win: rate(records.reduce((sum, row) => sum + row.wins, 0), appearances)};
  });
  const values = plotted.filter(row => row.win !== null).map(row => row.win);
  const min = Math.max(0, Math.floor(Math.min(.4, ...values) * 20) / 20);
  const max = Math.min(1, Math.ceil(Math.max(.6, ...values) * 20) / 20);
  const position = value => (value - min) / (max - min) * 100;
  const chart = plotted.map(({name, win}) => {
    const row = node('div', undefined, 'chart-row');
    const track = node('div', undefined, 'track');
    track.setAttribute('aria-hidden', 'true');
    const band = node('span', undefined, 'target');
    band.style.left = position(thresholds.win_rate_min) + '%';
    band.style.width = (position(thresholds.win_rate_max) - position(thresholds.win_rate_min)) + '%';
    track.append(band);
    if (win !== null) {
      const out = win < thresholds.win_rate_min || win > thresholds.win_rate_max;
      const dot = node('span', undefined, out ? 'dot flag' : 'dot');
      dot.style.left = position(win) + '%';
      track.append(dot);
    }
    row.append(node('span', name), track, node('span', win === null ? '—' : percent(win)));
    return row;
  });
  const axis = node('div', undefined, 'axis');
  const ticks = node('div');
  ticks.append(...[min, (min + max) / 2, max].map(value => node('span', Math.round(value * 100) + '%')));
  axis.append(node('span'), ticks, node('span'));
  byId('chart').replaceChildren(...chart, axis);
  byId('performance-rows').replaceChildren(...shown.map(row => tableRow([
    row.character, row.skill_group, percent(row.win), percent(row.pick), count(row.appearances), row.id
  ])));
}

function showReview(announce = false) {
  const priorities = baseline(current.rows, current.scenario.roster);
  current.report = {scenario: current.scenario.name, update: currentUpdate, method: 'statistics_baseline',
    priorities: priorities.map(item => item.report)};
  const elements = priorities.map(({report, selected}, index) => {
    const item = node('article', undefined, 'priority');
    const detail = selected.map(row => row.skill_group + ' ' + percent(row.win)).join(' · ');
    item.append(node('strong', (index + 1) + '. ' + report.character), node('span', report.action, 'tag'),
      node('p', detail));
    return item;
  });
  if (!elements.length) elements.push(node('p', 'No characters met the baseline review thresholds.'));
  if (announce) {
    const status = node('span', 'Review updated. ', 'sr-only');
    elements.unshift(status);
  }
  byId('priority-list').replaceChildren(...elements);
}

function updateScenario() {
  const scenario = dataset.find(item => item.name === scenarioSelect.value);
  const rows = scenario.stats.filter(row => row.update === currentUpdate).map(prepare);
  current = {scenario, rows};
  byId('characters').textContent = count(new Set(rows.map(row => row.character)).size);
  byId('records').textContent = count(rows.length);
  byId('comments').textContent = count(scenario.feedback.length);
  byId('feedback-rows').replaceChildren(...scenario.feedback.map(row => tableRow([
    row.comment_id, row.character, row.update, row.skill_level, row.text
  ])));
  updatePerformance();
  showReview();
}

let current;
for (const {name} of dataset) {
  const title = name.replace(/^\d+[a-z]?_/, '').replaceAll('_', ' ');
  scenarioSelect.add(new Option(title[0].toUpperCase() + title.slice(1), name));
}
scenarioSelect.addEventListener('change', updateScenario);
skillSelect.addEventListener('change', updatePerformance);
byId('run').addEventListener('click', () => {
  showReview(true);
  byId('priorities').scrollIntoView({block: 'nearest'});
});
byId('download').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify(current.report, null, 2) + '\n'], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const link = node('a');
  link.href = url;
  link.download = 'balancecheck-' + current.scenario.name + '.json';
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
function updateNavigation() {
  const hash = location.hash || '#overview';
  for (const link of document.querySelectorAll('nav a')) {
    const active = link.hash === hash;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
}
window.addEventListener('hashchange', updateNavigation);
updateNavigation();
updateScenario();
