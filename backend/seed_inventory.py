"""
Seed inventory data for Company X
"""
import database

def seed_inventory():
    """Add sample inventory items"""
    print("Seeding inventory data...")
    
    inventory_items = [
        # Office Supplies
        ("A4 Paper", "Office Supplies", 500, "reams", "Storage Room A", "White printer paper, 80gsm"),
        ("Blue Pens", "Office Supplies", 150, "boxes", "Storage Room A", "Ballpoint pens, blue ink"),
        ("Black Pens", "Office Supplies", 120, "boxes", "Storage Room A", "Ballpoint pens, black ink"),
        ("Notebooks", "Office Supplies", 75, "units", "Storage Room A", "A5 lined notebooks"),
        ("Staplers", "Office Supplies", 8, "units", "Storage Room A", "Standard office staplers"),
        
        # Electronics
        ("Laptops", "Electronics", 25, "units", "IT Storage", "Dell Latitude 5420, i5, 16GB RAM"),
        ("Monitors", "Electronics", 30, "units", "IT Storage", "24-inch LED monitors"),
        ("Keyboards", "Electronics", 15, "units", "IT Storage", "Wireless keyboards"),
        ("Mice", "Electronics", 18, "units", "IT Storage", "Wireless optical mice"),
        ("USB Cables", "Electronics", 45, "units", "IT Storage", "USB-C to USB-A, 2m"),
        
        # Furniture
        ("Office Chairs", "Furniture", 12, "units", "Warehouse B", "Ergonomic mesh back chairs"),
        ("Desks", "Furniture", 8, "units", "Warehouse B", "Adjustable height desks"),
        ("Filing Cabinets", "Furniture", 5, "units", "Warehouse B", "4-drawer metal cabinets"),
        
        # Cleaning Supplies
        ("Disinfectant Spray", "Cleaning", 35, "bottles", "Janitor Closet", "Multi-surface disinfectant"),
        ("Paper Towels", "Cleaning", 60, "rolls", "Janitor Closet", "Industrial paper towels"),
        ("Trash Bags", "Cleaning", 40, "boxes", "Janitor Closet", "50-gallon heavy duty"),
        
        # Kitchen Supplies
        ("Coffee Beans", "Kitchen", 12, "kg", "Kitchen", "Arabica coffee beans"),
        ("Tea Bags", "Kitchen", 200, "boxes", "Kitchen", "Assorted tea flavors"),
        ("Paper Cups", "Kitchen", 25, "packs", "Kitchen", "8oz disposable cups"),
        ("Sugar Packets", "Kitchen", 80, "boxes", "Kitchen", "Individual sugar sachets"),
        
        # Safety Equipment
        ("Hard Hats", "Safety", 20, "units", "Safety Room", "ANSI certified hard hats"),
        ("Safety Vests", "Safety", 15, "units", "Safety Room", "High-visibility vests"),
        ("First Aid Kits", "Safety", 6, "units", "Safety Room", "Complete first aid kits"),
        ("Fire Extinguishers", "Safety", 8, "units", "Various Locations", "ABC type, 5lb"),
    ]
    
    for item in inventory_items:
        name, category, quantity, unit, location, description = item
        database.execute_insert("""
            INSERT INTO inventory (name, category, quantity, unit, location, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, category, quantity, unit, location, description))
    
    print(f"✓ Added {len(inventory_items)} inventory items")

if __name__ == "__main__":
    # Initialize database first
    database.init_db()
    
    # Check if inventory is already seeded
    existing = database.execute_query("SELECT COUNT(*) as count FROM inventory")
    if existing[0]["count"] > 0:
        print("Inventory already seeded. Skipping...")
    else:
        seed_inventory()
    
    print("Done!")
