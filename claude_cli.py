"""
Terminal-based Claude Chat Interface
Stores conversations locally in JSON files
Features: conversation history, cost tracking, model selection, streaming
Run: python claude_cli.py
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Storage directory
STORAGE_DIR = Path("conversations")
STORAGE_DIR.mkdir(exist_ok=True)

# Available models
MODELS = {
    "1": ("Claude Sonnet 4.5", "claude-sonnet-4-5-20250929"),
    "2": ("Claude Opus 4", "claude-opus-4-20250514"),
    "3": ("Claude Sonnet 4", "claude-sonnet-4-20250514"),
}

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text, color):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}")

def print_header():
    """Print welcome header"""
    print_colored("\n" + "="*60, Colors.CYAN)
    print_colored("         🤖 CLAUDE CLI CHAT INTERFACE", Colors.BOLD + Colors.CYAN)
    print_colored("="*60 + "\n", Colors.CYAN)

def calculate_cost(input_tokens, output_tokens, model):
    """Calculate cost based on model pricing"""
    # Pricing per million tokens
    pricing = {
        "claude-sonnet-4-5-20250929": (3, 15),
        "claude-opus-4-20250514": (15, 75),
        "claude-sonnet-4-20250514": (3, 15),
    }

    input_cost, output_cost = pricing.get(model, (3, 15))
    cost = (input_tokens * input_cost / 1_000_000) + (output_tokens * output_cost / 1_000_000)
    return cost

def save_conversation(conversation_id, messages, model_name, total_cost):
    """Save conversation to JSON file"""
    filename = STORAGE_DIR / f"{conversation_id}.json"
    data = {
        "id": conversation_id,
        "created": datetime.now().isoformat(),
        "model": model_name,
        "messages": messages,
        "total_cost": total_cost
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_conversation(conversation_id):
    """Load conversation from JSON file"""
    filename = STORAGE_DIR / f"{conversation_id}.json"
    if filename.exists():
        with open(filename, 'r') as f:
            data = json.load(f)
            return data
    return None

def list_conversations():
    """List all saved conversations"""
    conversations = []
    for file in STORAGE_DIR.glob("*.json"):
        with open(file, 'r') as f:
            data = json.load(f)
            # Get first user message as preview
            preview = "New conversation"
            for msg in data.get("messages", []):
                if msg["role"] == "user":
                    preview = msg["content"][:60] + "..." if len(msg["content"]) > 60 else msg["content"]
                    break
            conversations.append({
                "id": data.get("id"),
                "created": data.get("created"),
                "preview": preview,
                "cost": data.get("total_cost", 0.0),
                "model": data.get("model", "Unknown")
            })
    return sorted(conversations, key=lambda x: x["created"], reverse=True)

def select_model():
    """Let user select a model"""
    print_colored("\n📋 Available Models:", Colors.CYAN)
    for key, (name, _) in MODELS.items():
        print(f"  {key}. {name}")

    while True:
        choice = input(f"\n{Colors.GREEN}Select model (1-3) [default: 1]: {Colors.RESET}").strip()
        if not choice:
            choice = "1"
        if choice in MODELS:
            return MODELS[choice]
        print_colored("Invalid choice. Please select 1, 2, or 3.", Colors.RED)

def show_menu():
    """Show main menu"""
    print_colored("\n📋 Menu:", Colors.CYAN)
    print("  1. New conversation")
    print("  2. Load conversation")
    print("  3. List conversations")
    print("  4. Exit")
    return input(f"\n{Colors.GREEN}Choose option: {Colors.RESET}").strip()

def chat_loop(messages, model_id, model_name, conversation_id, total_cost):
    """Main chat loop"""
    print_colored(f"\n💬 Chat started with {model_name}", Colors.GREEN)
    print_colored("Commands: 'exit' to quit, 'save' to save and quit, 'clear' to clear screen", Colors.YELLOW)
    print_colored("For multi-line input, end with '###' on a new line\n", Colors.YELLOW)

    while True:
        # Get user input
        try:
            print_colored("You:", Colors.BOLD + Colors.BLUE)

            # Check for multi-line input
            first_line = input().strip()

            if first_line.lower() == 'exit':
                choice = input(f"{Colors.YELLOW}Save before exiting? (y/n): {Colors.RESET}").strip().lower()
                if choice == 'y':
                    save_conversation(conversation_id, messages, model_name, total_cost)
                    print_colored("💾 Conversation saved!", Colors.GREEN)
                break

            if first_line.lower() == 'save':
                save_conversation(conversation_id, messages, model_name, total_cost)
                print_colored("💾 Conversation saved!", Colors.GREEN)
                break

            if first_line.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            # Handle multi-line input
            user_input = first_line
            if first_line.endswith('###'):
                user_input = first_line[:-3].strip()
            else:
                lines = [first_line]
                while True:
                    line = input()
                    if line.strip() == '###':
                        break
                    lines.append(line)
                user_input = '\n'.join(lines)

            if not user_input.strip():
                continue

            # Add to messages
            messages.append({"role": "user", "content": user_input})

            # Get Claude response
            print_colored("\nClaude:", Colors.BOLD + Colors.GREEN)

            try:
                full_response = ""

                # Stream response
                with client.messages.stream(
                    model=model_id,
                    max_tokens=8000,
                    messages=messages
                ) as stream:
                    for text in stream.text_stream:
                        print(text, end='', flush=True)
                        full_response += text

                    print()  # New line after response

                    # Get usage stats
                    final_message = stream.get_final_message()
                    input_tokens = final_message.usage.input_tokens
                    output_tokens = final_message.usage.output_tokens

                    # Calculate cost
                    cost = calculate_cost(input_tokens, output_tokens, model_id)
                    total_cost += cost

                    # Show stats
                    print_colored(f"\n📊 Tokens: {input_tokens} in / {output_tokens} out | Cost: ${cost:.4f} | Total: ${total_cost:.4f}", Colors.CYAN)

                # Add assistant response
                messages.append({"role": "assistant", "content": full_response})

                # Auto-save after each exchange
                save_conversation(conversation_id, messages, model_name, total_cost)

            except Exception as e:
                print_colored(f"\n❌ Error: {str(e)}", Colors.RED)
                messages.pop()  # Remove user message if failed

        except KeyboardInterrupt:
            print_colored("\n\n⚠️  Interrupted. Save conversation? (y/n): ", Colors.YELLOW)
            choice = input().strip().lower()
            if choice == 'y':
                save_conversation(conversation_id, messages, model_name, total_cost)
                print_colored("💾 Conversation saved!", Colors.GREEN)
            break
        except EOFError:
            break

def main():
    """Main function"""
    print_header()

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print_colored("❌ Error: ANTHROPIC_API_KEY not found in environment!", Colors.RED)
        print_colored("Create a .env file with: ANTHROPIC_API_KEY=your_key_here", Colors.YELLOW)
        return

    while True:
        choice = show_menu()

        if choice == "1":
            # New conversation
            model_name, model_id = select_model()
            conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            messages = []
            total_cost = 0.0
            chat_loop(messages, model_id, model_name, conversation_id, total_cost)

        elif choice == "2":
            # Load conversation
            conversations = list_conversations()
            if not conversations:
                print_colored("\n❌ No saved conversations found.", Colors.RED)
                continue

            print_colored("\n💾 Saved Conversations:", Colors.CYAN)
            for i, conv in enumerate(conversations[:20], 1):
                created = datetime.fromisoformat(conv['created']).strftime("%Y-%m-%d %H:%M")
                print(f"  {i}. [{created}] {conv['preview']} (${conv['cost']:.4f})")

            choice_idx = input(f"\n{Colors.GREEN}Select conversation (1-{len(conversations[:20])}): {Colors.RESET}").strip()
            try:
                idx = int(choice_idx) - 1
                if 0 <= idx < len(conversations[:20]):
                    conv_data = load_conversation(conversations[idx]['id'])
                    if conv_data:
                        print_colored(f"\n✅ Loaded: {conversations[idx]['preview']}", Colors.GREEN)
                        model_name = conv_data.get('model', 'Claude Sonnet 4.5')
                        # Find model ID from name
                        model_id = None
                        for _, (name, mid) in MODELS.items():
                            if name == model_name:
                                model_id = mid
                                break
                        if not model_id:
                            model_id = MODELS["1"][1]

                        chat_loop(
                            conv_data['messages'],
                            model_id,
                            model_name,
                            conv_data['id'],
                            conv_data.get('total_cost', 0.0)
                        )
                else:
                    print_colored("Invalid selection.", Colors.RED)
            except ValueError:
                print_colored("Invalid input.", Colors.RED)

        elif choice == "3":
            # List conversations
            conversations = list_conversations()
            if not conversations:
                print_colored("\n❌ No saved conversations found.", Colors.RED)
                continue

            print_colored(f"\n💾 Total Conversations: {len(conversations)}", Colors.CYAN)
            total_cost = sum(c['cost'] for c in conversations)
            print_colored(f"💰 Total Cost: ${total_cost:.4f}\n", Colors.CYAN)

            for i, conv in enumerate(conversations[:20], 1):
                created = datetime.fromisoformat(conv['created']).strftime("%Y-%m-%d %H:%M")
                print(f"  {i}. [{created}] {conv['model']}")
                print(f"     {conv['preview']}")
                print(f"     Cost: ${conv['cost']:.4f}\n")

        elif choice == "4":
            print_colored("\n👋 Goodbye!\n", Colors.GREEN)
            break

        else:
            print_colored("\n❌ Invalid choice. Please select 1-4.", Colors.RED)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_colored(f"\n❌ Fatal error: {str(e)}", Colors.RED)
        sys.exit(1)
