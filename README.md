# CCB - Claude Chat Bot

A local, terminal-based Claude interface using just the Anthropic API. No subscriptions, no external tools - just you, the terminal, and Claude's API.

## Features

- **Two Interfaces**: Terminal CLI and Streamlit Web UI
- **Local Storage**: All conversations saved as JSON files in `conversations/` directory
- **Cost Tracking**: Real-time token usage and cost calculation
- **Multiple Models**: Support for Claude Sonnet 4.5, Opus 4, and Sonnet 4
- **Streaming Responses**: See Claude's responses in real-time
- **Conversation Management**: Save, load, and resume conversations
- **No Database Required**: Simple JSON-based storage

## Quick Setup (5 Minutes)

### Step 1: Install Dependencies

```bash
cd Desktop\CCB
pip install -r requirements.txt
```

### Step 2: Add Your API Key

1. Get your API key from [Anthropic Console](https://console.anthropic.com/settings/keys)
2. Open `.env` file and replace `your_api_key_here` with your actual API key:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### Step 3: Run the Application

**Option A: Terminal CLI (Recommended for simplicity)**
```bash
python claude_cli.py
```

**Option B: Streamlit UI (Recommended for better UX)**
```bash
streamlit run app.py
```

## Usage Guide

### Terminal CLI (`claude_cli.py`)

**Features:**
- Interactive menu system
- Color-coded output
- Multi-line input support (end with `###`)
- Auto-save after each exchange
- Conversation history management

**Commands:**
- `exit` - Quit (with save prompt)
- `save` - Save and quit
- `clear` - Clear screen
- Multi-line input: Type your message, end with `###` on a new line

**Example Session:**
```
📋 Menu:
  1. New conversation
  2. Load conversation
  3. List conversations
  4. Exit

Choose option: 1

📋 Available Models:
  1. Claude Sonnet 4.5
  2. Claude Opus 4
  3. Claude Sonnet 4

Select model (1-3) [default: 1]: 1

💬 Chat started with Claude Sonnet 4.5
Commands: 'exit' to quit, 'save' to save and quit, 'clear' to clear screen
For multi-line input, end with '###' on a new line

You:
Hello! Can you help me write a Python function?

Claude:
[Response streams here in real-time]

📊 Tokens: 150 in / 450 out | Cost: $0.0070 | Total: $0.0070
```

### Streamlit UI (`app.py`)

**Features:**
- Modern web interface
- Sidebar with conversation history
- Model selector dropdown
- Real-time streaming responses
- Session statistics
- One-click conversation loading

**Access:**
- Opens automatically in your browser
- Usually at `http://localhost:8501`

## File Structure

```
CCB/
├── claude_cli.py          # Terminal-based CLI
├── app.py                 # Streamlit web UI
├── .env                   # API key configuration
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── conversations/        # Auto-created, stores JSON conversation files
    ├── 20250105_143022.json
    ├── 20250105_151530.json
    └── ...
```

## Cost Information

**Pricing (per million tokens):**
- **Claude Sonnet 4.5**: $3 input / $15 output
- **Claude Opus 4**: $15 input / $75 output
- **Claude Sonnet 4**: $3 input / $15 output

**Estimated costs:**
- Short conversation (~10 exchanges): $0.05 - $0.15
- Medium conversation (~50 exchanges): $0.25 - $0.75
- Long conversation (~100 exchanges): $0.50 - $1.50

The actual cost depends on conversation length and model choice. Both interfaces show real-time cost tracking.

## Conversation Storage

Conversations are stored as JSON files in `conversations/` directory:

```json
{
  "id": "20250105_143022",
  "created": "2025-01-05T14:30:22.123456",
  "model": "Claude Sonnet 4.5",
  "messages": [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ],
  "total_cost": 0.0042
}
```

**Benefits:**
- Easy to backup (just copy the folder)
- Human-readable format
- No database setup required
- Portable across systems
- Version control friendly

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Check that `.env` file exists in the CCB directory
- Verify the API key is correctly formatted (starts with `sk-ant-`)
- Ensure no extra spaces or quotes around the key

### "Module not found" error
- Run `pip install -r requirements.txt`
- Make sure you're in the CCB directory

### Streamlit won't start
- Check if port 8501 is already in use
- Try: `streamlit run app.py --server.port 8502`

### Conversations not saving
- Check write permissions for the `conversations/` directory
- The directory is created automatically on first run

## Tips

1. **For Quick Chats**: Use the terminal CLI - faster startup
2. **For Long Sessions**: Use Streamlit UI - better for reviewing history
3. **Multi-line Input** (CLI): Perfect for code snippets, end with `###`
4. **Cost Management**: Start with Sonnet 4.5 (cheapest), use Opus 4 for complex tasks
5. **Backup**: Periodically copy the `conversations/` folder to backup your chats

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, macOS, or Linux
- **Internet**: Required for API calls
- **Disk Space**: Minimal (conversations are text files)

## Privacy & Security

- **All conversations stored locally** on your machine
- **No data sent to third parties** (only Anthropic API)
- **API key stored in local .env file** (never committed to git)
- **No telemetry or tracking**

## Next Steps

1. **Try the Terminal CLI**: `python claude_cli.py`
2. **Try the Streamlit UI**: `streamlit run app.py`
3. **Experiment with different models** to find your preference
4. **Check the `conversations/` folder** to see your saved chats

## Support

- **Anthropic API Docs**: https://docs.anthropic.com
- **Get API Key**: https://console.anthropic.com/settings/keys
- **Pricing**: https://www.anthropic.com/pricing

## License

Free to use for personal projects. Respects Anthropic's API terms of service.

---

**Built with ❤️ for Claude API users who want a simple, local chat interface.**
