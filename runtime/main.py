from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import datetime
import json
import os
import csv
import io

from .ledger import EventLedger # Import the EventLedger class

# Initialize FastAPI app
app = FastAPI(
    title="SimDecisions Event Ledger API",
    description="API for recording and querying simulation events.",
    version="1.0.0",
)

# Initialize EventLedger
# Assuming data/events.db is relative to the project root,
# but the ledger expects it relative to where the script is run
# or absolute. For FastAPI, it's usually relative to the project root
# where uvicorn is started.
script_dir = os.path.dirname(__file__)
db_path = os.path.join(script_dir, "..", "data", "events.db")
ledger = EventLedger(db_path=os.path.abspath(db_path))

# Pydantic model for the POST /api/events request body
class EventCreate(BaseModel):
    event_type: str
    actor: str
    target: Optional[str] = None
    domain: Optional[str] = None
    signal_type: Optional[str] = Field(None, pattern="^(gravity|light|internal)$")
    oracle_tier: Optional[int] = Field(None, ge=0, le=4)
    random_seed: Optional[int] = None
    completion_promise: Optional[str] = None
    verification_method: Optional[str] = None
    payload_json: Optional[Dict[str, Any]] = None
    cost_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    cost_carbon: Optional[float] = None

# Endpoint to record a new event
@app.post("/api/events", summary="Record a new event in the ledger")
async def record_event_endpoint(event: EventCreate):
    try:
        event_id = ledger.record_event(
            event_type=event.event_type,
            actor=event.actor,
            target=event.target,
            domain=event.domain,
            signal_type=event.signal_type,
            oracle_tier=event.oracle_tier,
            random_seed=event.random_seed,
            completion_promise=event.completion_promise,
            verification_method=event.verification_method,
            payload_json=event.payload_json,
            cost_tokens=event.cost_tokens,
            cost_usd=event.cost_usd,
            cost_carbon=event.cost_carbon
        )
        return {"status": "ok", "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Endpoint to query events
@app.get("/api/events", summary="Query events from the ledger")
async def query_events_endpoint(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    actor: Optional[str] = Query(None, description="Filter by actor (universal entity ID)"),
    target: Optional[str] = Query(None, description="Filter by target"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    signal_type: Optional[str] = Query(None, pattern="^(gravity|light|internal)$", description="Filter by signal_type (gravity/light/internal)"),
    oracle_tier: Optional[int] = Query(None, ge=0, le=4, description="Filter by oracle tier (0-4)"),
    start: Optional[datetime.datetime] = Query(None, description="Start of time range (ISO 8601)"),
    end: Optional[datetime.datetime] = Query(None, description="End of time range (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    try:
        # Convert datetime objects to ISO 8601 strings for ledger
        start_str = start.isoformat() if start else None
        end_str = end.isoformat() if end else None

        events = ledger.query_events(
            event_type=event_type,
            actor=actor,
            target=target,
            domain=domain,
            signal_type=signal_type,
            oracle_tier=oracle_tier,
            start_timestamp=start_str,
            end_timestamp=end_str,
            limit=limit,
            offset=offset
        )
        # Convert Row objects to dicts and payload_json back to dict
        parsed_events = []
        for event_row in events:
            event_dict = dict(event_row)
            if event_dict.get('payload_json'):
                try:
                    event_dict['payload_json'] = json.loads(event_dict['payload_json'])
                except json.JSONDecodeError:
                    pass # Keep as string if decoding fails
            parsed_events.append(event_dict)
            
        return {"status": "ok", "data": parsed_events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Endpoint to export events (JSON or CSV format per ADR-002)
@app.get("/api/events/export", summary="Export all events from the ledger")
async def export_events_endpoint(
    format: str = Query("json", pattern="^(json|csv)$", description="Export format: json or csv")
):
    try:
        events = ledger.query_events(limit=1000000)

        # Parse events
        parsed_events = []
        for event_row in events:
            event_dict = dict(event_row)
            if event_dict.get('payload_json') and format == "json":
                try:
                    event_dict['payload_json'] = json.loads(event_dict['payload_json'])
                except json.JSONDecodeError:
                    pass
            parsed_events.append(event_dict)

        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            if parsed_events:
                fieldnames = [
                    'id', 'timestamp', 'event_type', 'actor', 'target', 'domain',
                    'signal_type', 'oracle_tier', 'random_seed', 'completion_promise',
                    'verification_method', 'payload_json', 'cost_tokens', 'cost_usd', 'cost_carbon'
                ]
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(parsed_events)

            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=events.csv"}
            )
        else:
            return {"status": "ok", "data": parsed_events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Health check endpoint
@app.get("/api/health", summary="Health check endpoint")
async def health_check():
    return {"status": "ok", "message": "API is healthy"}