# Duracost - Installation Calculator

A fence installation cost calculator application with a React frontend and FastAPI backend. Includes both an International Calculator and a UK-specific Calculator.

## Overview

This project calculates installation costs per meter for racing fence installations. Users can input project details including country, fence type, meters, and gates to get a detailed cost breakdown with markup options.

## Project Structure

```
.
├── frontend/           # React frontend (CRA with Craco)
│   ├── src/
│   │   ├── components/ # UI components (shadcn/ui)
│   │   ├── App.js      # Main application (International)
│   │   ├── UKCalculator.js # UK-specific calculator
│   │   └── index.js    # Entry point
│   ├── craco.config.js # Craco configuration with API proxy
│   └── package.json
├── backend/
│   ├── server.py       # FastAPI backend server (includes both calculators)
│   └── requirements.txt
└── replit.md           # Project documentation
```

## Architecture

- **Frontend**: React 19 with Craco, Tailwind CSS, shadcn/ui components
- **Backend**: FastAPI with Motor (async MongoDB driver)
- **Database**: MongoDB (requires MONGO_URL environment variable)

## Two Calculator Modes

### International Calculator (/)
- 8 workers base
- Country-based minimum wage calculations
- Ground fixing methods
- Supervision costs + flight tickets
- Fence types: OR, PR1, PR2

### UK Calculator (/uk)
- 2 workers base (£200/day each)
- Productivity: OR = 270m/day, PR/CM/CT/HM = 60m/day for 2 workers
- Accommodation: £75/day per person
- Transportation: £250 one-time
- Concrete cost: £2/meter for PR, CM, CT, HM systems
- Time-sensitive mode: calculates required workers to meet deadline
- Gate calculation: 2 hours per gate for 2 workers

## Environment Variables

- `REACT_APP_BACKEND_URL`: Backend API URL (empty for proxy mode)
- `MONGO_URL`: MongoDB connection string (default: mongodb://localhost:27017)
- `DB_NAME`: Database name (default: test_database)
- `CORS_ORIGINS`: Allowed CORS origins (default: *)

## Running the Project

The project has two workflows:
1. **Frontend**: Runs on port 5000 (exposed for webview, proxies /api to backend)
2. **Backend**: Runs on port 8000 (internal API)

## API Endpoints

### International API (/api)
- GET /api/countries - List available countries
- POST /api/calculate-preview - Calculate pricing
- POST /api/archive - Save calculation
- GET /api/calculations - Get archived calculations
- POST /api/delete-calculations - Delete calculations

### UK API (/api/uk)
- GET /api/uk/fence-types - List UK fence types
- POST /api/uk/calculate-preview - Calculate UK pricing
- POST /api/uk/archive - Save UK calculation
- GET /api/uk/calculations - Get archived UK calculations
- POST /api/uk/delete-calculations - Delete UK calculations

## Features

- Password-protected access (DFS_1991..)
- Switch between International and UK calculators
- Project details input
- Cost breakdown calculation
- Markup options (30%, 40%, 50%, 60%)
- Archive calculations to MongoDB
- View and delete archived calculations

## Recent Changes

- 2024-12-17: Added UK-specific calculator with time-sensitive mode
- 2024-12-17: Configured for Replit environment with proper host settings and API proxy
