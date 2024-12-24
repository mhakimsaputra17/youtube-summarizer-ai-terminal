import os
from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import track
from rich.table import Table
from rich import print
from rich.markdown import Markdown
import re
import time
import sys

# Load environment variables
load_dotenv()

# Inisialisasi Rich Console
console = Console()

class ChatWithYoutube:
    def __init__(self):
        try:
            # Load environment variables
            self.api_key = ''  # Changed to use GITHUB_TOKEN
            self.endpoint = "https://models.inference.ai.azure.com"  # Fixed endpoint
            self.model_name = "gpt-4o"  # Fixed model name

            # Validate environment variables
            if not self.api_key:
                raise ValueError("GITHUB_TOKEN not found in environment variables")

            self.client = OpenAI(
                base_url=self.endpoint,
                api_key=self.api_key,
            )
            self.transcript = ""
            self.video_id = ""
            self.video_title = ""
            self.history = []

        except Exception as e:
            console.print(f"[red]Initialization Error: {str(e)}[/red]")
            sys.exit(1)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_video_id(self, url):
        """Ekstrak video ID dari URL YouTube"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard YouTube URL
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',  # Short YouTube URL
            r'(?:embed\/)([0-9A-Za-z_-]{11})'  # Embedded YouTube URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def validate_url(self, url):
        """Validasi URL YouTube"""
        if not url:
            return False
        if not ('youtube.com' in url or 'youtu.be' in url):
            return False
        return self.get_video_id(url) is not None

    def get_transcript(self, url):
        """Ambil transkrip dari video YouTube"""
        try:
            if not self.validate_url(url):
                raise ValueError("Invalid YouTube URL")

            self.video_id = self.get_video_id(url)
            transcript_list = YouTubeTranscriptApi.get_transcript(self.video_id)
            
            # Format transcript dengan timestamp
            formatted_transcript = []
            for item in transcript_list:
                timestamp = time.strftime('%H:%M:%S', time.gmtime(item['start']))
                formatted_transcript.append(f"[{timestamp}] {item['text']}")
            
            self.transcript = '\n'.join(formatted_transcript)
            return True

        except Exception as e:
            error_msg = str(e)
            if "No transcript found" in error_msg:
                console.print("[red]No transcript available for this video.[/red]")
            elif "Invalid YouTube URL" in error_msg:
                console.print("[red]Please enter a valid YouTube URL.[/red]")
            else:
                console.print(f"[red]Error: {error_msg}[/red]")
            return False

    def chunk_transcript(self, text, max_chunk_size=4000):
        """Split transcript into smaller chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            # Approximate token count (rough estimate: 4 chars = 1 token)
            word_tokens = len(word) // 4 + 1
            if current_size + word_tokens > max_chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_tokens
            else:
                current_chunk.append(word)
                current_size += word_tokens
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def summarize_video(self):
        """Buat ringkasan video"""
        try:
            if not self.transcript:
                raise ValueError("No transcript available")

            chunks = self.chunk_transcript(self.transcript)
            summaries = []

            for i, chunk in enumerate(chunks, 1):
                with console.status(f"[bold green]Generating summary for part {i}/{len(chunks)}...") as status:
                    prompt = (
                        "Summarize this YouTube video by identifying the key points discussed and their core explanations. "
                        "Use clear headings and relevant emojis to structure the summary. "
                        "Crucially, highlight the single most important takeaway message of the video. "
                        "Format the summary in a concise and easily digestible manner, similar to an executive summary in a news article. "
                        "Avoid phrases like 'the video says'.\n\n"
                        f"{chunk}"
                    )

                    response = self.client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=self.model_name
                    )
                    
                    summaries.append(response.choices[0].message.content)

            if len(summaries) > 1:
                final_prompt = (
                    "Create a cohesive summary from these sections, maintaining the emoji headings "
                    "and structural format. Combine similar topics under unified headings and ensure "
                    "a smooth flow between sections:\n\n" +
                    "\n\n".join([f"Section {i+1}:\n{s}" for i, s in enumerate(summaries)])
                )

                # Updated API call format
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": final_prompt}],
                    model=self.model_name,
                )
                
                final_summary = response.choices[0].message.content
            else:
                final_summary = summaries[0]

            self.history.append({"type": "summary", "content": final_summary})
            return final_summary

        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg

    def chat_with_video(self, question):
        """Chat tentang konten video"""
        try:
            if not self.transcript:
                raise ValueError("No transcript available")

            chunks = self.chunk_transcript(self.transcript, max_chunk_size=3000)
            answers = []

            for i, chunk in enumerate(chunks, 1):
                with console.status(f"[bold green]Analyzing part {i}/{len(chunks)}...") as status:
                    prompt = (
                        "Find the answer to the following question within this video transcript excerpt:\n\n"
                        f"{chunk}\n\n"
                        f"Question: {question}\n\n"
                        "Answer concisely. If the answer is not present in this excerpt, output 'NO_RELEVANT_INFO'."
                    )

                    response = self.client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=self.model_name
                    )
                    
                    chunk_answer = response.choices[0].message.content
                    if chunk_answer != "NO_RELEVANT_INFO":
                        answers.append(chunk_answer)

            if len(answers) > 1:
                final_prompt = (
                    "Create a clear and concise answer by combining "
                    f"these relevant pieces of information about the question: {question}\n\n" +
                    "\n\n".join([f"Info {i+1}:\n{a}" for i, a in enumerate(answers)])
                )

                # Updated API call format
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": final_prompt}],
                    model=self.model_name,
                )
                
                final_answer = response.choices[0].message.content
            elif len(answers) == 1:
                final_answer = answers[0]
            else:
                final_answer = "I couldn't find relevant information to answer your question in the video transcript."

            self.history.append({"type": "chat", "question": question, "answer": final_answer})
            return final_answer

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg

    def display_menu(self):
        """Tampilkan menu utama"""
        self.clear_screen()
        console.print(Panel.fit(
            "[bold blue]🎥 ChatWithYoutube[/bold blue]",
            border_style="blue"
        ))
        
        table = Table(show_header=False, border_style="blue")
        table.add_row("[1]", "[yellow]📝 Input YouTube URL[/yellow]")
        table.add_row("[2]", "[yellow]📄 Show Transcript[/yellow]")
        table.add_row("[3]", "[yellow]📋 Summarize Video[/yellow]")
        table.add_row("[4]", "[yellow]💬 Chat about Video[/yellow]")
        table.add_row("[5]", "[yellow]📜 View History[/yellow]")
        table.add_row("[6]", "[yellow]❌ Exit[/yellow]")
        
        console.print(table)

    def view_history(self):
        """Tampilkan riwayat interaksi"""
        if not self.history:
            console.print("[yellow]No history available yet.[/yellow]")
            return

        for i, item in enumerate(self.history, 1):
            if item["type"] == "summary":
                console.print(Panel(
                    item["content"],
                    title=f"[bold]Summary #{i}[/bold]",
                    border_style="yellow"
                ))
            else:
                console.print(Panel(
                    f"Q: {item['question']}\n\nA: {item['answer']}",
                    title=f"[bold]Chat #{i}[/bold]",
                    border_style="cyan"
                ))

    def run(self):
        """Main program loop"""
        try:
            while True:
                self.display_menu()
                choice = Prompt.ask(
                    "Select an option",
                    choices=["1", "2", "3", "4", "5", "6"]
                )

                if choice == "1":
                    url = Prompt.ask("\n[bold green]Enter YouTube URL[/bold green]")
                    with console.status("[bold green]Fetching transcript...") as status:
                        if self.get_transcript(url):
                            console.print("[bold green]✓ Transcript fetched successfully![/bold green]")
                        time.sleep(1)

                elif choice == "2":
                    if not self.transcript:
                        console.print("[red]Please input a YouTube URL first![/red]")
                    else:
                        console.print(Panel(
                            Markdown(self.transcript),
                            title="[bold]Video Transcript[/bold]",
                            border_style="green"
                        ))
                    Prompt.ask("\nPress Enter to continue")

                elif choice == "3":
                    if not self.transcript:
                        console.print("[red]Please input a YouTube URL first![/red]")
                    else:
                        summary = self.summarize_video()
                        console.print(Panel(
                            Markdown(summary),
                            title="[bold]Video Summary[/bold]",
                            border_style="yellow"
                        ))
                    Prompt.ask("\nPress Enter to continue")

                elif choice == "4":
                    if not self.transcript:
                        console.print("[red]Please input a YouTube URL first![/red]")
                    else:
                        while True:
                            question = Prompt.ask(
                                "\n[bold green]Ask a question about the video (or 'exit' to return)[/bold green]"
                            )
                            if question.lower() == 'exit':
                                break
                            response = self.chat_with_video(question)
                            console.print(Panel(
                                Markdown(response),
                                title="[bold]Answer[/bold]",
                                border_style="cyan"
                            ))

                elif choice == "5":
                    self.view_history()
                    Prompt.ask("\nPress Enter to continue")

                elif choice == "6":
                    console.print("[bold blue]Thank you for using ChatWithYoutube! 👋[/bold blue]")
                    break

        except KeyboardInterrupt:
            console.print("\n[bold red]Program terminated by user[/bold red]")
        except Exception as e:
            console.print(f"\n[bold red]An unexpected error occurred: {str(e)}[/bold red]")
        finally:
            console.print("[bold blue]Program ended[/bold blue]")

def main():
    try:
        app = ChatWithYoutube()
        app.run()
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()