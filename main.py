from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

app = FastAPI(title="Notion Proxy API for Custom GPT")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

class UpdateRequest(BaseModel):
    subject: str
    unit: str
    updatedNote: str

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Notion Proxy API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #2563eb; }
                code { background-color: #f1f5f9; padding: 2px 5px; border-radius: 4px; }
                pre { background-color: #f1f5f9; padding: 15px; border-radius: 8px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <h1>Notion Proxy API for Custom GPT</h1>
            <p>This API serves as a proxy between a Custom GPT and the Notion API.</p>
            <h2>API Endpoints</h2>
            <p><strong>POST /update-progress</strong> - Update a note in Notion</p>
            <h3>Request Body Example:</h3>
            <pre>
{
  "subject": "Math",
  "unit": "Calculus",
  "updatedNote": "Learned derivatives and integrals."
}
            </pre>
            <p>For more details, see the <a href="/docs">API documentation</a>.</p>
        </body>
    </html>
    """

@app.post("/update-progress")
def update_progress(data: UpdateRequest):
    # Step 1: Query the database
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    query_payload = {
        "filter": {
            "and": [
                {
                    "property": "Subject",
                    "select": {"equals": data.subject}
                },
                {
                    "property": "Unit",
                    "rich_text": {"equals": data.unit}
                }
            ]
        }
    }

    response = requests.post(query_url, headers=headers, json=query_payload)
    results = response.json().get("results", [])

    if not results:
        raise HTTPException(status_code=404, detail="No matching entry found.")

    page = results[0]
    page_id = page["id"]
    
    previous_note = ""
    if "Note" in page["properties"]:
        note_data = page["properties"]["Note"]
        if note_data["type"] == "rich_text":
            previous_note = "".join([t["plain_text"] for t in note_data["rich_text"]])

    # Step 2: Update the note
    update_url = f"https://api.notion.com/v1/pages/{page_id}"
    update_payload = {
        "properties": {
            "Note": {
                "rich_text": [
                    {
                        "text": {"content": data.updatedNote}
                    }
                ]
            }
        }
    }

    update_res = requests.patch(update_url, headers=headers, json=update_payload)
    if update_res.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to update the note.")

    return {
        "subject": data.subject,
        "unit": data.unit,
        "previousNote": previous_note,
        "updatedNote": data.updatedNote
    } 