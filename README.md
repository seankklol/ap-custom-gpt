# Notion Proxy API for Custom GPT

This repository contains a FastAPI server that acts as a proxy between a Custom GPT action and the Notion API.

## Features

- Accepts `subject`, `unit`, and `updatedNote` via POST request
- Searches your Notion database using filters
- Reads the existing `Note`
- Updates the note
- Returns both previous and updated note to GPT

## File Structure

```
notion-gpt-api/
├── main.py              # FastAPI server code
├── requirements.txt     # Python dependencies
├── render.yaml          # Render.com configuration
└── .env (optional)      # Local environment variables
```

## Setup Instructions

### 1. Create a Notion Integration

1. Go to [https://www.notion.com/my-integrations](https://www.notion.com/my-integrations)
2. Create a new integration
3. Copy the **Internal Integration Token**
4. Share your **Notion database** with this integration

### 2. Deploy on Render.com

1. Go to [https://render.com](https://render.com) and log in or create an account
2. Click "New Web Service"
3. Choose "Deploy from GitHub"
4. Connect your GitHub and select this repository
5. Render will auto-detect the app from the `render.yaml` configuration
6. Set your environment variables:
   - `NOTION_TOKEN`: your Notion internal integration token
   - `DATABASE_ID`: your Notion database ID (e.g., `Progress-database-1bb6de3a6fd780e2bc72f1462a6709b4`)
7. Click "Deploy"

### 3. Add to Custom GPT (Actions Tab)

Use the Render.com URL in your OpenAPI schema:

```yaml
servers:
  - url: https://your-app-name.onrender.com
```

## Local Development

1. Create a `.env` file with your Notion token and database ID:
```
NOTION_TOKEN=secret_xxx
DATABASE_ID=your-database-id
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the server:
```
uvicorn main:app --reload
```

## API Usage

Send a POST request to `/update-progress` with the following JSON body:

```json
{
  "subject": "Math",
  "unit": "Calculus",
  "updatedNote": "Learned derivatives and integrals."
}
```

The API will return:

```json
{
  "subject": "Math",
  "unit": "Calculus",
  "previousNote": "Started learning calculus basics.",
  "updatedNote": "Learned derivatives and integrals."
}
``` # ap-custom-gpt
