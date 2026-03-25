import os
import sys
from openai import OpenAI

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # Read API key from the standard environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Check for demo mode
    demo_mode = os.environ.get("DEMO_MODE", "").lower() in ("1", "true", "yes")
    
    if demo_mode:
        print("\n[DEMO MODE ACTIVE] No real API calls will be made.")
    elif not api_key:
        print("\n" + "="*50)
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        print("Please set it using: setx OPENAI_API_KEY \"your_key_here\" (Windows)")
        print("Then restart your terminal.")
        print("="*50 + "\n")
        sys.exit(1)

    # Initialize Client
    client = OpenAI(api_key=api_key or "demo", base_url="https://api.deepseek.com")

    # Conversation History
    messages = [
        {"role": "system", "content": "You are a helpful and concise assistant."}
    ]

    clear_screen()
    print("--- DeepSeek CLI Chatbot ---")
    print("Type 'exit', 'quit', or 'clear' to manage the chat.\n")

    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ('exit', 'quit'):
                print("\nGoodbye!")
                break
                
            if user_input.lower() == 'clear':
                messages = [messages[0]] # Reset to system prompt
                clear_screen()
                print("--- Chat Cleared ---")
                continue

            # Add user message to history
            messages.append({"role": "user", "content": user_input})

            print("\nAssistant: ", end="", flush=True)

            if demo_mode:
                print("This is a mocked response (Demo Mode).")
                messages.append({"role": "assistant", "content": "This is a mocked response (Demo Mode)."})
                continue

            # API Call with Streaming
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True
            )

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content

            # Add assistant response to history
            messages.append({"role": "assistant", "content": full_response})
            print() # New line after the full response

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n\n[ERROR] Request failed: {e}")
            # Remove the last message if it failed
            if messages[-1]['role'] == 'user':
                messages.pop()

if __name__ == "__main__":
    main()
