import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()

# Initialize the Azure OpenAI LLM
def init_llm():
    return AzureChatOpenAI(
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.3,
        max_tokens=5000,
        streaming=True  # Enable streaming for better UX
    )

# Initialize session state
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    if "llm_chain" not in st.session_state:
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a helpful AI assistant. Answer questions clearly and concisely."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ])

        # Create LLM chain
        st.session_state.llm_chain = LLMChain(
            llm=init_llm(),
            prompt=prompt,
            memory=st.session_state.memory,
            verbose=True
        )

# Main function
def main():
    st.set_page_config(page_title="Azure OpenAI Chatbot", page_icon="🤖")
    st.title("Azure OpenAI Chatbot (GPT-4)")

    init_session_state()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # File upload functionality
    uploaded_files = st.file_uploader("Upload files", type=["txt", "pdf", "docx", "py"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Process each uploaded file
            file_content = None
            if uploaded_file.type == "text/plain":
                file_content = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/pdf":
                # Example: Process PDF file (requires PyPDF2 or similar library)
                from PyPDF2 import PdfReader
                reader = PdfReader(uploaded_file)
                file_content = " ".join(page.extract_text() for page in reader.pages)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # Example: Process DOCX file (requires python-docx library)
                from docx import Document
                doc = Document(uploaded_file)
                file_content = " ".join(paragraph.text for paragraph in doc.paragraphs)
            elif uploaded_file.type == "text/x-python":
                # Process Python file
                file_content = uploaded_file.read().decode("utf-8")

            if file_content:
                st.session_state.messages.append({"role": "user", "content": f"Uploaded file content from {uploaded_file.name}:\n\n{file_content}"})
                with st.chat_message("user"):
                    st.markdown(f"Uploaded file content from **{uploaded_file.name}**:\n\n{file_content}")

    # Chat input
    if prompt := st.chat_input("What's up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # Stream the response
            for chunk in st.session_state.llm_chain.stream({"question": prompt}):
                full_response += chunk["text"]
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()