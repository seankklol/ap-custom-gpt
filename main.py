from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

app = FastAPI()

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

class UpdateRequest(BaseModel):
    subject: str
    unit: str
    updatedNote: str

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
        return {"error": "No matching entry found."}, 404

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
        return {"error": "Failed to update the note."}, 500

    return {
        "subject": data.subject,
        "unit": data.unit,
        "previousNote": previous_note,
        "updatedNote": data.updatedNote
    } 