from __future__ import annotations

import streamlit as st

from streamlit_ui.client import ApiClient, ApiClientError

FLAG_STATUS_OPTIONS = ['pending', 'relevant', 'irrelevant']


st.set_page_config(
    page_title='Content Monitoring & Flagging',
    page_icon='🛡️',
    layout='wide',
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .metric-card {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 16px;
        padding: 1rem;
        background: rgba(14, 17, 23, 0.02);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False, ttl=5)
def fetch_flags(base_url: str) -> list[dict]:
    return ApiClient(base_url=base_url).list_flags()


@st.dialog('Request failed')
def show_api_error(error_message: str) -> None:
    st.error(error_message)


st.title('🛡️ Content Monitoring & Flagging System')
st.caption('A clean Streamlit control panel for managing keywords, triggering scans, and reviewing flags.')

with st.sidebar:
    st.header('Configuration')
    api_base_url = st.text_input('Backend API URL', value='http://127.0.0.1:8000')
    request_timeout = st.slider('Request timeout (seconds)', min_value=5, max_value=60, value=10)
    st.markdown('---')
    st.markdown(
        'Use this UI to add keywords, run scans against the mock dataset, and review flags from the Django API.'
    )

client = ApiClient(base_url=api_base_url, timeout=request_timeout)

def load_flags() -> list[dict]:
    try:
        return client.list_flags()
    except ApiClientError as exc:
        show_api_error(str(exc))
        return []


flags = load_flags()
pending_flags = sum(flag['status'] == 'pending' for flag in flags)
relevant_flags = sum(flag['status'] == 'relevant' for flag in flags)
irrelevant_flags = sum(flag['status'] == 'irrelevant' for flag in flags)

metric_columns = st.columns(4)
metric_columns[0].metric('Total Flags', len(flags))
metric_columns[1].metric('Pending Review', pending_flags)
metric_columns[2].metric('Relevant', relevant_flags)
metric_columns[3].metric('Irrelevant', irrelevant_flags)

summary_tab, keywords_tab, scan_tab, flags_tab = st.tabs(
    ['Overview', 'Keywords', 'Scan Control', 'Flag Review']
)

with summary_tab:
    st.subheader('System Overview')
    st.write(
        'This dashboard surfaces the current review queue and lets operators quickly run scans and manage flag states.'
    )
    if flags:
        st.dataframe(
            [
                {
                    'Flag ID': flag['id'],
                    'Keyword': flag['keyword']['name'],
                    'Content Item': flag['content_item'],
                    'Score': flag['score'],
                    'Status': flag['status'],
                    'Last Reviewed At': flag['last_reviewed_at'],
                }
                for flag in flags
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info('No flags found yet. Add a keyword and trigger a scan to populate results.')

with keywords_tab:
    st.subheader('Create Monitoring Keyword')
    with st.form('create-keyword-form', clear_on_submit=True):
        keyword_name = st.text_input('Keyword name', placeholder='e.g. alert')
        submitted = st.form_submit_button('Add keyword', use_container_width=True)

    if submitted:
        if not keyword_name.strip():
            st.warning('Please enter a keyword name before submitting.')
        else:
            try:
                created_keyword = client.create_keyword(keyword_name.strip())
            except ApiClientError as exc:
                show_api_error(str(exc))
            else:
                fetch_flags.clear()
                st.success(f"Keyword created: {created_keyword['name']}")

with scan_tab:
    st.subheader('Trigger Scan Workflow')
    dataset_path = st.text_input(
        'Optional dataset override',
        placeholder='Leave blank to use content_monitoring/data/mock_content.json',
    )
    st.write(
        'Run the scan workflow to load content records, apply keyword matching, and update the current flag queue.'
    )
    if st.button('Run scan', type='primary', use_container_width=True):
        try:
            summary = client.trigger_scan(dataset_path.strip() or None)
        except ApiClientError as exc:
            show_api_error(str(exc))
        else:
            fetch_flags.clear()
            st.success('Scan completed successfully.')
            st.json(summary)

with flags_tab:
    st.subheader('Review Flags')
    st.write('Refresh the queue, inspect each flag, and update the review status directly from the dashboard.')
    if st.button('Refresh flags', use_container_width=False):
        fetch_flags.clear()
        st.rerun()

    if not flags:
        st.info('No flags available for review.')
    else:
        for flag in flags:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.markdown(
                    f"**Keyword:** {flag['keyword']['name']}  \n"
                    f"**Content Item ID:** {flag['content_item']}  \n"
                    f"**Score:** {flag['score']}"
                )
                col2.metric('Status', flag['status'].title())
                col3.metric('Reviewed At', flag['last_reviewed_at'] or 'Not reviewed')

                new_status = st.selectbox(
                    'Update status',
                    FLAG_STATUS_OPTIONS,
                    index=FLAG_STATUS_OPTIONS.index(flag['status']),
                    key=f"status-{flag['id']}",
                )
                if st.button('Save status', key=f"save-{flag['id']}"):
                    try:
                        client.update_flag_status(flag['id'], new_status)
                    except ApiClientError as exc:
                        show_api_error(str(exc))
                    else:
                        fetch_flags.clear()
                        st.success(f"Updated flag #{flag['id']} to {new_status}.")
                        st.rerun()
