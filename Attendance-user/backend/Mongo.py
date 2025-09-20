from Csvhandler import addnewdata,Getcsvdataformat,Deletecsvdata,Updatecsvdata
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, date
from fastapi.exceptions import HTTPException
from fastapi import FastAPI, HTTPException
from auth.auth_handler import signJWT
from model import RemoteWorkRequest
from bson.objectid import ObjectId
from pymongo import MongoClient
from dateutil import parser
from bson import json_util
from bson import ObjectId
from datetime import datetime, date
import bcrypt, requests, socket
import pytz 
import json
import traceback

# Helper function for timezone-aware timestamps
def get_current_timestamp_iso():
    """Get current timestamp in IST timezone with proper ISO format"""
    return datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()

def format_timestamp_iso(dt):
    """Convert datetime to ISO format with timezone info"""
    if dt.tzinfo is None:
        # If naive datetime, assume it's in IST
        dt = pytz.timezone("Asia/Kolkata").localize(dt)
    return dt.isoformat()

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["RBG_AI"]

Users = db["Users"]
Add = db.Dataset
Leave = db.Leave_Details
Clock = db.Attendance
RemoteWork = db.RemoteWork
admin = db.admin
Tasks = db.tasks
Managers = db.managers
Notifications = db.notifications


# Others
def Adddata(data,id,filename):
    a=Add.insert_one({'userid':id,'data':data,'filename':filename})
    return str(a.inserted_id)

def Editdata(data,id,filename):
    a=Add.update_one({"userid":id},{"$set":{"data":data,'filename':filename}})
    return "done"

def deletedata(id):
    a=Add.delete_one({'_id':id})
    return "done"

def addcsv(name,data,id):
    old=Add.find_one({'user_id':id})
    if old:
        print(id)
        a=addnewdata(name,data,id)
        print(a)
        return 's'
    else:
        a=addnewdata(name,data,id)
        print(a)
        u=Add.insert_one({'user_id':id,'path':a,'filename':name})
        return str(u.inserted_id)

def Getcsvdata(id):
    res=Getcsvdataformat(f'./Csvdata/{id}.csv')
    return res

def Updatecsv(name,data,id,fileid):
    res=Updatecsvdata(id=id,data=data,fileid=fileid,name=name)
    return res

def Deletecsv(id,fileid):
    res=Deletecsvdata(fileid=fileid,id=id)
    return res

def Hashpassword(password):
    bytePwd = password.encode('utf-8')
    mySalt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(bytePwd, mySalt)
    return pwd_hash

def CheckPassword(password,pwd_hash):
    password = password.encode('utf-8')
    check=bcrypt.checkpw(password, pwd_hash)
    return check
    
def Signup(email,password,name):
    check_old_user=Users.find_one({'email':email})
    if check_old_user:
        raise HTTPException(status_code=300, detail="Email already Exists")
    else:
        Haspass=Hashpassword(password)
        a=Users.insert_one({'email':email,'password':Haspass,'name':name })
        return signJWT(email, "user")

def cleanid(data):
    obid=data.get('_id')
    data.update({'id':str(obid)})
    del data['_id']
    return data
  
def signin(email,password):
    checkuser=Users.find_one({'email': email})
    checkadmin=admin.find_one({'email': email})
    if (checkuser):
        checkpass=CheckPassword(password,checkuser.get('password'))
        if (checkpass):
            a=signJWT(email, "user")
            b=checkuser
            checkuser=cleanid(checkuser)
            checkuser.update(a)
            return {"jwt":a, "Details":b, "isadmin":False}
        else :
            raise HTTPException(status_code=300, detail="Given Password is Incorrect")
    elif (checkadmin):
        result = admin_signin(checkadmin, password, email)
        return result
    else:
        raise HTTPException(status_code=300, detail="Given Email does not exists")

def admin_Signup(email,password,name,phone,position,date_of_joining):
    check_old_user=admin.find_one({'email':email})
    if check_old_user:
        raise HTTPException(status_code=300, detail="Email already Exists")
    else:
        Haspass=Hashpassword(password)
        a=admin.insert_one({'email':email,'password':Haspass,'name':name, 'phone':phone, 'position':position, 'date_of_joining':date_of_joining})
        return signJWT(email, "admin")
    
def admin_signin(checkuser, password, email):
    if (checkuser):
        checkpass=CheckPassword(password,checkuser.get('password'))
        if (checkpass):
            a=signJWT(email, "admin")
            b=checkuser
            checkuser=cleanid(checkuser)
            checkuser.update(a)
            return {"jwt":a, "Details":b, "isadmin":True}
     
# # Google Signin      
# def Gsignin(client_name,email):
#     checkuser=Users.find_one({'email': email})
#     checkadmin=admin.find_one({'email': email})
#     checkmanager=Managers.find_one({'email': email})
#     selected_date = date.today().strftime("%d-%m-%Y")
#     if (checkuser):
#             a=signJWT(client_name)
#             b=checkuser
#             checkuser=cleanid(checkuser)
#             checkuser.update(a)
#             print(checkuser)
#             # # Keep the real admin status from DB, don’t overwrite
#             # is_admin_from_db = checkuser.get("isadmin", False)
#             # checkuser.update({"isloggedin": True, "isadmin": is_admin_from_db})
#             checkuser.update({"isloggedin":True, "isadmin":False})
#             return checkuser
#     elif (checkadmin):
#         result = admin_Gsignin(checkadmin, client_name)
#         return result
#     elif (checkmanager):
#         result = manager_Gsignin(checkmanager, client_name)
#         print(result)
#         return result
#     else:
#         raise HTTPException(status_code=300, detail="Given Email does not exists")

# Google Signin      
def Gsignin(client_name, email):
    checkuser = Users.find_one({'email': email})
    checkadmin = admin.find_one({'email': email})
    checkmanager = Managers.find_one({'email': email})
    selected_date = date.today().strftime("%d-%m-%Y")

    if checkuser:
        role = "admin" if checkuser.get("isadmin", False) else "user"
        a = signJWT(client_name, role)
        b = checkuser
        checkuser = cleanid(checkuser)
        checkuser.update(a)
        is_admin_from_db = checkuser.get("isadmin", False)
        checkuser.update({"isloggedin": True, "isadmin": is_admin_from_db})
        # checkuser.update({"isloggedin": True, "isadmin": False})
        return checkuser
    elif checkadmin:
        result = admin_Gsignin(checkadmin, client_name)
        return result
    elif checkmanager:
        result = manager_Gsignin(checkmanager, client_name)
        return result
    else:
        # Auto-create a new user if email doesn't exist
        new_user = {
            "name": client_name,
            "email": email,
            "isadmin": False,
            "isloggedin": True,
            "created_at": selected_date,
        }
        inserted_id = Users.insert_one(new_user).inserted_id
        user_doc = Users.find_one({"_id": inserted_id})
        user_doc = cleanid(user_doc)
        jwt_token = signJWT(client_name, "user")
        user_doc.update(jwt_token)
        return user_doc


# UserID
def Userbyid(id):
    user=Add.find({'userid':id})
    data=[]
    for i in user:
        data.append(cleanid(i))
    return data


# Admin ID
def adminbyid(id):
    user=Add.find({'userid':id})
    data=[]
    for i in user:
        data.append(cleanid(i))
    return data

# Admin Google Signin
def admin_Gsignin(checkuser, client_name):
    
    if (checkuser):
        a = signJWT(client_name, "admin")
        b = checkuser
        checkuser = cleanid(checkuser)
        checkuser.update(a)
        checkuser.update({"isloggedin":True, "isadmin":True})
        return checkuser
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
# Manager Google Signin
def manager_Gsignin(checkuser, client_name):
    
    if (checkuser):
        a = signJWT(client_name, "manager")
        b = checkuser
        checkuser = cleanid(checkuser)
        checkuser.update(a)
        checkuser.update({"isloggedin":True, "ismanger":True})
        return checkuser
    else:
        raise HTTPException(status_code=404, detail="User not found")


def Clockin(userid, name, time):
    today = date.today()

    try:
        # Parse the clock-in time
        clockin_time = datetime.strptime(time, "%I:%M:%S %p")

        # Determine the status based on clock-in time
        status = "Present" if datetime.strptime("08:30:00 AM", "%I:%M:%S %p") <= clockin_time <= datetime.strptime("10:30:00 AM", "%I:%M:%S %p") else "Late"

        # Check for an existing record for today
        existing_record = Clock.find_one({'date': str(today), 'name': name})

        if existing_record and 'clockin' in existing_record:
            # If the user has already clocked in, return the existing time
            existing_clockin_time = existing_record['clockin']
            return f"Already clocked in at {existing_clockin_time}"
        elif existing_record:
            # If a record exists without clock-in, update it
            Clock.find_one_and_update(
                {'date': str(today), 'name': name},
                {'$set': {'clockin': time, 'status': status}}
            )
        else:
            # If no record exists, create a new one
            record = {
                'userid': userid,
                'date': str(today),
                'name': name,
                'clockin': time,
                'status': status,
                'remark': ''
            }

            if today.weekday() == 6:  # Sunday (weekday() returns 6 for Sunday)
                record['bonus_leave'] = "Not Taken"  # Add Sunday-specific data

            Clock.insert_one(record)

        # Create attendance notification for successful clock-in
        create_attendance_notification(
            userid=userid,
            message=f"Successfully clocked in at {time}. Status: {status}",
            priority="low",
            attendance_type="clock_in"
        )

        return "Clock-in successful"

    except ValueError as e:
        print(f"Error parsing time: {e}")
        return "Invalid time format"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while clocking in"



def parse_time_string(time_str):
    try:
        return parser.parse(time_str)
    except ValueError:
        if "PM" in time_str.upper():
            return datetime.strptime(time_str, "%I %p")
        else:
            return datetime.strptime(time_str, "%H:%M")

# Define the auto-clockout function
def auto_clockout():
    print("Running auto-clockout task...")
    today = datetime.now(pytz.timezone("Asia/Kolkata")).date()
    clockout_default_time = datetime.strptime("09:30:00 AM", "%I:%M:%S %p").time()  # Default clock-out time

    # Find all users who clocked in today but haven't clocked out
    clocked_in_users = Clock.find({'date': str(today), 'clockout': {'$exists': False}})

    for record in clocked_in_users:
        name = record['name']
        userid = record.get('userid', '')
        clockin_time = parser.parse(record['clockin'])

        # Set clock-out time to default time (8:00 PM)
        clockout_time = datetime.combine(today, clockout_default_time)

        # Calculate total hours worked
        total_seconds_worked = (clockout_time - clockin_time).total_seconds()
        total_hours_worked = total_seconds_worked / 3600
        remaining_seconds = total_seconds_worked % 3600
        total_minutes_worked = remaining_seconds // 60

        # Add a remark based on hours worked
        remark = "N/A" if total_hours_worked >= 8 else "Incomplete"

        hours_text = f'{int(total_hours_worked)} hours {int(total_minutes_worked)} minutes'

        # Update the clock-out time in the database
        Clock.find_one_and_update(
            {'_id': record['_id']},  # Use the record's unique ID for update
            {'$set': {
                'clockout': clockout_time.strftime("%I:%M:%S %p"),
                'total_hours_worked': hours_text,
                'remark': remark
            }}
        )

        # Create auto clock-out notification
        if userid:
            create_attendance_notification(
                userid=userid,
                message=f"Automatic clock-out completed at {clockout_time.strftime('%I:%M:%S %p')}. Total work time: {hours_text}. Please review your attendance.",
                priority="medium",
                attendance_type="auto_clock_out"
            )

        print(f"Auto clock-out completed for user: {name}")

    print("Auto-clockout task completed.")

def Clockout(userid, name, time):
    today = datetime.now(pytz.timezone("Asia/Kolkata")).date()  # Use datetime.now() with timezone
    current_time = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    clockout_default_time = datetime.strptime("9:30:00 AM", "%I:%M:%S %p").time()  # Default clock-out time (8:00 PM)

    # Check the clock-in record for the user today
    record = Clock.find_one({'date': str(today), 'name': name})
    
    if record:
        # Check if clock-out is already recorded for today
        if 'clockout' in record:
            return f"Clock-out already recorded at {record['clockout']}"

        clockin_time = parser.parse(record['clockin'])

        # Determine the clock-out time
        if not time:
            # If no clock-out time is provided, set default to 8:00 PM
            if current_time >= clockout_default_time:
                clockout_time = datetime.combine(today, clockout_default_time)
            else:
                # If called before 6:00 PM without manual clock-out, consider no action yet
                return "Clock-out not yet due for auto clock-out. Manual clock-out required before 6:00 PM.", None
        else:
            # Parse the provided time as clock-out time
            clockout_time = parse_time_string(time)

        # Calculate total hours worked
        total_seconds_worked = (clockout_time - clockin_time).total_seconds()
        total_hours_worked = total_seconds_worked / 3600
        remaining_seconds = total_seconds_worked % 3600
        total_minutes_worked = remaining_seconds // 60

        # Add a remark based on hours worked
        remark = "N/A" if total_hours_worked >= 8 else "Incomplete"

        hours_text = f'{int(total_hours_worked)} hours {int(total_minutes_worked)} minutes'

        # Update the clock-out time in the database
        Clock.find_one_and_update(
            {'date': str(today), 'name': name},
            {'$set': {
                'clockout': clockout_time.strftime("%I:%M:%S %p"),
                'total_hours_worked': hours_text,
                'remark': remark
            }}
        )

        # Create attendance notification for successful clock-out
        create_attendance_notification(
            userid=userid,
            message=f"Successfully clocked out at {clockout_time.strftime('%I:%M:%S %p')}. Total work time: {hours_text}",
            priority="low",
            attendance_type="clock_out"
        )

        return "Clock-out sucessful"
    else:
        # No clock-in record found for today; prompt user to clock-in first
        return "Clock-in required before clock-out."


def PreviousDayClockout(userid, name):
    today = datetime.now(pytz.timezone("Asia/Kolkata")).date()
    previous_day = today - timedelta(days=1)
    # clockout_default_time = datetime.strptime("6:30:00 PM", "%I:%M:%S %p").time()
    clockout_default_time = datetime.strptime("3:00:00 PM", "%I:%M:%S %p").time()
    
    # Fetch the previous day's record
    prev_day_record = Clock.find_one({'date': str(previous_day), 'name': name})
    if not prev_day_record:
        return "No clock-in record found for the previous day."

    if 'clockout' in prev_day_record:
        return f"Clock-out already recorded at {prev_day_record['clockout']} for the previous day."

    # Parse the clock-in time
    prev_clockin_time = parser.parse(prev_day_record['clockin'])
    
    # Set the clock-in date to be the same as previous_day
    prev_clockin_time = prev_clockin_time.replace(year=previous_day.year, month=previous_day.month, day=previous_day.day)
    
    # Combine the previous_day with the default clock-out time to set prev_clockout_time
    prev_clockout_time = datetime.combine(previous_day, clockout_default_time)

    # Calculate total hours worked for the previous day
    total_seconds_worked = (prev_clockout_time - prev_clockin_time).total_seconds()
    total_hours_worked = total_seconds_worked / 3600
    remaining_seconds = total_seconds_worked % 3600
    total_minutes_worked = remaining_seconds // 60

    # Add a remark based on hours worked
    remark = "N/A" if total_hours_worked >= 8 else "Incomplete"

    # Update the previous day's record with the default clock-out time
    Clock.find_one_and_update(
        {'date': str(previous_day), 'name': name},
        {'$set': {
            'clockout': prev_clockout_time.strftime("%I:%M:%S %p"),
            'total_hours_worked': f'{int(total_hours_worked)} hours {int(total_minutes_worked)} minutes',
            'remark': remark
        }}
    )
    return f"Previous day's clock-out auto-recorded for {name} at {prev_clockout_time.strftime('%I:%M:%S %p')}."


# User Page Attendance Details
def attendance_details(userid: str):
    clock_records = Clock.find({"userid": userid}, {'_id': 0})
    return list(clock_records)
    

# Admin Page Attendance Details
def get_attendance_by_date():
    attendance_data = list(Clock.find({}, {"_id": 0}))
    return attendance_data

