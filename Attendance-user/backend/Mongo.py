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
from typing import List, Dict


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
holidays_collection = db["holidays"]
AttendanceStats = db["attendance_stats"]  # For caching calculated stats
WorkingDays = db["working_days"]  # For storing yearly working days

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
        return signJWT(email)

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
            a=signJWT(email)
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
        return signJWT(email)
    
def admin_signin(checkuser, password, email):
    if (checkuser):
        checkpass=CheckPassword(password,checkuser.get('password'))
        if (checkpass):
            a=signJWT(email)
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
        a = signJWT(client_name)
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
        jwt_token = signJWT(client_name)
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
        a = signJWT(client_name)
        b = checkuser
        checkuser = cleanid(checkuser)
        checkuser.update(a)
        checkuser.update({"isloggedin":True, "isadmin":True})
        return checkuser
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
# Admin Google Signin
def manager_Gsignin(checkuser, client_name):
    
    if (checkuser):
        a = signJWT(client_name)
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

        # Update the clock-out time in the database
        Clock.find_one_and_update(
            {'_id': record['_id']},  # Use the record's unique ID for update
            {'$set': {
                'clockout': clockout_time.strftime("%I:%M:%S %p"),
                'total_hours_worked': f'{int(total_hours_worked)} hours {int(total_minutes_worked)} minutes',
                'remark': remark
            }}
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

        # Update the clock-out time in the database
        Clock.find_one_and_update(
            {'date': str(today), 'name': name},
            {'$set': {
                'clockout': clockout_time.strftime("%I:%M:%S %p"),
                'total_hours_worked': f'{int(total_hours_worked)} hours {int(total_minutes_worked)} minutes',
                'remark': remark
            }}
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
        log_message(f"Conflict: {userid} already has {existing_single_leave['leaveType']} on {selected_date_dt}.")
        return f"Leave request conflicts with an existing {existing_single_leave['leaveType']} on {selected_date_dt}."

    # Check for Multi-Day Leave Conflict
    existing_wfh = RemoteWork.find_one(wfh)
    if existing_wfh:
        log_message(f"Conflict: {userid} already has remote work from {existing_wfh['fromDate']} to {existing_wfh.get('toDate', selected_date_dt)}.")
        return f"Leave request conflicts with an existing remote work from {existing_wfh['fromDate']} to {existing_wfh.get('toDate', selected_date_dt)}."
    
    existing_lop = Leave.find_one(lop)
    if existing_lop:
        log_message(f"Conflict: {userid} already has {existing_lop['leaveType']} from {existing_lop['selectedDate']} to {existing_lop.get('ToDate', selected_date_dt)}.")
        return f"Leave request conflicts with an existing {existing_lop['leaveType']} from {existing_lop['selectedDate']} to {existing_lop.get('ToDate', selected_date_dt)}."

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
    if check_leave_conflict(userid, selected_date_dt):
        return "Leave request conflicts with an existing leave or remote work."

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

    user_info = Users.find_one({"_id": ObjectId(userid)}, {"position": 1})
    user_position = user_info.get("position", "User") if user_info else "User"

    employee_id = get_employee_id_from_db(employee_name)
    new_leave = {
        "userid": userid,
        "Employee_ID": employee_id,
        "employeeName": employee_name,
        "time": time,
        "position": user_position,
        "leaveType": leave_type,
        "selectedDate": selected_date_dt,  # Stored as `datetime` object
        "requestDate": request_date_dt,  # Stored as `datetime` object
        "reason": reason,
    }

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
    # Convert to datetime objects
    selected_date_dt = datetime.strptime(selected_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
    request_date_dt = datetime.strptime(request_date.strftime("%d-%m-%Y"), "%d-%m-%Y")

    # Check if the request date is a Sunday
    if request_date_dt.weekday() == 6:
        return "Request date is a Sunday. Request not allowed."

    # Check for existing leave conflicts
    if check_leave_conflict(userid, selected_date_dt):
        return f"Leave request conflicts with an existing leave or remote work on {selected_date_dt.strftime('%d-%m-%Y')}."

    combo_leave = Clock.find_one({"userid": userid, "bonus_leave": "Not Taken"})

    user_info = Users.find_one({"_id": ObjectId(userid)}, {"position": 1})
    user_position = user_info.get("position", "User") if user_info else "User"

    employee_id = get_employee_id_from_db(employee_name)

    if combo_leave:
        new_leave = {
            "userid": userid,
            "Employee_ID": employee_id,
            "employeeName": employee_name,
            "time": time,
            "position": user_position,
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



def get_user_leave_requests_with_history(selected_option, show_processed=False):
    """
    Get leave requests with option to include processed ones
    show_processed: False = only pending, True = only processed, None = all
    """
    if selected_option == "Leave":
        base_filter = {"leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]}}
    elif selected_option == "LOP":
        base_filter = {"leaveType": "Other Leave"}
    elif selected_option == "Permission":
        base_filter = {"leaveType": "Permission"}
    else:
        return []
    
    # Add status filter based on show_processed parameter
    if show_processed is False:  # Only pending
        base_filter["status"] = {"$exists": False}
    elif show_processed is True:  # Only processed
        base_filter["status"] = {"$exists": True}
    # If show_processed is None, don't add status filter (show all)
    
    leave_request = list(Leave.find(base_filter))
    
    # Clean the IDs and format dates
    for index, leave in enumerate(leave_request):
        leave_request[index] = cleanid(leave)

    for leave in leave_request:
        if selected_option == "Leave" or selected_option == "Permission":
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
        else:
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            if "ToDate" in leave:
                leave["ToDate"] = leave["ToDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")

    return leave_request

def get_manager_leave_requests_with_history(selected_option, show_processed=False):
    """Get manager/HR leave requests with history option"""
    managers_and_hr = list(Users.find({"position": {"$in": ["Manager", "HR"]}}))
    user_ids = [str(user["_id"]) for user in managers_and_hr]

    if selected_option == "Leave":
        base_filter = {
            "leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]},
            "userid": {"$in": user_ids}
        }
    elif selected_option == "LOP":
        base_filter = {
            "leaveType": "Other Leave",
            "userid": {"$in": user_ids}
        }
    elif selected_option == "Permission":
        base_filter = {
            "leaveType": "Permission",
            "userid": {"$in": user_ids}
        }
    else:
        return []
    
    # Add status filter
    if show_processed is False:  # Only pending
        base_filter["status"] = {"$exists": False}
    elif show_processed is True:  # Only processed
        base_filter["status"] = {"$exists": True}
    
    leave_request = list(Leave.find(base_filter))
    
    # Process the results
    for index, leave in enumerate(leave_request):
        leave_request[index] = cleanid(leave)

    for leave in leave_request:
        if selected_option == "Leave" or selected_option == "Permission":
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
        else:
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            if "ToDate" in leave:
                leave["ToDate"] = leave["ToDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")

    return leave_request

def get_only_user_leave_requests_with_history(selected_option, TL_name, show_processed=False):
    """Get user leave requests under TL with history option"""
    users = list(Users.find({"position": {"$ne":"Manager"}, "name":{"$ne":TL_name}, "TL":TL_name}))
    user_ids = [str(user["_id"]) for user in users]

    if selected_option == "Leave":
        base_filter = {
            "leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]},
            "userid": {"$in": user_ids}
        }
    elif selected_option == "LOP":
        base_filter = {
            "leaveType": "Other Leave",
            "userid": {"$in": user_ids}
        }
    elif selected_option == "Permission":
        base_filter = {
            "leaveType": "Permission",
            "userid": {"$in": user_ids}
        }
    else:
        return []
    
    # Add status filter
    if show_processed is False:  # Only pending
        base_filter["status"] = {"$exists": False}
    elif show_processed is True:  # Only processed
        base_filter["status"] = {"$exists": True}
    
    leave_request = list(Leave.find(base_filter))
    
    # Clean the IDs for each leave request
    for index, leave in enumerate(leave_request):
        leave_request[index] = cleanid(leave)

    for leave in leave_request:
        if selected_option == "Leave" or selected_option == "Permission":
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
        else:
            leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            if "ToDate" in leave:
                leave["ToDate"] = leave["ToDate"].strftime("%d-%m-%Y")
            leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
    
    return leave_request

# Similar functions for Remote Work requests
def get_remote_work_requests_with_history(show_processed=False):
    """Get remote work requests with history option"""
    base_filter = {}
    
    if show_processed is False:  # Only pending
        base_filter = {"Recommendation":"Recommend", "status": {"$exists": False}}
    elif show_processed is True:  # Only processed
        base_filter = {"status": {"$exists": True}}
    
    list1 = list()
    res = RemoteWork.find(base_filter)
    
    for user in res:
        cleanid(user)
        user["fromDate"] = user["fromDate"].strftime("%d-%m-%Y")
        user["toDate"] = user["toDate"].strftime("%d-%m-%Y")
        user["requestDate"] = user["requestDate"].strftime("%d-%m-%Y")
        list1.append(user)
    return list1

def get_admin_page_remote_work_requests_with_history(show_processed=False):
    """Get admin page remote work requests with history"""
    managers = list(Users.find({"$or":[{"position": "Manager"}, {"department": "HR"}]}))
    manager_ids = [str(manager["_id"]) for manager in managers]
    
    base_filter = {"userid": {"$in":manager_ids}}
    
    if show_processed is False:  # Only pending
        base_filter.update({"Recommendation": {"$exists":False}, "status": {"$exists":False}})
    elif show_processed is True:  # Only processed
        base_filter.update({"status": {"$exists":True}})
    
    list1 = list()
    res = RemoteWork.find(base_filter)
    
    for user in res:
        cleanid(user)
        user["fromDate"] = user["fromDate"].strftime("%d-%m-%Y")
        user["toDate"] = user["toDate"].strftime("%d-%m-%Y")
        user["requestDate"] = user["requestDate"].strftime("%d-%m-%Y")
        list1.append(user)
    return list1

def get_TL_page_remote_work_requests_with_history(TL, show_processed=False):
    """Get TL page remote work requests with history"""
    users = list(Users.find({"TL":TL}))
    users_ids = [str(user["_id"]) for user in users]
    
    base_filter = {"userid": {"$in":users_ids}}
    
    if show_processed is False:  # Only pending
        base_filter.update({"status": {"$exists": False}, "Recommendation":{"$exists":False}})
    elif show_processed is True:  # Only processed
        base_filter.update({"status": {"$exists":True}})
    
    list1 = list()
    res = RemoteWork.find(base_filter)
    
    for user in res:
        cleanid(user)
        user["fromDate"] = user["fromDate"].strftime("%d-%m-%Y")
        user["toDate"] = user["toDate"].strftime("%d-%m-%Y")
        user["requestDate"] = user["requestDate"].strftime("%d-%m-%Y")
        list1.append(user)
    return list1

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
        
        result = Leave.update_one(
            {"_id": ObjectId(leave_id)},
            {"$set": {"status": status}}
        )
        print(result)
        if result.modified_count > 0:
            return {"message": "Status updated successfully"}
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
        
        result = Leave.update_one(
            {"_id": ObjectId(leave_id)},
            {"$set": {"status": status}}
        )
        print(result)
        if result.modified_count > 0:
            return {"message": "Status updated successfully"}
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
        # Convert input strings to datetime objects
        from_date_dt = datetime.strptime(from_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
        to_date_dt = datetime.strptime(to_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
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

        user_info = Users.find_one({"_id": ObjectId(userid)}, {"position": 1})
        user_position = user_info.get("position", "User") if user_info else "User"

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
                    "position": user_position,
                    "fromDate": from_date_dt,  # ✅ Stored as `datetime` object
                    "toDate": to_date_dt,  # ✅ Stored as `datetime` object
                    "requestDate": request_date_dt,  # ✅ Stored as `datetime` object
                    "reason": reason,
                    "ip":ip,
                }
                result = RemoteWork.insert_one(new_request)
                print("Insert result:", result.inserted_id)
                return "Remote work request stored successfully."
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
    res = RemoteWork.find({"userid": {"$in":manager_ids}, "Recommendation": {"$exists":False}, "status": {"$exists":False}})
    print(res)
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
    
    # Prepare a list of manager IDs
    users_ids = [str(user["_id"]) for user in users]
    list1 = list()
    res = RemoteWork.find({"userid": {"$in":users_ids}, "status": {"$exists": False}, "Recommendation":{"$exists":False}})
    print(res)
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
        print("Updating status in MongoDB:")
        print("User ID:", userid)
        print("Status:", status)
        
        result = RemoteWork.update_one({"_id":ObjectId(wfh_id), "userid": userid, "status":None, "Recommendation": "Recommend"}, {"$set": {"status": status}, "$unset": { "Recommendation": ""}})
        if result.modified_count > 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error updating status: {e}")
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
    selected_date = datetime.strptime(selected_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
    To_date = datetime.strptime(To_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
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

        user_info = Users.find_one({"_id": ObjectId(userid)}, {"position": 1})
        user_position = user_info.get("position", "User") if user_info else "User"
        
        employee_id = get_employee_id_from_db(employee_name)
         
        if num_weekdays_from_to <= 3 and future_days <= 3:
            new_request = {
                "userid": userid,
                "Employee_ID": employee_id, 
                "employeeName": employee_name,
                "time": time,
                "position": user_position,
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
    # Convert to datetime objects
    selected_date_dt = datetime.strptime(selected_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
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

    user_info = Users.find_one({"_id": ObjectId(userid)}, {"position": 1})
    user_position = user_info.get("position", "User") if user_info else "User"

    new_leave = {
        "userid": userid,
        "Employee_ID": employee_id,
        "employeeName": employee_name,
        "time": time,
        "position": user_position,
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




# Holiday and Working Days Management (already in your code)
def insert_holidays(year: int, holidays: list):
    """Insert or update holidays for a given year"""
    holidays_collection.update_one(
        {"year": year},
        {"$set": {"year": year, "holidays": holidays}},
        upsert=True
    )
    return {"message": f"Holidays updated for {year}"}

def get_holidays(year: int):
    """Fetch holidays for a given year"""
    return holidays_collection.find_one({"year": year})

def calculate_working_days(year: int, holidays: list):
    """Calculate working days for a year excluding Sundays and holidays"""
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    delta = timedelta(days=1)
    
    working_days = []
    current = start
    
    holiday_dates = {h["date"] for h in holidays}
    
    while current <= end:
        is_sunday = current.weekday() == 6  # 6 = Sunday
        is_holiday = current.strftime("%Y-%m-%d") in holiday_dates
        if not is_sunday and not is_holiday:
            working_days.append(current.strftime("%Y-%m-%d"))
        current += delta
    
    return working_days

def get_working_days_count_till_date(year: int, till_date: date = None):
    """Get working days count from start of year till specified date (or today)"""
    if till_date is None:
        till_date = date.today()
    
    holiday_doc = get_holidays(year)
    if not holiday_doc:
        return 0
    
    holidays = holiday_doc["holidays"]
    holiday_dates = {h["date"] for h in holidays}
    
    start = datetime(year, 1, 1).date()
    end = min(till_date, datetime(year, 12, 31).date())
    
    working_days_count = 0
    current = start
    
    while current <= end:
        is_sunday = current.weekday() == 6
        is_holiday = current.strftime("%Y-%m-%d") in holiday_dates
        if not is_sunday and not is_holiday:
            working_days_count += 1
        current += timedelta(days=1)
    
    return working_days_count

# New Attendance Calculation Functions

def calculate_user_attendance_stats(userid: str, year: int = None):
    """Calculate attendance statistics for a specific user"""
    if year is None:
        year = date.today().year
    
    # Get user info to get username
    try:
        user = Users.find_one({"_id": ObjectId(userid)}, {"name": 1})
        username = user.get("name", "Unknown") if user else "Unknown"
    except Exception as e:
        print(f"Error fetching user info for {userid}: {e}")
        username = "Unknown"
    
    # Get total working days till today
    total_working_days = get_working_days_count_till_date(year)
    
    if total_working_days == 0:
        return {
            "userid": userid,
            "username": username,
            "year": year,
            "total_working_days": 0,
            "present_days": 0,
            "attendance_percentage": 0,
            "leave_days_taken": 0,
            "leave_percentage": 0,
            "last_updated": datetime.now()
        }
    
    # Count present days (where status is "Present" or "Late")
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    present_days = Clock.count_documents({
        "userid": userid,
        "date": {
            "$gte": start_date,
            "$lte": end_date
        },
        "status": {"$in": ["Present", "Late"]}
    })
    
    # Count leave days taken (approved leaves)
    leave_days = Leave.count_documents({
        "userid": userid,
        "status": "Approved",
        "selectedDate": {
            "$gte": datetime(year, 1, 1),
            "$lte": datetime(year, 12, 31)
        }
    })
    
    # Calculate multi-day leaves (LOP/Other Leave)
    multi_day_leaves = Leave.find({
        "userid": userid,
        "status": "Approved",
        "leaveType": "Other Leave",
        "selectedDate": {
            "$gte": datetime(year, 1, 1),
            "$lte": datetime(year, 12, 31)
        }
    })
    
    additional_leave_days = 0
    for leave in multi_day_leaves:
        if "ToDate" in leave:
            from_date = leave["selectedDate"]
            to_date = leave["ToDate"]
            # Count weekdays between from_date and to_date
            current = from_date
            while current <= to_date:
                if current.weekday() != 6:  # Not Sunday
                    additional_leave_days += 1
                current += timedelta(days=1)
    
    total_leave_days = leave_days + additional_leave_days
    
    # Calculate percentages
    attendance_percentage = round((present_days / total_working_days) * 100, 2) if total_working_days > 0 else 0
    leave_percentage = round((total_leave_days / total_working_days) * 100, 2) if total_working_days > 0 else 0
    
    stats = {
        "userid": userid,
        "username": username,
        "year": year,
        "total_working_days": total_working_days,
        "present_days": present_days,
        "attendance_percentage": attendance_percentage,
        "leave_days_taken": total_leave_days,
        "leave_percentage": leave_percentage,
        "last_updated": datetime.now()
    }
    
    # Cache the stats
    AttendanceStats.update_one(
        {"userid": userid, "year": year},
        {"$set": stats},
        upsert=True
    )
    
    return stats

def get_user_attendance_dashboard(userid: str):
    """Get attendance dashboard for individual user"""
    current_year = date.today().year
    stats = calculate_user_attendance_stats(userid, current_year)
    
    # Get user info for display
    user = Users.find_one({"_id": ObjectId(userid)}, {"name": 1, "email": 1, "department": 1, "position": 1})
    
    return {
        "user_info": {
            "userid": userid,
            "name": user.get("name", "Unknown") if user else "Unknown",
            "email": user.get("email", "") if user else "",
            "department": user.get("department", "") if user else "",
            "position": user.get("position", "") if user else ""
        },
        "attendance_stats": stats,
        "year": current_year
    }

def get_team_attendance_stats(team_leader: str, year: int = None):
    """Get attendance statistics for all team members under a team leader"""
    if year is None:
        year = date.today().year
    
    # Get team members
    team_members = list(Users.find(
        {"TL": team_leader, "position": {"$ne": "Manager"}},
        {"_id": 1, "name": 1, "email": 1, "department": 1, "position": 1}
    ))
    
    team_stats = []
    total_attendance = 0
    
    for member in team_members:
        userid = str(member["_id"])
        stats = calculate_user_attendance_stats(userid, year)
        stats["user_info"] = {
            "name": member.get("name"),
            "email": member.get("email"),
            "department": member.get("department"),
            "position": member.get("position")
        }
        team_stats.append(stats)
        total_attendance += stats["attendance_percentage"]
    
    average_attendance = round(total_attendance / len(team_members), 2) if team_members else 0
    
    return {
        "team_leader": team_leader,
        "year": year,
        "team_size": len(team_members),
        "average_attendance": average_attendance,
        "team_stats": team_stats
    }

def get_department_attendance_stats(department: str = None, year: int = None):
    """Get attendance statistics for a department or all employees (for admin)"""
    if year is None:
        year = date.today().year
    
    # Build query based on role
    query = {"position": {"$ne": "Admin"}}
    if department:
        query["department"] = department
    
    employees = list(Users.find(query, {"_id": 1, "name": 1, "email": 1, "department": 1, "position": 1, "TL": 1}))
    
    all_stats = []
    total_attendance = 0
    department_stats = {}
    
    for employee in employees:
        userid = str(employee["_id"])
        stats = calculate_user_attendance_stats(userid, year)
        stats["user_info"] = {
            "name": employee.get("name"),
            "email": employee.get("email"),
            "department": employee.get("department"),
            "position": employee.get("position"),
            "team_leader": employee.get("TL", "")
        }
        all_stats.append(stats)
        total_attendance += stats["attendance_percentage"]
        
        # Group by department for admin view
        dept = employee.get("department", "Unknown")
        if dept not in department_stats:
            department_stats[dept] = {"total": 0, "count": 0, "employees": []}
        department_stats[dept]["total"] += stats["attendance_percentage"]
        department_stats[dept]["count"] += 1
        department_stats[dept]["employees"].append(stats)
    
    # Calculate department averages
    for dept in department_stats:
        department_stats[dept]["average_attendance"] = round(
            department_stats[dept]["total"] / department_stats[dept]["count"], 2
        ) if department_stats[dept]["count"] > 0 else 0
    
    overall_average = round(total_attendance / len(employees), 2) if employees else 0
    
    return {
        "year": year,
        "total_employees": len(employees),
        "overall_average_attendance": overall_average,
        "department_wise_stats": department_stats,
        "all_employee_stats": all_stats
    }

def get_manager_team_attendance(manager_userid: str, year: int = None):
    """Get attendance stats for all teams under a manager"""
    if year is None:
        year = date.today().year
    
    # Get all team leaders under this manager
    team_leaders = list(Users.find(
        {"position": "TL", "manager": manager_userid},  # Assuming TLs have manager field
        {"_id": 1, "name": 1}
    ))
    
    if not team_leaders:
        # If no specific TL structure, get all non-manager employees
        return get_department_attendance_stats(year=year)
    
    manager_stats = {
        "manager_userid": manager_userid,
        "year": year,
        "teams": [],
        "overall_average": 0
    }
    
    total_attendance = 0
    total_employees = 0
    
    for tl in team_leaders:
        tl_name = tl["name"]
        team_stats = get_team_attendance_stats(tl_name, year)
        manager_stats["teams"].append(team_stats)
        total_attendance += team_stats["average_attendance"] * team_stats["team_size"]
        total_employees += team_stats["team_size"]
    
    manager_stats["overall_average"] = round(total_attendance / total_employees, 2) if total_employees > 0 else 0
    manager_stats["total_employees"] = total_employees
    
    return manager_stats

# Daily update function to recalculate stats
def update_daily_attendance_stats():
    """Run this daily to update attendance statistics for all users"""
    current_year = date.today().year
    
    # Get all active users
    users = Users.find({"status": {"$ne": "Inactive"}}, {"_id": 1})
    
    updated_count = 0
    for user in users:
        userid = str(user["_id"])
        try:
            calculate_user_attendance_stats(userid, current_year)
            updated_count += 1
        except Exception as e:
            print(f"Error updating stats for user {userid}: {e}")
    
    print(f"Updated attendance stats for {updated_count} users")
    return updated_count

