import sqlite3
import os

def analyze():
    print("[DB ANALYZER] Checking product price statistics in oraculo.db...")
    db_path = "oraculo.db"
    
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Total products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    
    # 2. Products with p25_price > 0
    cursor.execute("SELECT COUNT(*) FROM products WHERE p25_price > 0")
    p25_gt_zero = cursor.fetchone()[0]
    
    # 3. Products with avg_market_price > 0
    cursor.execute("SELECT COUNT(*) FROM products WHERE avg_market_price > 0")
    avg_gt_zero = cursor.fetchone()[0]
    
    # 4. Products with retail_price > 0
    cursor.execute("SELECT COUNT(*) FROM products WHERE retail_price > 0")
    retail_gt_zero = cursor.fetchone()[0]

    # 5. Let's inspect some values
    cursor.execute("SELECT id, name, p25_price, avg_market_price, retail_price FROM products LIMIT 5")
    rows = cursor.fetchall()

    print(f"\nTotal Products: {total_products}")
    print(f"Products with p25_price > 0: {p25_gt_zero}")
    print(f"Products with avg_market_price > 0: {avg_gt_zero}")
    print(f"Products with retail_price > 0: {retail_gt_zero}")
    
    print("\nSample Products:")
    for row in rows:
        print(f"- ID {row[0]}: '{row[1]}' | p25={row[2]} | avg={row[3]} | retail={row[4]}")
        
    # 6. Check how many offers have opportunity_score > 0
    cursor.execute("SELECT COUNT(*) FROM offers WHERE opportunity_score > 0")
    offers_score_gt_zero = cursor.fetchone()[0]
    print(f"\nOffers with opportunity_score > 0: {offers_score_gt_zero}")
        
    conn.close()

if __name__ == "__main__":
    analyze()
