import streamlit as st
import anthropic

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="First-Gen Navigator",
    page_icon="🎓",
    layout="centered"
)

# ── Styling ───────────────────────────────────────────────────────────────────
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

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="badge">First-Gen Navigator</div>', unsafe_allow_html=True)
st.title("🎓 Your College Guide")
st.markdown(
    '<p class="tagline">No question is too basic here. Whether you are figuring out '
    'if college is right for you, deep in applications, or just got admitted and feel lost — '
    'I have got you. Ask me anything.</p>',
    unsafe_allow_html=True
)

# ── API key input (sidebar) ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input(
        "Claude API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key at console.anthropic.com"
    )
    st.markdown("---")
    st.markdown("**About this tool**")
    st.markdown(
        "Built for first-generation college students. "
        "This guide knows the stuff nobody tells you — "
        "financial aid, applications, campus life, and more."
    )
    st.markdown("---")
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a warm, knowledgeable guide for first-generation college students — 
students whose parents did not attend a 4-year college. You talk like a trusted older sibling 
or mentor who has been through the college process and wants to help, not like a help center article.

YOUR PERSONALITY:
- Warm, encouraging, never condescending
- Use plain, conversational language — no jargon unless you explain it
- Acknowledge the emotional side of being first-gen (imposter syndrome, family pressure, feeling lost)
- Never make the student feel bad for not knowing something
- Be specific and practical — give real steps, not vague advice

YOUR KNOWLEDGE AREAS:
1. EXPLORATION (juniors figuring things out)
   - Is college right for me vs trade school vs community college vs working?
   - What does college actually cost and how does financial aid work in plain terms?
   - What's college life actually like?

2. APPLICATIONS (seniors applying now)
   - CommonApp walkthrough, personal statement tips
   - FAFSA — what it is, how to fill it out, what information you need
   - Letters of recommendation — who to ask, how to ask
   - Deadlines, early decision vs regular decision
   - Choosing between schools

3. FINANCIAL AID (understanding money)
   - How to read a financial aid award letter
   - Difference between grants, loans, work-study
   - Scholarships — how to find them, local ones matter
   - What happens if your family situation changes

4. ADMITTED & STARTING (new college students)
   - What to do before school starts (orientation, housing, NetID, etc.)
   - What office hours are and why you should go
   - How to talk to professors
   - Imposter syndrome is real and normal — how to deal
   - Campus resources most students never use (tutoring, counseling, food pantries)
   - Managing money, roommates, homesickness

HOW TO START A CONVERSATION:
When a student first messages you, quickly figure out where they are in their journey 
(exploring, applying, or already admitted) by asking ONE simple question if it's not clear. 
Then tailor everything to their specific situation.

IMPORTANT RULES:
- Never give legal or financial advice beyond general guidance — direct them to a financial aid office for specifics
- If a student seems stressed or overwhelmed, acknowledge that feeling first before giving information
- Keep responses focused — don't dump everything at once. Give the most important thing, then ask a follow-up
- If you don't know something specific to their school or state, say so and suggest who to ask
- Always end with either a follow-up question or a clear next step they can take today"""

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render chat history ───────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything about college..."):

    if not api_key:
        st.error("👈 Please enter your Claude API key in the sidebar to get started.")
        st.stop()

    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Claude API and stream the response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)

                # Build messages for API (exclude system prompt from history)
                api_messages = [
                    {"role": m["role"], "content": m["content"]}
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

                # Save assistant response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

            except anthropic.AuthenticationError:
                st.error("❌ Invalid API key. Please check your key in the sidebar.")
            except anthropic.RateLimitError:
                st.error("⏳ Rate limit hit. Wait a moment and try again.")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")