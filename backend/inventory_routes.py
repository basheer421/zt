"""
Inventory management API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import database

router = APIRouter(prefix="/inventory", tags=["inventory"])

class InventoryItem(BaseModel):
    name: str
    category: str
    quantity: int
    unit: str
    location: Optional[str] = None
    description: Optional[str] = None

class InventoryItemResponse(InventoryItem):
    id: int
    created_at: str
    updated_at: str

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

@router.get("/items", response_model=List[InventoryItemResponse])
async def get_all_items():
    """Get all inventory items"""
    try:
        items = database.execute_query("""
            SELECT * FROM inventory 
            ORDER BY category, name
        """)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{item_id}", response_model=InventoryItemResponse)
async def get_item(item_id: int):
    """Get a specific inventory item"""
    try:
        items = database.execute_query("""
            SELECT * FROM inventory WHERE id = ?
        """, (item_id,))
        
        if not items:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return items[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/items", response_model=InventoryItemResponse)
async def create_item(item: InventoryItem):
    """Create a new inventory item"""
    try:
        item_id = database.execute_insert("""
            INSERT INTO inventory (name, category, quantity, unit, location, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item.name, item.category, item.quantity, item.unit, item.location, item.description))
        
        # Return the created item
        created_item = database.execute_query("""
            SELECT * FROM inventory WHERE id = ?
        """, (item_id,))
        
        return created_item[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/items/{item_id}", response_model=InventoryItemResponse)
async def update_item(item_id: int, item: InventoryItemUpdate):
    """Update an inventory item"""
    try:
        # Check if item exists
        existing = database.execute_query("""
            SELECT * FROM inventory WHERE id = ?
        """, (item_id,))
        
        if not existing:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Build update query dynamically based on provided fields
        updates = []
        params = []
        
        if item.name is not None:
            updates.append("name = ?")
            params.append(item.name)
        if item.category is not None:
            updates.append("category = ?")
            params.append(item.category)
        if item.quantity is not None:
            updates.append("quantity = ?")
            params.append(item.quantity)
        if item.unit is not None:
            updates.append("unit = ?")
            params.append(item.unit)
        if item.location is not None:
            updates.append("location = ?")
            params.append(item.location)
        if item.description is not None:
            updates.append("description = ?")
            params.append(item.description)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(item_id)
            
            database.execute_update(f"""
                UPDATE inventory 
                SET {', '.join(updates)}
                WHERE id = ?
            """, tuple(params))
        
        # Return updated item
        updated_item = database.execute_query("""
            SELECT * FROM inventory WHERE id = ?
        """, (item_id,))
        
        return updated_item[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Delete an inventory item"""
    try:
        # Check if item exists
        existing = database.execute_query("""
            SELECT * FROM inventory WHERE id = ?
        """, (item_id,))
        
        if not existing:
            raise HTTPException(status_code=404, detail="Item not found")
        
        database.execute_update("""
            DELETE FROM inventory WHERE id = ?
        """, (item_id,))
        
        return {"message": "Item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories():
    """Get all unique categories"""
    try:
        categories = database.execute_query("""
            SELECT DISTINCT category FROM inventory 
            ORDER BY category
        """)
        return [c["category"] for c in categories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
