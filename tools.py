import os
import uuid
import sqlite3
from datetime import datetime
from langchain_core.tools import tool
import httpx

# ==========================================
# HELPER: Local SQL Database Connection
# ==========================================
def get_db_connection():
    """Connects to our local SQLite database (chinhin_erp.db)."""
    # check_same_thread=False is required for FastAPI/Streamlit compatibility
    conn = sqlite3.connect('chinhin_erp.db', check_same_thread=False)
    # This allows us to access data by column name: row['buyer_name']
    conn.row_factory = sqlite3.Row 
    return conn

def row_to_dict(row):
    """Simplified helper to convert SQLite Row to a standard Dictionary"""
    if not row: return None
    return dict(row)

# ==========================================
# TOOL 1: Retrieve Buyer Info
# ==========================================
@tool
def get_buyer_status(buyer_id: str) -> str:
    """
    Use this tool to find a homebuyer's current transaction status and milestones.
    Input should be a buyer_id (e.g., 'USER-1234').
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Transactions WHERE buyer_id = ?", (buyer_id.upper(),))
        row = cursor.fetchone()
        
        if row:
            data = row_to_dict(row)
            return f"Data found for {buyer_id}: {data}"
        return f"Error: No transaction found for Buyer ID {buyer_id}."
        
    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        if 'conn' in locals(): conn.close()

# ==========================================
# TOOL 2: Simulate iDsaya E-Signature
# ==========================================
@tool
def trigger_idsaya_esignature(transaction_id: str) -> str:
    """
    Use this tool ONLY when the user explicitly agrees to sign their SPA.
    Input should be the transaction_id (e.g., 'TXN-ABC12345').
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT is_spa_signed FROM Transactions WHERE transaction_id = ?", (transaction_id.upper(),))
        row = cursor.fetchone()
        
        if not row:
            return "Error: Transaction ID not found."
        
        if row['is_spa_signed']:
            return "The SPA is already signed."
            
        idsaya_id = f"IDS-{uuid.uuid4().hex[:6].upper()}"
        
        cursor.execute("""
            UPDATE Transactions 
            SET is_spa_signed = 1, 
                idsaya_transaction_id = ?, 
                current_stage = '3_PENDING_ESTAMP' 
            WHERE transaction_id = ?
        """, (idsaya_id, transaction_id.upper()))
        
        conn.commit()
        return f"Success: iDsaya signature completed. Stage updated to 3_PENDING_ESTAMP. ID: {idsaya_id}"
        
    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        if 'conn' in locals(): conn.close()

# ==========================================
# TOOL 3: Simulate LHDN E-Stamping
# ==========================================
@tool
def submit_lhdn_estamp(transaction_id: str) -> str:
    """
    Use this tool to submit a signed SPA to the government (LHDN) for stamping.
    Input should be the transaction_id.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT is_spa_signed FROM Transactions WHERE transaction_id = ?", (transaction_id.upper(),))
        row = cursor.fetchone()
        
        if not row:
            return "Error: Transaction ID not found."
        
        if not row['is_spa_signed']:
            return "Error: Cannot stamp an unsigned SPA. Please sign via iDsaya first."
            
        lhdn_cert = f"LHDN-{uuid.uuid4().hex[:6].upper()}"
        
        cursor.execute("""
            UPDATE Transactions 
            SET is_spa_stamped = 1, 
                lhdn_certificate_no = ?, 
                current_stage = '4_CONSTRUCTION_ACTIVE' 
            WHERE transaction_id = ?
        """, (lhdn_cert, transaction_id.upper()))
        
        conn.commit()
        return f"Success: LHDN Stamping completed. Certificate No: {lhdn_cert}."
        
    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        if 'conn' in locals(): conn.close()

# ==========================================
# TOOL 4: Check Construction Progress
# ==========================================
@tool
def check_construction_progress(unit_id: str) -> str:
    """
    Use this tool to check the physical construction progress of a property.
    Input should be the unit_id (e.g., 'CHI-45-678').
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT project_name, construction_percentage FROM Properties WHERE unit_id = ?", (unit_id.upper(),))
        row = cursor.fetchone()
        
        if row:
            return f"Unit {unit_id} ({row['project_name']}) is currently at {row['construction_percentage']}% completion."
        return "Error: Unit ID not found in ERP."
        
    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        if 'conn' in locals(): conn.close()

# ==========================================
# TOOL 5: Search Market Trends
# ==========================================
@tool
def search_market_trends(topic: str) -> str:
    """
    Use this tool to search the live web for property market news, 
    bank interest rates (BLR/OPR), or Chin Hin corporate updates.
    Input should be a search query (e.g., 'Malaysia bank interest rates 2026').
    """
    try:
        target_url = f"https://www.thestar.com.my/search/?q={topic.replace(' ', '+')}"
        reader_url = f"https://r.jina.ai/{target_url}"
        
        with httpx.Client() as client:
            response = client.get(reader_url, timeout=10.0)
            return response.text[:2000] 
            
    except Exception as e:
        return f"Could not access live web data: {str(e)}"

# ==========================================
# TOOL 6: Read iDsaya Guides
# ==========================================
@tool
def get_idsaya_espa_guide() -> str:
    """
    Use this tool to read the official guides for iDsaya and Malaysia Government's Digital ID eSPA signing.
    """
    try:
        file1 = os.path.join("project_docs", "What Is iDsaya_ Malaysia Government’s Digital ID & Guide to eSPA Signing.html")
        file2 = os.path.join("project_docs", "iDsaya – Verified and Validated Identity Profile Services.html")
        
        content = ""
        # Read the first guide
        if os.path.exists(file1):
            with open(file1, "r", encoding="utf-8") as f:
                content += f.read() + "\n\n"
        # Read the second guide
        if os.path.exists(file2):
            with open(file2, "r", encoding="utf-8") as f:
                content += f.read()
                
        return content if content else "Error: iDsaya HTML files not found in project_docs folder."
    except Exception as e:
        return f"Error reading local files: {str(e)}"

# ==========================================
# TOOL 7: Read LHDN Stamping Guide
# ==========================================
@tool
def get_lhdn_stamping_guide() -> str:
    """
    Use this tool to read the official guide on how to digitally stamp a document in Malaysia using LHDN STAMPS.
    """
    try:
        file_path = os.path.join("project_docs", "How do I digitally stamp a document in Malaysia (LHDN STAMPS)_.html")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Error: LHDN STAMPS HTML file not found in project_docs folder."
    except Exception as e:
        return f"Error reading local file: {str(e)}"