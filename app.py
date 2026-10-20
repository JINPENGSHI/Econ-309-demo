import streamlit as st
from pathlib import Path
from agent import run_scenario, SCENARIOS

st.set_page_config(page_title='ECON 309 AI Demo', page_icon='📈', layout='wide')
st.title('📈 ECON 309 AI Demo')
st.caption('Offline, deterministic classroom demonstration — no API key, no real LLM inference.')
st.info('This app **simulates** LLM and agent choices using a predefined script. Tool calls, validation, data loading, and calculations execute for real. A trace is not private model chain-of-thought.')

with st.sidebar:
    st.header('Configure the demo')
    mode = st.radio('Capability mode', ['LLM only','LLM + tools','ReAct loop','Harness + recovery','Skills + memory'], index=2)
    scenario = st.selectbox('Economic research task',list(SCENARIOS))
    inject_error = st.checkbox('Inject invalid tool arguments',value=True,disabled=mode not in ('Harness + recovery','Skills + memory'))
    max_calls = st.slider('Harness tool-call budget',1,8,6)
    st.divider()
    st.write('**Session memory**')
    preference = st.selectbox('Preferred output style',['Brief summary','Detailed explanation','Emphasize graphs'])
    if st.button('Save preference to memory'):
        st.session_state['preference'] = preference
        st.success('Saved for this browser session')
    if st.button('Clear memory'):
        st.session_state.pop('preference',None)
        st.success('Cleared')
    st.caption('Memory is Streamlit session state, not a vector database.')

mode_notes = {
 'LLM only':'Scripted language output without verification or external actions.',
 'LLM + tools':'Fixed script invokes real, allowlisted Python functions.',
 'ReAct loop':'Scripted plan → action → observation → verification sequence.',
 'Harness + recovery':'Real validation and tool-call budget; scripted error recovery.',
 'Skills + memory':'Adds a reusable checklist and a saved session preference.'
}
st.subheader(mode)
st.write(mode_notes[mode])
start,end=SCENARIOS[scenario]
st.markdown(f'**Research goal:** Describe the change in U.S. unemployment between **{start}** and **{end}**.')
if st.button('▶ Run demonstration',type='primary'):
    st.session_state['run'] = run_scenario(scenario,mode,inject_error,max_calls,
                                          skill=mode=='Skills + memory',
                                          memory=st.session_state.get('preference') if mode=='Skills + memory' else None)
    st.session_state['run_signature']=(mode,scenario,inject_error,max_calls)

run=st.session_state.get('run')
if run:
    if st.session_state.get('run_signature') != (mode,scenario,inject_error,max_calls):
        st.warning('Settings changed. Press Run demonstration to refresh the trace.')
    left,right=st.columns([1.1,1])
    with left:
        st.subheader('Observable execution trace')
        for i,item in enumerate(run['trace'],1):
            with st.expander(f'{i:02d} · {item["phase"]}: {item["description"]}', expanded=True):
                if item['detail']: st.write(item['detail'])
        st.subheader('Harness audit log')
        if run['harness']:
            st.dataframe(run['harness'],use_container_width=True,hide_index=True)
        else:
            st.caption('No tools were called.')
    with right:
        st.subheader('Data and result')
        if run['summary']:
            summary=run['summary']
            c1,c2=st.columns(2)
            c1.metric('Change',f'{summary["change_pp"]:+.1f} pp')
            c2.metric('Peak in window',f'{summary["peak"]:.1f}%',summary['peak_date'],delta_color='off')
        if run['rows'] is not None:
            rows=run['rows'].set_index('date')
            st.line_chart(rows['unemployment_rate'],y_label='Unemployment rate (%)',x_label='Month')
            with st.expander('Inspect actual observations'):
                st.dataframe(rows,use_container_width=True)
        else:
            st.warning('No verified data output in this mode/run.')
        st.caption('Source: BLS unemployment rate (LNS14000000), mirrored in FRED as UNRATE. The bundled CSV is a small, historical classroom excerpt.')

with st.expander('What are the concepts?'):
    st.markdown('''**GPT / transformer:** A trained model for processing token sequences; this demo does not execute one.  
**Tool:** A callable Python function that fetches or calculates data.  
**ReAct:** An iterative pattern of acting, observing, and deciding what to do next; here its choices are pre-scripted.  
**Harness:** The software that validates requests, enforces budgets, records events, and handles failures.  
**Skill:** Reusable instructions for a task type.  
**Memory:** Stored context carried across interactions; here, a preference in session state.  
**Chain-of-thought:** Private model reasoning is not exposed; the visible plan is an explanatory summary.''')
    st.markdown('**Discuss:** Which actions are truly executed? Which choices are pre-scripted? What would a live model add? What risks would that introduce?')
    st.code((Path(__file__).parent/'skills/economic_analysis/SKILL.md').read_text(),language='markdown')
