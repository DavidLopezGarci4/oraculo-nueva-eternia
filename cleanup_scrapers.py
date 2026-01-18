import sys
from pathlib import Path

# Add project root to Python path
root_path = Path(__file__).resolve().parent
sys.path.append(str(root_path))

from src.infrastructure.database_cloud import SessionCloud as Session
from src.domain.models import ScraperStatusModel

def cleanup_duplicates():
    with Session() as db:
        statuses = db.query(ScraperStatusModel).all()
        
        # Deduplication strategy: Keep the one with most capital letters (likely standardized)
        unique_map = {}
        to_delete = []
        
        for s in statuses:
            key = s.spider_name.lower()
            if key not in unique_map:
                unique_map[key] = s
            else:
                existing = unique_map[key]
                # Compare capitals
                new_caps = len([c for c in s.spider_name if c.isupper()])
                old_caps = len([c for c in existing.spider_name if c.isupper()])
                
                if new_caps > old_caps:
                    to_delete.append(existing)
                    unique_map[key] = s
                else:
                    to_delete.append(s)
        
        if to_delete:
            print(f"Cleaning up {len(to_delete)} duplicate entries...")
            for s in to_delete:
                print(f"Deleting duplicate: {s.spider_name} (ID: {s.id})")
                db.delete(s)
            db.commit()
            print("Cleanup complete.")
        else:
            print("No duplicates found.")

if __name__ == "__main__":
    cleanup_duplicates()
