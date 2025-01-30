from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.RBG_AI  # Use the correct database name
Attendance = db.Attendance  # Reference the Attendance collection
admin = db.admin
users = db.Users
# Parameters for updating attendance
user_id = "67810a665a059d3c21b26c0b"  # Replace with the actual user ID
new_date = datetime.strptime("2025-01-05", "%Y-%m-%d")  # Specify the previous Sunday


update_fields = {
    "userid": "67810a665a059d3c21b26c0b",
    "date": new_date.strftime("%Y-%m-%d"),
    "name": "dhivya",
    "clockin": "09:15:00 AM",  # Updated clock-in time
    "status": "Present",  # Updated status
    "remark": "Incomplete",  # Updated remark
    "clockout": "03:17:25 PM",  # Retained original value
    "total_hours_worked": "0 hours 22 minutes",  # Retained original value
    "bonus_leave": "Not Taken"
}

# Check if the record exists for the given user and date
existing_record = Attendance.find_one({"userid": user_id, "date": new_date.strftime("%Y-%m-%d")})

if existing_record:
    # Update the existing record
    Attendance.update_one(
        {"_id": existing_record["_id"]},
        {"$set": update_fields}
    )
    print(f"Attendance updated for {new_date.strftime('%Y-%m-%d')}.")
else:
    # Insert a new attendance record if not found
    Attendance.insert_one(update_fields)
    print(f"Attendance added for {new_date.strftime('%Y-%m-%d')}.")

# Retrieve and print the updated/added record for verification
updated_attendance = Attendance.find_one({"userid": user_id, "date": new_date.strftime("%Y-%m-%d")})
print(updated_attendance)



    
# # Update the document in the collection
# users.update_one({"_id": ObjectId("676a33e27afb525b32ea649e")}, {"$set": {"skills": [
#     {
#       "name": "Python",
#       "level": 80
#     },
#     {
#       "name": "FastAPI",
#       "level": 70
#     }
#   ]}})

# print("Documents transformed successfully.")
