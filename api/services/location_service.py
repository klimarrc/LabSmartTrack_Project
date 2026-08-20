"""
Location Service.
Handles fetching facilities and rooms from the database.
"""
from api.models.location_model import Facility, Room


class LocationService:
    
    def all_facilities(self):
        """
        Fetch all facilities from the database.
        """
        db_facilities = Facility.query.all()
        facilities = []
        for facility in db_facilities:
            facilities.append({
                "facility_id": facility.id,
                "name": facility.name,
            })
        return facilities

    def all_rooms(self):
        """
        Fetch all rooms across all facilities from the database.
        """
        db_rooms = Room.query.all()
        rooms = []
        for room in db_rooms:
            rooms.append({
                "facility_id": room.facility_id,
                "facility_name": room.facility.name if room.facility else "Unknown",
                "room_id": room.id,
                "name": room.name,
            })
        return rooms