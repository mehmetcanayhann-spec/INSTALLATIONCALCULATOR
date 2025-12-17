from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import math
import certifi
import ssl

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection configuration
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'test_database')

# Check if it's an Atlas connection (mongodb+srv) or local
if 'mongodb+srv' in mongo_url or 'mongodb.net' in mongo_url:
    # Atlas connection with SSL
    client = AsyncIOMotorClient(
        mongo_url,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000
    )
else:
    # Local MongoDB connection
    client = AsyncIOMotorClient(mongo_url)

db = client[db_name]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"MongoDB configured: {db_name}")

app = FastAPI()
api_router = APIRouter(prefix="/api")

COUNTRY_MIN_WAGES = {
    "United Kingdom": 12.21,
    "Ireland": 13.50,
    "France": 11.88,
    "Germany": 12.82,
    "Netherlands": 13.68,
    "Belgium": 12.01,
    "Spain": 8.51,
    "Italy": 9.80,
    "Portugal": 5.23,
    "Poland": 4.95,
    "Czech Republic": 4.95,
    "Austria": 12.85,
    "Switzerland": 25.00,
    "Sweden": 0.00,
    "Norway": 0.00,
    "Denmark": 0.00,
    "United Arab Emirates": 2.72,
    "Saudi Arabia": 2.67,
    "Qatar": 2.00,
    "Kuwait": 2.72,
    "Oman": 1.68,
    "Bahrain": 2.13,
    "Turkey": 3.29,
    "Egypt": 1.36,
    "Jordan": 2.27,
    "Lebanon": 1.00,
    "United States": 7.25,
    "Canada": 11.00,
    "Australia": 23.23,
    "New Zealand": 22.70,
}

class CalculationRequest(BaseModel):
    user_name: str
    project_name: str
    country: str
    fence_type: str
    meters: float
    gates: int

class CostBreakdown(BaseModel):
    work_days: float
    daily_rate_per_man: Optional[float] = 0.0
    labor_cost: float
    tools_cost: float
    supervision_cost: float
    flight_ticket: float
    ground_fixing_screws: Optional[float] = 0.0
    raw_total: float
    rate_per_meter: float
    markup_30: float
    markup_40: float
    markup_50: float
    markup_60: float

class Calculation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_name: str
    project_name: str
    country: str
    fence_type: str
    meters: float
    gates: int
    breakdown: CostBreakdown
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CalculationResponse(BaseModel):
    calculation: Calculation

@api_router.get("/")
async def root():
    return {"message": "Racing Fence Installation Pricing API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@api_router.get("/countries")
async def get_countries():
    return {"countries": sorted(list(COUNTRY_MIN_WAGES.keys()))}

def calculate_pricing(request: CalculationRequest):
    """Helper function to calculate pricing without saving to database"""
    if request.country not in COUNTRY_MIN_WAGES:
        raise HTTPException(status_code=400, detail="Invalid country selected")
    
    min_wage = COUNTRY_MIN_WAGES[request.country]
    
    if min_wage == 0:
        min_wage = 15.00
    
    fence_types = {
"OR":136,
"PR1":136,
"PR2":128}
 
    daily_capacity = fence_types[request.fence_type]
    
    fence_days = request.meters / daily_capacity
    gate_days = request.gates * 0.25
    setup_cleanup_days = 1
    total_work_days_calculated = fence_days + gate_days + setup_cleanup_days
    
    total_work_days = math.ceil(total_work_days_calculated)
    
    hourly_labor_rate = 2 * min_wage
    daily_rate_per_man = hourly_labor_rate * 8
    daily_labor_cost = 8 * daily_rate_per_man
    total_labor_cost = daily_labor_cost * total_work_days
    
    tools_base = 200
    tools_daily = 100 * total_work_days
    total_tools_cost = tools_base + tools_daily
    
    supervision_daily = 250 * total_work_days
    flight_ticket = 500
    total_supervision_cost = supervision_daily
    
    ground_fixing_screws_cost = request.meters * 0.78
    
    raw_total = total_labor_cost + total_tools_cost + total_supervision_cost + flight_ticket + ground_fixing_screws_cost
    rate_per_meter = raw_total / request.meters
    
    breakdown = CostBreakdown(
        work_days=float(total_work_days),
        daily_rate_per_man=round(daily_rate_per_man, 2),
        labor_cost=round(total_labor_cost, 2),
        tools_cost=round(total_tools_cost, 2),
        supervision_cost=round(total_supervision_cost, 2),
        flight_ticket=flight_ticket,
        ground_fixing_screws=round(ground_fixing_screws_cost, 2),
        raw_total=round(raw_total, 2),
        rate_per_meter=round(rate_per_meter, 2),
        markup_30=round(raw_total * 1.30, 2),
        markup_40=round(raw_total * 1.40, 2),
        markup_50=round(raw_total * 1.50, 2),
        markup_60=round(raw_total * 1.60, 2)
    )
    
    calculation = Calculation(
        user_name=request.user_name,
        project_name=request.project_name,
        country=request.country,
        fence_type=request.fence_type,
        meters=request.meters,
        gates=request.gates,
        breakdown=breakdown
    )
    
    return calculation

@api_router.post("/calculate-preview", response_model=CalculationResponse)
async def calculate_preview(request: CalculationRequest):
    """Calculate pricing without saving to database"""
    calculation = calculate_pricing(request)
    return {"calculation": calculation}

@api_router.post("/archive", response_model=CalculationResponse)
async def archive_calculation(calculation: Calculation):
    """Save calculation to archive"""
    doc = calculation.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.calculations.insert_one(doc)
    
    return {"calculation": calculation}

class DeleteRequest(BaseModel):
    ids: List[str]

@api_router.post("/delete-calculations")
async def delete_calculations(request: DeleteRequest):
    """Delete calculations by IDs"""
    try:
        result = await db.calculations.delete_many({"id": {"$in": request.ids}})
        return {"deleted_count": result.deleted_count, "ids": request.ids}
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error deleting calculations: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete calculations")

@api_router.get("/calculations")
async def get_calculations():
    calculations = await db.calculations.find({}, {"_id": 0}).sort("timestamp", -1).to_list(100)
    
    result = []
    for calc in calculations:
        try:
            if isinstance(calc['timestamp'], str):
                calc['timestamp'] = datetime.fromisoformat(calc['timestamp'])
            
            # Add default values for new fields if they don't exist (backwards compatibility)
            if 'breakdown' in calc:
                if 'daily_rate_per_man' not in calc['breakdown']:
                    calc['breakdown']['daily_rate_per_man'] = 0.0
                if 'ground_fixing_screws' not in calc['breakdown']:
                    calc['breakdown']['ground_fixing_screws'] = 0.0
            
            # Validate and convert to Calculation model
            validated_calc = Calculation(**calc)
            result.append(validated_calc.model_dump())
        except Exception as e:
            # Skip invalid calculations
            logger = logging.getLogger(__name__)
            logger.warning(f"Skipping invalid calculation: {e}")
            continue
    
    return result

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()