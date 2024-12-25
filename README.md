# 🎥 YouTube Summarizer AI Terminal

A powerful command-line tool that helps you understand YouTube videos better through AI-powered summaries and interactive chat.

## ✨ Features

- 📝 **Transcript Extraction**: Automatically fetches video transcripts from YouTube URLs
- 📋 **Smart Summarization**: Creates concise, structured summaries with key points and takeaways
- 💬 **Interactive Chat**: Ask questions about the video content and get relevant answers
- 📜 **History Tracking**: Keep track of your summaries and chat interactions
- 🎨 **Rich Terminal UI**: Beautiful and intuitive command-line interface using Rich library

## 🛠️ Technologies Used

- Python 3.x
- OpenAI GPT-4
- YouTube Transcript API
- Rich (Terminal UI)
- dotenv

## 📋 Prerequisites

- Python 3.x installed
- OpenAI API key
- Internet connection

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/mhakimsaputra17/youtube-summarizer-ai-terminal.git
cd youtube-summarizer-ai-terminal
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root and add:
```env
OPENAI_API_KEY=your_api_key_here
```

## 💻 Usage

1. Run the application:
```bash
python main.py
```

2. Choose from the available options:
- [1] 📝 Input YouTube URL
- [2] 📄 Show Transcript
- [3] 📋 Summarize Video
- [4] 💬 Chat about Video
- [5] 📜 View History
- [6] ❌ Exit

## 🔍 How It Works

1. **URL Input**: Enter a YouTube video URL
2. **Transcript Processing**: The tool fetches and processes the video transcript
3. **AI Analysis**: Uses GPT-4o to analyze and summarize content
4. **Interactive Features**: Chat with the AI about the video content
5. **History Management**: Keep track of all interactions and summaries

## 🎯 Key Features Explained

### Transcript Extraction
- Supports multiple YouTube URL formats
- Handles various transcript formats
- Error handling for unavailable transcripts

### Smart Summarization
- Chunks long transcripts for better processing
- Identifies key points and main takeaways
- Adds emojis and clear headings for better readability

### Interactive Chat
- Context-aware responses
- Handles multiple transcript chunks
- Provides relevant answers based on video content

## ⚠️ Error Handling

The application includes robust error handling for:
- Invalid YouTube URLs
- Missing transcripts
- API failures
- Network issues

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest enhancements
- 🔧 Submit pull requests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o API
- YouTube Transcript API developers
- Rich library contributors

## 📞 Contact

Created by [@mhakimsaputra17](https://github.com/mhakimsaputra17)

---

⭐ Star this repository if you find it helpful!
