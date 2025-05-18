import os
import gradio as gr
import time
from file_handler import FileHandler
from agent_factory import AgentFactory
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Store uploaded files
uploaded_files = {}
current_agent_name = "Dabby Consultant"
available_agents = ["Dabby Consultant", "Auditor Agent", "Tax Agent"]

# Initialize agent
agent = AgentFactory.get_agent(current_agent_name)

def upload_file(files, chatbot, session_id):
    """Handle file uploads"""
    file_list = FileHandler.handle_uploaded_files(files, session_id, uploaded_files)
    
    # Create a message to show files were uploaded
    if files and len(files) > 0:
        file_names = ", ".join([os.path.basename(f.name) for f in files])
        message = f"Uploaded {len(files)} file(s): {file_names}"
        
        # Add to chatbot
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", message))
        return updated_chatbot, gr.update(value=file_list)
    
    return chatbot, gr.update(value=file_list)

def analyze_file(file_name, chatbot, session_id):
    """Analyze a selected file"""
    if not file_name or file_name.strip() == "":
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", "No file selected. Please select a file from the list."))
        return updated_chatbot
        
    if session_id not in uploaded_files or not uploaded_files[session_id]:
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", "No files uploaded. Please upload files first."))
        return updated_chatbot
    
    # Find the selected file in the uploaded files
    selected_file = None
    for file in uploaded_files[session_id]:
        if file["name"] == file_name:
            selected_file = file
            break
    
    if not selected_file:
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", f"File '{file_name}' not found in uploaded files."))
        return updated_chatbot
    
    # Create a copy of the chatbot
    updated_chatbot = chatbot.copy() if chatbot else []
    
    # Add a message indicating analysis is in progress
    updated_chatbot.append((f"Analyzing file: {file_name}", "Processing..."))
    
    # Get response from agent
    try:
        response = agent.analyze_file(file_name, selected_file["path"], session_id)
        
        # Update the last message with the actual response
        updated_chatbot[-1] = (f"Analyzing file: {file_name}", response)
    except Exception as e:
        # If there's an error, update the message accordingly
        updated_chatbot[-1] = (f"Analyzing file: {file_name}", f"Error analyzing file: {str(e)}")
    
    return updated_chatbot

def chat(message, chatbot, session_id):
    """Handle chat interactions"""
    if not message.strip():
        return chatbot
    
    # Create a copy of the chatbot
    updated_chatbot = chatbot.copy() if chatbot else []
    
    # Add to chatbot for display
    updated_chatbot.append((message, "Thinking..."))
    yield updated_chatbot
    
    try:
        response = agent.chat(message, session_id)
        
        # Update chatbot
        updated_chatbot[-1] = (message, response)
    except Exception as e:
        # If there's an error, update the message accordingly
        updated_chatbot[-1] = (message, f"Error: {str(e)}")
    
    yield updated_chatbot

def change_agent(agent_name, session_id):
    """Change the current agent"""
    global agent, current_agent_name
    current_agent_name = agent_name
    agent = AgentFactory.get_agent(agent_name)
    
    return f"Agent switched to {agent_name}"

def clear_chat(session_id):
    """Clear the chat history"""
    agent.clear_history(session_id)
    return []

def create_ui():
    """Create the Gradio UI"""
    with gr.Blocks(title="DABBY", theme=gr.themes.Soft(), css="""
        .toggle-btn {
            min-width: 40px !important;
            max-width: 40px !important;
            height: 40px !important;
            border-radius: 50% !important;
            padding: 0 !important;
            font-size: 20px !important;
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 100;
        }
        .sidebar {
            border-right: 1px solid #e0e0e0;
            padding-right: 20px;
        }
        .main-container {
            flex: 1;
            padding-left: 20px;
        }
        .header {
            margin-bottom: 20px;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 10px;
        }
    """) as app:
        session_id = gr.State(value=str(time.time()))
        sidebar_visible = gr.State(value=True)
        
        with gr.Row():
            # Sidebar column
            with gr.Column(scale=1, visible=True, elem_classes="sidebar") as sidebar:
                gr.Markdown("# DABBY", elem_classes="header")
                agent_dropdown = gr.Dropdown(
                    choices=available_agents,
                    value=current_agent_name,
                    label="Select Agent"
                )
                
                with gr.Accordion("Workbench", open=True):
                    file_upload = gr.File(
                        file_count="multiple",
                        label="Upload Files (PDF, CSV, Excel, DOCX, TXT)"
                    )
                    file_list = gr.List(label="Uploaded Files")
                    selected_file = gr.Textbox(label="Selected File to Analyze")
                    analyze_button = gr.Button("Analyze Selected File")
            
            # Chat area
            with gr.Column(scale=3, elem_classes="main-container"):
                # Toggle sidebar button at the top
                toggle_button = gr.Button(
                    value="❮", 
                    elem_classes="toggle-btn"
                )
                
                chatbot = gr.Chatbot(height=600)
                with gr.Row():
                    message = gr.Textbox(
                        placeholder=f"Ask {current_agent_name}...",
                        show_label=False
                    )
                    submit_button = gr.Button("Send")
                
                clear_button = gr.Button("Clear Chat")
        
        # Set up event handlers
        agent_dropdown.change(
            fn=change_agent,
            inputs=[agent_dropdown, session_id],
            outputs=[gr.Textbox(visible=False)]
        ).then(
            fn=lambda agent_name: f"Ask {agent_name}...",
            inputs=[agent_dropdown],
            outputs=[message]
        )
        
        file_upload.upload(
            fn=upload_file,
            inputs=[file_upload, chatbot, session_id],
            outputs=[chatbot, file_list]
        )
        
        file_list.select(
            fn=lambda x: x,
            inputs=[file_list],
            outputs=[selected_file]
        )
        
        analyze_button.click(
            fn=analyze_file,
            inputs=[selected_file, chatbot, session_id],
            outputs=[chatbot]
        )
        
        submit_button.click(
            fn=chat,
            inputs=[message, chatbot, session_id],
            outputs=[chatbot]
        )
        
        message.submit(
            fn=chat,
            inputs=[message, chatbot, session_id],
            outputs=[chatbot]
        )
        
        clear_button.click(
            fn=clear_chat,
            inputs=[session_id],
            outputs=[chatbot]
        )
        
        # Toggle sidebar visibility
        def toggle_sidebar(is_visible):
            return not is_visible
        
        def get_toggle_icon(is_visible):
            return "❮" if is_visible else "❯"
        
        toggle_button.click(
            fn=toggle_sidebar,
            inputs=[sidebar_visible],
            outputs=[sidebar_visible]
        ).then(
            fn=lambda x: gr.update(visible=x),
            inputs=[sidebar_visible],
            outputs=[sidebar]
        ).then(
            fn=get_toggle_icon,
            inputs=[sidebar_visible],
            outputs=[toggle_button]
        )
    
    return app

if __name__ == "__main__":
    app = create_ui()
    app.launch(share=False)
