# Simple Data Keeper

A lightweight file storage microservice built with FastAPI.

## API Endpoints

- `POST /files` - Upload a file
- `GET /files/{file_id}` - Download a file
- `DELETE /files/{file_id}` - Delete a file
- `GET /ping` - Health check

## Features

- File upload with optional hash verification
- Background file processing support
- Local file storage driver
- Health monitoring endpoint

## Getting Started

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
uvicorn app.main:app
```
API documentation available at `/docs` when running in development mode.
