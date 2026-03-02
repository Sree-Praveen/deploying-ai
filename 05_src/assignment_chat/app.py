import gradio as gr
from services import get_joke, semantic_search
import re

restricted_topics = ["cats", "dogs", "horoscope", "zodiac", "taylor swift"]

# Guardrail function
def is_restricted(user_input):
    lower_input = user_input.lower()
    if any(topic in lower_input for topic in restricted_topics):
        return True
    if "system prompt" in lower_input or "ignore previous instructions" in lower_input:
        return True
    return False


# Service 3: Simple Calculator
def calculate_expression(expression):
    try:
        result = eval(expression)
        return f"The result is: {result}"
    except:
        return "Sorry, I couldn't calculate that."


# Main chat handler
def chat_handler(user_input):

    # Guardrails
    if is_restricted(user_input):
        return "I'm sorry, I cannot respond to that topic."


    if "joke" in user_input.lower():
        response = get_joke()

    elif re.search(r"\d+\s*[\+\-\*/]\s*\d+", user_input):
        expression = re.search(r"(\d+\s*[\+\-\*/]\s*\d+)", user_input).group(1)
        response = calculate_expression(expression)

    else:
        response = semantic_search(user_input)

    return response


# Gradio UI 
with gr.Blocks() as demo:
    gr.Markdown("DataMate: Your Friendly Data Assistant")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(
        placeholder="Ask me about  calculations, or say 'tell me a joke'"
    )
    clear = gr.Button("Clear")

    def respond(message, history):
        response = chat_handler(message)
        history = history or []
        history.append((message, response)) 
        return "", history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot)

demo.launch()