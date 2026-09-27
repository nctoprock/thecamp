/**
 * THE PRAEDIUM GROUP — Agent Score Card automation
 *
 * Paste this whole file into the Score Card Google Sheet:
 *   Extensions → Apps Script → replace Code.gs → Save → reload the sheet.
 * A "Score Card" menu appears. Run, in order:
 *   1. Rename tabs from Settings
 *   2. Share & protect tabs        (emails each agent a Google share invite)
 *   3. Install weekly email triggers
 *
 * Layout constants below must match build_scorecard.py.
 */

var SETTINGS_SHEET = 'Settings';
var DASHBOARD_SHEET = 'Dashboard';
var AGENT_ROW0 = 14;        // first agent row on Settings
var NUM_AGENTS = 7;
var SC_HEADER_ROW = 14;     // weekly table header row on each Scorecard tab
var SC_FIRST_DATA = 15;

// Scorecard columns (1-based)
var C = {
  WEEK: 1, DAYS: 2, HOURS: 3, COMM_HOURS: 4, PROSP_HOURS: 5, CALLS: 6, CONVOS: 7, MEETINGS: 8,
  OPPS: 9, DB: 10, FOLLOWUPS: 11, MC: 12, SPHERE: 13, LISTINGS: 14, ASSIGNMENTS: 15, LOIS: 16,
  UC: 17, CLOSINGS: 18, VOLUME: 19, GCI: 20, PIPELINE: 21, WIN: 22, OBSTACLE: 23, FOCUS: 24,
  UPDATED: 25, STATUS: 26
};
var FIRST_INPUT_COL = C.DAYS, LAST_INPUT_COL = C.FOCUS;

var NAVY = '#1F3A5F', GOLD = '#C9A227';

/* ------------------------------------------------------------------ menu */

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Score Card')
    .addItem('LAUNCH: share + send each agent their personal link', 'launch')
    .addSeparator()
    .addItem('1. Rename tabs from Settings', 'renameTabsFromSettings')
    .addItem('2. Share & protect tabs', 'shareAndProtect')
    .addItem('3. Install weekly email triggers', 'installTriggers')
    .addSeparator()
    .addItem('Send agent reminders now', 'sendAgentReminders')
    .addItem('Send me the team summary now', 'sendOwnerSummary')
    .addItem('Preview: send me one agent reminder', 'sendTestReminderToOwner')
    .addSeparator()
    .addItem('Remove all email triggers', 'removeTriggers')
    .addToUi();
}

/** Stamps "Last Updated" whenever an agent edits their weekly row. */
function onEdit(e) {
  var sh = e.range.getSheet();
  if (!/ Scorecard$/.test(sh.getName())) return;
  var r0 = e.range.getRow(), r1 = e.range.getLastRow();
  var c0 = e.range.getColumn(), c1 = e.range.getLastColumn();
  if (r1 < SC_FIRST_DATA || c1 < FIRST_INPUT_COL || c0 > LAST_INPUT_COL) return;
  var now = new Date();
  for (var r = Math.max(r0, SC_FIRST_DATA); r <= r1; r++) {
    sh.getRange(r, C.UPDATED).setValue(now);
  }
}

/* ---------------------------------------------------------------- config */

function cfg_() {
  var ss = SpreadsheetApp.getActive();
  var s = ss.getSheetByName(SETTINGS_SHEET);
  var v = s.getRange('C4:C11').getValues().map(function (r) { return r[0]; });
  return {
    ss: ss,
    tz: ss.getSpreadsheetTimeZone(),
    ownerName: String(v[0] || 'Team Lead'),
    ownerEmail: String(v[1] || Session.getEffectiveUser().getEmail()).trim(),
    team: String(v[2] || 'The Praedium Group'),
    reminderDay: String(v[3] || 'FRIDAY').toUpperCase(),
    reminderHour: Number(v[4] === '' ? 9 : v[4]),
    summaryDay: String(v[5] || 'MONDAY').toUpperCase(),
    summaryHour: Number(v[6] === '' ? 7 : v[6]),
    nudge: String(v[7]).toLowerCase() !== 'no'
  };
}

