import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APIConnectionError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Load environment variables
load_dotenv()

# Initialize OpenAI client with NVIDIA endpoint
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

# Configuration
QUEUE_FILE = "research_queue.md"
OUTPUT_DIR = Path("research_outputs")
PRIMARY_MODEL = "nvidia/nemotron-3-super-120b-a12b"
FALLBACK_MODEL = "meta/llama-3.1-405b-instruct"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type((RateLimitError, APIConnectionError, TimeoutError)),
    reraise=True
)
def fetch_research(topic, model=PRIMARY_MODEL):
    """Fetches research content with exponential backoff on rate limits."""
    print(f"  -> Attempting with model: {model}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an autonomous research agent. Provide detailed, well-structured analytical responses formatted in Markdown."},
            {"role": "user", "content": topic}
        ],
        stream=True,
        temperature=0.6,
        top_p=0.9,
    )
    
    output = []
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            output.append(content)
    print() # New line after stream
    return "".join(output)


def process_topic(topic):
    """Processes a single topic, handling fallbacks if necessary."""
    try:
        return fetch_research(topic, model=PRIMARY_MODEL)
    except Exception as e:
        print(f"\n  [!] Primary model failed with error: {e}")
        print(f"  -> Falling back to {FALLBACK_MODEL}")
        try:
            return fetch_research(topic, model=FALLBACK_MODEL)
        except Exception as e:
            print(f"\n  [!] Fallback model also failed: {e}")
            return None


def sanitize_filename(name):
    """Creates a safe filename from a topic string."""
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name)
    name = name.strip().replace(' ', '_').lower()
    return name[:50] + ".md"


def main():
    if not os.path.exists(QUEUE_FILE):
        print(f"Queue file '{QUEUE_FILE}' not found. Please create one.")
        return

    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match blocks starting with '- [ ] ' up to the next '- [ ] ' or '- [x] ' or EOF
    pattern = re.compile(r'(- \[ \] .*)(?=(?:\n- \[ [ x] \] )|\Z)', re.DOTALL)
    matches = list(pattern.finditer(content))

    if not matches:
        print("\nNo new topics found in the queue.")
        return

    for match in matches:
        block = match.group(1)
        # First line is the title line
        lines = block.splitlines()
        first_line = lines[0].replace("- [ ] ", "").strip()
        full_topic = block.replace("- [ ] ", "", 1).strip()
        
        print(f"\n[Processing] {first_line[:80]}...")
        
        result = process_topic(full_topic)
        
        if result:
            filename = sanitize_filename(first_line)
            filepath = OUTPUT_DIR / filename
            
            final_content = f"# {first_line}\n\n{result}"
            
            with open(filepath, 'w', encoding='utf-8') as out_f:
                out_f.write(final_content)
            print(f"[Success] Saved output to {filepath}")
            
            # Replace '- [ ] ' with '- [x] ' for this specific block in content
            content = content[:match.start()] + block.replace("- [ ] ", "- [x] ", 1) + content[match.end():]
            with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Queue updated successfully.")
        else:
            print(f"[Failed] Could not complete research for: {first_line[:50]}")

if __name__ == "__main__":
    main()
