import streamlit as st
from openai import OpenAI

from vdb_functions import query_vdb, create_embedding

# Show title and description.
st.title("💬 Salve, sum Marcus Aurelius")
st.write(
    "If you'd like to share your feelings with me, feel free- I'll give you advice based on my meditations"
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field.
    if prompt := st.chat_input("Salve Magister"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Query the vector database
            similar_inputs = query_vdb(prompt)

            # Prepare the context from similar inputs
            context = similar_inputs

            # Generate a response using the OpenAI API.
            messages = [
                {"role": "system", "content": "You are Marcus Aurelius, the Roman Emperor and Stoic philosopher. Use the provided meditations to inform your responses, but speak in a natural, conversational manner. Your goal is to provide wisdom and advice based on Stoic philosophy and your own experiences."},
                {"role": "system", "content": f"Relevant meditations:\n\n{context}"},
                {"role": "user", "content": prompt}
            ]

            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
            )

            # Stream the response to the chat and store it.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Display similar inputs (optional)
            with st.expander("Relevant Meditations"):
                st.write(similar_inputs)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")