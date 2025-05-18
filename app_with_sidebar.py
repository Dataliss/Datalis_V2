import os
import gradio as gr
import time
from file_handler import FileHandler
from agent_factory import AgentFactory
import dotenv
from company_info import create_company_info_ui

# Load environment variables
dotenv.load_dotenv()

# Store uploaded files and company info
uploaded_files = {}
company_details = {}
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
    if hasattr(agent, 'clear_history') and callable(agent.clear_history):
        agent.clear_history(session_id)
    elif hasattr(agent, 'conversation_history'):
        if session_id in agent.conversation_history:
            agent.conversation_history[session_id] = []
    return []

def create_ui():
    """Create the Gradio UI with home page and sidebar"""
    with gr.Blocks(title="Datalis - AI-Powered Financial Intelligence", 
                  theme=gr.themes.Soft(), 
                  css="""
        .container {
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 260px;
            border-right: 1px solid rgba(31, 41, 55, 0.1);
            padding: 20px;
            background-color: #202437;
            color: white;
            transition: all 0.3s;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        }
        .main-content {
            flex: 1;
            padding: 20px;
            transition: all 0.3s;
        }
        .header-logo {
            margin-bottom: 30px;
            font-size: 24px;
            font-weight: bold;
            color: white;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 15px;
        }
        .agent-dropdown {
            margin-bottom: 20px !important;
            background-color: #3D4166 !important;
            color: white !important;
            border-radius: 0 0 4px 4px !important;
            padding: 10px !important;
            border: none !important;
        }
        .agent-dropdown select,
        .agent-dropdown > :first-child {
            background-color: #3D4166 !important;
            color: white !important;
            border: none !important;
        }
        .agent-dropdown .gr-dropdown {
            background-color: #3D4166 !important;
        }
        .agent-dropdown label {
            display: none !important;
        }
        .agent-header {
            background-color: #4B50C8 !important;
            color: white !important;
            padding: 10px 15px !important;
            border-top-left-radius: 4px !important;
            border-top-right-radius: 4px !important;
            margin-bottom: 0 !important;
            font-weight: bold !important;
        }
        .home-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            height: 100%;
            padding: 40px;
            max-width: 1000px;
            margin: 0 auto;
        }
        .home-title {
            font-size: 48px;
            font-weight: bold;
            color: #0066cc;
            margin-bottom: 20px;
        }
        .home-subtitle {
            font-size: 18px;
            color: #6B7280;
            max-width: 600px;
            margin-bottom: 40px;
        }
        .agent-btn {
            margin: 10px;
            min-width: 200px;
        }
        .chat-interface {
            display: none;
        }
        .accordion {
            margin-top: 20px;
        }
        .chatbot {
            height: calc(100vh - 220px);
            min-height: 400px;
        }
        .chatbox-container {
            margin-top: 20px;
        }
        .fixed-height-chatbot .wrap {
            max-height: calc(100vh - 280px);
        }
        .dashboard-preview {
            max-width: 80%;
            margin: 40px auto;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }
    """) as app:
        session_id = gr.State(value=str(time.time()))
          with gr.Blocks():
            # Tabs for Home and Chat
            with gr.Tabs() as tabs:
                with gr.TabItem("Home", id=0) as home_tab:
                    with gr.Row(elem_classes="home-container"):
                        with gr.Column():
                            gr.Markdown(
                                """
                                # AI-Powered Financial Intelligence
                                
                                Transform complex financial data into actionable insights
                                with our specialized AI chatbots for finance professionals.
                                """
                            )
                            
                            gr.Markdown("### Select an agent to get started")
                            
                            with gr.Row():
                                dabby_btn = gr.Button("Dabby Consultant", elem_classes="agent-btn", variant="primary")
                                auditor_btn = gr.Button("Auditor Agent", elem_classes="agent-btn", variant="primary")
                                tax_btn = gr.Button("Tax Agent", elem_classes="agent-btn", variant="primary")
                            
                            gr.Markdown("""
                            ### Dashboard Preview
                            """)
                            
                            gr.HTML("""
                            <img src="https://placehold.co/800x450/e6f7ff/0066cc?text=Datalis+Dashboard+Preview" 
                                 alt="Dashboard Preview" class="dashboard-preview">                            """)
                
                with gr.TabItem("Chat", id=1) as chat_tab:
                    with gr.Row(elem_classes="container"):                        # Sidebar
                        with gr.Column(elem_classes="sidebar"):
                            gr.Markdown("# Datalis", elem_classes="header-logo")
                            
                            gr.Markdown("### Choose Agent", elem_classes="agent-header")
                            agent_dropdown = gr.Dropdown(
                                choices=available_agents,
                                value=current_agent_name,
                                label="",
                                elem_classes="agent-dropdown",
                                interactive=True
                            )
                            
                            with gr.Accordion("File Upload", open=True, elem_classes="accordion"):
                                file_upload = gr.File(
                                    file_count="multiple",
                                    label="Upload Files (PDF, CSV, Excel, DOCX, TXT)"
                                )
                                file_list = gr.List(label="Uploaded Files", interactive=True)
                                selected_file = gr.Textbox(label="Selected File to Analyze")
                                analyze_button = gr.Button("Analyze Selected File", variant="primary")
                            
                            with gr.Accordion("Company Details (KYC)", open=False, elem_classes="accordion"):
                                company_info = create_company_info_ui()
                            
                            clear_button = gr.Button("Clear Chat", variant="secondary")
                        
                        # Main Content (Chat Interface)
                        with gr.Column(elem_classes="main-content"):
                            agent_label = gr.Markdown(f"## {current_agent_name}")
                            
                            chatbot = gr.Chatbot(
                                elem_classes=["chatbot", "fixed-height-chatbot"],
                                show_label=False
                            )
                            
                            with gr.Row(elem_classes="chatbox-container"):
                                message = gr.Textbox(
                                    placeholder=f"Ask {current_agent_name}...",
                                    show_label=False,
                                    container=False,
                                    scale=9
                                )
                                submit_button = gr.Button("Send", scale=1)
        
        # Set up event handlers
        agent_dropdown.change(
            fn=change_agent,
            inputs=[agent_dropdown, session_id],
            outputs=[gr.Textbox(visible=False)]
        ).then(
            fn=lambda agent_name: f"## {agent_name}",
            inputs=[agent_dropdown],
            outputs=[agent_label]
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
          # Home page agent buttons to switch to chat tab with selected agent
        def select_agent_and_switch_tab(agent_name):
            global agent, current_agent_name
            current_agent_name = agent_name
            agent = AgentFactory.get_agent(agent_name)
            return agent_name, gr.update(selected=1)
            
        dabby_btn.click(
            fn=lambda: select_agent_and_switch_tab("Dabby Consultant"),
            outputs=[agent_dropdown, tabs]
        )
            
        auditor_btn.click(
            fn=lambda: select_agent_and_switch_tab("Auditor Agent"),
            outputs=[agent_dropdown, tabs]
        )
            
        tax_btn.click(
            fn=lambda: select_agent_and_switch_tab("Tax Agent"),
            outputs=[agent_dropdown, tabs]
        )
    
    return app

if __name__ == "__main__":
    app = create_ui()
    app.launch(share=False)
