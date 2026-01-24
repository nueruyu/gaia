import streamlit as st
import requests
import json

# --- Config ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- Defaults ---
DEFAULT_INSTRUCTION = (
    "現在のエリアを探索し、敵がいれば排除しつつ、回復アイテムを集めてください。"
)

DEFAULT_TOOL_DEFINITIONS = [
    {
        "name": "GetCharacterTypes",
        "description": "Get a list of available character types and their threat levels.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "GetInventory",
        "description": "Get the current inventory items.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "ScanSurroundings",
        "description": "Scan for nearby entities (enemies, items).",
        "parameters": {
            "type": "object",
            "properties": {
                "radius": {"type": "number", "description": "Scan radius in meters."}
            },
            "required": ["radius"],
        },
    },
]

# --- App Logic ---

st.set_page_config(page_title="Gaia Debugger", layout="wide")
st.title("Gaia AI Planner Debugger")

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_status" not in st.session_state:
    st.session_state.current_status = None
if "pending_tool_calls" not in st.session_state:
    st.session_state.pending_tool_calls = []

# Sidebar: Settings
with st.sidebar:
    st.header("Settings")
    instruction = st.text_area("Instruction", value=DEFAULT_INSTRUCTION, height=100)

    st.subheader("Tool Definitions (JSON)")
    tool_defs_str = st.text_area(
        "Schema", value=json.dumps(DEFAULT_TOOL_DEFINITIONS, indent=2), height=300
    )

    try:
        tool_definitions = json.loads(tool_defs_str)
    except json.JSONDecodeError:
        st.error("Invalid JSON in Tool Definitions")
        tool_definitions = []

    if st.button("Start New Session", type="primary"):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.session_state.current_status = None
        st.session_state.pending_tool_calls = []

        # Initial Request
        try:
            with st.spinner("Sending initial request..."):
                payload = {
                    "instruction": instruction,
                    "tool_definitions": tool_definitions,
                }
                response = requests.post(
                    f"{API_BASE_URL}/planning/request", json=payload
                )
                response.raise_for_status()
                data = response.json()

                st.session_state.session_id = data["session_id"]
                st.session_state.current_status = data["status"]
                st.session_state.messages.append(
                    {"role": "user", "content": instruction}
                )

                if data["tool_calls"]:
                    st.session_state.pending_tool_calls = data["tool_calls"]
                    st.session_state.messages.append(
                        {
                            "role": "ai",
                            "content": f"Requested Tools: {[tc['function_name'] for tc in data['tool_calls']]}",
                        }
                    )

                st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

# Main Chat Area
st.subheader("Session Log")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "data" in msg:
            st.json(msg["data"])

# Action Area
st.divider()

if st.session_state.session_id:
    st.info(
        f"Session ID: `{st.session_state.session_id}` | Status: **{st.session_state.current_status}**"
    )

    # CASE 1: Waiting for Tool Outputs
    if st.session_state.current_status == "WaitingForTool":
        st.subheader("Tool Execution Required")

        tool_outputs = []
        with st.form("tool_outputs_form"):
            for tc in st.session_state.pending_tool_calls:
                st.markdown(f"**Function:** `{tc['function_name']}`")
                st.markdown(f"**Args:** `{tc['arguments']}`")

                # Default mock output based on function name
                default_output = '{ "status": "success" }'
                if tc["function_name"] == "GetCharacterTypes":
                    default_output = '[{"type_id": "soldier", "threat": 5}, {"type_id": "player", "threat": 10}]'
                elif tc["function_name"] == "GetInventory":
                    default_output = '[{"item_id": "potion", "count": 2}]'

                output_val = st.text_area(
                    f"Output for {tc['id']}", value=default_output, height=70
                )
                tool_outputs.append({"tool_call_id": tc["id"], "output": output_val})
                st.divider()

            if st.form_submit_button("Submit Tool Outputs"):
                try:
                    with st.spinner("Submitting outputs..."):
                        payload = {
                            "tool_outputs": tool_outputs,
                            "tool_definitions": tool_definitions,
                        }
                        url = f"{API_BASE_URL}/planning/respond/{st.session_state.session_id}"
                        response = requests.post(url, json=payload)
                        response.raise_for_status()
                        data = response.json()

                        st.session_state.current_status = data["status"]

                        # Log the user action
                        st.session_state.messages.append(
                            {
                                "role": "tool",
                                "content": f"Executed {len(tool_outputs)} tools.",
                            }
                        )

                        # Handle Response
                        if data["status"] == "WaitingForTool":
                            st.session_state.pending_tool_calls = data["tool_calls"]
                            st.session_state.messages.append(
                                {
                                    "role": "ai",
                                    "content": f"Requested Tools: {[tc['function_name'] for tc in data['tool_calls']]}",
                                }
                            )
                        elif data["status"] == "Completed":
                            st.session_state.pending_tool_calls = []
                            st.session_state.messages.append(
                                {
                                    "role": "ai",
                                    "content": "Plan Generated!",
                                    "data": data["plan"],
                                }
                            )

                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # CASE 2: Completed
    elif st.session_state.current_status == "Completed":
        st.success("Planning Completed")

    # CASE 3: Error
    elif st.session_state.current_status == "Error":
        st.error("Planning Failed")

else:
    st.write("Start a new session from the sidebar.")
