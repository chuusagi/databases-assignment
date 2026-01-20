import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import motor.motor_asyncio
import io
from bson import ObjectId

# load environment variables from .env file for sensitive data
load_dotenv()

app = FastAPI()

# connect to mongodb atlas using the motor async driver
# this establishes a connection to the 'event_management_db' database
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://database-assignment:123@cluster0.xxxxx.mongodb.net/event_management_db?retryWrites=true&w=majorityg")
db = client.event_management_db

# --- data models ---
# these pydantic models define the structure of data for requests and responses

class Event(BaseModel):
    name: str
    description: str
    date: str
    venue_id: str
    max_attendees: int

class Attendee(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class Venue(BaseModel):
    name: str
    address: str
    capacity: int

class Booking(BaseModel):
    event_id: str
    attendee_id: str
    ticket_type: str
    quantity: int

# --- event endpoints ---

@app.post("/events")
async def create_event(event: Event):
    # converts the pydantic model to a dictionary
    # adds a timestamp and inserts the document into the 'events' collection
    event_doc = event.dict()
    event_doc["created_at"] = datetime.utcnow()
    result = await db.events.insert_one(event_doc)
    return {"message": "Event created", "id": str(result.inserted_id)}

@app.get("/events")
async def get_events():
    # fetches up to 100 event documents from the 'events' collection
    # converts the mongodb objectid to a string so it can be sent as json
    events = await db.events.find().to_list(100)
    for event in events:
        event["_id"] = str(event["_id"])
    return events

@app.get("/events/{event_id}")
async def get_event(event_id: str):
    # looks for a specific event by converting the string id into a bson objectid
    # raises a 404 error if the event doesn't exist
    try:
        event = await db.events.find_one({"_id": ObjectId(event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        event["_id"] = str(event["_id"])
        return event
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")

@app.put("/events/{event_id}")
async def update_event(event_id: str, event: Event):
    # searches for the event by id and replaces its fields with the new data
    # $set ensures only the specified fields are updated
    try:
        event_doc = event.dict()
        event_doc["updated_at"] = datetime.utcnow()
        result = await db.events.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": event_doc}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"message": "Event updated successfully"}
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    # removes the event document from the 'events' collection
    try:
        result = await db.events.delete_one({"_id": ObjectId(event_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"message": "Event deleted successfully"}
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")

# --- attendee endpoints ---

@app.post("/attendees")
async def create_attendee(attendee: Attendee):
    # inserts a new attendee document into the 'attendees' collection
    attendee_doc = attendee.dict()
    attendee_doc["registered_at"] = datetime.utcnow()
    result = await db.attendees.insert_one(attendee_doc)
    return {"message": "Attendee created", "id": str(result.inserted_id)}

@app.get("/attendees")
async def get_attendees():
    # retrieves a list of all attendees registered in the system
    attendees = await db.attendees.find().to_list(100)
    for attendee in attendees:
        attendee["_id"] = str(attendee["_id"])
    return attendees

@app.get("/attendees/{attendee_id}")
async def get_attendee(attendee_id: str):
    # finds a single attendee by their unique mongodb objectid
    try:
        attendee = await db.attendees.find_one({"_id": ObjectId(attendee_id)})
        if not attendee:
            raise HTTPException(status_code=404, detail="ID/Attendee not found")
        attendee["_id"] = str(attendee["_id"])
        return attendee
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

@app.put("/attendees/{attendee_id}")
async def update_attendee(attendee_id: str, attendee: Attendee):
    # updates personal details for a specific attendee
    try:
        result = await db.attendees.update_one(
            {"_id": ObjectId(attendee_id)},
            {"$set": attendee.dict()}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Attendee not found")
        return {"message": "Attendee updated successfully"}
    except:
        raise HTTPException(status_code=400, detail="Invalid attendee ID")

@app.delete("/attendees/{attendee_id}")
async def delete_attendee(attendee_id: str):
    # removes an attendee from the database
    try:
        result = await db.attendees.delete_one({"_id": ObjectId(attendee_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Attendee not found")
        return {"message": "Attendee deleted successfully"}
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

# --- venue endpoints ---

@app.post("/venues")
async def create_venue(venue: Venue):
    # adds a new location (venue) where events can be held
    venue_doc = venue.dict()
    venue_doc["created_at"] = datetime.utcnow()
    result = await db.venues.insert_one(venue_doc)
    return {"message": "Venue created", "id": str(result.inserted_id)}

@app.get("/venues")
async def get_venues():
    # list all available venues stored in the database
    venues = await db.venues.find().to_list(100)
    for venue in venues:
        venue["_id"] = str(venue["_id"])
    return venues

@app.get("/venues/{venue_id}")
async def get_venue(venue_id: str):
    # gets specific venue information using its unique id
    try:
        venue = await db.venues.find_one({"_id": ObjectId(venue_id)})
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")
        venue["_id"] = str(venue["_id"])
        return venue
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

@app.put("/venues/{venue_id}")
async def update_venue(venue_id: str, venue: Venue):
    # updates venue details like capacity or address
    try:
        result = await db.venues.update_one(
            {"_id": ObjectId(venue_id)},
            {"$set": venue.dict()}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Venue not found")
        return {"message": "Venue updated successfully"}
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

@app.delete("/venues/{venue_id}")
async def delete_venue(venue_id: str):
    # removes a venue record
    try:
        result = await db.venues.delete_one({"_id": ObjectId(venue_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Venue not found")
        return {"message": "Venue deleted successfully"}
    except:
        raise HTTPException(status_code=400, detail="Invalid  ID")

# --- booking endpoints ---

@app.post("/bookings")
async def create_booking(booking: Booking):
    # relational check: verifies the event and attendee actually exist before booking
    # this maintains data integrity between different collections
    try:
        event = await db.events.find_one({"_id": ObjectId(booking.event_id)})
        attendee = await db.attendees.find_one({"_id": ObjectId(booking.attendee_id)})
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        if not attendee:
            raise HTTPException(status_code=404, detail="Attendee not found")
        
        booking_doc = booking.dict()
        booking_doc["booked_at"] = datetime.utcnow()
        result = await db.bookings.insert_one(booking_doc)
        
        return {"message": "Booking created", "id": str(result.inserted_id)}
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=400, detail="Invalid event or attendee ID")

@app.get("/bookings")
async def get_bookings():
    # retrieves all ticket/event bookings
    bookings = await db.bookings.find().to_list(100)
    for booking in bookings:
        booking["_id"] = str(booking["_id"])
    return bookings

@app.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    # retrieves a specific booking record
    try:
        booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        booking["_id"] = str(booking["_id"])
        return booking
    except:
        raise HTTPException(status_code=400, detail="Invalid booking ID")

@app.put("/bookings/{booking_id}")
async def update_booking(booking_id: str, booking: Booking):
    # modifies an existing booking (e.g., changing quantity)
    try:
        result = await db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": booking.dict()}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Booking not found")
        return {"message": "Booking updated successfully"}
    except:
        raise HTTPException(status_code=400, detail="Invalid booking ID")

@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: str):
    # cancels/deletes a booking
    try:
        result = await db.bookings.delete_one({"_id": ObjectId(booking_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Booking not found")
        return {"message": "Booking deleted successfully"}
    except:
        raise HTTPException(status_code=400, detail="Invalid booking ID")

# --- file storage and retrieval (posters, videos, photos) ---

@app.post("/upload_event_poster/{event_id}")
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
    # file storage: reads the raw binary data from the upload
    # stores the binary content directly in the 'event_posters' collection as a 'bytes' field
    # this is suitable for smaller files (typically < 16mb in mongodb)
    content = await file.read() 
    poster_doc = {
        "event_id": event_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.event_posters.insert_one(poster_doc)
    return {"message": "Event poster uploaded", "id": str(result.inserted_id)}

@app.get("/event_poster/{event_id}")
async def get_event_poster(event_id: str):
    # file retrieval: finds the poster document by event_id
    # uses streamingresponse to stream the binary data back to the user's browser
    # io.bytesio treats the binary 'content' field like a readable file stream
    poster = await db.event_posters.find_one({"event_id": event_id})
    if not poster:
        raise HTTPException(status_code=404, detail="Poster not found")
    
    return StreamingResponse(
        io.BytesIO(poster["content"]),
        media_type=poster["content_type"],
        headers={"Content-Disposition": f'inline; filename="{poster["filename"]}"'}
    )

@app.post("/upload_promo_video/{event_id}")
async def upload_promo_video(event_id: str, file: UploadFile = File(...)):
    # similar to posters, video content is read and stored as binary data
    # note: mongodb has a 16mb document limit unless using gridfs
    content = await file.read()
    
    video_doc = {
        "event_id": event_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.promo_videos.insert_one(video_doc)
    return {"message": "Promol video uploaded", "id": str(result.inserted_id)}

@app.get("/promo_video/{event_id}")
async def get_promo_video(event_id: str):
    # retrieves the video binary data and streams it to the client
    # the media_type ensures the browser knows how to play the video (e.g., video/mp4)
    video = await db.promo_videos.find_one({"event_id": event_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return StreamingResponse(
        io.BytesIO(video["content"]),
        media_type=video["content_type"],
        headers={"Content-Disposition": f'inline; filename="{video["filename"]}"'}
    )

@app.post("/upload_venue_photo/{venue_id}")
async def upload_venue_photo(venue_id: str, file: UploadFile = File(...)):
    # stores venue images in the 'venue_photos' collection
    content = await file.read()
    photo_doc = {
        "venue_id": venue_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.venue_photos.insert_one(photo_doc)
    return {"message": "Venue photo uploaded", "id": str(result.inserted_id)}

@app.get("/venue_photo/{venue_id}")
async def get_venue_photo(venue_id: str):
    # streams the venue photo back to the client based on the venue_id
    photo = await db.venue_photos.find_one({"venue_id": venue_id})
    if not photo:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return StreamingResponse(
        io.BytesIO(photo["content"]),
        media_type=photo["content_type"],
        headers={"Content-Disposition": f'inline; filename="{photo["filename"]}"'}
    )