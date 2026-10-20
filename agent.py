"""Deterministic teaching trace, NOT an LLM or autonomous decision maker."""
from harness import Harness
from tools import summarize_period

SCENARIOS = {
 'Great Recession': ('2007-01', '2009-10'),
 'COVID-19 shock': ('2020-02', '2020-04'),
 'Recovery comparison': ('2009-10', '2012-10'),
}

def run_scenario(scenario, mode, inject_error=False, max_calls=6, skill=False, memory=None):
    start, end = SCENARIOS[scenario]
    harness = Harness(max_calls=max_calls)
    trace = []
    def event(phase, description, detail=''):
        trace.append({'phase':phase,'description':description,'detail':detail})
    event('GOAL', f'Analyze unemployment from {start} to {end}.')
    if mode == 'LLM only':
        event('MODEL OUTPUT', 'A model might produce a fluent response from learned patterns.',
              'No tools were called. No dataset was checked. This is scripted text, not model inference.')
        return {'trace':trace,'harness':harness.events,'summary':None,'rows':None}
    if skill:
        event('SKILL', 'Load economic_analysis/SKILL.md',
              'Instructions: use source data; compute percentage-point differences; report units; verify dates.')
    if memory:
        event('MEMORY', 'Read saved session preference', str(memory))
    if mode in ('ReAct loop','Harness + recovery','Skills + memory'):
        event('PLAN', 'Retrieve the observations, inspect them, calculate change, and verify units.',
              'This is a scripted, public-facing plan—not private chain-of-thought.')
    if inject_error and mode in ('Harness + recovery','Skills + memory'):
        event('ACTION', 'get_unemployment_data(start="2007", end="2009")', 'Intentionally invalid format')
        harness.execute('get_unemployment_data',start='2007',end='2009')
        event('OBSERVATION', 'Harness rejects the invalid dates.', harness.events[-1]['message'])
        event('RETRY', 'Correct date format to YYYY-MM.', f'Use {start} and {end}')
    event('ACTION', f'get_unemployment_data(start="{start}", end="{end}")')
    rows = harness.execute('get_unemployment_data',start=start,end=end)
    if rows is None:
        event('STOP', 'Execution stopped: data unavailable or budget exhausted.')
        return {'trace':trace,'harness':harness.events,'summary':None,'rows':None}
    event('OBSERVATION', f'Retrieved {len(rows)} monthly observations.',
          f'First: {rows.iloc[0].unemployment_rate:.1f}%; last: {rows.iloc[-1].unemployment_rate:.1f}%')
    event('ACTION', 'calculate_change(first, last)')
    change = harness.execute('calculate_change',first=float(rows.iloc[0].unemployment_rate),last=float(rows.iloc[-1].unemployment_rate))
    if change is None:
        event('STOP', 'Execution stopped: calculation unavailable or budget exhausted.')
        return {'trace':trace,'harness':harness.events,'summary':None,'rows':rows}
    summary = summarize_period(rows)
    event('OBSERVATION', f'Change = {change:+.1f} percentage points.')
    if mode in ('ReAct loop','Harness + recovery','Skills + memory'):
        event('VERIFY', 'Check that the result is in percentage points, not percent.',
              f'{summary["last"]:.1f} - {summary["first"]:.1f} = {change:+.1f} pp')
    event('FINAL', f'Unemployment changed by {change:+.1f} percentage points.',
          f'Peak within selected period: {summary["peak"]:.1f}% ({summary["peak_date"]}).')
    return {'trace':trace,'harness':harness.events,'summary':summary,'rows':rows}
