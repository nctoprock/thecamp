# Praedium Group — Agent Score Card

A Google Sheet for 7 agents. Each agent fills in a one-time **Growth Assessment** and updates a **Weekly Scorecard**. You get a live **Dashboard**. Automated emails go out each week:

| Email | To | When (default) |
|---|---|---|
| "Please update your Score Card" + link to their tab | Each agent | Friday ~9 AM |
| Nudge if last week's row is still blank | Only agents who missed | Monday ~9 AM |
| Team summary: who updated, key numbers, wins/obstacles | You | Monday ~7 AM |

## Files

| File | What it is |
|---|---|
| `Praedium_Agent_Score_Card.xlsx` | The shared workbook: Start Here, Dashboard, Settings, and a Scorecard tab plus an Assessment tab for each of the 7 agents |
| `Praedium_Development_Review_PRIVATE.xlsx` | Your post-meeting review (scores 1–5 and 30/90-day objectives). It's a **separate file** because agents can view every tab of a shared sheet. Don't share it. |
| `Code.gs` | Apps Script for the email reminders, weekly summary, sharing, tab protection, and the auto "Last Updated" stamp |
| `build_scorecard.py` | Regenerates both .xlsx files (`pip install openpyxl && python3 build_scorecard.py`) |

## Setup (about 10 minutes)

1. **Upload:** In Google Drive, go to New → File upload and pick `Praedium_Agent_Score_Card.xlsx`. Open it and choose **File → Save as Google Sheets**. Work in the Google Sheets copy from here on.
2. **Settings tab:** Enter each agent's name, email, and Market Center. Check your email and the reminder days and hours.
3. **Script:** Go to **Extensions → Apps Script**. Delete the starter code, paste all of `Code.gs`, and save. Under Project Settings (gear icon), set the time zone to yours. Reload the sheet, and a **Score Card** menu appears.
4. From the **Score Card** menu, run in order. Google will ask you to authorize the script the first time.
   1. **Rename tabs from Settings**. "Agent 1 Scorecard" becomes "Jane Smith Scorecard", and so on.
   2. **Share & protect tabs**. This shares the sheet with each agent, and Google emails them an invite. Each agent can edit only the yellow cells on their own tabs.
   3. **Install weekly email triggers**
5. Optional: run **Preview: send me one agent reminder** to see what agents will receive.

If you change the schedule on Settings later, run **Install weekly email triggers** again.

## How it works

- **Weekly Scorecard:** One row per week (Monday dates) from Sep 28, 2026 through Dec 2027. It tracks hours, calls, decision-maker conversations, meetings, new opportunities, database adds, open follow-ups, Market Center conversations, sphere touches, listings, assignments, LOIs, contracts, closings, volume, GCI, pipeline GCI, and win / obstacle / next-week focus.
- **Q4 progress:** This pulls the goals from Section 13 of the agent's Assessment and compares them to actual results, with an On pace / Behind flag.
- **Status column:** Shows ✓ Updated, Due Friday, ⚠ Missing, or Upcoming. "Last Updated" is stamped automatically when an agent edits a row.
- **Dashboard:** One row per agent for any week. Change the "Week of" date to look at a past week. It shows assessment completion, consistency %, Q4 GCI against goal, and more.

## Privacy note

Everyone the sheet is shared with can **view** every tab, including other agents' numbers and assessment answers. Protection only controls who can **edit**. If agents shouldn't see each other's data, the setup can be switched to one file per agent that feeds your master dashboard.
