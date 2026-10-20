# AI Economist Lab — Offline classroom demo

A **deterministic simulation** of LLM-only, tool use, ReAct, harness/recovery, skills, and memory. It does **not** run an LLM. It *does* run real Python tools, validate inputs, enforce a call budget, and chart a bundled historical dataset.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows, open PowerShell in the extracted folder and run the same commands (or use `py -m pip ...` and `py -m streamlit run app.py`). A browser opens automatically.

## Teaching sequence (10–15 minutes)

1. Run **LLM only**: observe that no evidence is checked.
2. Run **LLM + tools**: see real data retrieval and calculations.
3. Run **ReAct loop**: compare plan/action/observation/verification events.
4. Run **Harness + recovery** with injected error: show invalid `YYYY` dates rejected, then repaired. Reduce call budget to 1 to show a halted run.
5. Run **Skills + memory**: save a preference in the sidebar and run again; inspect `skills/economic_analysis/SKILL.md`.
6. Switch scenarios and compare data outputs. Ask students which decisions were simulated versus executed.

## Data provenance

`data/unemployment.csv` contains a *small selected excerpt* of historical monthly U.S. unemployment-rate observations (seasonally adjusted), based on BLS series LNS14000000 / FRED `UNRATE`. **The file is not a complete time series**. It includes the windows used in the demo. The app displays the actual observation count for each window. For the complete current dataset, see https://fred.stlouisfed.org/series/UNRATE .

## Safety and limitations

No external network calls, API keys, arbitrary Python execution, or autonomous actions. Model responses and action selection are scripted for pedagogy. Skill instructions are displayed, not dynamically executed. Memory is session-only. A live agent would require an LLM API, structured tool-call protocol, secure execution, and stronger permissions.
