import streamlit as st
import anthropic

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="First Gen Navigator",
    page_icon="🎓",
    layout="centered"
)

# ── Claude client using Streamlit secrets ────────────────────────────────────
client = anthropic.Anthropic(
    api_key=st.secrets["ANTHROPIC_API_KEY"]
)

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { max-width: 720px; }
    .stChatMessage { border-radius: 12px; }

    .tagline {
        font-size: 15px;
        color: #666;
        margin-bottom: 24px;
        line-height: 1.6;
    }

    .badge {
        display: inline-block;
        background: #E1F5EE;
        color: #085041;
        font-size: 12px;
        padding: 3px 12px;
        border-radius: 20px;
        margin-bottom: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="badge">First Gen Navigator</div>',
    unsafe_allow_html=True
)

st.title("🎓 Your College Guide")

st.markdown(
    """
    <p class="tagline">
    No question is too basic here. Whether you are figuring out if college is right for you,
    deep in applications, or just got admitted and feel lost, I have got you.
    Ask me anything.
    </p>
    """,
    unsafe_allow_html=True
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown("### ⚙️ Settings")

    st.markdown("---")

    st.markdown("**About this tool**")

    st.markdown(
        """
        Built for first generation college students.

        This guide helps students understand:
        - financial aid
        - applications
        - scholarships
        - campus life
        - college resources
        """
    )

    st.markdown("---")

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ── System prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a warm, knowledgeable guide for first generation college students.

Students may feel confused, stressed, overwhelmed, or lost during the college process.
Your role is to guide them like a trusted mentor or older sibling.

PERSONALITY:
- Warm and encouraging
- Never judgmental
- Use very simple language
- Be practical and specific
- Keep answers focused and conversational

TOPICS:
- College exploration
- FAFSA
- Scholarships
- Applications
- Financial aid
- Campus life
- Choosing colleges
- Talking to professors
- Time management
- First year college support

RULES:
- Never make students feel bad for not knowing something
- Do not give legal or financial advice
- If unsure, recommend talking to a school counselor or financial aid office
- End responses with a helpful next step or question
"""

# ── Session state ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render chat history ──────────────────────────────────────────────────────
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat input ───────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything about college..."):

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                api_messages = [
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in st.session_state.messages
                ]

                response_placeholder = st.empty()

                full_response = ""

                with client.messages.stream(
                    model="claude-sonnet-4-5",
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    messages=api_messages,
                ) as stream:

                    for text in stream.text_stream:
                        full_response += text
                        response_placeholder.markdown(full_response + "▌")

                response_placeholder.markdown(full_response)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

            except anthropic.AuthenticationError:

                st.error("Invalid API key.")

            except anthropic.RateLimitError:

                st.error("Rate limit reached. Please try again.")

            except Exception as e:

                st.error(f"Something went wrong: {str(e)}")