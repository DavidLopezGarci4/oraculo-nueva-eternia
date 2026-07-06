import os
import json

log_dir = r"C:\Users\dace8\.gemini\antigravity\brain\f2726ea7-8397-419d-94e8-f63fddb3fbcd\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript_full.jsonl")

def search_context():
    if not os.path.exists(transcript_path):
        return
        
    messages = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    content = data.get("content", "")
                    messages.append(("USER", content))
                elif data.get("type") == "PLANNER_RESPONSE":
                    content = data.get("content", "")
                    messages.append(("AGENT", content))
            except Exception as e:
                pass
                
    # Write last 30 messages to scratch/prev_messages.txt
    with open("scratch/prev_messages.txt", "w", encoding="utf-8") as out:
        out.write(f"Total messages: {len(messages)}\n")
        # Find where "titulo" or "descripción" or Motu or Smyths is mentioned in USER messages
        user_msgs = [m for m in messages if m[0] == "USER"]
        out.write("--- LATEST USER MESSAGES ---\n")
        for idx, (sender, msg) in enumerate(user_msgs[-15:]):
            out.write(f"\n[USER MESSAGE {idx}]:\n{msg}\n")
            
        out.write("\n--- LATEST EXCHANGE FLOW ---\n")
        for idx, (sender, msg) in enumerate(messages[-25:]):
            out.write(f"\n[{sender} - {idx}]:\n{msg[:1000]}\n")

if __name__ == "__main__":
    search_context()