function agents_() {
  var s = SpreadsheetApp.getActive().getSheetByName(SETTINGS_SHEET);
  var rows = s.getRange(AGENT_ROW0, 1, NUM_AGENTS, 6).getValues();
  return rows.map(function (r, i) {
    return {
      num: i + 1, row: AGENT_ROW0 + i,
      name: String(r[1]).trim() || ('Agent ' + (i + 1)),
      email: String(r[2]).trim(),
      scorecardTab: String(r[3]).trim(),
      assessmentTab: String(r[4]).trim()
    };
  });
}

function activeAgents_() {
  return agents_().filter(function (a) { return a.email && /@/.test(a.email); });
}

/* ------------------------------------------------------- tabs & sharing */

function renameTabsFromSettings() {
  var ss = SpreadsheetApp.getActive();
  var s = ss.getSheetByName(SETTINGS_SHEET);
  var changed = [];
  agents_().forEach(function (a) {
    var nm = String(s.getRange(a.row, 2).getValue()).trim();
    if (!nm) return;
    var wantSc = nm + ' Scorecard', wantAs = nm + ' Assessment';
    var sc = ss.getSheetByName(a.scorecardTab), as = ss.getSheetByName(a.assessmentTab);
    if (sc && a.scorecardTab !== wantSc) { sc.setName(wantSc); changed.push(wantSc); }
    if (as && a.assessmentTab !== wantAs) { as.setName(wantAs); changed.push(wantAs); }
    s.getRange(a.row, 4, 1, 2).setValues([[wantSc, wantAs]]);
  });
  toast_(changed.length ? 'Renamed: ' + changed.join(', ') : 'Nothing to rename.');
}

/**
 * Shares the workbook with every agent (editor) and locks it down so each
 * agent can edit ONLY the yellow cells on their own two tabs.
 * Note: anyone the file is shared with can still VIEW every tab.
 */
function shareAndProtect() {
  var c = cfg_(), ss = c.ss;
  var list = activeAgents_();
  if (!list.length) { toast_('Add agent emails on Settings first.'); return; }
  var me = Session.getEffectiveUser().getEmail();

  list.forEach(function (a) {
    if (a.email.toLowerCase() !== me.toLowerCase()) ss.addEditor(a.email);
  });

  // Clear old protections this script created
  ss.getProtections(SpreadsheetApp.ProtectionType.SHEET).concat(ss.getProtections(SpreadsheetApp.ProtectionType.RANGE))
    .forEach(function (p) { if (/^ScoreCard:/.test(p.getDescription())) p.remove(); });

  var ownerOnly = function (prot) {
    prot.removeEditors(prot.getEditors());
    prot.addEditor(me);
    if (prot.canDomainEdit()) prot.setDomainEdit(false);
    return prot;
  };

  // Owner-only tabs
  ['Start Here', DASHBOARD_SHEET, SETTINGS_SHEET].forEach(function (n) {
    var sh = ss.getSheetByName(n);
    if (sh) ownerOnly(sh.protect().setDescription('ScoreCard:' + n));
  });

  list.forEach(function (a) {
    var sc = ss.getSheetByName(a.scorecardTab), as = ss.getSheetByName(a.assessmentTab);
    [sc, as].forEach(function (sh) {
      if (!sh) return;
      var p = sh.protect().setDescription('ScoreCard:' + sh.getName());
      p.removeEditors(p.getEditors());
      p.addEditors([me, a.email]);
      if (p.canDomainEdit()) p.setDomainEdit(false);
    });
    if (sc) {
      // formulas/labels inside the agent's own tab stay owner-only
      ownerOnly(sc.getRange(1, 1, SC_HEADER_ROW, sc.getMaxColumns()).protect().setDescription('ScoreCard:hdr ' + a.num));
      ownerOnly(sc.getRange(SC_FIRST_DATA, C.WEEK, sc.getMaxRows() - SC_HEADER_ROW, 1).protect().setDescription('ScoreCard:wk ' + a.num));
      ownerOnly(sc.getRange(SC_FIRST_DATA, C.STATUS, sc.getMaxRows() - SC_HEADER_ROW, 1).protect().setDescription('ScoreCard:st ' + a.num));
    }
    if (as) {
      ownerOnly(as.getRange('A1:F3').protect().setDescription('ScoreCard:ahdr ' + a.num));
      ownerOnly(as.getRange('A:B').protect().setDescription('ScoreCard:alab ' + a.num));
      ownerOnly(as.getRange('F:F').protect().setDescription('ScoreCard:aflag ' + a.num));
    }
  });
  toast_('Shared with ' + list.length + ' agent(s) and protected.');
}

