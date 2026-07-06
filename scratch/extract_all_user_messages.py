import os
import json

log_dir = r"C:\Users\dace8\.gemini\antigravity\brain\f2726ea7-8397-419d-94e8-f63fddb3fbcd\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript_full.jsonl")

def extract():
    print(f"Reading {transcript_path}...")
    if not os.path.exists(transcript_path):
        print("Transcript file does not exist!")
        return
        
    found_html = False
    with open(transcript_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            try:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    content = data.get("content", "")
                    if "smyths-toys-app" in content:
                        print(f"Found HTML in USER_INPUT at line {idx}!")
                        # Extract HTML starting from <body or div id="smyths-toys-app"
                        start_tag = 'div id="smyths-toys-app"'
                        pos = content.find(start_tag)
                        if pos == -1:
                            # Try body tag
                            start_tag = '<body class="antialiased">'
                            pos = content.find(start_tag)
                        if pos != -1:
                            html_block = content[pos:]
                            # Find where user request ended or write to end
                            # If there's an ending tag we can search for, or write the rest
                            out_path = "scratch/user_smyths_html.html"
                            with open(out_path, "w", encoding="utf-8") as out:
                                out.write(html_block)
                            print(f"Saved {len(html_block)} bytes of html to {out_path}")
                            found_html = True
                            break
            except Exception as e:
                pass
                
    if not found_html:
        print("Could not find any user message containing 'smyths-toys-app'!")

if __name__ == "__main__":
    extract()