# Employee ID
def get_employee_id_from_db(name: str):
    try:
        user = Users.find_one({'name': name}, {'_id': 1})
        if user:
            return str(user["_id"])
        else:
            return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def add_employee_id_to_leave_details(employee_id: str, employee_name: str , userid:str):
    try:
        Leave.insert_one({
            'userid': userid,
            'employeeName': employee_name,
            'Employee_ID' : employee_id,
            'time': "",  
            'leaveType': "",  
            'selectedDate': "",  
            'requestDate': "", 
            'reason': "" 
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Leave Management
# Date Format 
def format_timestamp(timestamp):
    parsed_timestamp = datetime.fromisoformat(str(timestamp))
    timezone = pytz.timezone("Asia/Kolkata")
    formatted_timestamp = parsed_timestamp.astimezone(timezone)
    return formatted_timestamp

# Weekend calculation
def count_weekdays(start_date, end_date):
    """
    Count the number of weekdays (excluding Sundays) between two dates.
    """
    count = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() != 6:  
            count += 1
        current_date += timedelta(days=1)
    return count

def log_message(message):
    print(f"{message}")

def check_leave_conflict(userid, selected_date):
    # Convert date to datetime (MongoDB stores dates as ISODate)
    selected_date_dt = selected_date

    print(selected_date_dt)  # Debugging

    #Filter for Single-Day Leave Conflicts (Casual, Sick, Bonus, Permission)
    single_day_leave_filter = {
        "userid": userid,
        "selectedDate": selected_date_dt,
        "leaveType": {"$in": ["Casual Leave", "Sick Leave", "Bonus Leave", "Permission"]}
    }

    #Filter for Multi-Day Leave Conflicts (Other Leave)
    wfh = {
        "userid": userid,
        "$or": [
            {"fromDate": {"$lte": selected_date_dt}, "toDate": {"$gte": selected_date_dt}}  # Remote Work conflict
        ]  # Leave ends after or on this date
    }

    lop = {
        "userid": userid,
        "selectedDate": {"$lte": selected_date_dt},  # Leave starts before or on this date
        "ToDate": {"$gte": selected_date_dt}  # Leave ends after or on this date
    }

    # Check for Single-Day Leave Conflict
    existing_single_leave = Leave.find_one(single_day_leave_filter)
    if existing_single_leave:
        conflict_message = f"Conflict: {userid} already has {existing_single_leave['leaveType']} on {selected_date_dt}."
        log_message(conflict_message)
        print(conflict_message)
        return conflict_message

    # Check for Multi-Day Leave Conflict
    existing_wfh = RemoteWork.find_one(wfh)
    if existing_wfh:
        conflict_message = f"Conflict: {userid} already has remote work from {existing_wfh['fromDate']} to {existing_wfh.get('toDate', selected_date_dt)}."
        log_message(conflict_message)
        return conflict_message
    
    existing_lop = Leave.find_one(lop)
    if existing_lop:
        conflict_message = f"Conflict: {userid} already has {existing_lop['leaveType']} from {existing_lop['selectedDate']} to {existing_lop.get('ToDate', selected_date_dt)}."
        log_message(conflict_message)
        return conflict_message

    return None 

def check_multi_day_leave_conflict(userid, from_date, to_date):
    print(f"Checking multi-day leave conflict from {from_date} to {to_date}")

    # Check for conflicts in a single query
    conflict = Leave.find_one({
        "userid": userid,
        "$or": [
            {"selectedDate": {"$lte": to_date}, "ToDate": {"$gte": from_date}},  # Properly check for LOP conflict
            {"selectedDate": {"$gte": from_date, "$lte": to_date}, "leaveType": {"$ne": "Other Leave"}},  # Single-day leave conflict
        ]
    })
    
    # Check for Remote Work conflicts separately inside `$or`
    remote_conflict = RemoteWork.find_one({
        "userid": userid,
        "$or": [
            {"fromDate": {"$lte": to_date}, "toDate": {"$gte": from_date}}  # Remote Work conflict
        ]
    })

    if conflict:
        log_message(f"Conflict: {userid} already has {conflict['leaveType']} from {conflict['selectedDate']} to {conflict.get('toDate', conflict['selectedDate'])}.")
        return f"Leave request conflicts with an existing {conflict['leaveType']} from {conflict['selectedDate']} to {conflict.get('toDate', conflict['selectedDate'])}."

    if remote_conflict:
        log_message(f"Conflict: {userid} already has Remote Work from {remote_conflict['fromDate']} to {remote_conflict['toDate']}.")
        return f"Leave request conflicts with existing Remote Work from {remote_conflict['fromDate']} to {remote_conflict['toDate']}."

    return None



def store_leave_request(userid, employee_name, time, leave_type, selected_date, request_date, reason):
    try:
        # Ensure dates are stored as `datetime` objects
        selected_date_dt = datetime.strptime(selected_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
        request_date_dt = datetime.strptime(request_date.strftime("%d-%m-%Y"), "%d-%m-%Y")

        # Check if the request date is a Sunday (weekday() returns 6 for Sunday)
        if request_date_dt.weekday() == 6:
            return "Request date is a Sunday. Request not allowed."
        
        if selected_date_dt.weekday() == 6:
            return "Selected date is a Sunday. Request not allowed."

        if leave_type == "Sick Leave" and selected_date_dt != request_date_dt:
            return "Sick Leave is permitted for today only."
        
        # Check for existing leave on the same date
        conflict_result = check_leave_conflict(userid, selected_date_dt)
        if conflict_result:
            return conflict_result  # This returns the conflict message

        combo_leave = Clock.find_one({"userid": userid, "bonus_leave": "Not Taken"})
        if combo_leave:
            return f"A combo leave is available for {combo_leave['date']}"

        if leave_type == "Casual Leave":
            weekdays_count = count_weekdays(request_date_dt + timedelta(days=1), selected_date_dt)
            if weekdays_count < 1:
                return "Two days prior notice for Casual Leave."

        if leave_type == "Casual Leave":
            # Check if adjacent days have conflicts
            if is_leave_taken(userid, selected_date_dt + timedelta(days=1), "Sick Leave"):
                return "Casual Leave cannot be taken if the next day is Sick Leave."

            if is_leave_taken(userid, selected_date_dt - timedelta(days=1), "Sick Leave"):
                return "Casual Leave cannot be taken if the previous day is Sick Leave."

            if is_leave_taken(userid, selected_date_dt + timedelta(days=1), "Casual Leave"):
                return "Casual Leave cannot be taken if the next day is also Casual Leave."

            if is_leave_taken(userid, selected_date_dt - timedelta(days=1), "Casual Leave"):
                return "Casual Leave cannot be taken if the previous day is also Casual Leave."

        # Count leaves for the user in the given month
        current_month = selected_date_dt.strftime("%m-%Y")
        leave_count_cursor = Leave.aggregate([
            {
                '$match': {
                    'userid': userid,
                    'selectedDate': {
                        '$gte': datetime.strptime(f"01-{current_month}", "%d-%m-%Y"),
                        '$lt': datetime.strptime(f"01-{current_month}", "%d-%m-%Y") + timedelta(days=31)
                    },
                    'leaveType': leave_type
                }
            },
            {
                '$group': {
                    '_id': '$leaveType',
                    'count': {'$sum': 1}
                }
            }
        ])

        leave_count = list(leave_count_cursor)
        if leave_count and leave_count[0]["count"] >= 1:
            return f"You have already taken a {leave_type} this month."

        employee_id = get_employee_id_from_db(employee_name)
        new_leave = {
            "userid": userid,
            "Employee_ID": employee_id,
            "employeeName": employee_name,
            "time": time,
            "leaveType": leave_type,
            "selectedDate": selected_date_dt,  # Stored as `datetime` object
            "requestDate": request_date_dt,  # Stored as `datetime` object
            "reason": reason,
        }

        result = Leave.insert_one(new_leave)
        return "Leave request stored successfully"
    except Exception as e:
        print(f"Error in store_leave_request: {e}")
        return f"Error processing leave request: {str(e)}"

    result = Leave.insert_one(new_leave)
    return "Leave request stored successfully"

def is_leave_taken(userid, selected_date, leave_type):
    # Check if leave of given type is taken on the selected date
    leave_entry = Leave.find_one({
        "userid": userid,
        "selectedDate": format_timestamp(selected_date),
        "leaveType": leave_type
    })
    
    return leave_entry is not None


# User Page Leave History
def leave_History_Details(userid: str,selected_option):
    if selected_option == "Leave":
        leave_request = list(Leave.find({'userid' : userid, "leaveType": {"$in": ["Sick", "Casual", "Bonus"]}}))
    elif selected_option == "LOP":
        leave_request = list(Leave.find({'userid' : userid, "leaveType": "Other Leave"}))
    elif selected_option == "Permission":
        leave_request = list(Leave.find({'userid' : userid,"leaveType": "Permission"}))
    else:
        leave_request = []
    
    for index, leave in enumerate(leave_request):
        leave_request[index] = cleanid(leave)
        
    return leave_request

def delete_leave(userid, fromdate, requestdate, leavetype):
    result = Leave.delete_one({"userid":userid, "leaveType": leavetype, "selectedDate": format_timestamp(fromdate), "requestDate":format_timestamp(requestdate)})
    if result.deleted_count>0:
        return "Deleted"
    else:
        return "Invalid request"

def store_sunday_request(userid, employee_name, time, leave_type, selected_date, reason, request_date):
    # Convert string dates to datetime objects if needed
    if isinstance(selected_date, str):
        try:
            selected_date_dt = datetime.strptime(selected_date, "%Y-%m-%d")
        except ValueError:
            selected_date_dt = datetime.strptime(selected_date, "%d-%m-%Y")
    else:
        selected_date_dt = datetime.strptime(selected_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
    
    if isinstance(request_date, str):
        try:
            request_date_dt = datetime.strptime(request_date, "%Y-%m-%d")
        except ValueError:
            request_date_dt = datetime.strptime(request_date, "%d-%m-%Y")
    else:
        request_date_dt = datetime.strptime(request_date.strftime("%d-%m-%Y"), "%d-%m-%Y")

    # Check if the request date is a Sunday
    if request_date_dt.weekday() == 6:
        return "Request date is a Sunday. Request not allowed."

    # Check for existing leave conflicts
    if check_leave_conflict(userid, selected_date_dt):
        return f"Leave request conflicts with an existing leave or remote work on {selected_date_dt.strftime('%d-%m-%Y')}."

    combo_leave = Clock.find_one({"userid": userid, "bonus_leave": "Not Taken"})
    employee_id = get_employee_id_from_db(employee_name)

    if combo_leave:
        new_leave = {
            "userid": userid,
            "Employee_ID": employee_id,
            "employeeName": employee_name,
            "time": time,
            "leaveType": leave_type,
            "selectedDate": selected_date_dt,  # ✅ Stored as `datetime` object
            "requestDate": request_date_dt,  # ✅ Stored as `datetime` object
            "reason": reason,
        }

        Clock.find_one_and_update({"userid": userid, "bonus_leave": "Not Taken"}, {"$set": {"bonus_leave": "Taken"}})
        Leave.insert_one(new_leave)
        return "Leave request stored successfully"
    else:
        return "No bonus leave available"


# Manger Page Leave Requests
def get_user_leave_requests(selected_option):
    if selected_option == "Leave":
        leave_request = list(Leave.find({"leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]}, "status":"Recommend"}))
    elif selected_option == "LOP":
        leave_request = list(Leave.find({"leaveType": "Other Leave", "status":"Recommend"}))
    elif selected_option == "Permission":
        leave_request = list(Leave.find({"leaveType": "Permission", "status":"Recommend"}))
    else:
        leave_request = []
    
    # Clean the IDs for each leave request
    for index, leave in enumerate(leave_request):
        leave_request[index] = cleanid(leave)

    for leave in leave_request:
        if selected_option == "Leave" or selected_option == "Permission":
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
        else:
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            leave["ToDate"] = leave["ToDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")

    return leave_request

# Admin Page Leave Requests
# def get_manager_leave_requests(selected_option):
#     managers = list(Users.find({"position": "Manager"}))
#     print(f"Found {len(managers)} managers")
    
#     # Prepare a list of manager IDs
#     manager_ids = [str(manager["_id"]) for manager in managers]
#     print(f"Manager IDs: {manager_ids}")

#     # Debug: Check what leave requests exist for managers
#     all_manager_leaves = list(Leave.find({"userid": {"$in": manager_ids}}))
#     print(f"Total manager leaves in DB: {len(all_manager_leaves)}")
    
#     # Check status values
#     status_values = [leave.get("status") for leave in all_manager_leaves]
#     print(f"Status values found: {set(status_values)}")

#     if selected_option == "Leave":
#         leave_request = list(Leave.find({
#             "leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]},
#             "status": {"$exists": False},
#             "userid": {"$in": manager_ids}
#         }))
#         print(f"Found {len(leave_request)} leave requests with no status")
        
#         # Also check what would be found with different status conditions
#         with_status = list(Leave.find({
#             "leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]},
#             "userid": {"$in": manager_ids}
#         }))
#         print(f"Total leave requests (any status): {len(with_status)}")
        
#     # ... rest of your conditions
    
#     return leave_request

# Admin Page Leave Requests
def get_manager_leave_requests(selected_option):
    # Get Manager + HR IDs
    managers_and_hr = list(Users.find({"position": {"$in": ["Manager", "HR"]}}))
    user_ids = [str(user["_id"]) for user in managers_and_hr]


    if selected_option == "Leave":
        leave_request = list(Leave.find({
            "leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]},
            "status": {"$exists": False},
            "userid": {"$in": user_ids}
        }))
    elif selected_option == "LOP":
        leave_request = list(Leave.find({
            "leaveType": "Other Leave",
            "status": {"$exists": False},
            "userid": {"$in": user_ids}
        }))
    elif selected_option == "Permission":
        leave_request = list(Leave.find({
            "leaveType": "Permission",
            "status": {"$exists": False},
            "userid": {"$in": user_ids}
        }))
    else:
        leave_request = []
    
    # Process the results
    for index, leave in enumerate(leave_request):
        leave_request[index] = cleanid(leave)

    for leave in leave_request:
        if selected_option == "Leave" or selected_option == "Permission":
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
        else:
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            leave["ToDate"] = leave["ToDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")

    return leave_request

# TL Page Leave Requests
def get_only_user_leave_requests(selected_option,TL_name):
    users = list(Users.find({"position": {"$ne":"Manager"}, "name":{"$ne":TL_name}, "TL":TL_name}))
     
    # Prepare a list of user IDs
    user_ids = [str(user["_id"]) for user in users]

    if selected_option == "Leave":
        leave_request = list(Leave.find({
            "leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]},
            "status": {"$exists":False},
            "userid": {"$in": user_ids}
        }))
        print(leave_request)
    elif selected_option == "LOP":
        leave_request = list(Leave.find({
            "leaveType": "Other Leave",
            "status": {"$exists":False},
            "userid": {"$in": user_ids}
        }))
    elif selected_option == "Permission":
        leave_request = list(Leave.find({
            "leaveType": "Permission",
            "status": {"$exists":False},
            "userid": {"$in": user_ids}
        }))
    else:
        leave_request = []
    
    # Clean the IDs for each leave request
    for index, leave in enumerate(leave_request):
        leave_request[index] = cleanid(leave)

    for leave in leave_request:
        if selected_option == "Leave" or selected_option == "Permission":
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
        else:
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            leave["ToDate"] = leave["ToDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
    
    return leave_request

# HR Response for Leave Request
def updated_user_leave_requests_status_in_mongo(leave_id, status):
    try:
        print("Updating status in MongoDB:")
        print("Received Leave ID:", leave_id)
        print("Received Status:", status)
        
        # First, get the leave request details before updating
        leave_request = Leave.find_one({"_id": ObjectId(leave_id)})
        if not leave_request:
            return {"message": "Leave request not found"}
        
        result = Leave.update_one(
            {"_id": ObjectId(leave_id)},
            {"$set": {"status": status}}
        )
        print(result)
        if result.modified_count > 0:
            # Return detailed information for notifications
            response_data = {
                "message": "Status updated successfully",
                "userid": leave_request.get("userid"),
                "employee_name": leave_request.get("employeeName"),
                "leave_type": leave_request.get("leaveType"),
                "leave_date": leave_request.get("selectedDate").strftime("%d-%m-%Y") if leave_request.get("selectedDate") else "Unknown Date",
                "status": status,
                "hr_action": True  # Flag to indicate this was an HR action
            }
            
            # If status is "Recommend", immediately notify HR (this case shouldn't happen in HR endpoint but kept for safety)
            if status.lower() in ["recommend", "recommended"]:
                try:
                    import asyncio
                    # Create an async task to notify HR
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, schedule the notification
                        asyncio.create_task(notify_hr_recommended_leave(
                            employee_name=response_data["employee_name"],
                            employee_id=response_data["userid"],
                            leave_type=response_data["leave_type"],
                            leave_date=response_data["leave_date"],
                            recommended_by="Approver",
                            leave_id=leave_id
                        ))
                        print(f"✅ Scheduled HR notification for recommended leave: {response_data['employee_name']}")
                    else:
                        # If no loop, run sync
                        loop.run_until_complete(notify_hr_recommended_leave(
                            employee_name=response_data["employee_name"],
                            employee_id=response_data["userid"],
                            leave_type=response_data["leave_type"],
                            leave_date=response_data["leave_date"],
                            recommended_by="Approver",
                            leave_id=leave_id
                        ))
                        print(f"✅ Immediate HR notification sent for recommended leave: {response_data['employee_name']}")
                except Exception as hr_notify_error:
                    print(f"⚠️ Error sending immediate HR notification: {hr_notify_error}")
            
            print(f"✅ HR final decision processed: {status} for {response_data['employee_name']}")
            return response_data
        else:
            return {"message": "No records found for the given leave ID or the status is already updated"}
            
    except Exception as e:
        print(f"Error updating status: {e}")
        raise Exception("Error updating status in MongoDB")
    
#Admin and TL page Recommendation Page
def recommend_manager_leave_requests_status_in_mongo(leave_id, status):
    try:
        print("Updating status in MongoDB:")
        print("Received Leave ID:", leave_id)
        print("Received Status:", status)
        
        # First, get the leave request details before updating
        leave_request = Leave.find_one({"_id": ObjectId(leave_id)})
        if not leave_request:
            return {"message": "Leave request not found"}
        
        result = Leave.update_one(
            {"_id": ObjectId(leave_id)},
            {"$set": {"status": status}}
        )
        print(result)
        
        if result.modified_count > 0:
            # Return detailed information for notifications
            response_data = {
                "message": "Status updated successfully",
                "userid": leave_request.get("userid"),
                "employee_name": leave_request.get("employeeName"),
                "leave_type": leave_request.get("leaveType"),
                "leave_date": leave_request.get("selectedDate").strftime("%d-%m-%Y") if leave_request.get("selectedDate") else "Unknown Date",
                "recommender_name": "Admin"  # You can make this dynamic based on who is making the recommendation
            }
            
            # If status is "Recommend", immediately notify HR
            if status.lower() in ["recommend", "recommended"]:
                try:
                    import asyncio
                    # Create an async task to notify HR
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, schedule the notification
                        asyncio.create_task(notify_hr_recommended_leave(
                            employee_name=response_data["employee_name"],
                            employee_id=response_data["userid"],
                            leave_type=response_data["leave_type"],
                            leave_date=response_data["leave_date"],
                            recommended_by=response_data["recommender_name"],
                            leave_id=leave_id
                        ))
                        print(f"✅ Scheduled HR notification for recommended leave: {response_data['employee_name']}")
                    else:
                        # If no loop, run sync
                        loop.run_until_complete(notify_hr_recommended_leave(
                            employee_name=response_data["employee_name"],
                            employee_id=response_data["userid"],
                            leave_type=response_data["leave_type"],
                            leave_date=response_data["leave_date"],
                            recommended_by=response_data["recommender_name"],
                            leave_id=leave_id
                        ))
                        print(f"✅ Immediate HR notification sent for recommended leave: {response_data['employee_name']}")
                except Exception as hr_notify_error:
                    print(f"⚠️ Error sending immediate HR notification: {hr_notify_error}")
            
            return response_data
        else:
            return {"message": "No records found for the given leave ID or the status is already updated"}
            
    except Exception as e:
        print(f"Error updating status: {e}")
        raise Exception("Error updating status in MongoDB")
    
# Admin Page Leave History Dashboard
def get_approved_leave_history(TL_name):
    users = list(Users.find({"position": {"$ne":"Manager"},"TL":TL_name}))
    # Prepare a list of user IDs
    user_ids = [str(user["_id"]) for user in users]
    
    if users:
        leave_requests = list(Leave.find({"userid": {"$in": user_ids}, "status": "Approved"},{"_id":0}))
        wfh_requests = list(RemoteWork.find({"userid":{"$in": user_ids}, "status": "Approved"},{"_id":0}))
    else:
        leave_requests = list(Leave.find({"status": "Approved"}, {"_id": 0}))
        wfh_requests = list(RemoteWork.find({"status": "Approved"}, {"_id": 0}))

    for wfh_request in wfh_requests:
        wfh_request["leaveType"]= "Remote Work"
        wfh_request["selectedDate"] = wfh_request["fromDate"]
        wfh_request["Employee_ID"] = wfh_request["employeeID"]
        del wfh_request["employeeID"]
        del wfh_request["fromDate"]
        leave_requests.append(wfh_request)

    for leave_request in leave_requests:
        if leave_request.get("leaveType") == "Sick Leave" or leave_request.get("leaveType")  == "Permission" or leave_request.get("leaveType") == "Casual Leave" or leave_request.get("leaveType") == "Bonus Leave":
            leave_request["selectedDate"] = leave_request["selectedDate"].strftime("%d-%m-%Y")
            leave_request["requestDate"] = leave_request["requestDate"].strftime("%d-%m-%Y")
        elif leave_request.get("leaveType") == "Remote Work":
            leave_request["selectedDate"] = leave_request["selectedDate"].strftime("%d-%m-%Y")
            leave_request["toDate"] = leave_request["toDate"].strftime("%d-%m-%Y")
            leave_request["requestDate"] = leave_request["requestDate"].strftime("%d-%m-%Y")
        else:
            leave_request["selectedDate"] = leave_request["selectedDate"].strftime("%d-%m-%Y")
            leave_request["ToDate"] = leave_request["ToDate"].strftime("%d-%m-%Y")
            leave_request["requestDate"] = leave_request["requestDate"].strftime("%d-%m-%Y")
        
    return leave_requests

def leave_update_notification():
    sick_leave = Leave.count_documents({"leaveType": "Sick Leave", "Recommedation": "Recommend", "status": {"$exists": False}})
    casual_leave = Leave.count_documents({"leaveType": "Casual Leave", "Recommedation": "Recommend", "status": {"$exists": False}})
    lop = Leave.count_documents({"leaveType": "Other Leave" ,"Recommedation": "Recommend", "status": {"$exists": False}})
    bonus_leave = Leave.count_documents({"leaveType": "Bonus Leave", "Recommedation": "Recommend", "status": {"$exists": False}})
    permission_leave = Leave.count_documents({"leaveType": "Permission", "Recommedation": "Recommend", "status": {"$exists": False}})
    wfh = RemoteWork.count_documents({"Recommedation": "Recommend", "status": {"$exists": False}})
    leave_counts = {
        "Sick Leave": sick_leave,
        "Casual Leave": casual_leave,
        "Other Leave (LOP)": lop,
        "Bonus Leave": bonus_leave,
        "Permission Leave": permission_leave,
        "Remote Work": wfh
    }
    message = []
    for leave_type, count in leave_counts.items():
        if count > 0:
             message.append(f"{count} {leave_type} are pending approval.")
    print(message)
    return message

#Admin page
def managers_leave_recommend_notification():
    managers = list(Users.find({"position": "Manager"}))
    
    # Prepare a list of manager IDs
    manager_ids = [str(manager["_id"]) for manager in managers]

    sick_leave = Leave.count_documents({"userid": {"$in":manager_ids}, "leaveType": "Sick Leave", "Recommendation": {"$exists": False}, "status": {"$exists": False}})
    casual_leave = Leave.count_documents({"userid": {"$in":manager_ids}, "leaveType": "Casual Leave", "Recommedation":  {"$exists": False} , "status": {"$exists": False}})
    lop = Leave.count_documents({"userid": {"$in":manager_ids}, "leaveType": "Other Leave" ,"Recommedation": {"$exists": False}, "status": {"$exists": False}})
    bonus_leave = Leave.count_documents({"userid": {"$in":manager_ids}, "leaveType": "Bonus Leave", "Recommedation": {"$exists": False}, "status": {"$exists": False}})
    permission_leave = Leave.count_documents({"userid": {"$in":manager_ids}, "leaveType": "Permission", "Recommedation": {"$exists": False}, "status": {"$exists": False}})
    wfh = RemoteWork.count_documents({"userid": {"$in":manager_ids}, "Recommedation":  {"$exists": False}, "status": {"$exists": False}})
    leave_counts = {
        "Sick Leave": sick_leave,
        "Casual Leave": casual_leave,
        "Other Leave (LOP)": lop,
        "Bonus Leave": bonus_leave,
        "Permission Leave": permission_leave,
        "Remote Work": wfh
    }
    message = []
    for leave_type, count in leave_counts.items():
        if count > 0:
             message.append(f"{count} {leave_type} are pending approval.")
    print(message)
    return message

#TL page
def users_leave_recommend_notification(TL):
    users = list(Users.find({"position": {"$ne":"Manager"}, "TL":TL}))
    
    # Prepare a list of manager IDs
    users_ids = [str(user["userid"]) for user in users]

    sick_leave = Leave.count_documents({"userid": {"$in":users_ids}, "leaveType": "Sick Leave", "Recommedation":  {"$exists": False}, "status": {"$exists": False}})
    casual_leave = Leave.count_documents({"userid": {"$in":users_ids}, "leaveType": "Casual Leave", "Recommedation": {"$exists": False}, "status": {"$exists": False}})
    lop = Leave.count_documents({"userid": {"$in":users_ids}, "leaveType": "Other Leave" ,"Recommedation": {"$exists": False}, "status": {"$exists": False}})
    bonus_leave = Leave.count_documents({"userid": {"$in":users_ids}, "leaveType": "Bonus Leave", "Recommedation": {"$exists": False}, "status": {"$exists": False}})
    permission_leave = Leave.count_documents({"userid": {"$in":users_ids}, "leaveType": "Permission", "Recommedation": {"$exists": False}, "status": {"$exists": False}})
    wfh = RemoteWork.count_documents({"userid": {"$in":users_ids}, "Recommedation": {"$exists": False}, "status": {"$exists": False}})
    leave_counts = {
        "Sick Leave": sick_leave,
        "Casual Leave": casual_leave,
        "Other Leave (LOP)": lop,
        "Bonus Leave": bonus_leave,
        "Permission Leave": permission_leave,
        "Remote Work": wfh
    }
    message = []
    for leave_type, count in leave_counts.items():
        if count > 0:
             message.append(f"{count} {leave_type} are pending approval.")
    print(message)
    return message


import traceback
from bson import ObjectId
from fastapi import HTTPException

def store_remote_work_request(userid, employeeName, time, from_date, to_date, request_date, reason, ip):
    try:
        # Convert string dates to datetime objects if needed
        if isinstance(from_date, str):
            try:
                from_date_dt = datetime.strptime(from_date, "%Y-%m-%d")
            except ValueError:
                from_date_dt = datetime.strptime(from_date, "%d-%m-%Y")
        else:
            from_date_dt = datetime.strptime(from_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
            
        if isinstance(to_date, str):
            try:
                to_date_dt = datetime.strptime(to_date, "%Y-%m-%d")
            except ValueError:
                to_date_dt = datetime.strptime(to_date, "%d-%m-%Y")
        else:
            to_date_dt = datetime.strptime(to_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
            
        if isinstance(request_date, str):
            try:
                request_date_dt = datetime.strptime(request_date, "%Y-%m-%d")
            except ValueError:
                request_date_dt = datetime.strptime(request_date, "%d-%m-%Y")
        else:
            request_date_dt = datetime.strptime(request_date.strftime("%d-%m-%Y"), "%d-%m-%Y")

        print(f"Storing remote work request for {employeeName}, UserID: {userid}...")
        print(f"Request Date: {request_date_dt}, From Date: {from_date_dt}, To Date: {to_date_dt}")

        # Validation: To_date should be after or equal to From_date
        if to_date_dt < from_date_dt:
            return "To date should be after or equal to from date."

        # Validation: Request date must not be on a Sunday
        if request_date_dt.weekday() == 6:
            return "Request date is a Sunday. Remote work request not allowed."

        # Check if remote work conflicts with existing leave or remote work requests
        if check_multi_day_leave_conflict(userid, from_date_dt, to_date_dt):
            return "Remote work request conflicts with an existing leave or remote work during this period."

        # Calculate weekdays
        num_weekdays_request_to_from = count_weekdays(request_date_dt, from_date_dt)
        num_weekdays_from_to = count_weekdays(from_date_dt, to_date_dt)
        future_days = (to_date_dt - from_date_dt).days

        print(f"Weekdays from request to start: {num_weekdays_request_to_from}, Future days: {future_days}")

        # Fetch Employee ID
        employee_id = get_employee_id_from_db(employeeName)
        if not employee_id:
            return "Invalid employee name."

        # Validation: Request must be at least 5 days in advance and for a maximum of 3 weekdays
        if num_weekdays_request_to_from >= 4:
            if num_weekdays_from_to <= 3 and future_days <= 3:
                new_request = {
                    "userid": userid,
                    "employeeID": employee_id,
                    "employeeName": employeeName,
                    "time": time,
                    "fromDate": from_date_dt,  # ✅ Stored as `datetime` object
                    "toDate": to_date_dt,  # ✅ Stored as `datetime` object
                    "requestDate": request_date_dt,  # ✅ Stored as `datetime` object
                    "reason": reason,
                    "ip":ip,
                    "status": "Pending",  # Add default status
                    "created_at": get_current_timestamp_iso()  # Add timestamp
                }
                result = RemoteWork.insert_one(new_request)
                wfh_id = str(result.inserted_id)
                print("Insert result:", wfh_id)
                
                # Return success with WFH ID for notifications
                return {
                    "success": True,
                    "message": "Remote work request stored successfully.",
                    "wfh_id": wfh_id,
                    "from_date": from_date_dt.strftime("%Y-%m-%d"),
                    "to_date": to_date_dt.strftime("%Y-%m-%d")
                }
            else:
                return "Remote work can be taken for a maximum of 3 days."
        else:
            return "Remote work request must be made at least 5 days in advance."

    except Exception as e:
        print(f"Error occurred: {e}")
        return "An error occurred while processing the request."



# User Remote Work History
def Remote_History_Details(userid:str):
    Remote_History = list(RemoteWork.find({'userid' : userid},{'_id':0}))
    for wfh in Remote_History:
        wfh["fromDate"] = wfh["fromDate"].strftime("%d-%m-%Y")
        wfh["toDate"] = wfh["toDate"].strftime("%d-%m-%Y")
        wfh["requestDate"] = wfh["requestDate"].strftime("%d-%m-%Y")

    return Remote_History

# HR Page Remote Requests
def get_remote_work_requests():
    list1 = list()
    res = RemoteWork.find({"Recommendation":"Recommend", "status": {"$exists": False}})
    print(res)
    for user in res:
        cleanid(user)
        user["fromDate"] = user["fromDate"].strftime("%d-%m-%Y")
        user["toDate"] = user["toDate"].strftime("%d-%m-%Y")
        user["requestDate"] = user["requestDate"].strftime("%d-%m-%Y")
        list1.append(user)
    return list1

# Admin Page Remote Requests
def get_admin_page_remote_work_requests():
    managers = list(Users.find({"$or":[{"position": "Manager"}, {"department": "HR"}]}))
    
    # Prepare a list of manager IDs
    manager_ids = [str(manager["_id"]) for manager in managers]
    list1 = list()
    # Fixed query: Show manager WFH requests with status "Pending" that need admin approval
    res = RemoteWork.find({"userid": {"$in":manager_ids}, "status": "Pending"})
    print(f"Admin page WFH query result: {list(res)}")
    res = RemoteWork.find({"userid": {"$in":manager_ids}, "status": "Pending"})  # Re-query due to cursor exhaustion
    for user in res:
        cleanid(user)
        user["fromDate"] = user["fromDate"].strftime("%d-%m-%Y")
        user["toDate"] = user["toDate"].strftime("%d-%m-%Y")
        user["requestDate"] = user["requestDate"].strftime("%d-%m-%Y")
        list1.append(user)
    return list1

# TL Page Remote Requests
def get_TL_page_remote_work_requests(TL):
    users = list(Users.find({"TL":TL}))
    
    # Prepare a list of user IDs under this TL
    users_ids = [str(user["_id"]) for user in users]
    list1 = list()
    # Show employee WFH requests that are pending manager approval (status "Pending" and no recommendation)
    res = RemoteWork.find({"userid": {"$in":users_ids}, "status": "Pending", "Recommendation":{"$exists":False}})
    print(f"TL WFH query result: {list(res)}")
    res = RemoteWork.find({"userid": {"$in":users_ids}, "status": "Pending", "Recommendation":{"$exists":False}})  # Re-query due to cursor exhaustion
    for user in res:
        cleanid(user)
        user["fromDate"] = user["fromDate"].strftime("%d-%m-%Y")
        user["toDate"] = user["toDate"].strftime("%d-%m-%Y")
        user["requestDate"] = user["requestDate"].strftime("%d-%m-%Y")
        list1.append(user)
    return list1

# Status Response for Remote Work
def update_remote_work_request_status_in_mongo(userid, status, wfh_id):
    try:
        print("Updating WFH status in MongoDB:")
        print("User ID:", userid)
        print("Status:", status)
        print("WFH ID:", wfh_id)
        
        # Check if this is a manager WFH request that needs admin approval
        wfh_request = RemoteWork.find_one({"_id": ObjectId(wfh_id)})
        if not wfh_request:
            print("WFH request not found")
            return False
            
        user = Users.find_one({"_id": ObjectId(userid)})
        is_manager = user and user.get("position") == "Manager"
        
        if is_manager:
            # For manager requests, admin can directly approve/reject from "Pending" status
            result = RemoteWork.update_one(
                {"_id": ObjectId(wfh_id), "userid": userid, "status": "Pending"}, 
                {"$set": {"status": status}}
            )
        else:
            # For regular employee requests, update from "Recommend" status (after TL approval)
            result = RemoteWork.update_one(
                {"_id": ObjectId(wfh_id), "userid": userid, "status": None, "Recommendation": "Recommend"}, 
                {"$set": {"status": status}, "$unset": {"Recommendation": ""}}
            )
        
        if result.modified_count > 0:
            print(f"✅ WFH status updated successfully to {status}")
            return True
        else:
            print(f"❌ No WFH request updated - check conditions")
            return False
    except Exception as e:
        print(f"Error updating WFH status: {e}")
        raise Exception("Error updating status in MongoDB")

    return False

def update_remote_work_request_recommend_in_mongo(userid, status, wfh_id):
    try:
        print("Updating status in MongoDB:")
        print("User ID:", userid)
        print("Status:", status)
        print(wfh_id)
        
        # result = RemoteWork.update_one({"_id":ObjectId(wfh_id), "userid": userid, "Recommendation":None}, {"$set": {"Recommendation": status}})
        result = RemoteWork.find_one_and_update({"_id":ObjectId(wfh_id), "userid": userid, "Recommendation":None}, {"$set": {"Recommendation": status}})
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error updating status: {e}")
        raise Exception("Error updating status in MongoDB")

    return False


def store_Other_leave_request(userid, employee_name, time, leave_type, selected_date, To_date, request_date, reason):
    # Convert string dates to datetime objects if needed
    if isinstance(selected_date, str):
        try:
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
        except ValueError:
            selected_date = datetime.strptime(selected_date, "%d-%m-%Y")
    else:
        selected_date = datetime.strptime(selected_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
        
    if isinstance(To_date, str):
        try:
            To_date = datetime.strptime(To_date, "%Y-%m-%d")
        except ValueError:
            To_date = datetime.strptime(To_date, "%d-%m-%Y")
    else:
        To_date = datetime.strptime(To_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
        
    if isinstance(request_date, str):
        try:
            request_date = datetime.strptime(request_date, "%Y-%m-%d")
        except ValueError:
            request_date = datetime.strptime(request_date, "%d-%m-%Y")
    else:
        request_date = datetime.strptime(request_date.strftime("%d-%m-%Y"), "%d-%m-%Y")

    if request_date.weekday() == 6:
        return "Request date is a Sunday. Request not allowed."

    if To_date < selected_date:
        return "To date should be after or equal to from date."
    
    #Check if leave or remote work overlaps with the given date range
    if check_multi_day_leave_conflict(userid, selected_date, To_date):
        return f"Leave request conflicts with an existing leave or remote work during this period."


    num_weekdays_request_to_from = count_weekdays(request_date, selected_date)
    
    if leave_type == "Other Leave":
        weekdays_count = count_weekdays(request_date + timedelta(days=1), selected_date)
        num_weekdays_from_to = count_weekdays(selected_date, To_date)
        
        future_days = (To_date - selected_date).days
        
        employee_id = get_employee_id_from_db(employee_name)
         
        if num_weekdays_from_to <= 3 and future_days <= 3:
            new_request = {
                "userid": userid,
                "Employee_ID": employee_id, 
                "employeeName": employee_name,
                "time": time,
                "leaveType": leave_type,
                "selectedDate": selected_date,
                "ToDate" : To_date,
                "requestDate": request_date,
                "reason": reason,
            }
            result = Leave.insert_one(new_request)
            print("result", result)
            return "Leave request stored successfully"
        else:
            return "Other Leave can be taken for a maximum of 3 days"
    # else:
        # return "Other Leave request can only be made at least 2 days prior"


def store_Permission_request(userid, employee_name, time, leave_type, selected_date, request_date, Time_Slot, reason):
    # Convert string dates to datetime objects if needed
    if isinstance(selected_date, str):
        try:
            selected_date_dt = datetime.strptime(selected_date, "%Y-%m-%d")
        except ValueError:
            selected_date_dt = datetime.strptime(selected_date, "%d-%m-%Y")
    else:
        selected_date_dt = datetime.strptime(selected_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
        
    if isinstance(request_date, str):
        try:
            request_date_dt = datetime.strptime(request_date, "%Y-%m-%d")
        except ValueError:
            request_date_dt = datetime.strptime(request_date, "%d-%m-%Y")
    else:
        request_date_dt = datetime.strptime(request_date.strftime("%d-%m-%Y"), "%d-%m-%Y")

    # Check for existing leave conflicts
    if check_leave_conflict(userid, selected_date_dt):
        return "Leave request conflicts with an existing leave or remote work."

    # Ensure request date is not a Sunday
    if request_date_dt.weekday() == 6:
        return "Request date is a Sunday. Request not allowed."

    # Permission is only allowed for the same day
    if leave_type == "Permission" and selected_date_dt != request_date_dt:
        return "Permission is permitted for today only."

    employee_id = get_employee_id_from_db(employee_name)

    new_leave = {
        "userid": userid,
        "Employee_ID": employee_id,
        "employeeName": employee_name,
        "time": time,
        "leaveType": leave_type,
        "selectedDate": selected_date_dt,  # ✅ Stored as `datetime` object
        "requestDate": request_date_dt,  # ✅ Stored as `datetime` object
        "timeSlot": Time_Slot,
        "reason": reason,
    }

    result = Leave.insert_one(new_leave)
    return "Leave request stored successfully"


def Otherleave_History_Details(userid):

    # Filter by userid and leaveType "Other"
    leave_history = list(Leave.find({"userid": userid, "leaveType": "Other Leave"}))

    # Convert ObjectId to string for JSON serialization
    for item in leave_history:
        item["_id"] = str(item["_id"])
        item["selectedDate"] = item["selectedDate"].strftime("%d-%m-%Y")
        item["ToDate"] = item["ToDate"].strftime("%d-%m-%Y")
        item["requestDate"] = item["requestDate"].strftime("%d-%m-%Y")


    return leave_history

def normal_leave_details(userid):

    # Filter by userid and leaveType "Other"
    leave_history = list(Leave.find({"userid": userid,"leaveType":{"$ne":"Other Leave"}}))

    # Convert ObjectId to string for JSON serialization
    for item in leave_history:
        item["_id"] = str(item["_id"])
        item["selectedDate"] = item["selectedDate"].strftime("%d-%m-%Y")
        item["requestDate"] = item["requestDate"].strftime("%d-%m-%Y")
    
    return leave_history


def Permission_History_Details(userid):

    # Filter by userid and leaveType "Other"
    leave_history = list(Leave.find({"userid": userid, "leaveType": "Permission"}))

    # Convert ObjectId to string for JSON serialization
    for item in leave_history:
        item["_id"] = str(item["_id"])
        item["_id"] = str(item["_id"])
        item["selectedDate"] = item["selectedDate"].strftime("%d-%m-%Y")
        item["requestDate"] = item["requestDate"].strftime("%d-%m-%Y")

    return leave_history

def get_all_users():
        # Fetch all users from the Users collection
        users = list(Users.find({}, {"password": 0}))  # Exclude the password field
        # Prepare a list of users with only name, email, and id
        user_list = []
        for user in users:
            user_data = {
                "id": str(user["_id"]),  # Convert ObjectId to string
                "email": user.get("email"),
                "name": user.get("name"),
                "department": user.get("department"),
                "position": user.get("position"),
                "status": user.get("status"),
            }
            user_list.append(user_data)
        return user_list

def get_admin_info(email):
    admin_info = admin.find_one({'email':email}, {"password":0})
    return admin_info

def add_task_list(tasks, userid: str, today, due_date):
    for task in tasks:
        t = {
            "task": task,
            "status": "Not completed",
            "date": today,
            "due_date": due_date,
            "userid": userid,
        }
        result = Tasks.insert_one(t)
    return "Task added Successfully"

def manager_task_assignment(task:str, userid: str, TL, today, due_date):
    task = {
        "task": task,
        "status": "Not completed",
        "date": today,
        "due_date": due_date,
        "userid": userid,
        "TL": TL,
    }
    result = Tasks.insert_one(task)
    return str(result.inserted_id)

def edit_the_task(taskid, userid, cdate, due_date, updated_task=None, status=None):
    update_fields = {}
    if updated_task and updated_task != "string":
        update_fields["task"] = updated_task
    if status and status != "string":
        update_fields["status"] = status
        update_fields["completed_date"] = cdate
    if due_date and due_date != "string":
        update_fields["due_date"] = due_date

    if update_fields:
        result = Tasks.update_one({"_id": ObjectId(taskid), "userid": userid}, {"$set": update_fields})
        if result.matched_count > 0:
            return "Task updated successfully"
        else:
            return "Task not found"
    else:
        return "No fields to update"


def delete_a_task(taskid):
    try:
        result = Tasks.delete_one({"_id": ObjectId(taskid)})
        if result.deleted_count > 0:
            return "Deleted"
        return "Task not found"
    except Exception as e:
        return f"Error: {str(e)}"



def get_the_tasks(userid: str, date: str = None):
    query = {"userid": userid}

    # If date filter is provided, add it to query
    if date:
        query["date"] = date  

    tasks = list(Tasks.find(query))
    task_list = []
    for task in tasks:
        task_data = {
            "task": task.get("task"),
            "status": task.get("status"),
            "date": task.get("date"),
            "due_date": task.get("due_date"),
            "userid": task.get("userid"),
            "taskid": str(task.get("_id"))  # ensure ObjectId → str
        }
        task_list.append(task_data)

    return task_list

# def get_user_info(userid):
#     result = Users.find_one({"_id": ObjectId(userid)}, {"_id": 0, "password": 0})
#     return result

def get_user_info(userid):
    print("Connected DB:", db.name)
    print("Collection:", Users.name)
    print("Searching for user ID:", userid)
    
    try:
        obj_id = ObjectId(userid)
    except Exception as e:
        return {"error": f"Invalid ID format: {str(e)}", "userid": userid}

    result = Users.find_one({"_id": obj_id}, {"password": 0})
    if result:
        result["_id"] = str(result["_id"])  # JSON safe
        return result
    else:
        print("User not found in collection")
        return {"error": "User not found", "userid": userid}


def get_admin_information(userid):
    # print(userid)
    # result = admin.find_one({"_id":ObjectId(userid)},{"_id":0,"password":0})
    # return result
    try:
        obj_id = ObjectId(userid)
    except Exception as e:
        return {"error": f"Invalid ID format: {str(e)}", "userid": userid}

    result = Users.find_one({"_id": obj_id}, {"password": 0})
    if result:
        result["_id"] = str(result["_id"])  # JSON safe
        return result
    else:
        print("User not found in collection")
        return {"error": "User not found", "userid": userid}


def get_last_digits():
    users = Users.find({}, {"userid": 1})  # Querying only 'userid' field

    last_digits_list = [
        int(str(user.get("userid"))[-3:])  # Extract last 3 digits safely
        for user in users if user.get("userid")  # Ignore None values
    ]

    if not last_digits_list:  # Handle case when no users exist
        return 1  # Start from 1 if no existing users

    max_digits = max(last_digits_list)  # Get max value
    print(max_digits)
    return max_digits + 1  # Increment properly



def generate_userid(dept,doj):
    last_digit = str((get_last_digits())).zfill(3)
    doj = "".join(doj.split("-")[::-1])
    return dept+str(doj)+last_digit
    


def add_an_employee(employee_data):
        # Insert the employee data into the Users collection
        # userid = generate_userid(employee_data["department"],employee_data["date_of_joining"])
        # employee_data["userid"] = userid
        print(employee_data)
        result = Users.insert_one(employee_data)
        return {"message": "Employee details added successfully"}
    
    
def auto_approve_manager_leaves():
    Leave.update_many(
        {"position":"Manager", "status": "Recommend"},
        {"$set": {"status": "Approved"}}
    )

    return {"message": "Manager leave requests have been auto-approved where applicable."}

def get_user_info(userid):
 result = Users.find_one({"$or":[{"userid":userid}]},{"_id":0,"password":0})
 return result

# def edit_an_employee(employee_data):
#  try:
#  # Insert the employee data into the Users collection
#   result = Users.find_one_and_update({"userid":employee_data["userid"]},{"$set":employee_data})
#   return {"message": "Employee details edited successfully"}
#  except Exception as e:
#   raise HTTPException(status_code=500, detail=str(e))

def edit_an_employee(employee_data):
    """Edit employee data with proper validation"""
    try:
        print(f"Editing employee with userid: {employee_data.get('userid')}")
        print(f"Employee data: {employee_data}")
        
        # Validate required fields
        required_fields = ['userid', 'name', 'email', 'phone', 'position', 'department']
        for field in required_fields:
            if not employee_data.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Clean the data - remove empty education and skills entries
        clean_education = [
            edu for edu in employee_data.get('education', []) 
            if edu.get('degree') or edu.get('institution') or edu.get('year')
        ]
        
        clean_skills = [
            skill for skill in employee_data.get('skills', []) 
            if skill.get('name') and skill.get('level')
        ]
        
        # Update the employee_data with cleaned arrays
        employee_data['education'] = clean_education
        employee_data['skills'] = clean_skills
        
        # Find and update the employee
        result = Users.find_one_and_update(
            {"userid": employee_data["userid"]},
            {"$set": employee_data},
            return_document=True
        )
        
        if result:
            return {"message": "Employee details updated successfully"}
        else:
            # Try updating by ObjectId if userid doesn't work
            try:
                obj_id = ObjectId(employee_data["userid"])
                result = Users.find_one_and_update(
                    {"_id": obj_id},
                    {"$set": employee_data},
                    return_document=True
                )
                if result:
                    return {"message": "Employee details updated successfully"}
                else:
                    raise HTTPException(status_code=404, detail="Employee not found")
            except:
                raise HTTPException(status_code=404, detail="Employee not found")
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in edit_an_employee: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def get_managers() :
    users = list(Users.find({"position": "Manager"}, {"_id":0}))
    return users

from datetime import datetime

def task_assign_to_multiple_users(task_details):
    inserted_ids = []
    
    for item in task_details:
        tasks = item.get("Tasks", [])  # Extracting tasks from Task_details
        for task in tasks:
            task_entry = {
                "task": task,
                "status": "Not completed",
                "date": datetime.strptime(item["date"], "%Y-%m-%d").strftime("%d-%m-%Y"),
                "due_date": datetime.strptime(item["due_date"], "%Y-%m-%d").strftime("%d-%m-%Y"),
                "userid": item["userid"],
                "TL": item["TL"],
            }
            result = Tasks.insert_one(task_entry)
            inserted_ids.append(str(result.inserted_id))
    
    return inserted_ids

async def task_assign_to_multiple_users_with_notification(task_details, assigner_name=None, single_notification_per_user=True):
    """Enhanced version that creates tasks and sends comprehensive notifications
    
    Args:
        task_details: List of task assignment details
        assigner_name: Name of the person assigning tasks
        single_notification_per_user: If True, sends one notification per user with all tasks.
                                    If False, sends one notification per individual task.
    """
    inserted_ids = []
    user_tasks = {}  # Group tasks by user for single notification option
    
    for item in task_details:
        tasks = item.get("Tasks", [])  # Extracting tasks from Task_details
        userid = item["userid"]
        due_date = datetime.strptime(item["due_date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        
        # Initialize user tasks if not exists
        if userid not in user_tasks:
            user_tasks[userid] = {
                "tasks": [],
                "due_date": due_date,
                "assigner_name": assigner_name or item.get("TL", "Manager")
            }
        
        for task in tasks:
            task_entry = {
                "task": task,
                "status": "Not completed",
                "date": datetime.strptime(item["date"], "%Y-%m-%d").strftime("%d-%m-%Y"),
                "due_date": due_date,
                "userid": userid,
                "TL": item["TL"],
            }
            result = Tasks.insert_one(task_entry)
            task_id = str(result.inserted_id)
            inserted_ids.append(task_id)
            
            # Add task to user's task list
            user_tasks[userid]["tasks"].append({
                "title": task,
                "task_id": task_id
            })
    
    # Send enhanced notifications based on preference
    if single_notification_per_user:
        # Send one notification per user with all their tasks
        for userid, user_data in user_tasks.items():
            try:
                task_count = len(user_data["tasks"])
                if task_count == 1:
                    # Single task - use specific manager assignment notification
                    await create_task_manager_assigned_notification(
                        userid=userid,
                        task_title=user_data["tasks"][0]["title"],
                        manager_name=user_data["assigner_name"],
                        task_id=user_data["tasks"][0]["task_id"],
                        due_date=user_data["due_date"],
                        priority="high"
                    )
                else:
                    # Multiple tasks - use summary
                    task_titles = [task["title"] for task in user_data["tasks"]]
                    summary_title = f"{task_count} tasks: " + ", ".join(task_titles[:2])
                    if task_count > 2:
                        summary_title += f" and {task_count - 2} more"
                    
                    await create_task_manager_assigned_notification(
                        userid=userid,
                        task_title=summary_title,
                        manager_name=user_data["assigner_name"],
                        task_id=None,  # Multiple tasks, no single ID
                        due_date=user_data["due_date"],
                        priority="high"
                    )
                
                print(f"✅ Sent enhanced notification to user {userid} for {task_count} tasks")
            except Exception as e:
                print(f"Error sending enhanced notification to user {userid}: {e}")
    else:
        # Send one notification per individual task using enhanced notifications
        for userid, user_data in user_tasks.items():
            for task_data in user_data["tasks"]:
                try:
                    await create_task_manager_assigned_notification(
                        userid=userid,
                        task_title=task_data["title"],
                        manager_name=user_data["assigner_name"],
                        task_id=task_data["task_id"],
                        due_date=user_data["due_date"],
                        priority="high"
                    )
                except Exception as e:
                    print(f"Error sending notification for task {task_data['title']}: {e}")
    
    return inserted_ids


def get_single_task(taskid):
    tasks = list(Tasks.find({"_id": ObjectId(taskid)}))
    for task in tasks:
        task["_id"] = str(task.get("_id"))
    return tasks

def assigned_task(tl, userid=None):
    if userid:
        tasks = list(Tasks.find({"userid": userid, "TL":tl}))
    else:
        tasks = list(Tasks.find({"TL":tl}))
    task_list = []
    for task in tasks:
        task_data = {
            "task": task.get("task"),
            "status": task.get("status"),
            "date": task.get("date"),
            "due_date": task.get("due_date"),
            "userid": task.get("userid"),
            "taskid": str(task.get("_id"))
        }
        task_list.append(task_data)  
    return task_list

def get_team_members(TL):
    team_members = list(Users.find({"TL":TL}, {"_id":0}))
    return team_members

def get_public_ip():
    try:
        ip = requests.get("https://api64.ipify.org?format=text").text
        print(ip)
        return ip
    except requests.RequestException:
        return "Unable to fetch public IP"
    
def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(ip)
        return ip
    except Exception:
        return "Unable to fetch local IP"

# Notification System Functions

def get_role_based_action_url(userid, notification_type, base_path=None):
    """Get the appropriate action URL based on user role and notification type"""
    try:
        # Get user info to determine role
        user = Users.find_one({"_id": ObjectId(userid)}) if ObjectId.is_valid(userid) else None
        if not user:
            return base_path or '/User/Clockin_int'
        
        is_admin = user.get("isadmin", False)
        position = user.get("position", "").lower()
        department = user.get("department", "").lower()
        
        # Determine user role - HR users should be treated as admin-level for routing
        is_hr = ("hr" in position or "hr" in department)
        is_admin_level = is_admin or is_hr
        
        # Define URL mappings for different notification types
        url_mappings = {
            # Task-related notifications
            'task': {
                'admin': '/admin/task',
                'user': '/User/task'
            },
            'task_created': {
                'admin': '/admin/task',
                'user': '/User/task'
            },
            'task_manager_assigned': {
                'admin': '/admin/task',
                'user': '/User/task'
            },
            'task_overdue': {
                'admin': '/admin/task',
                'user': '/User/task'
            },
            'task_due_soon': {
                'admin': '/admin/task',
                'user': '/User/task'
            },
            
            # Leave-related notifications
            'leave': {
                'admin': '/admin/leaveapproval',
                'user': '/User/LeaveHistory'
            },
            'leave_submitted': {
                'admin': '/admin/leaveapproval',
                'user': '/User/LeaveHistory'
            },
            'leave_approved': {
                'admin': '/admin/leaveapproval',
                'user': '/User/LeaveHistory'
            },
            'leave_rejected': {
                'admin': '/admin/leaveapproval',
                'user': '/User/LeaveHistory'
            },
            'leave_recommended': {
                'admin': '/admin/leaveapproval',
                'user': '/User/LeaveHistory'
            },
            'leave_admin_pending': {
                'admin': '/admin/leaveapproval',
                'user': '/User/Leave'
            },
            'leave_manager_pending': {
                'admin': '/admin/leaveapproval',
                'user': '/User/Leave'
            },
            'leave_hr_final_approval': {
                'admin': '/admin/leaveapproval',
                'user': '/User/LeaveHistory'
            },
            'leave_final_approval_required': {
                'admin': '/admin/leaveapproval',
                'user': '/User/LeaveHistory'
            },
            
            # WFH-related notifications
            'wfh': {
                'admin': '/admin/wfh',
                'user': '/User/Remote_details'
            },
            'wfh_submitted': {
                'admin': '/admin/wfh',
                'user': '/User/Remote_details'
            },
            'wfh_approved': {
                'admin': '/admin/wfh',
                'user': '/User/Remote_details'
            },
            'wfh_rejected': {
                'admin': '/admin/wfh',
                'user': '/User/Remote_details'
            },
            'wfh_admin_pending': {
                'admin': '/admin/wfh',
                'user': '/User/Workfromhome'
            },
            'wfh_manager_pending': {
                'admin': '/admin/wfh',
                'user': '/User/Workfromhome'
            },
            'wfh_hr_final_approval': {
                'admin': '/admin/wfh',
                'user': '/User/Remote_details'
            },
            'wfh_hr_pending': {
                'admin': '/admin/wfh',
                'user': '/User/Remote_details'
            },
            'wfh_final_approval_required': {
                'admin': '/admin/wfh',
                'user': '/User/Remote_details'
            },
            
            # Attendance-related notifications
            'attendance': {
                'admin': '/admin/time',
                'user': '/User/Clockin_int/Clockdashboard'
            },
            
            # Employee management notifications
            'employee': {
                'admin': '/admin/employee',
                'user': '/User/profile'
            },
            
            # System notifications
            'system': {
                'admin': '/admin/profile',
                'user': '/User/profile'
            }
        }
        
        # Get the appropriate URL based on role
        role_key = 'admin' if is_admin_level else 'user'
        
        if notification_type in url_mappings:
            return url_mappings[notification_type][role_key]
        
        # Fallback to base_path if provided
        if base_path:
            return base_path
        
        # Default fallback
        return '/admin' if is_admin_level else '/User/Clockin_int'
        
    except Exception as e:
        print(f"Error determining role-based action URL: {e}")
        return base_path or '/User/Clockin_int'

async def create_notification_with_websocket(userid, title, message, notification_type, priority="medium", action_url=None, related_id=None, metadata=None):
    """Create a new notification and send via WebSocket"""
    try:
        # Determine the appropriate action URL based on user role and notification type
        if action_url is None:
            action_url = get_role_based_action_url(userid, notification_type)
        
        notification_id = create_notification(userid, title, message, notification_type, priority, action_url, related_id, metadata)
        
        if notification_id:
            # Import here to avoid circular imports
            from websocket_manager import notification_manager
            
            # Prepare notification data for WebSocket
            notification_data = {
                "_id": notification_id,
                "userid": userid,
                "title": title,
                "message": message,
                "type": notification_type,
                "priority": priority,
                "action_url": action_url,
                "related_id": related_id,
                "metadata": metadata or {},
                "is_read": False,
                "created_at": get_current_timestamp_iso()
            }
            
            # Send real-time notification
            await notification_manager.send_personal_notification(userid, notification_data)
            
            # Update unread count
            unread_count = get_unread_notification_count(userid)
            await notification_manager.send_unread_count_update(userid, unread_count)
            
        return notification_id
    except Exception as e:
        print(f"Error creating notification with websocket: {e}")
        return create_notification(userid, title, message, notification_type, priority, action_url, related_id, metadata)

def create_notification(userid, title, message, notification_type, priority="medium", action_url=None, related_id=None, metadata=None):
    """Create a new notification with timezone-aware timestamps"""
    try:
        # Determine the appropriate action URL based on user role and notification type
        if action_url is None:
            action_url = get_role_based_action_url(userid, notification_type)
        
        notification = {
            "userid": userid,
            "title": title,
            "message": message,
            "type": notification_type,
            "priority": priority,
            "action_url": action_url,
            "related_id": related_id,
            "metadata": metadata or {},
            "is_read": False,
            "created_at": get_current_timestamp_iso(),
            "updated_at": get_current_timestamp_iso()
        }
        result = Notifications.insert_one(notification)
        print(f"✅ Created notification with timestamp: {notification['created_at']}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None

def get_notifications(userid, notification_type=None, priority=None, is_read=None, limit=50):
    """Get notifications for a user with optional filters"""
    try:
        query = {"userid": userid}
        
        if notification_type:
            query["type"] = notification_type
        if priority:
            query["priority"] = priority
        if is_read is not None:
            query["is_read"] = is_read
            
        notifications = list(Notifications.find(query)
                           .sort("created_at", -1)
                           .limit(limit))
        
        for notification in notifications:
            notification["_id"] = str(notification["_id"])
            # Ensure timezone-aware timestamps are properly formatted
            created_at = notification["created_at"]
            updated_at = notification.get("updated_at")
            
            # Handle created_at timestamp
            if isinstance(created_at, str):
                # Already a string, keep as is
                pass
            elif isinstance(created_at, datetime):
                # If datetime is not timezone-aware, make it timezone-aware
                if created_at.tzinfo is None:
                    created_at = pytz.timezone("Asia/Kolkata").localize(created_at)
                # Convert to ISO format with timezone info
                notification["created_at"] = format_timestamp_iso(created_at)
            
            # Handle updated_at timestamp
            if updated_at:
                if isinstance(updated_at, str):
                    # Already a string, keep as is
                    pass
                elif isinstance(updated_at, datetime):
                    # If datetime is not timezone-aware, make it timezone-aware
                    if updated_at.tzinfo is None:
                        updated_at = pytz.timezone("Asia/Kolkata").localize(updated_at)
                    # Convert to ISO format with timezone info
                    notification["updated_at"] = format_timestamp_iso(updated_at)
            else:
                # Set updated_at to created_at if not present
                notification["updated_at"] = notification["created_at"]
            
        return notifications
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return []

def mark_notification_read(notification_id, is_read=True):
    """Mark a notification as read/unread"""
    try:
        result = Notifications.update_one(
            {"_id": ObjectId(notification_id)},
            {
                "$set": {
                    "is_read": is_read,
                    "updated_at": datetime.now(pytz.timezone("Asia/Kolkata"))
                }
            }
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error marking notification: {e}")
        return False

def mark_all_notifications_read(userid):
    """Mark all notifications as read for a user"""
    try:
        result = Notifications.update_many(
            {"userid": userid, "is_read": False},
            {
                "$set": {
                    "is_read": True,
                    "updated_at": datetime.now(pytz.timezone("Asia/Kolkata"))
                }
            }
        )
        return result.modified_count
    except Exception as e:
        print(f"Error marking all notifications read: {e}")
        return 0

def get_unread_notification_count(userid):
    """Get count of unread notifications for a user"""
    try:
        count = Notifications.count_documents({"userid": userid, "is_read": False})
        return count
    except Exception as e:
        print(f"Error getting unread count: {e}")
        return 0

def delete_notification(notification_id):
    """Delete a notification"""
    try:
        result = Notifications.delete_one({"_id": ObjectId(notification_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting notification: {e}")
        return False

def get_notifications_by_type(userid, notification_type):
    """Get notifications by type for a user"""
    try:
        notifications = list(Notifications.find(
            {"userid": userid, "type": notification_type}
        ).sort("created_at", -1))
        
        for notification in notifications:
            notification["_id"] = str(notification["_id"])
            # Ensure timezone-aware timestamps are properly formatted
            created_at = notification["created_at"]
            updated_at = notification["updated_at"]
            
            # Convert to ISO format with timezone info
            notification["created_at"] = format_timestamp_iso(created_at)
            notification["updated_at"] = format_timestamp_iso(updated_at)
            
        return notifications
    except Exception as e:
        print(f"Error getting notifications by type: {e}")
        return []

# Helper functions to create specific notification types
def create_task_notification(userid, task_title, action, task_id=None, priority="medium"):
    """Create task-related notification"""
    title = f"Task {action}"
    message = f"Task '{task_title}' has been {action.lower()}"
    # Use the role-based action URL system
    action_url = get_role_based_action_url(userid, "task")
    
    return create_notification(
        userid=userid,
        title=title,
        message=message,
        notification_type="task",
        priority=priority,
        action_url=action_url,
        related_id=task_id,
        metadata={"task_title": task_title, "action": action}
    )

async def create_task_assignment_notification(userid, task_title, assigner_name, task_id=None, due_date=None, priority="high"):
    """Create enhanced task assignment notification with WebSocket support"""
    try:
        print(f"🔄 Creating task notification for user {userid}: '{task_title}' by {assigner_name}")
        
        # Get user info for personalized message
        user = Users.find_one({"_id": ObjectId(userid)}) if ObjectId.is_valid(userid) else None
        user_name = user.get("name", "User") if user else "User"
        
        title = f"New Task Assigned"
        message = f"Hi {user_name}, you have been assigned a new task: '{task_title}'"
        if assigner_name:
            message += f" by {assigner_name}"
        if due_date:
            message += f". Due date: {due_date}"
        
        # Check for duplicate notifications (same user, task, and assigner within last minute)
        one_minute_ago = datetime.now(pytz.timezone("Asia/Kolkata")) - timedelta(minutes=1)
        existing_notification = Notifications.find_one({
            "userid": userid,
            "title": title,
            "metadata.task_title": task_title,
            "metadata.assigner_name": assigner_name,
            "created_at": {"$gte": one_minute_ago}
        })
        
        if existing_notification:
            print(f"⚠️ Duplicate notification detected for user {userid}, task '{task_title}'. Skipping.")
            return str(existing_notification["_id"])
        
        # Create notification in database
        notification_id = create_notification(
            userid=userid,
            title=title,
            message=message,
            notification_type="task",
            priority=priority,
            action_url=get_role_based_action_url(userid, "task"),
            related_id=task_id,
            metadata={
                "task_title": task_title,
                "action": "Assigned",
                "assigner_name": assigner_name,
                "due_date": due_date
            }
        )
        
        if notification_id:
            # Send real-time WebSocket notification
            from websocket_manager import notification_manager
            
            notification_data = {
                "_id": notification_id,
                "userid": userid,
                "title": title,
                "message": message,
                "type": "task",
                "priority": priority,
                "action_url": get_role_based_action_url(userid, "task"),
                "related_id": task_id,
                "metadata": {
                    "task_title": task_title,
                    "action": "Assigned",
                    "assigner_name": assigner_name,
                    "due_date": due_date
                },
                "is_read": False,
                "created_at": get_current_timestamp_iso()
            }
            
            await notification_manager.send_personal_notification(userid, notification_data)
            
            # Update unread count
            unread_count = get_unread_notification_count(userid)
            await notification_manager.send_unread_count_update(userid, unread_count)
            
            print(f"✅ Task assignment notification sent to {user_name} ({userid}) - ID: {notification_id}")
            
        return notification_id
    except Exception as e:
        print(f"Error creating task assignment notification: {e}")
        # Fallback to regular notification
        return create_task_notification(userid, task_title, "Assigned", task_id, priority)

def create_leave_notification(userid, leave_type, action, leave_id=None, priority="medium", manager_name=None):
    """
    Create enhanced leave-related notification
    Actions: submitted, approved, rejected, recommended
    manager_name: Can be Manager, Admin, or other approver name
    """
    action_lower = action.lower()
    
    # Define notification content based on action
    if action_lower == "submitted":
        title = f"Leave Request Submitted"
        message = f"Your {leave_type} leave request has been submitted successfully and is pending approval"
        priority = "medium"
        notification_type = "leave_submitted"
    elif action_lower == "approved":
        title = f"Leave Request Approved ✅"
        message = f"Your {leave_type} leave request has been approved"
        priority = "high"
        notification_type = "leave_approved"
    elif action_lower == "rejected":
        title = f"Leave Request Rejected ❌"
        message = f"Your {leave_type} leave request has been rejected"
        priority = "high"
        notification_type = "leave_rejected"
    elif action_lower == "recommended":
        title = f"Leave Request Recommended 👍"
        manager_text = f" by {manager_name}" if manager_name else ""
        message = f"Your {leave_type} leave request has been recommended{manager_text} and forwarded for HR review"
        priority = "medium"
        notification_type = "leave_recommended"
    else:
        # Fallback for backward compatibility
        title = f"Leave Request {action}"
        message = f"Your {leave_type} request has been {action_lower}"
        notification_type = "leave"
    
    action_url = get_role_based_action_url(userid, notification_type)
    
    return create_notification(
        userid=userid,
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        action_url=action_url,
        related_id=leave_id,
        metadata={
            "leave_type": leave_type, 
            "action": action,
            "manager_name": manager_name
        }
    )

def create_wfh_notification(userid, action, wfh_id=None, priority="medium", request_date=None):
    """
    Create enhanced work from home notification
    Actions: submitted, approved, rejected
    """
    action_lower = action.lower()
    
    # Define notification content based on action
    if action_lower == "submitted":
        title = f"WFH Request Submitted"
        date_text = f" for {request_date}" if request_date else ""
        message = f"Your work from home request{date_text} has been submitted successfully and is pending approval"
        priority = "medium"
        notification_type = "wfh_submitted"
    elif action_lower == "approved":
        title = f"WFH Request Approved ✅"
        date_text = f" for {request_date}" if request_date else ""
        message = f"Your work from home request{date_text} has been approved"
        priority = "high"
        notification_type = "wfh_approved"
    elif action_lower == "rejected":
        title = f"WFH Request Rejected ❌"
        date_text = f" for {request_date}" if request_date else ""
        message = f"Your work from home request{date_text} has been rejected"
        priority = "high"
        notification_type = "wfh_rejected"
    else:
        # Fallback for backward compatibility
        title = f"WFH Request {action}"
        message = f"Your work from home request has been {action_lower}"
        notification_type = "wfh"
    
    action_url = get_role_based_action_url(userid, notification_type)
    
    return create_notification(
        userid=userid,
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        action_url=action_url,
        related_id=wfh_id,
        metadata={
            "action": action,
            "request_date": request_date
        }
    )

def create_system_notification(userid, title, message, priority="low"):
    """Create system notification"""
    return create_notification(
        userid=userid,
        title=title,
        message=message,
        notification_type="system",
        priority=priority,
        action_url=None,
        related_id=None,
        metadata={"system_message": True}
    )

def create_attendance_notification(userid, message, priority="medium", attendance_type="general"):
    """Create attendance-related notification"""
    
    # Set title based on attendance type
    if attendance_type == "clock_in":
        title = "✅ Clock-in Success"
        priority = "low"
    elif attendance_type == "clock_out":
        title = "✅ Clock-out Success"
        priority = "low"
    elif attendance_type == "auto_clock_out":
        title = "🔄 Auto Clock-out"
        priority = "medium"
    elif attendance_type == "missed_clock_out":
        title = "⚠️ Missed Clock-out"
        priority = "high"
    else:
        title = "📋 Attendance Alert"
    
    action_url = get_role_based_action_url(userid, "attendance")
    
    return create_notification(
        userid=userid,
        title=title,
        message=message,
        notification_type="attendance",
        priority=priority,
        action_url=action_url,
        related_id=None,
        metadata={
            "attendance_alert": True,
            "attendance_type": attendance_type
        }
    )

# Specific attendance notification functions
async def notify_clock_in_success(userid, time, status="Present"):
    """Send notification for successful clock-in"""
    message = f"Successfully clocked in at {time}. Status: {status}"
    create_attendance_notification(userid, message, "low", "clock_in")

async def notify_clock_out_success(userid, time, total_hours=""):
    """Send notification for successful clock-out"""
    hours_text = f" Total work time: {total_hours}" if total_hours else ""
    message = f"Successfully clocked out at {time}.{hours_text}"
    create_attendance_notification(userid, message, "low", "clock_out")

async def notify_auto_clock_out(userid, time):
    """Send notification for auto clock-out"""
    message = f"Automatic clock-out completed at {time}. Please review your attendance."
    create_attendance_notification(userid, message, "medium", "auto_clock_out")

async def notify_missed_clock_out(userid, date=None):
    """Send notification for missed clock-out"""
    date_text = f" for {date}" if date else ""
    message = f"Clock-out missed{date_text}. Please contact HR or use manual correction."
    create_attendance_notification(userid, message, "high", "missed_clock_out")

# WebSocket-enabled convenience functions for real-time notifications

async def notify_leave_submitted(userid, leave_type, leave_id=None):
    """Send real-time notification when leave is submitted"""
    return await create_notification_with_websocket(
        userid=userid,
        title="Leave Request Submitted",
        message=f"Your {leave_type} leave request has been submitted successfully and is pending approval",
        notification_type="leave_submitted",
        priority="medium",
        action_url=None,  # Will be determined by role-based system
        related_id=leave_id,
        metadata={"leave_type": leave_type, "action": "submitted"}
    )

async def notify_leave_approved(userid, leave_type, leave_id=None):
    """Send real-time notification when leave is approved"""
    return await create_notification_with_websocket(
        userid=userid,
        title="Leave Request Approved ✅",
        message=f"Your {leave_type} leave request has been approved",
        notification_type="leave_approved",
        priority="high",
        action_url=None,  # Will be determined by role-based system
        related_id=leave_id,
        metadata={"leave_type": leave_type, "action": "approved"}
    )

async def notify_leave_rejected(userid, leave_type, leave_id=None, reason=None):
    """Send real-time notification when leave is rejected"""
    reason_text = f". Reason: {reason}" if reason else ""
    return await create_notification_with_websocket(
        userid=userid,
        title="Leave Request Rejected ❌",
        message=f"Your {leave_type} leave request has been rejected{reason_text}",
        notification_type="leave_rejected",
        priority="high",
        action_url=None,  # Will be determined by role-based system
        related_id=leave_id,
        metadata={"leave_type": leave_type, "action": "rejected", "reason": reason}
    )

async def notify_leave_recommended(userid, leave_type, approver_name, leave_id=None):
    """Send real-time notification when leave is recommended by manager or admin"""
    return await create_notification_with_websocket(
        userid=userid,
        title="Leave Request Recommended 👍",
        message=f"Your {leave_type} leave request has been recommended by {approver_name} and forwarded for HR review",
        notification_type="leave_recommended",
        priority="medium",
        action_url=None,  # Will be determined by role-based system
        related_id=leave_id,
        metadata={"leave_type": leave_type, "action": "recommended", "manager_name": approver_name}
    )

async def notify_wfh_submitted(userid, request_date=None, wfh_id=None):
    """Send real-time notification when WFH request is submitted"""
    date_text = f" for {request_date}" if request_date else ""
    return await create_notification_with_websocket(
        userid=userid,
        title="WFH Request Submitted",
        message=f"Your work from home request{date_text} has been submitted successfully and is pending approval",
        notification_type="wfh_submitted",
        priority="medium",
        action_url=None,  # Will be determined by role-based system
        related_id=wfh_id,
        metadata={"action": "submitted", "request_date": request_date}
    )

async def notify_wfh_approved(userid, request_date=None, wfh_id=None):
    """Send real-time notification when WFH request is approved"""
    date_text = f" for {request_date}" if request_date else ""
    return await create_notification_with_websocket(
        userid=userid,
        title="WFH Request Approved ✅",
        message=f"Your work from home request{date_text} has been approved",
        notification_type="wfh_approved",
        priority="high",
        action_url=None,  # Will be determined by role-based system
        related_id=wfh_id,
        metadata={"action": "approved", "request_date": request_date}
    )

async def notify_wfh_rejected(userid, request_date=None, wfh_id=None, reason=None):
    """Send real-time notification when WFH request is rejected"""
    date_text = f" for {request_date}" if request_date else ""
    reason_text = f". Reason: {reason}" if reason else ""
    return await create_notification_with_websocket(
        userid=userid,
        title="WFH Request Rejected ❌",
        message=f"Your work from home request{date_text} has been rejected{reason_text}",
        notification_type="wfh_rejected",
        priority="high",
        action_url=None,  # Will be determined by role-based system
        related_id=wfh_id,
        metadata={"action": "rejected", "request_date": request_date, "reason": reason}
    )

async def notify_manager_wfh_request(employee_name, employee_id, request_date_from, request_date_to, manager_id, wfh_id=None):
    """Send notification to manager when employee submits WFH request"""
    date_range = f"from {request_date_from} to {request_date_to}" if request_date_from != request_date_to else f"for {request_date_from}"
    return await create_notification_with_websocket(
        userid=manager_id,
        title="New WFH Request Pending Approval",
        message=f"{employee_name} has submitted a work from home request {date_range} requiring your approval",
        notification_type="wfh_manager_pending",
        priority="high",
        action_url=None,  # Will be determined by role-based system
        related_id=wfh_id,
        metadata={
            "action": "manager_approval_needed",
            "employee_name": employee_name,
            "employee_id": employee_id,
            "request_date_from": request_date_from,
            "request_date_to": request_date_to
        }
    )

async def get_user_manager_id(userid):
    """Get the manager ID for a given user"""
    try:
        user = Users.find_one({"_id": ObjectId(userid)})
        if not user:
            print(f"⚠️ User not found: {userid}")
            return None
            
        tl_name = user.get("TL")
        if not tl_name:
            print(f"⚠️ No TL assigned for user: {user.get('name', 'Unknown')}")
            return None
            
        # Find the manager by name
        manager = Users.find_one({"name": tl_name, "position": {"$in": ["Manager", "TL", "Team Lead"]}})
        if not manager:
            print(f"⚠️ Manager/TL not found: {tl_name}")
            return None
            
        return str(manager["_id"])
    except Exception as e:
        print(f"❌ Error finding user manager: {e}")
        return None

async def notify_manager_leave_request(employee_name, employee_id, leave_type, leave_date, manager_id, leave_id=None):
    """Send notification to manager when employee submits leave request"""
    return await create_notification_with_websocket(
        userid=manager_id,
        title="New Leave Request Pending Approval",
        message=f"{employee_name} has submitted a {leave_type} request for {leave_date} requiring your approval",
        notification_type="leave_manager_pending",
        priority="high",
        action_url=None,  # Will be determined by role-based system
        related_id=leave_id,
        metadata={
            "action": "manager_approval_needed",
            "employee_name": employee_name,
            "employee_id": employee_id,
            "leave_type": leave_type,
            "leave_date": leave_date
        }
    )

# Task Management and Deadline Notification System
async def check_and_notify_overdue_tasks():
    """Check for overdue tasks and notify users and managers"""
    try:
        current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
        current_date = current_time.strftime("%d-%m-%Y")
        
        print(f"🔍 Checking for overdue tasks at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Find all incomplete tasks
        incomplete_tasks = list(Tasks.find({"status": {"$ne": "Completed"}}))
        overdue_tasks = []
        
        for task in incomplete_tasks:
            due_date_str = task.get("due_date")
            if due_date_str:
                try:
                    # Parse due date (format: DD-MM-YYYY)
                    due_date = datetime.strptime(due_date_str, "%d-%m-%Y")
                    current_date_obj = datetime.strptime(current_date, "%d-%m-%Y")
                    
                    if due_date < current_date_obj:
                        overdue_tasks.append(task)
                except ValueError:
                    print(f"⚠️ Invalid date format for task {task.get('_id')}: {due_date_str}")
        
        print(f"📋 Found {len(overdue_tasks)} overdue tasks")
        
        # Process overdue tasks
        for task in overdue_tasks:
            await handle_overdue_task(task)
        
        return len(overdue_tasks)
    except Exception as e:
        print(f"Error checking overdue tasks: {e}")
        return 0

async def handle_overdue_task(task):
    """Handle a single overdue task - notify user and manager"""
    try:
        task_id = str(task.get("_id"))
        userid = task.get("userid")
        task_title = task.get("task")
        due_date = task.get("due_date")
        tl_name = task.get("TL")
        
        # Get user information
        user = Users.find_one({"_id": ObjectId(userid)}) if ObjectId.is_valid(userid) else None
        user_name = user.get("name", "User") if user else "User"
        
        # Check if we already notified about this overdue task today
        today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
        existing_notification = Notifications.find_one({
            "userid": userid,
            "type": "task_overdue",
            "related_id": task_id,
            "metadata.notification_date": today
        })
        
        if existing_notification:
            print(f"⏭️ Already notified user {userid} about overdue task {task_id} today")
        else:
            # Notify user about overdue task
            await create_overdue_task_notification(userid, task_title, due_date, task_id)
        
        # Notify manager/TL about overdue task
        await notify_manager_about_overdue_task(userid, user_name, task_title, due_date, tl_name, task_id)
        
    except Exception as e:
        print(f"Error handling overdue task: {e}")

async def create_overdue_task_notification(userid, task_title, due_date, task_id):
    """Create notification for user about overdue task"""
    try:
        user = Users.find_one({"_id": ObjectId(userid)}) if ObjectId.is_valid(userid) else None
        user_name = user.get("name", "User") if user else "User"
        
        title = "Task Overdue"
        message = f"Hi {user_name}, your task '{task_title}' was due on {due_date} and is now overdue. Please complete it as soon as possible."
        
        notification_id = create_notification(
            userid=userid,
            title=title,
            message=message,
            notification_type="task_overdue",
            priority="high",
            action_url="/User/task",
            related_id=task_id,
            metadata={
                "task_title": task_title,
                "due_date": due_date,
                "notification_date": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
            }
        )
        
        if notification_id:
            # Send real-time WebSocket notification
            from websocket_manager import notification_manager
            
            notification_data = {
                "_id": notification_id,
                "userid": userid,
                "title": title,
                "message": message,
                "type": "task_overdue",
                "priority": "high",
                "action_url": "/User/task",
                "related_id": task_id,
                "is_read": False,
                "created_at": get_current_timestamp_iso()
            }
            
            await notification_manager.send_personal_notification(userid, notification_data)
            
            # Update unread count
            unread_count = get_unread_notification_count(userid)
            await notification_manager.send_unread_count_update(userid, unread_count)
            
            print(f"🚨 Overdue task notification sent to {user_name} for task: {task_title}")
        
        return notification_id
    except Exception as e:
        print(f"Error creating overdue task notification: {e}")
        return None

async def notify_manager_about_overdue_task(userid, user_name, task_title, due_date, tl_name, task_id):
    """Notify manager/TL about employee's overdue task"""
    try:
        # Find manager/TL by name first, then by position
        manager = None
        if tl_name:
            manager = Users.find_one({"name": tl_name})
        
        # If no specific TL found, notify all managers
        if not manager:
            managers = list(Users.find({"position": "Manager"}))
        else:
            managers = [manager]
        
        for manager in managers:
            manager_id = str(manager["_id"])
            manager_name = manager.get("name", "Manager")
            
            # Check if already notified this manager today
            today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
            existing_notification = Notifications.find_one({
                "userid": manager_id,
                "type": "employee_task_overdue",
                "related_id": task_id,
                "metadata.notification_date": today
            })
            
            if existing_notification:
                continue
            
            title = "Employee Task Overdue"
            message = f"Hi {manager_name}, {user_name}'s task '{task_title}' was due on {due_date} and is now overdue."
            
            notification_id = create_notification(
                userid=manager_id,
                title=title,
                message=message,
                notification_type="employee_task_overdue",
                priority="high",
                action_url="/Manager/tasks",
                related_id=task_id,
                metadata={
                    "employee_name": user_name,
                    "employee_id": userid,
                    "task_title": task_title,
                    "due_date": due_date,
                    "notification_date": today
                }
            )
            
            if notification_id:
                # Send real-time WebSocket notification
                from websocket_manager import notification_manager
                
                notification_data = {
                    "_id": notification_id,
                    "userid": manager_id,
                    "title": title,
                    "message": message,
                    "type": "employee_task_overdue",
                    "priority": "high",
                    "action_url": "/Manager/tasks",
                    "related_id": task_id,
                    "is_read": False,
                    "created_at": get_current_timestamp_iso()
                }
                
                await notification_manager.send_personal_notification(manager_id, notification_data)
                
                print(f"📢 Manager {manager_name} notified about {user_name}'s overdue task: {task_title}")
        
    except Exception as e:
        print(f"Error notifying manager about overdue task: {e}")

async def check_upcoming_deadlines_enhanced():
    """Enhanced deadline checking with multiple reminder periods"""
    try:
        current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
        reminder_periods = [0, 1, 3, 7]  # Days before due date to send reminders
        
        total_notifications = 0
        
        for days_ahead in reminder_periods:
            target_date = (current_time + timedelta(days=days_ahead)).strftime("%d-%m-%Y")
            
            # Find tasks due on the target date that are not completed
            upcoming_tasks = list(Tasks.find({
                "due_date": target_date,
                "status": {"$ne": "Completed"}
            }))
            
            print(f"📅 Found {len(upcoming_tasks)} tasks due in {days_ahead} days ({target_date})")
            
            for task in upcoming_tasks:
                await create_task_due_soon_notification(
                    userid=task.get("userid"),
                    task_title=task.get("task"),
                    task_id=str(task.get("_id")),
                    days_remaining=days_ahead
                )
                total_notifications += 1
        
        return total_notifications
    except Exception as e:
        print(f"Error checking enhanced upcoming deadlines: {e}")
        return 0

async def check_upcoming_deadlines():
    """Check for tasks due soon and notify users"""
    try:
        current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
        tomorrow = (current_time + timedelta(days=1)).strftime("%d-%m-%Y")
        
        # Find tasks due tomorrow that are not completed
        upcoming_tasks = list(Tasks.find({
            "due_date": tomorrow,
            "status": {"$ne": "Completed"}
        }))
        
        print(f"📅 Found {len(upcoming_tasks)} tasks due tomorrow")
        
        for task in upcoming_tasks:
            await create_deadline_reminder_notification(task)
        
        return len(upcoming_tasks)
    except Exception as e:
        print(f"Error checking upcoming deadlines: {e}")
        return 0

async def create_deadline_reminder_notification(task):
    """Create reminder notification for tasks due soon"""
    try:
        userid = task.get("userid")
        task_title = task.get("task")
        due_date = task.get("due_date")
        task_id = str(task.get("_id"))
        
        # Check if already reminded today
        today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
        existing_notification = Notifications.find_one({
            "userid": userid,
            "type": "task_deadline_reminder",
            "related_id": task_id,
            "metadata.reminder_date": today
        })
        
        if existing_notification:
            return
        
        user = Users.find_one({"_id": ObjectId(userid)}) if ObjectId.is_valid(userid) else None
        user_name = user.get("name", "User") if user else "User"
        
        title = "Task Deadline Reminder"
        message = f"Hi {user_name}, reminder: your task '{task_title}' is due tomorrow ({due_date}). Please ensure timely completion."
        
        notification_id = create_notification(
            userid=userid,
            title=title,
            message=message,
            notification_type="task_deadline_reminder",
            priority="medium",
            action_url="/User/task",
            related_id=task_id,
            metadata={
                "task_title": task_title,
                "due_date": due_date,
                "reminder_date": today
            }
        )
        
        if notification_id:
            # Send real-time WebSocket notification
            from websocket_manager import notification_manager
            
            notification_data = {
                "_id": notification_id,
                "userid": userid,
                "title": title,
                "message": message,
                "type": "task_deadline_reminder",
                "priority": "medium",
                "action_url": "/User/task",
                "related_id": task_id,
                "is_read": False,
                "created_at": get_current_timestamp_iso()
            }
            
            await notification_manager.send_personal_notification(userid, notification_data)
            
            print(f"⏰ Deadline reminder sent to {user_name} for task: {task_title}")
        
        return notification_id
    except Exception as e:
        print(f"Error creating deadline reminder: {e}")
        return None

# Enhanced Task Notification Functions
async def create_task_created_notification(userid, task_title, creator_name, task_id=None, due_date=None, priority="medium"):
    """Create notification when a new task is created by user themselves"""
    try:
        user = Users.find_one({"_id": ObjectId(userid)}) if ObjectId.is_valid(userid) else None
        user_name = user.get("name", "User") if user else "User"
        
        title = "Task Created"
        message = f"Hi {user_name}, you have successfully created a new task: '{task_title}'"
        if due_date:
            message += f". Due date: {due_date}"
        
        notification_id = create_notification(
            userid=userid,
            title=title,
            message=message,
            notification_type="task_created",
            priority=priority,
            action_url="/User/task",
            related_id=task_id,
            metadata={
                "task_title": task_title,
                "action": "Created",
                "creator_name": creator_name,
                "due_date": due_date
            }
        )
        
        if notification_id:
            from websocket_manager import notification_manager
            
            notification_data = {
                "_id": notification_id,
                "userid": userid,
                "title": title,
                "message": message,
                "type": "task_created",
                "priority": priority,
                "action_url": "/User/task",
                "related_id": task_id,
                "is_read": False,
                "created_at": get_current_timestamp_iso()
            }
            
            await notification_manager.send_personal_notification(userid, notification_data)
            print(f"✅ Task creation notification sent to {user_name}: {task_title}")
        
        return notification_id
    except Exception as e:
        print(f"Error creating task creation notification: {e}")
        return None

async def create_task_updated_notification(userid, task_title, updater_name, changes, task_id=None, priority="medium"):
    """Create notification when a task is updated"""
    try:
        user = Users.find_one({"_id": ObjectId(userid)}) if ObjectId.is_valid(userid) else None
        user_name = user.get("name", "User") if user else "User"
        
        title = "Task Updated"
        message = f"Hi {user_name}, your task '{task_title}' has been updated"
        if updater_name and updater_name != user_name:
            message += f" by {updater_name}"
        
        # Add specific changes to message
        if changes:
            change_list = []
            if changes.get("title_changed"):
                change_list.append("title")
            if changes.get("due_date_changed"):
                change_list.append(f"due date to {changes.get('new_due_date')}")
            if changes.get("status_changed"):
                change_list.append(f"status to {changes.get('new_status')}")
            
            if change_list:
                message += f". Changes: {', '.join(change_list)}"
        
        notification_id = create_notification(
            userid=userid,
            title=title,
            message=message,
            notification_type="task_updated",
            priority=priority,
            action_url="/User/task",
            related_id=task_id,
            metadata={
                "task_title": task_title,
                "action": "Updated",
                "updater_name": updater_name,
                "changes": changes
            }
        )
        
        if notification_id:
            from websocket_manager import notification_manager
            
            notification_data = {
                "_id": notification_id,
                "userid": userid,
                "title": title,
                "message": message,
                "type": "task_updated",
                "priority": priority,
                "action_url": "/User/task",
                "related_id": task_id,
                "is_read": False,
                "created_at": get_current_timestamp_iso()
            }
            
            await notification_manager.send_personal_notification(userid, notification_data)
            print(f"✅ Task update notification sent to {user_name}: {task_title}")
        
        return notification_id
    except Exception as e:
        print(f"Error creating task update notification: {e}")
        return None

async def create_task_manager_assigned_notification(userid, task_title, manager_name, task_id=None, due_date=None, priority="high"):
    """Create specific notification when a manager assigns a task"""
    try:
        user = Users.find_one({"_id": ObjectId(userid)}) if ObjectId.is_valid(userid) else None
        user_name = user.get("name", "User") if user else "User"
        
        title = "Task Assigned by Manager"
        message = f"Hi {user_name}, your manager {manager_name} has assigned you a new task: '{task_title}'"
        if due_date:
            message += f". Due date: {due_date}"
        
        notification_id = create_notification(
            userid=userid,
            title=title,
            message=message,
            notification_type="task_manager_assigned",
            priority=priority,
            action_url="/User/task",
            related_id=task_id,
            metadata={
                "task_title": task_title,
                "action": "Assigned by Manager",
                "manager_name": manager_name,
                "due_date": due_date
            }
        )
        
        if notification_id:
            from websocket_manager import notification_manager
            
            notification_data = {
                "_id": notification_id,
                "userid": userid,
                "title": title,
                "message": message,
                "type": "task_manager_assigned",
                "priority": priority,
                "action_url": "/User/task",
                "related_id": task_id,
                "is_read": False,
                "created_at": get_current_timestamp_iso()
            }
            
            await notification_manager.send_personal_notification(userid, notification_data)
            print(f"🎯 Manager assignment notification sent to {user_name} from {manager_name}: {task_title}")
        
        return notification_id
    except Exception as e:
        print(f"Error creating manager assignment notification: {e}")
        return None

async def create_task_due_soon_notification(userid, task_title, task_id, days_remaining, priority="medium"):
    """Create notification for tasks due soon (configurable days)"""
    try:
        user = Users.find_one({"_id": ObjectId(userid)}) if ObjectId.is_valid(userid) else None
        user_name = user.get("name", "User") if user else "User"
        
        if days_remaining == 1:
            title = "Task Due Tomorrow"
            message = f"Hi {user_name}, reminder: your task '{task_title}' is due tomorrow. Please ensure timely completion."
        elif days_remaining == 0:
            title = "Task Due Today"
            message = f"Hi {user_name}, urgent: your task '{task_title}' is due today. Please complete it immediately."
            priority = "high"
        else:
            title = f"Task Due in {days_remaining} Days"
            message = f"Hi {user_name}, reminder: your task '{task_title}' is due in {days_remaining} days."
        
        # Check if already reminded today for this specific timeframe
        today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
        existing_notification = Notifications.find_one({
            "userid": userid,
            "type": "task_due_soon",
            "related_id": task_id,
            "metadata.days_remaining": days_remaining,
            "metadata.reminder_date": today
        })
        
        if existing_notification:
            return str(existing_notification["_id"])
        
        notification_id = create_notification(
            userid=userid,
            title=title,
            message=message,
            notification_type="task_due_soon",
            priority=priority,
            action_url="/User/task",
            related_id=task_id,
            metadata={
                "task_title": task_title,
                "days_remaining": days_remaining,
                "reminder_date": today
            }
        )
        
        if notification_id:
            from websocket_manager import notification_manager
            
            notification_data = {
                "_id": notification_id,
                "userid": userid,
                "title": title,
                "message": message,
                "type": "task_due_soon",
                "priority": priority,
                "action_url": "/User/task",
                "related_id": task_id,
                "is_read": False,
                "created_at": get_current_timestamp_iso()
            }
            
            await notification_manager.send_personal_notification(userid, notification_data)
            print(f"⏰ Due soon notification sent to {user_name}: {task_title} ({days_remaining} days)")
        
        return notification_id
    except Exception as e:
        print(f"Error creating due soon notification: {e}")
        return None

async def notify_task_completion(userid, task_title, task_id, tl_name):
    """Notify manager/TL when employee completes a task"""
    try:
        # Get user information
        user = Users.find_one({"_id": ObjectId(userid)}) if ObjectId.is_valid(userid) else None
        user_name = user.get("name", "User") if user else "User"
        
        # Find manager/TL
        manager = None
        if tl_name:
            manager = Users.find_one({"name": tl_name})
        
        # If no specific TL found, notify all managers
        if not manager:
            managers = list(Users.find({"position": "Manager"}))
        else:
            managers = [manager]
        
        for manager in managers:
            manager_id = str(manager["_id"])
            manager_name = manager.get("name", "Manager")
            
            title = "Task Completed"
            message = f"Hi {manager_name}, {user_name} has completed the task: '{task_title}'"
            
            notification_id = create_notification(
                userid=manager_id,
                title=title,
                message=message,
                notification_type="task_completed",
                priority="medium",
                action_url="/Manager/tasks",
                related_id=task_id,
                metadata={
                    "employee_name": user_name,
                    "employee_id": userid,
                    "task_title": task_title,
                    "completed_date": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
                }
            )
            
            if notification_id:
                # Send real-time WebSocket notification
                from websocket_manager import notification_manager
                
                notification_data = {
                    "_id": notification_id,
                    "userid": manager_id,
                    "title": title,
                    "message": message,
                    "type": "task_completed",
                    "priority": "medium",
                    "action_url": "/Manager/tasks",
                    "related_id": task_id,
                    "is_read": False,
                    "created_at": get_current_timestamp_iso()
                }
                
                await notification_manager.send_personal_notification(manager_id, notification_data)
                
                print(f"✅ Manager {manager_name} notified about {user_name}'s task completion: {task_title}")
        
    except Exception as e:
        print(f"Error notifying task completion: {e}")

# Scheduler setup for automatic task checking
def setup_task_scheduler():
    """Setup background scheduler for task deadline checking"""
    try:
        scheduler = BackgroundScheduler()
        
        # Check for overdue tasks every day at 9 AM
        scheduler.add_job(
            func=lambda: asyncio.create_task(check_and_notify_overdue_tasks()),
            trigger="cron",
            hour=9,
            minute=0,
            id="check_overdue_tasks",
            replace_existing=True
        )
        
        # Enhanced deadline checking (multiple reminder periods) every day at 6 PM
        scheduler.add_job(
            func=lambda: asyncio.create_task(check_upcoming_deadlines_enhanced()),
            trigger="cron",
            hour=18,
            minute=0,
            id="check_upcoming_deadlines_enhanced", 
            replace_existing=True
        )
        
        # Also check every 4 hours during work hours for overdue tasks
        scheduler.add_job(
            func=lambda: asyncio.create_task(check_and_notify_overdue_tasks()),
            trigger="cron",
            hour="9,13,17",
            minute=0,
            id="check_overdue_tasks_frequent",
            replace_existing=True
        )
        
        # Morning reminder check (8 AM) for tasks due today
        scheduler.add_job(
            func=lambda: asyncio.create_task(check_upcoming_deadlines_enhanced()),
            trigger="cron",
            hour=8,
            minute=0,
            id="morning_deadline_check",
            replace_existing=True
        )
        
        scheduler.start()
        print("✅ Enhanced task deadline scheduler started successfully")
        return scheduler
    except Exception as e:
        print(f"Error setting up task scheduler: {e}")
        return None

# Import asyncio for scheduler
import asyncio

# Enhanced Manager Leave Notification Functions
async def get_admin_user_ids():
    """Get all admin user IDs"""
    try:
        # Get from admin collection first
        admin_users = list(admin.find({}, {"_id": 1}))
        admin_ids = [str(admin_user["_id"]) for admin_user in admin_users]
        
        # Also get users with admin-like positions from Users collection
        admin_positions = list(Users.find({"position": {"$in": ["Admin", "Administrator", "CEO", "Director"]}}, {"_id": 1}))
        admin_position_ids = [str(user["_id"]) for user in admin_positions]
        
        # Combine both lists and remove duplicates
        all_admin_ids = list(set(admin_ids + admin_position_ids))
        return all_admin_ids
    except Exception as e:
        print(f"❌ Error getting admin user IDs: {e}")
        return []

async def get_hr_user_ids():
    """Get all HR user IDs"""
    try:
        hr_users = list(Users.find({"$or": [
            {"position": "HR"},
            {"department": "HR"},
            {"position": {"$regex": "HR", "$options": "i"}},
            {"department": {"$regex": "HR", "$options": "i"}}
        ]}, {"_id": 1}))
        return [str(user["_id"]) for user in hr_users]
    except Exception as e:
        print(f"❌ Error getting HR user IDs: {e}")
        return []

async def get_user_position(userid):
    """Get user position from database"""
    try:
        user = Users.find_one({"_id": ObjectId(userid)})
        if user:
            return user.get("position", "")
        return ""
    except Exception as e:
        print(f"❌ Error getting user position: {e}")
        return ""

async def notify_admin_manager_leave_request(manager_name, manager_id, leave_type, leave_date, leave_id=None):
    """Send notification to admin when manager submits leave request"""
    try:
        admin_ids = await get_admin_user_ids()
        
        for admin_id in admin_ids:
            await create_notification_with_websocket(
                userid=admin_id,
                title="Manager Leave Request Pending Admin Review",
                message=f"Manager {manager_name} has submitted a {leave_type} request for {leave_date} requiring admin approval",
                notification_type="leave_admin_pending",
                priority="high",
                action_url=None,  # Will be determined by role-based system
                related_id=leave_id,
                metadata={
                    "action": "admin_approval_needed",
                    "manager_name": manager_name,
                    "manager_id": manager_id,
                    "leave_type": leave_type,
                    "leave_date": leave_date
                }
            )
        print(f"✅ Admin notifications sent for manager leave request: {manager_name}")
        return True
    except Exception as e:
        print(f"❌ Error sending admin notification for manager leave: {e}")
        return False

async def notify_admin_manager_wfh_request(manager_name, manager_id, request_date_from, request_date_to, wfh_id=None):
    """Send notification to admin when manager submits WFH request"""
    try:
        admin_ids = await get_admin_user_ids()
        
        date_range = f"from {request_date_from} to {request_date_to}" if request_date_from != request_date_to else f"for {request_date_from}"
        
        for admin_id in admin_ids:
            await create_notification_with_websocket(
                userid=admin_id,
                title="Manager WFH Request Pending Admin Review",
                message=f"Manager {manager_name} has submitted a work from home request {date_range} requiring admin approval",
                notification_type="wfh_admin_pending",
                priority="high",
                action_url=None,  # Will be determined by role-based system
                related_id=wfh_id,
                metadata={
                    "action": "admin_approval_needed",
                    "manager_name": manager_name,
                    "manager_id": manager_id,
                    "request_date_from": request_date_from,
                    "request_date_to": request_date_to
                }
            )
        print(f"✅ Admin notifications sent for manager WFH request: {manager_name}")
        return True
    except Exception as e:
        print(f"❌ Error sending admin notification for manager WFH: {e}")
        return False

async def notify_hr_recommended_leave(employee_name, employee_id, leave_type, leave_date, recommended_by, leave_id=None):
    """Send notification to HR when a leave is recommended for their review"""
    try:
        hr_ids = await get_hr_user_ids()
        
        for hr_id in hr_ids:
            await create_notification_with_websocket(
                userid=hr_id,
                title="Leave Request Recommended - HR Review Requested",
                message=f"{employee_name}'s {leave_type} request for {leave_date} has been recommended by {recommended_by} for your review",
                notification_type="leave_hr_final_approval",
                priority="high",
                action_url=None,  # Will be determined by role-based system
                related_id=leave_id,
                metadata={
                    "action": "hr_review_requested",
                    "employee_name": employee_name,
                    "employee_id": employee_id,
                    "leave_type": leave_type,
                    "leave_date": leave_date,
                    "recommended_by": recommended_by
                }
            )
        print(f"✅ HR notifications sent for recommended leave: {employee_name}")
        return True
    except Exception as e:
        print(f"❌ Error sending HR notification for recommended leave: {e}")
        return False

async def notify_hr_recommended_wfh(employee_name, employee_id, request_date_from, request_date_to, recommended_by, wfh_id=None):
    """Send notification to HR when a WFH request is recommended for their review"""
    try:
        hr_ids = await get_hr_user_ids()
        
        date_range = f"from {request_date_from} to {request_date_to}" if request_date_from != request_date_to else f"for {request_date_from}"
        
        for hr_id in hr_ids:
            await create_notification_with_websocket(
                userid=hr_id,
                title="WFH Request Recommended - HR Review Requested",
                message=f"{employee_name}'s work from home request {date_range} has been recommended by {recommended_by} for your review",
                notification_type="wfh_hr_final_approval",
                priority="high",
                action_url=None,  # Will be determined by role-based system
                related_id=wfh_id,
                metadata={
                    "action": "hr_review_requested",
                    "employee_name": employee_name,
                    "employee_id": employee_id,
                    "request_date_from": request_date_from,
                    "request_date_to": request_date_to,
                    "recommended_by": recommended_by
                }
            )
        print(f"✅ HR notifications sent for recommended WFH: {employee_name}")
        return True
    except Exception as e:
        print(f"❌ Error sending HR notification for recommended WFH: {e}")
        return False

async def notify_hr_pending_leaves():
    """Notify HR about all pending leave requests that need their review"""
    try:
        # Get all leaves with status "Recommend" that are pending HR approval
        pending_leaves = list(Leave.find({"status": "Recommend"}))
        
        if not pending_leaves:
            print("No pending leaves for HR notification")
            return {"message": "No pending leaves found"}
        
        hr_ids = await get_hr_user_ids()
        if not hr_ids:
            print("No HR users found for notification")
            return {"message": "No HR users found"}
        
        notification_count = 0
        for leave in pending_leaves:
            employee_name = leave.get("employeeName", "Unknown Employee")
            leave_type = leave.get("leaveType", "Leave")
            leave_date = leave.get("selectedDate")
            leave_date_str = leave_date.strftime("%d-%m-%Y") if leave_date else "Unknown Date"
            leave_id = str(leave.get("_id"))
            
            for hr_id in hr_ids:
                try:
                    await create_notification_with_websocket(
                        userid=hr_id,
                        title="Pending Leave Review Required",
                        message=f"{employee_name}'s {leave_type} request for {leave_date_str} is waiting for your review",
                        notification_type="leave_hr_pending",
                        priority="high",
                        action_url=None,  # Will be determined by role-based system
                        related_id=leave_id,
                        metadata={
                            "action": "hr_approval_needed",
                            "employee_name": employee_name,
                            "employee_id": leave.get("userid"),
                            "leave_type": leave_type,
                            "leave_date": leave_date_str,
                            "status": "pending_hr_approval"
                        }
                    )
                    notification_count += 1
                except Exception as e:
                    print(f"Error sending notification to HR {hr_id}: {e}")
        
        print(f"✅ Sent {notification_count} HR notifications for pending leaves")
        return {"message": f"Sent {notification_count} notifications to HR", "pending_leaves": len(pending_leaves)}
        
    except Exception as e:
        print(f"❌ Error in notify_hr_pending_leaves: {e}")
        return {"error": str(e)}

async def auto_notify_hr_on_recommendation():
    """Automatically notify HR when a leave is recommended (used as callback)"""
    try:
        result = await notify_hr_pending_leaves()
        print(f"✅ Auto HR notification result: {result}")
        return result
    except Exception as e:
        print(f"❌ Error in auto HR notification: {e}")
        return {"error": str(e)}

async def notify_hr_pending_wfh():
    """Notify HR about all pending WFH requests that need their review"""
    try:
        # Get all WFH requests with status "Recommend" that are pending HR approval
        pending_wfh = list(RemoteWork.find({"Recommendation": "Recommend", "status": {"$exists": False}}))
        
        if not pending_wfh:
            print("No pending WFH requests for HR notification")
            return {"message": "No pending WFH requests found"}
        
        hr_ids = await get_hr_user_ids()
        if not hr_ids:
            print("No HR users found for notification")
            return {"message": "No HR users found"}
        
        notification_count = 0
        for wfh in pending_wfh:
            employee_name = wfh.get("employeeName", "Unknown Employee")
            from_date = wfh.get("fromDate")
            to_date = wfh.get("toDate")
            from_date_str = from_date.strftime("%d-%m-%Y") if from_date else "Unknown Date"
            to_date_str = to_date.strftime("%d-%m-%Y") if to_date else "Unknown Date"
            date_range = f"from {from_date_str} to {to_date_str}" if from_date_str != to_date_str else f"for {from_date_str}"
            wfh_id = str(wfh.get("_id"))
            
            for hr_id in hr_ids:
                try:
                    await create_notification_with_websocket(
                        userid=hr_id,
                        title="Pending WFH Review Required",
                        message=f"{employee_name}'s work from home request {date_range} is waiting for your review",
                        notification_type="wfh_hr_pending",
                        priority="high",
                        action_url=None,  # Will be determined by role-based system
                        related_id=wfh_id,
                        metadata={
                            "action": "hr_approval_needed",
                            "employee_name": employee_name,
                            "employee_id": wfh.get("userid"),
                            "request_date_from": from_date_str,
                            "request_date_to": to_date_str,
                            "status": "pending_hr_approval"
                        }
                    )
                    notification_count += 1
                except Exception as e:
                    print(f"Error sending notification to HR {hr_id}: {e}")
        
        print(f"✅ Sent {notification_count} HR notifications for pending WFH requests")
        return {"message": f"Sent {notification_count} notifications to HR", "pending_wfh": len(pending_wfh)}
        
    except Exception as e:
        print(f"❌ Error in notify_hr_pending_wfh: {e}")
        return {"error": str(e)}

async def auto_notify_hr_on_wfh_recommendation():
    """Automatically notify HR when a WFH request is recommended (used as callback)"""
    try:
        result = await notify_hr_pending_wfh()
        print(f"✅ Auto HR WFH notification result: {result}")
        return result
    except Exception as e:
        print(f"❌ Error in auto HR WFH notification: {e}")
        return {"error": str(e)}

async def notify_admin_pending_leaves():
    """Notify admin about all pending manager leave requests that need admin approval"""
    try:
        # Get all manager user IDs first
        manager_users = list(Users.find({"position": "Manager"}, {"_id": 1}))
        manager_ids = [str(manager["_id"]) for manager in manager_users]
        
        if not manager_ids:
            print("No managers found")
            return {"message": "No managers found"}
        
        # Get all leaves from managers that don't have Recommendation or status fields (i.e., pending admin approval)
        pending_leaves = list(Leave.find({
            "userid": {"$in": manager_ids},
            "Recommendation": {"$exists": False},
            "status": {"$exists": False}
        }))
        
        if not pending_leaves:
            print("No pending manager leaves for admin notification")
            return {"message": "No pending manager leaves found"}
        
        admin_ids = await get_admin_user_ids()
        if not admin_ids:
            print("No admin users found for notification")
            return {"message": "No admin users found"}
        
        notification_count = 0
        for leave in pending_leaves:
            manager_name = leave.get("employeeName", "Unknown Manager")
            leave_type = leave.get("leaveType", "Leave")
            leave_date = leave.get("selectedDate")
            leave_date_str = leave_date.strftime("%d-%m-%Y") if leave_date else "Unknown Date"
            leave_id = str(leave.get("_id"))
            manager_id = leave.get("userid")
            
            for admin_id in admin_ids:
                try:
                    await create_notification_with_websocket(
                        userid=admin_id,
                        title="Manager Leave Request Pending Approval",
                        message=f"Manager {manager_name}'s {leave_type} request for {leave_date_str} is waiting for your approval",
                        notification_type="leave_admin_pending",
                        priority="high",
                        action_url="/Admin/manager_leave_approval",
                        related_id=leave_id,
                        metadata={
                            "action": "admin_approval_needed",
                            "manager_name": manager_name,
                            "manager_id": manager_id,
                            "leave_type": leave_type,
                            "leave_date": leave_date_str,
                            "status": "pending_admin_approval"
                        }
                    )
                    notification_count += 1
                except Exception as e:
                    print(f"Error sending notification to admin {admin_id}: {e}")
        
        print(f"✅ Sent {notification_count} admin notifications for pending manager leaves")
        return {"message": f"Sent {notification_count} notifications to admin", "pending_leaves": len(pending_leaves)}
        
    except Exception as e:
        print(f"❌ Error in notify_admin_pending_leaves: {e}")
        return {"error": str(e)}

async def auto_notify_admin_on_manager_request():
    """Automatically notify admin when a manager submits leave (used as callback)"""
    try:
        result = await notify_admin_pending_leaves()
        print(f"✅ Auto admin notification result: {result}")
        return result
    except Exception as e:
        print(f"❌ Error in auto admin notification: {e}")
        return {"error": str(e)}

async def notify_admin_pending_wfh():
    """Notify admin about all pending manager WFH requests that need admin approval"""
    try:
        # Get all manager WFH requests with status "Pending" that are waiting for admin approval
        managers = list(Users.find({"position": "Manager"}))
        manager_ids = [str(manager["_id"]) for manager in managers]
        
        pending_wfh = list(RemoteWork.find({"userid": {"$in": manager_ids}, "status": "Pending"}))
        
        if not pending_wfh:
            print("No pending manager WFH requests for admin notification")
            return {"message": "No pending manager WFH requests found"}
        
        admin_ids = await get_admin_user_ids()
        if not admin_ids:
            print("No admin users found for notification")
            return {"message": "No admin users found"}
        
        notification_count = 0
        for wfh in pending_wfh:
            manager_name = wfh.get("employeeName", "Unknown Manager")
            from_date = wfh.get("fromDate")
            to_date = wfh.get("toDate")
            from_date_str = from_date.strftime("%d-%m-%Y") if from_date else "Unknown Date"
            to_date_str = to_date.strftime("%d-%m-%Y") if to_date else "Unknown Date"
            date_range = f"from {from_date_str} to {to_date_str}" if from_date_str != to_date_str else f"for {from_date_str}"
            wfh_id = str(wfh.get("_id"))
            manager_id = wfh.get("userid")
            
            for admin_id in admin_ids:
                try:
                    await create_notification_with_websocket(
                        userid=admin_id,
                        title="Manager WFH Request Pending Approval",
                        message=f"Manager {manager_name}'s work from home request {date_range} is waiting for your approval",
                        notification_type="wfh_admin_pending",
                        priority="high",
                        action_url="/Admin/wfh_approval",
                        related_id=wfh_id,
                        metadata={
                            "action": "admin_approval_needed",
                            "manager_name": manager_name,
                            "manager_id": manager_id,
                            "request_date_from": from_date_str,
                            "request_date_to": to_date_str
                        }
                    )
                    notification_count += 1
                except Exception as e:
                    print(f"❌ Error sending notification to admin {admin_id}: {e}")
        
        print(f"✅ Sent {notification_count} admin notifications for pending manager WFH requests")
        return {"message": f"Sent {notification_count} notifications", "pending_count": len(pending_wfh)}
        
    except Exception as e:
        print(f"❌ Error in notify_admin_pending_wfh: {e}")
        return {"error": str(e)}

async def auto_notify_admin_on_manager_wfh_request():
    """Automatically notify admin when a manager submits WFH request (used as callback)"""
    try:
        result = await notify_admin_pending_wfh()
        print(f"✅ Auto admin WFH notification result: {result}")
        return result
    except Exception as e:
        print(f"❌ Error in auto admin WFH notification: {e}")
        return False