/* --------------------------------------------------------------- launch */

/** One click: share + protect, install weekly triggers, email each agent their own links. */
function launch() {
  var ui = SpreadsheetApp.getUi();
  var list = activeAgents_();
  var ok = ui.alert('Launch Score Card',
    'This will share the sheet with ' + list.length + ' people, lock each person to their own tabs, turn on the weekly emails, ' +
    'and send each person a welcome email with a link to THEIR scorecard:\n\n' +
    list.map(function (a) { return '• ' + a.name + ' <' + a.email + '>'; }).join('\n') + '\n\nContinue?',
    ui.ButtonSet.YES_NO);
  if (ok !== ui.Button.YES) return;
  shareAndProtect();
  installTriggers();
  sendWelcomeEmails_();
  ui.alert('Done — welcome emails sent to ' + list.length + ' people. Weekly reminders are on.');
}

function sendWelcomeEmails_() {
  var c = cfg_(), ss = c.ss;
  activeAgents_().forEach(function (a) {
    var sc = ss.getSheetByName(a.scorecardTab), as = ss.getSheetByName(a.assessmentTab);
    var scUrl = ss.getUrl() + '#gid=' + (sc ? sc.getSheetId() : '');
    var asUrl = ss.getUrl() + '#gid=' + (as ? as.getSheetId() : '');
    var first = a.name.split(' ')[0];
    var html = wrap_(c, 'Hi ' + esc_(first) + ',',
      '<p>I\'m rolling out the <b>Praedium Agent Score Card</b> — a tool to help each of us stay accountable, see where our time ' +
      'is going, and make sure I\'m giving you the right support to grow your commercial business.</p>' +
      '<p><b>This is not a report card.</b> There are no wrong answers, and estimates are completely fine.</p>' +
      '<p>These links open directly to <b>your</b> tabs — bookmark them:</p>' +
      '<p><b>1. Your Growth Assessment (one time)</b> — a snapshot of your business today. Please complete it before our next meeting. ' +
      'Your Q4 goals in Section 13 automatically feed your progress tracker.</p>' +
      button_(asUrl, 'Open my Assessment') +
      '<p><b>2. Your Weekly Scorecard</b> — one row per week. Please update your row by end of day every Friday (about 5 minutes).</p>' +
      button_(scUrl, 'Open my Weekly Scorecard') +
      '<ul style="font-size:13px"><li>Only fill in the <b>yellow cells</b> — everything else calculates automatically.</li>' +
      '<li>You can only edit your own tabs, so you can\'t break anyone else\'s.</li>' +
      '<li>You\'ll get a reminder each Friday with a direct link to your scorecard.</li>' +
      '<li>See the <b>Start Here</b> tab for what counts in each column.</li></ul>' +
      '<p style="font-size:13px">If a link asks you to request access, make sure you\'re signed in to Google as <b>' + esc_(a.email) + '</b>.</p>' +
      '<p>Questions? Reach out anytime. Looking forward to seeing everyone\'s progress this quarter.</p>');
    MailApp.sendEmail({ to: a.email, subject: 'Your Praedium Agent Score Card — personal links inside',
      htmlBody: html, name: c.ownerName, replyTo: c.ownerEmail });
  });
}

/* ------------------------------------------------------------- triggers */

var HANDLERS = ['sendAgentReminders', 'sendOwnerSummary', 'sendLateNudges'];

function installTriggers() {
  removeTriggers(true);
  var c = cfg_();
  var wd = function (d) { return ScriptApp.WeekDay[d] || ScriptApp.WeekDay.FRIDAY; };
  ScriptApp.newTrigger('sendAgentReminders').timeBased().onWeekDay(wd(c.reminderDay))
    .atHour(c.reminderHour).inTimezone(c.tz).create();
  ScriptApp.newTrigger('sendOwnerSummary').timeBased().onWeekDay(wd(c.summaryDay))
    .atHour(c.summaryHour).inTimezone(c.tz).create();
  if (c.nudge) {
    ScriptApp.newTrigger('sendLateNudges').timeBased().onWeekDay(ScriptApp.WeekDay.MONDAY)
      .atHour(9).inTimezone(c.tz).create();
  }
  toast_('Triggers installed: agent reminders ' + c.reminderDay + ' ~' + c.reminderHour + ':00, owner summary '
    + c.summaryDay + ' ~' + c.summaryHour + ':00' + (c.nudge ? ', late nudges MONDAY ~9:00' : '') + ' (' + c.tz + ').');
}

