import os
import time
import datetime
from google import genai
from google.genai import types

# 1. Load API Key
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = 'gemini-2.0-flash'

if not API_KEY:
    print("❌ Error: GEMINI_API_KEY environment variable not set.")
    exit()

client = genai.Client(api_key=API_KEY)

# 2. Initialize Chat Session (for memory)
# Setting a simple system instruction.
chat = client.chats.create(
    model=MODEL_NAME,
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful AI assistant.",
        temperature=0.7,
    )
)

def send_message_with_retry(chat_session, user_message, max_retries=3):
    """
    Sends a message with automatic retries for 503 errors.
    """
    for attempt in range(max_retries):
        try:
            response = chat_session.send_message(user_message)
            return response.text
            
        except Exception as e:
            error_str = str(e)
            if "503" in error_str or "429" in error_str:
                wait_time = 2 ** attempt
                print(f"⚠️ Server busy (503/429). Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return f"❌ An unrecoverable error occurred: {e}"
    
    return "❌ Server is currently too busy. Please try again in a minute."

# --- Main Loop ---
print(f"🤖 AI Chatbot (Connected and Ready)")
print("Type 'bye' to exit.\n")

while True:
    user_input = input("You: ")
    print('\n')
    
    if user_input.lower() in ["bye", "exit", "quit"]:
        print("🤖 AI Chatbot: Goodbye!")
        break

    # Check if the user is asking for the time or date
    time_keywords = ["time", "date", "day", "today", "now"]
    
    # Use 'any' to see if any keyword is in the user's (lowercase) input
    if any(keyword in user_input.lower() for keyword in time_keywords):
        
        # 1. Get the FRESH current time
        current_time = datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        
        # 2. Create a new, temporary prompt
        # This "wraps" the user's question with the real-time context
        prompt_with_context = f"""
        A user is asking: "{user_input}"
        
        For your reference, the current real-world time is: {current_time}.
        
        Please answer the user's question using this exact time.
        """
        
        # 3. Send the modified prompt
        response_text = send_message_with_retry(chat, prompt_with_context)
    
    else:
        # 4. If not a time question, just send the original input
        response_text = send_message_with_retry(chat, user_input)
    
    print("🤖 AI Chatbot:", response_text)