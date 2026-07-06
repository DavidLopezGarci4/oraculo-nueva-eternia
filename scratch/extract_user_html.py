import os
import json

log_dir = r"C:\Users\dace8\.gemini\antigravity\brain\f2726ea7-8397-419d-94e8-f63fddb3fbcd\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript_full.jsonl")

def extract():
    print(f"Reading {transcript_path}...")
    if not os.path.exists(transcript_path):
        print("Transcript file does not exist!")
        return
        
    last_user_message = ""
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    last_user_message = data.get("content", "")
            except Exception as e:
                pass
                
    if not last_user_message:
        print("No user message found!")
        return
        
    print("Found user message. Searching for HTML content...")
    # Find where <body class="antialiased"> starts
    start_tag = '<body class="antialiased">'
    idx = last_user_message.find(start_tag)
    if idx == -1:
        print("Could not find start tag!")
        # Let's write the whole message to check
        with open("scratch/last_msg.txt", "w", encoding="utf-8") as out:
            out.write(last_user_message)
        print("Wrote last_msg.txt for debug")
        return
        
    html_content = last_user_message[idx:]
    # Remove any trailing prompt markers or formatting if present
    # Usually it goes to the end of the input
    with open("scratch/user_smyths_html.html", "w", encoding="utf-8") as out:
        out.write(html_content)
    print(f"Extracted html content ({len(html_content)} bytes) to scratch/user_smyths_html.html")

if __name__ == "__main__":
    extract()