function removeTriggers(silent) {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (HANDLERS.indexOf(t.getHandlerFunction()) >= 0) ScriptApp.deleteTrigger(t);
  });
  if (silent !== true) toast_('Email triggers removed.');
}

/* ------------------------------------------------------------- week math */

function mondayOf_(d) {
  var x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  var dow = (x.getDay() + 6) % 7; // Mon=0
  x.setDate(x.getDate() - dow);
  return x;
}

/** Week being reported on: this week on Thu–Sun, otherwise last week. */
function reportWeek_() {
  var today = new Date(), m = mondayOf_(today);
  var dow = (today.getDay() + 6) % 7;
  if (dow < 3) m.setDate(m.getDate() - 7);
  return m;
}

function key_(d, tz) { return Utilities.formatDate(d, tz, 'yyyy-MM-dd'); }

/** Returns {row, values[], updated} for the given Monday on an agent's scorecard. */
function weekRow_(sh, monday, tz) {
  var n = sh.getLastRow() - SC_FIRST_DATA + 1;
  if (n < 1) return null;
  var dates = sh.getRange(SC_FIRST_DATA, C.WEEK, n, 1).getValues();
  var want = key_(monday, tz);
  for (var i = 0; i < n; i++) {
    if (dates[i][0] instanceof Date && key_(dates[i][0], tz) === want) {
      var row = SC_FIRST_DATA + i;
      var vals = sh.getRange(row, 1, 1, C.STATUS).getValues()[0];
      return { row: row, values: vals, updated: vals[C.UPDATED - 1] !== '' };
    }
  }
  return null;
}

function agentSnapshot_(a, monday, c) {
  var ss = c.ss;
  var sc = ss.getSheetByName(a.scorecardTab), as = ss.getSheetByName(a.assessmentTab);
  var snap = { agent: a, sc: sc, as: as, week: null, assessPct: 0, q4: {}, consistency: 0, pipeline: '' };
  if (!sc) return snap;
  snap.week = weekRow_(sc, monday, c.tz);
  var q4 = sc.getRange('C6:D12').getValues();
  snap.q4 = { gciGoal: q4[0][0], gci: q4[0][1], closingsGoal: q4[2][0], closings: q4[2][1] };
  var k = sc.getRange('K5:K11').getValues();
  snap.consistency = k[2][0]; snap.pipeline = k[5][0]; snap.assessPct = k[6][0];
  snap.url = ss.getUrl() + '#gid=' + sc.getSheetId();
  snap.assessUrl = as ? ss.getUrl() + '#gid=' + as.getSheetId() : snap.url;
  return snap;
}

/* ---------------------------------------------------------------- emails */

function sendAgentReminders() {
  var c = cfg_(), monday = mondayOf_(new Date());
  activeAgents_().forEach(function (a) {
    var s = agentSnapshot_(a, monday, c);
    sendReminder_(a.email, a, s, c, monday, false);
  });
}

function sendTestReminderToOwner() {
  var c = cfg_(), list = agents_(), monday = mondayOf_(new Date());
  var s = agentSnapshot_(list[0], monday, c);
  sendReminder_(c.ownerEmail, list[0], s, c, monday, false);
  toast_('Preview sent to ' + c.ownerEmail);
}

function sendLateNudges() {
  var c = cfg_(), last = mondayOf_(new Date());
  last.setDate(last.getDate() - 7);
  activeAgents_().forEach(function (a) {
    var s = agentSnapshot_(a, last, c);
    if (s.week && !s.week.updated) sendReminder_(a.email, a, s, c, last, true);
  });
}

