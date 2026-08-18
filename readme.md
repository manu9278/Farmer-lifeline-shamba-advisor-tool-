# Shamba Advisor

A two-stage command-line tool that helps a smallholder farmer diagnose a
problem on their shamba (farm/plot) — a pest, poor yield, unhealthy crop,
soil issue, and so on — and turns that diagnosis into a practical, low-cost
plan they can start this week.

## The problem it solves

Many smallholder farmers don't have easy, immediate access to an
agricultural extension officer when something goes wrong with their crop.
This tool gives fast, structured first-pass advice by chaining two AI calls
together:

1. **Diagnosis call** – takes the farmer's plain-language description of
   their shamba and the problem, and returns a structured diagnosis: likely
   causes, urgency level, and a general recommended approach.
2. **Action Plan call** – takes that diagnosis plus the original description
   and turns it into a concrete, affordable plan: what to do this week, what
   materials are needed, and warning signs that mean the farmer should seek
   in-person help.

The two calls are connected: the second prompt is built using the JSON
output of the first, so the plan is grounded in the actual diagnosis rather
than generic farming advice.

**This tool gives general, first-pass guidance only. It is not a substitute
for advice from a qualified agricultural extension officer, especially for
urgent or high-value crops.**

## How it works

- Both prompts are written using the **R-T-C-C-O framework**
  (Role – Task – Context – Constraints – Output format), visible directly in
  `shamba_advisor.py`.
- Responses are requested as JSON and parsed with `json.loads()`; malformed
  JSON is caught and reported instead of crashing the program.
- Every run's full report (description + diagnosis + plan) is saved as a
  timestamped `.json` file inside `outputs/`.
- The API key is loaded from a `.env` file via `python-dotenv` and is never
  hard-coded or committed (see `.gitignore`).

## Setup

1. Clone the repo and move into it:
   ```bash
   git clone https://github.com/<your-org>/wca-ai-tool-s11-[GroupName].git
   cd wca-ai-tool-s11-[GroupName]
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create your `.env` file from the example and add your real key:
   ```bash
   cp .env.example .env
   # then edit .env and paste your key from https://aistudio.google.com/apikey
   ```
4. Run the tool:
   ```bash
   python shamba_advisor.py
   ```

## Using the tool

You'll see a menu:

```
================ SHAMBA ADVISOR ================
1. Diagnose a shamba problem and get an action plan
2. View previously saved reports
3. Exit
```

- **Option 1** asks you to describe your shamba and the problem (e.g. "my
  maize leaves are turning yellow, half-acre plot near Nakuru, planted 3
  weeks ago"), runs both API calls, prints the diagnosis and action plan to
  the terminal, and saves the full report to
  `outputs/shamba_report_<timestamp>.json`.
- **Option 2** lists every report you've saved so far.
- **Option 3** exits the program.

## Example input

```
My tomato plants are wilting even though I water them every morning.
Quarter-acre plot in Kiambu, planted about a month ago, leaves have
brown spots near the bottom of the plant.
```

## Error handling

The tool handles, without crashing:
- A failed/unreachable API call (network error, invalid key, rate limit).
- Empty user input (re-prompts instead of sending a blank description to
  the API).
- Malformed JSON returned by the model (reports the issue and shows the raw
  reply instead of crashing).

## Project structure

```
shamba_advisor.py   # main program (both API calls, menu, file saving)
requirements.txt    # dependencies
.env.example         # template for your API key file
.gitignore           # keeps .env and outputs/ out of version control
outputs/             # generated reports (created automatically on first run)
```

## Team

| Name | GitHub handle | Contribution |
|------|----------------|---------------|
| [Member 1] | @handle | |
| [Member 2] | @handle | |
| [Member 3] | @handle | |

## Model used

This tool uses the Google Gemini API (`gemini-3.5-flash`).
