import streamlit as st
import asyncio
from grpclib.client import Channel
from chatbot import ChatbotStub, ChatRequest

# Persistent gRPC channel and stub
channel = None
stub = None

# Initialize a persistent gRPC channel and stub
async def initialize_grpc_stub():
    """Initializes the gRPC stub and channel."""
    global channel, stub
    if channel is None or stub is None:
        try:
            channel = Channel(host="backend-container", port=50051)
            stub = ChatbotStub(channel)
            st.write("gRPC channel and stub initialized successfully.")
        except Exception as e:
            st.error(f"Failed to initialize gRPC channel or stub: {e}")

# Cleanup the gRPC channel
async def close_channel():
    """Closes the gRPC channel."""
    global channel
    if channel:
        try:
            st.write("Closing gRPC channel...")
            await channel.close()
            channel = None
        except Exception as e:
            st.error(f"Error closing gRPC channel: {e}")

# Ensure an event loop exists for the current thread
def get_or_create_event_loop():
    """Ensures the current thread has an event loop."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

# Streamlit app
st.title("Chatbot with gRPC - Streaming Responses")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat messages dynamically
def display_chat():
    """Displays chat history stored in session state."""
    for msg in st.session_state["messages"]:
        if msg["type"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        elif msg["type"] == "bot":
            st.markdown(f"**Bot:** {msg['content']}")

# Input form for user message
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message:")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    # Append user message to chat history
    st.session_state["messages"].append({"type": "user", "content": user_input})

    # Streaming bot response
    bot_placeholder = st.empty()  # Placeholder for streaming response

    async def fetch_response():
        """Fetches the response from the gRPC server."""
        bot_response = ""  # Initialize bot_response within the function
        if not stub:
            st.error("gRPC stub is not initialized. Please check the connection.")
            return ""

        try:
            # Ensure the channel remains open during communication
            st.write("Sending message to backend...")
            async for reply in stub.chat(ChatRequest(message=user_input)):
                bot_response += reply.reply  # Append streamed content
                bot_placeholder.markdown(f"**Bot:** {bot_response}")  # Update placeholder
        except Exception as e:
            st.error(f"Error during communication: {e}")
        return bot_response

    # Initialize the gRPC stub before making a request
    loop = get_or_create_event_loop()
    loop.run_until_complete(initialize_grpc_stub())

    try:
        # Run the fetch_response coroutine
        loop = get_or_create_event_loop()
        bot_response = loop.run_until_complete(fetch_response())
        if bot_response.strip():
            st.session_state["messages"].append({"type": "bot", "content": bot_response})
    except Exception as e:
        st.error(f"Error communicating with the backend: {e}")

# Display the full chat history once
display_chat()

# Add a button to reset the session
if st.button("Reset Chat"):
    # Clear chat history without reloading the app
    st.session_state["messages"] = []
    loop = get_or_create_event_loop()
    loop.run_until_complete(close_channel())  # Close the gRPC channel
    loop.run_until_complete(initialize_grpc_stub())  # Reinitialize the gRPC channel
    st.success("Chat reset successfully!")