function sendReminder_(to, a, s, c, monday, late) {
  var wk = Utilities.formatDate(monday, c.tz, 'MMM d');
  var first = a.name.split(' ')[0];
  var subject = late
    ? 'Reminder: your Score Card for the week of ' + wk + ' is still open'
    : 'Weekly Score Card — please update for the week of ' + wk;
  var done = s.week && s.week.updated;
  var lines = [];
  lines.push(late
    ? 'Your Score Card row for the week of <b>' + wk + '</b> hasn’t been filled in yet. Please take 5 minutes today to catch it up.'
    : done
      ? 'Thanks — you’ve already started this week’s row. Please make sure it reflects the full week before the weekend.'
      : 'It’s Score Card time. Please take 5 minutes to fill in your row for the week of <b>' + wk + '</b>.');
  var html = wrap_(c, 'Hi ' + esc_(first) + ',',
    '<p>' + lines.join('</p><p>') + '</p>' +
    button_(s.url || c.ss.getUrl(), 'Open my Score Card') +
    '<table style="border-collapse:collapse;margin:16px 0;font-size:14px">' +
    kv_('Q4 GCI', money_(s.q4.gci) + (s.q4.gciGoal ? ' of ' + money_(s.q4.gciGoal) + ' goal' : ' (set your goal in the Assessment)')) +
    kv_('Q4 closings', num_(s.q4.closings) + (s.q4.closingsGoal ? ' of ' + s.q4.closingsGoal : '')) +
    kv_('Weekly consistency', pct_(s.consistency)) +
    kv_('Assessment complete', pct_(s.assessPct)) +
    '</table>' +
    (Number(s.assessPct) < 1
      ? '<p>Your Growth Assessment is ' + pct_(s.assessPct) + ' complete — <a href="' + s.assessUrl + '">finish it here</a> before our next meeting.</p>'
      : '') +
    '<p style="color:#6B7280;font-size:12px">Quick checklist: hours, calls/outreach, decision-maker conversations, meetings, new opportunities, ' +
    'Market Center conversations, pipeline GCI, and your win / obstacle / focus for next week.</p>');
  MailApp.sendEmail({ to: to, subject: subject, htmlBody: html, name: c.team + ' Score Card', replyTo: c.ownerEmail });
}

function sendOwnerSummary() {
  var c = cfg_(), monday = reportWeek_();
  var wk = Utilities.formatDate(monday, c.tz, 'MMM d, yyyy');
  var snaps = agents_().filter(function (a) { return a.email || a.name.indexOf('Agent ') !== 0; })
    .map(function (a) { return agentSnapshot_(a, monday, c); });
  if (!snaps.length) snaps = agents_().map(function (a) { return agentSnapshot_(a, monday, c); });

  var missing = snaps.filter(function (s) { return !(s.week && s.week.updated); })
    .map(function (s) { return esc_(s.agent.name); });
  var th = function (t) { return '<th style="background:' + NAVY + ';color:#fff;padding:6px 8px;font-size:12px;text-align:center">' + t + '</th>'; };
  var td = function (t, bg) { return '<td style="border:1px solid #E5E7EB;padding:6px 8px;font-size:12px;text-align:center;' + (bg ? 'background:' + bg : '') + '">' + t + '</td>'; };
  var tot = { hours: 0, calls: 0, convos: 0, meetings: 0, opps: 0, mc: 0, pipeline: 0, gci: 0 };
  var rows = snaps.map(function (s) {
    var v = s.week ? s.week.values : [];
    var g = function (col) { return v.length ? v[col - 1] : ''; };
    var n = function (col) { var x = Number(g(col)); return isNaN(x) ? 0 : x; };
    tot.hours += n(C.HOURS); tot.calls += n(C.CALLS); tot.convos += n(C.CONVOS); tot.meetings += n(C.MEETINGS);
    tot.opps += n(C.OPPS); tot.mc += n(C.MC); tot.pipeline += Number(s.pipeline) || 0; tot.gci += Number(s.q4.gci) || 0;
    var ok = s.week && s.week.updated;
    return '<tr>' +
      '<td style="border:1px solid #E5E7EB;padding:6px 8px;font-size:12px;font-weight:bold"><a href="' + (s.url || '#') + '">' + esc_(s.agent.name) + '</a></td>' +
      td(ok ? '✓' : '⚠ Missing', ok ? '#D1FAE5' : '#FEE2E2') +
      td(num_(g(C.HOURS))) + td(num_(g(C.CALLS))) + td(num_(g(C.CONVOS))) + td(num_(g(C.MEETINGS))) +
      td(num_(g(C.OPPS))) + td(num_(g(C.MC))) + td(money_(s.pipeline)) +
      td(money_(s.q4.gci) + (s.q4.gciGoal ? '<br><span style="color:#6B7280">of ' + money_(s.q4.gciGoal) + '</span>' : '')) +
      td(pct_(s.consistency)) + td(pct_(s.assessPct), Number(s.assessPct) < 1 ? '#FEF3C7' : '') +
      '</tr>';
  }).join('');
  var totalRow = '<tr style="font-weight:bold;background:#FBF6E5">' +
    '<td style="padding:6px 8px;font-size:12px">TEAM</td>' + td(snaps.length - missing.length + '/' + snaps.length) +
    td(num_(tot.hours)) + td(num_(tot.calls)) + td(num_(tot.convos)) + td(num_(tot.meetings)) + td(num_(tot.opps)) +
    td(num_(tot.mc)) + td(money_(tot.pipeline)) + td(money_(tot.gci)) + td('') + td('') + '</tr>';

  var notes = snaps.filter(function (s) { return s.week && (s.week.values[C.WIN - 1] || s.week.values[C.OBSTACLE - 1] || s.week.values[C.FOCUS - 1]); })
    .map(function (s) {
      var v = s.week.values;
      return '<p style="margin:10px 0;font-size:13px"><b>' + esc_(s.agent.name) + '</b><br>' +
        (v[C.WIN - 1] ? '🏆 ' + esc_(v[C.WIN - 1]) + '<br>' : '') +
        (v[C.OBSTACLE - 1] ? '🚧 ' + esc_(v[C.OBSTACLE - 1]) + '<br>' : '') +
        (v[C.FOCUS - 1] ? '🎯 ' + esc_(v[C.FOCUS - 1]) : '') + '</p>';
    }).join('');

  var dash = c.ss.getSheetByName(DASHBOARD_SHEET);
  var html = wrap_(c, 'Team Score Card — week of ' + wk,
    '<p>' + (missing.length ? '<b style="color:#991B1B">Not updated:</b> ' + missing.join(', ') : '<b style="color:#065F46">Everyone updated this week.</b>') + '</p>' +
    '<table style="border-collapse:collapse;margin:12px 0"><tr>' +
    th('Agent') + th('Updated') + th('Hours') + th('Calls') + th('DM Convos') + th('Meetings') + th('New Opps') +
    th('MC Convos') + th('Pipeline GCI') + th('Q4 GCI') + th('Consistency') + th('Assessment') +
    '</tr>' + rows + totalRow + '</table>' +
    (notes ? '<h3 style="color:' + NAVY + ';margin-top:20px">Wins · Obstacles · Next-week focus</h3>' + notes : '') +
    button_(c.ss.getUrl() + (dash ? '#gid=' + dash.getSheetId() : ''), 'Open Team Dashboard'));
  MailApp.sendEmail({ to: c.ownerEmail, subject: 'Team Score Card — week of ' + wk + (missing.length ? ' (' + missing.length + ' missing)' : ''),
    htmlBody: html, name: c.team + ' Score Card' });
}

