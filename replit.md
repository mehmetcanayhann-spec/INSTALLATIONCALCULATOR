# Duracost - Installation Calculator

A fence installation cost calculator application with a React frontend and FastAPI backend.

## Overview

This project calculates installation costs per meter for racing fence installations. Users can input project details including country, fence type, meters, and gates to get a detailed cost breakdown with markup options.

## Project Structure

```
.
├── frontend/           # React frontend (CRA with Craco)
│   ├── src/
│   │   ├── components/ # UI components (shadcn/ui)
│   │   ├── App.js      # Main application
│   │   └── index.js    # Entry point
│   ├── craco.config.js # Craco configuration
│   └── package.json
├── backend/
│   ├── server.py       # FastAPI backend server
│   └── requirements.txt
└── replit.md           # Project documentation
```

## Architecture

- **Frontend**: React 19 with Craco, Tailwind CSS, shadcn/ui components
- **Backend**: FastAPI with Motor (async MongoDB driver)
- **Database**: MongoDB (requires MONGO_URL environment variable)

## Environment Variables

- `REACT_APP_BACKEND_URL`: Backend API URL (default: http://localhost:8000)
- `MONGO_URL`: MongoDB connection string (default: mongodb://localhost:27017)
- `DB_NAME`: Database name (default: test_database)
- `CORS_ORIGINS`: Allowed CORS origins (default: *)

## Running the Project

The project has two workflows:
1. **Frontend**: Runs on port 5000 (exposed for webview)
2. **Backend**: Runs on port 8000 (internal API)

## Features

- Password-protected access
- Project details input (name, country, fence type, etc.)
- Cost breakdown calculation
- Markup options (30%, 40%, 50%, 60%)
- Archive calculations to MongoDB
- View and delete archived calculations

## Recent Changes

- 2024-12-17: Configured for Replit environment with proper host settings