/* --------------------------------------------------------------- helpers */

function wrap_(c, heading, body) {
  return '<div style="font-family:Arial,Helvetica,sans-serif;max-width:900px;color:#111827">' +
    '<div style="background:' + NAVY + ';color:#fff;padding:14px 18px;font-size:16px;font-weight:bold;border-bottom:4px solid ' + GOLD + '">' +
    esc_(c.team.toUpperCase()) + ' · AGENT SCORE CARD</div>' +
    '<div style="padding:16px 18px"><p style="font-size:15px"><b>' + heading + '</b></p>' + body +
    '<p style="margin-top:24px;font-size:13px">— ' + esc_(c.ownerName) + '</p></div></div>';
}
function button_(url, label) {
  return '<p><a href="' + url + '" style="display:inline-block;background:' + GOLD + ';color:#111827;padding:10px 18px;' +
    'text-decoration:none;font-weight:bold;border-radius:4px">' + label + '</a></p>';
}
function kv_(k, v) {
  return '<tr><td style="padding:4px 12px 4px 0;color:#6B7280">' + k + '</td><td style="padding:4px 0;font-weight:bold">' + v + '</td></tr>';
}
function esc_(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function num_(x) { return x === '' || x === null || x === undefined ? '—' : String(Math.round(Number(x) * 10) / 10); }
function money_(x) { var n = Number(x); return x === '' || isNaN(n) ? '—' : '$' + Math.round(n).toLocaleString('en-US'); }
function pct_(x) { var n = Number(x); return x === '' || isNaN(n) ? '—' : Math.round(n * 100) + '%'; }
function toast_(m) { SpreadsheetApp.getActive().toast(m, 'Score Card', 8); }
