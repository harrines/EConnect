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
import bcrypt
import pytz 
import json

# client = MongoClient("mongodb://127.0.0.1:27017/rbg")
client= MongoClient("mongodb+srv://narenkishor:jgcaG14dSeVPIGUi@rbg.jkizh.mongodb.net/?retryWrites=true&w=majority&appName=rbg/")
client=client.RBG_AI
Users=client.Users
Add=client.Dataset
Leave=client.Leave_Details
Clock=client.Attendance
RemoteWork = client.RemoteWork
admin = client.admin
Tasks = client.tasks
Managers = client.managers

# Others
def Adddata(data,id,filename):
    a=Add.insert_one({'userid':id,'data':data,'filename':filename})
    return str(a.inserted_id)

def Editdata(data,id,filename):
    a=Add.update_one({"_id":ObjectId(id)},{"$set":{"data":data,'filename':filename}})
    return "done"

def deletedata(id):
    a=Add.delete_one({'_id':ObjectId(id)})
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

# Google Signin      
def Gsignin(client_name,email):
    checkuser=Users.find_one({'email': email})
    checkadmin=admin.find_one({'email': email})
    checkmanager=Managers.find_one({'email': email})
    if (checkuser):
            a=signJWT(client_name)
            b=checkuser
            checkuser=cleanid(checkuser)
            checkuser.update(a)
            checkuser.update({"isloggedin":True, "isadmin":False})
            return checkuser
    elif (checkadmin):
        result = admin_Gsignin(checkadmin, client_name)
        return result
    elif (checkmanager):
        result = manager_Gsignin(checkmanager, client_name)
        return result
    else:
        raise HTTPException(status_code=300, detail="Given Email does not exists")

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

# Time management

# def Clockin(userid, name, time):
#     today = date.today()
    
#     clockin_time = datetime.strptime(time, "%I:%M:%S %p")
#     status = "Present" if datetime.strptime("09:00:00 AM", "%I:%M:%S %p") <= clockin_time <= datetime.strptime("10:30:00 AM", "%I:%M:%S %p") else "Late"
#     existing_record = Clock.find_one({'date': str(today), 'name': name})
    
#     if not existing_record:
#         Clock.insert_one({
#             'userid': userid,
#             'date': str(today),
#             'name': name,
#             'clockin': time,
#             'status': status,
#             'remark': ''
#         })
#     else:
#         Clock.find_one_and_update(
#             {'date': str(today), 'name': name},
#             {'$set': {'clockin': time, 'status': status}}
#         )
#     return True

# def Clockin(userid, name, time):
    # today = date.today()
#     a = Clock.find_one({'date': str(today), 'name': name})
#     status = "Present" if "08:30" <= time <= "10:30" else "Late"
#     if not a:
#         Clock.insert_one({'userid': userid, 'date': str(today), 'name': name, 'clockin': time, 'status': status, 'remark': ''})
#     else:
#         Clock.find_one_and_update({'date': str(today), 'name': name}, {'$set': {'clockin': time, 'status': status}})
#     return True

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


# def Clockout(userid, name, time):
#     today = date.today()
#     a = Clock.find_one({'date': str(today), 'name': name})

#     if a:
#         clockin_time = parser.parse(a['clockin'])
#         clockout_time = parser.parse(time)

#         total_seconds_worked = (clockout_time - clockin_time).total_seconds()
#         total_hours_worked = total_seconds_worked / 3600
#         remaining_seconds = total_seconds_worked % 3600
#         total_minutes_worked = remaining_seconds // 60
#         remark = "N/A" if total_hours_worked >= 8 else "Incomplete"

#         Clock.find_one_and_update(
#             {'date': str(today), 'name': name},
#             {'$set': {'clockout': time, 'total_hours_worked': f'{int(total_hours_worked)} hours {int(total_minutes_worked)} minutes', 'remark': remark}}
#         )

#         return f'{int(total_hours_worked)} hours {int(total_minutes_worked)} minutes', remark
#     else:
#         a = Clock.insert_one({'userid': userid, 'date': str(today), 'name': name, 'clockout': time})
#         return a, None, None
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
            return f"Clock-out already recorded at {record["clockout"]}"

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
def get_attendance_by_date(date):
    attendance_data = list(Clock.find({"date": str(date)}, {"_id": 0}))
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
    return formatted_timestamp.strftime("%d-%m-%Y")

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


def store_leave_request(userid, employee_name, time, leave_type, selected_date, request_date, reason,status):
    # Check if the request date is a Sunday (weekday() returns 6 for Sunday)
    if request_date.weekday() == 6:
        return "Request date is a Sunday. Request not allowed."
    
    if selected_date.weekday() == 6:
        return "Selected date is a Sunday. Request not allowed."

    if leave_type == "Sick Leave" and format_timestamp(selected_date) != format_timestamp(request_date):
        return "Sick Leave is permitted for today only."

 # Check if any leave or remote work overlaps with the selected date
    overlapping_leave = Leave.find_one({
        "userid": userid,
        "$or": [
            {"selectedDate": {"$lte": format_timestamp(selected_date)}, "ToDate": {"$gte": format_timestamp(selected_date)}},
            {"selectedDate": format_timestamp(selected_date)}  # For leaves without a ToDate field
        ]
    })

    overlapping_remote_work = RemoteWork.find_one({
        "userid": userid,
        "$or": [
            {"fromDate": {"$lte": format_timestamp(selected_date)}, "toDate": {"$gte": format_timestamp(selected_date)}},
            {"fromDate": format_timestamp(selected_date)}
        ]
    })

    if overlapping_leave:
        return f"Leave already applied: {overlapping_leave['leaveType']} from {overlapping_leave['selectedDate']} to {overlapping_leave.get('ToDate', overlapping_leave['selectedDate'])}"

    if overlapping_remote_work:
        return "Remote work already applied during this period."

    combo_leave = Clock.find_one({"userid":userid,"bonus_leave":"Not Taken"})
    if combo_leave:
        return f"A combo leave is available for {combo_leave['date']}"
    if leave_type == "Casual Leave":
        weekdays_count = count_weekdays(request_date + timedelta(days=1), selected_date)
        if weekdays_count < 1:
            return "Two days prior notice for Casual Leave."
        
    if leave_type == "Casual Leave":
        # Check if the next day is already taken for Sick Leave
        if is_leave_taken(userid, selected_date + timedelta(days=1), "Sick Leave"):
            return "Casual Leave cannot be taken if the next day is Sick Leave."
        
        # Check if the previous day is already taken for Sick Leave
        if is_leave_taken(userid, selected_date - timedelta(days=1), "Sick Leave"):
            return "Casual Leave cannot be taken if the previous day is Sick Leave."
        
        # Check if the next day is already taken for Casual Leave
        if is_leave_taken(userid, selected_date + timedelta(days=1), "Casual Leave"):
            return "Casual Leave cannot be taken if the next day is also Casual Leave."
        
        # Check if the previous day is already taken for Casual Leave
        if is_leave_taken(userid, selected_date - timedelta(days=1), "Casual Leave"):
            return "Casual Leave cannot be taken if the previous day is also Casual Leave."
    
    current_month = selected_date.strftime("%m-%Y")
    # Count leaves for the current user and leave type in the given month
    leave_count_cursor = Leave.aggregate([
        {
            '$match': {
                'userid': userid,
                'selectedDate': {'$regex': f".*{current_month}.*"},
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
    print(leave_count)
    if leave_count:
        leave_count = leave_count[0]
        if leave_count["count"] >= 1:
            return f"You have already taken a {leave_type} this month."


    employee_id = get_employee_id_from_db(employee_name)
    new_leave = {
        "userid": userid,
        "Employee_ID": employee_id, 
        "employeeName": employee_name,
        "time": time,
        "leaveType": leave_type,
        "selectedDate": format_timestamp(selected_date),
        "requestDate": format_timestamp(request_date),
        "reason": reason,
        "status":status,
        
    }

    result = Leave.insert_one(new_leave)

    print("result", result)
    return "Leave request stored successfully"

def is_leave_taken(userid, selected_date, leave_type):
    # Check if leave of given type is taken on the selected date
    leave_entry = Leave.find_one({
        "userid": userid,
        "selectedDate": format_timestamp(selected_date),
        "leaveType": leave_type
    })
    
    return leave_entry is not None


# # User Page Leave History
# def leave_History_Details(userid: str):
#     leave_History = Leave.find({'userid' : userid}, {'_id': 0})
#     return list(leave_History)

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
    # Ensure request date is not a Sunday
    if request_date.weekday() == 6:
        return "Request date is a Sunday. Request not allowed."

    # Check for overlapping leave or remote work
    overlapping_leave = Leave.find_one({
        "userid": userid,
        "$or": [
            {"selectedDate": {"$lte": format_timestamp(selected_date)}, "ToDate": {"$gte": format_timestamp(selected_date)}},
            {"selectedDate": format_timestamp(selected_date)}
        ]
    })

    overlapping_remote_work = RemoteWork.find_one({
        "userid": userid,
        "$or": [
            {"selectedDate": {"$lte": format_timestamp(selected_date)}, "ToDate": {"$gte": format_timestamp(selected_date)}},
            {"selectedDate": format_timestamp(selected_date)}
        ]
    })

    if overlapping_leave:
        return f"Leave already applied: {overlapping_leave['leaveType']} from {overlapping_leave['selectedDate']} to {overlapping_leave.get('ToDate', overlapping_leave['selectedDate'])}"
    
    if overlapping_remote_work:
        return "Remote work already applied during this period."

    combo_leave = Clock.find_one({"userid": userid, "bonus_leave": "Not Taken"})
    print(combo_leave)
    employee_id = get_employee_id_from_db(employee_name)

    if combo_leave:
        new_leave = {
            "userid": userid,
            "Employee_ID": employee_id,
            "employeeName": employee_name,
            "time": time,
            "leaveType": leave_type,
            "selectedDate": format_timestamp(selected_date),
            "reason": reason,
            "requestDate": format_timestamp(request_date),
        }

        Clock.find_one_and_update({"userid": userid, "bonus_leave": "Not Taken"}, {"$set": {"bonus_leave": "Taken"}})
        Leave.insert_one(new_leave)
        return "Leave request stored successfully"
    else:
        return "No bonus leave available"


# Manger Page Leave Requests
def get_user_leave_requests(request_date, selected_option):
    if selected_option == "Leave":
        leave_request = list(Leave.find({"requestDate": request_date.strftime("%d-%m-%Y"), "leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]}, "status":"Recommend"}))
    elif selected_option == "LOP":
        leave_request = list(Leave.find({"requestDate": request_date.strftime("%d-%m-%Y"), "leaveType": "Other Leave", "status":"Recommend"}))
    elif selected_option == "Permission":
        leave_request = list(Leave.find({"requestDate": request_date.strftime("%d-%m-%Y"), "leaveType": "Permission", "status":"Recommend"}))
    else:
        leave_request = []
    
    for index, leave in enumerate(leave_request):
        leave_request[index] = cleanid(leave)
        
    return leave_request

# Admin Page Leave Requests
def get_manager_leave_requests(request_date, selected_option):
    managers = list(Users.find({"position": "Manager"}))
    
    # Prepare a list of manager IDs
    manager_ids = [str(manager["_id"]) for manager in managers]

    if selected_option == "Leave":
        leave_request = list(Leave.find({
            "requestDate": request_date.strftime("%d-%m-%Y"),
            "leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]},
            "userid": {"$in": manager_ids}
        }))
        print(leave_request)
    elif selected_option == "LOP":
        leave_request = list(Leave.find({
            "requestDate": request_date.strftime("%d-%m-%Y"),
            "leaveType": "Other Leave",
            "userid": {"$in": manager_ids}
        }))
    elif selected_option == "Permission":
        leave_request = list(Leave.find({
            "requestDate": request_date.strftime("%d-%m-%Y"),
            "leaveType": "Permission",
            "userid": {"$in": manager_ids}
        }))
    else:
        leave_request = []
    
    # Clean the IDs for each leave request
    for index, leave in enumerate(leave_request):
        leave_request[index] = cleanid(leave)
    
    return leave_request

# TL Page Leave Requests
def get_only_user_leave_requests(request_date, selected_option,TL_name):
    users = list(Users.find({"position": {"$ne":"Manager"},"TL":TL_name}))
     
    # Prepare a list of user IDs
    user_ids = [str(user["_id"]) for user in users]

    if selected_option == "Leave":
        leave_request = list(Leave.find({
            "requestDate": request_date.strftime("%d-%m-%Y"),
            "leaveType": {"$in": ["Sick Leave", "Casual Leave", "Bonus Leave"]},
            "userid": {"$in": user_ids}
        }))
        print(leave_request)
    elif selected_option == "LOP":
        leave_request = list(Leave.find({
            "requestDate": request_date.strftime("%d-%m-%Y"),
            "leaveType": "Other Leave",
            "userid": {"$in": user_ids}
        }))
    elif selected_option == "Permission":
        leave_request = list(Leave.find({
            "requestDate": request_date.strftime("%d-%m-%Y"),
            "leaveType": "Permission",
            "userid": {"$in": user_ids}
        }))
    else:
        leave_request = []
    
    # Clean the IDs for each leave request
    for index, leave in enumerate(leave_request):
        leave_request[index] = cleanid(leave)
    
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
def get_approved_leave_history():
        leave_history = Leave.find({"status": "Approved"})
        return [{**item, "_id": str(item["_id"])} for item in leave_history]

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
def users_leave_recommend_notification():
    users = list(Users.find({"position": {"$ne":"Manager"}, "TL":TL}))
    
    # Prepare a list of manager IDs
    users_ids = [str(user["_id"]) for user in users]

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

# Remote Work Request
def store_remote_work_request(userid, employeeName, time, from_date, to_date, request_date, reason):
    try:
        print(f"Storing remote work request for {employeeName}, UserID: {userid}...")
        print(f"Request Date: {request_date}, From Date: {from_date}, To Date: {to_date}")
        
        selected_date = from_date
        # Validation: to_date >= from_date
        if to_date < from_date:
            return "To date should be after or equal to from date."

        # Validation: Request date not on Sunday
        if request_date.weekday() == 6:
            return "Request date is a Sunday. Remote work request not allowed."

        # Check if any leave or remote work overlaps with the date range
        overlapping_leave = Leave.find_one({
            "userid": userid,
            "$or": [
                {"selectedDate": {"$lte": format_timestamp(to_date)}, "ToDate": {"$gte": format_timestamp(selected_date)}},
                {"selectedDate": {"$gte": format_timestamp(selected_date), "$lte": format_timestamp(to_date)}}
            ]
        })

        overlapping_remote_work = RemoteWork.find_one({
            "userid": userid,
            "$or": [
                {"fromDate": {"$lte": format_timestamp(to_date)}, "toDate": {"$gte": format_timestamp(selected_date)}},
                {"fromDate": {"$gte": format_timestamp(selected_date), "$lte": format_timestamp(to_date)}}
            ]
        })

        if overlapping_leave:
            return f"Leave already applied: {overlapping_leave['leaveType']} from {overlapping_leave['selectedDate']} to {overlapping_leave.get('ToDate', overlapping_leave['selectedDate'])}"

        if overlapping_remote_work:
            return "Remote work already applied during this period."


        # Calculate weekdays
        num_weekdays_request_to_from = count_weekdays(request_date, from_date)
        num_weekdays_from_to = count_weekdays(from_date, to_date)
        future_days = (to_date - from_date).days

        print(f"Weekdays from request to start: {num_weekdays_request_to_from}, future days: {future_days}")

        # Fetch Employee ID
        employee_id = get_employee_id_from_db(employeeName)
        if not employee_id:
            return "Invalid employee name."

        # Validation: Request must be at least 5 days in advance and for max 3 weekdays
        if num_weekdays_request_to_from >= 4:
            if num_weekdays_from_to <= 3 and future_days <= 3:
                new_request = {
                    "userid": userid,
                    "employeeName": employeeName,
                    "time": time,
                    "fromDate": format_timestamp(from_date),
                    "toDate": format_timestamp(to_date),
                    "requestDate": format_timestamp(request_date),
                    "reason": reason,
                }
                result = RemoteWork.insert_one(new_request)
                print("Insert result:", result.inserted_id)
                return "Remote request successful"
            else:
                return "Remote work can be taken for a maximum of 3 days."
        else:
            return "Remote work request can only be made at least 5 days prior."

    except Exception as e:
        print(f"Error occurred: {e}")
        return "An error occurred while processing the request."



# User Remote Work History
def Remote_History_Details(userid:str):
    Remote_History = RemoteWork.find({'userid' : userid},{'_id':0})
    return list(Remote_History)

# HR Page Remote Requests
def get_remote_work_requests():
    list1 = list()
    res = RemoteWork.find({"Recommendation":"Recommend"})
    print(res)
    for user in res:
        cleanid(user)
        list1.append(user)
    return list1

# Admin Page Remote Requests
def get_admin_page_remote_work_requests():
    managers = list(Users.find({"position": "Manager"}))
    
    # Prepare a list of manager IDs
    manager_ids = [str(manager["_id"]) for manager in managers]
    list1 = list()
    res = RemoteWork.find({"userid": {"$in":manager_ids}})
    print(res)
    for user in res:
        cleanid(user)
        list1.append(user)
    return list1

# TL Page Remote Requests
def get_TL_page_remote_work_requests(TL):
    users = list(Users.find({"position": {"$ne":"Manager"}, "TL":TL}))
    
    # Prepare a list of manager IDs
    users_ids = [str(user["_id"]) for user in users]
    list1 = list()
    res = RemoteWork.find({"userid": {"$in":users_ids}})
    print(res)
    for user in res:
        cleanid(user)
        list1.append(user)
    return list1

# Status Response for Remote Work
def update_remote_work_request_status_in_mongo(userid, status):
    try:
        print("Updating status in MongoDB:")
        print("User ID:", userid)
        print("Status:", status)
        
        result = RemoteWork.update_one({"userid": userid, "status":None}, {"$set": {"status": status}})
        if result.modified_count > 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error updating status: {e}")
        raise Exception("Error updating status in MongoDB")

    return False

def update_remote_work_request_recommend_in_mongo(userid, status):
    try:
        print("Updating status in MongoDB:")
        print("User ID:", userid)
        print("Status:", status)
        
        result = RemoteWork.update_one({"userid": userid, "Recommendation":None}, {"$set": {"Recommendation": status}})
        if result.modified_count > 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error updating status: {e}")
        raise Exception("Error updating status in MongoDB")

    return False


def store_Other_leave_request(userid, employee_name, time, leave_type, selected_date, To_date, request_date, reason):
    # Check if the request date is a Sunday (weekday() returns 6 for Sunday)
    if request_date.weekday() == 6:
        return "Request date is a Sunday. Request not allowed."

    if To_date < selected_date:
        return "To date should be after or equal to from date."

 # Check if any leave or remote work overlaps with the date range
    overlapping_leave = Leave.find_one({
        "userid": userid,
        "$or": [
            {"selectedDate": {"$lte": format_timestamp(To_date)}, "ToDate": {"$gte": format_timestamp(selected_date)}},
            {"selectedDate": {"$gte": format_timestamp(selected_date), "$lte": format_timestamp(To_date)}}
        ]
    })

    overlapping_remote_work = RemoteWork.find_one({
        "userid": userid,
        "$or": [
            {"fromDate": {"$lte": format_timestamp(To_date)}, "toDate": {"$gte": format_timestamp(selected_date)}},
            {"fromDate": {"$gte": format_timestamp(selected_date), "$lte": format_timestamp(To_date)}}
        ]
    })

    if overlapping_leave:
        return f"Leave already applied: {overlapping_leave['leaveType']} from {overlapping_leave['selectedDate']} to {overlapping_leave.get('ToDate', overlapping_leave['selectedDate'])}"

    if overlapping_remote_work:
        return "Remote work already applied during this period."


    num_weekdays_request_to_from = count_weekdays(request_date, selected_date)
    
    # You can remove the restriction for "Other Leave" to be made at least 5 days prior
    # if num_weekdays_request_to_from == 2:
    if leave_type == "Other Leave":
        weekdays_count = count_weekdays(request_date + timedelta(days=1), selected_date)
        # if weekdays_count < 1:
        #     return "Two days prior notice for Other Leave." 
        # Check the number of weekdays between the selected dates
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
                "selectedDate": format_timestamp(selected_date),
                "ToDate" : format_timestamp(To_date),
                "requestDate": format_timestamp(request_date),
                "reason": reason,
            }
            result = Leave.insert_one(new_request)
            print("result", result)
            return "Leave request stored successfully"
        else:
            return "Other Leave can be taken for a maximum of 3 days"
    # else:
        # return "Other Leave request can only be made at least 2 days prior"


def store_Permission_request(userid, employee_name, time, leave_type, selected_date, request_date,Time_Slot, reason):
    # Check if the request date is a Sunday (weekday() returns 6 for Sunday)
    if request_date.weekday() == 6:
        return "Request date is a Sunday. Request not allowed."
 
    
    if leave_type == "Permission" and format_timestamp(selected_date) != format_timestamp(request_date):
        return "Permission is permitted for today only."
    
    overlapping_leave = Leave.find_one({
        "userid": userid,
        "$or": [
            {"selectedDate": {"$lte": format_timestamp(selected_date)}, "ToDate": {"$gte": format_timestamp(selected_date)}},
            {"selectedDate": format_timestamp(selected_date)}
        ]
    })

    overlapping_remote_work = RemoteWork.find_one({
        "userid": userid,
        "$or": [
            {"selectedDate": {"$lte": format_timestamp(selected_date)}, "ToDate": {"$gte": format_timestamp(selected_date)}},
            {"selectedDate": format_timestamp(selected_date)}
        ]
    })

    if overlapping_leave:
        return f"Cannot apply for Permission as leave is already applied: {overlapping_leave['leaveType']} from {overlapping_leave['selectedDate']} to {overlapping_leave.get('ToDate', overlapping_leave['selectedDate'])}"

    if overlapping_remote_work:
        return "Cannot apply for Permission as remote work is already scheduled during this period."
    employee_id = get_employee_id_from_db(employee_name)
    
    new_leave = {
        "userid": userid,
        "Employee_ID": employee_id, 
        "employeeName": employee_name,
        "time": time,
        "leaveType": leave_type,
        "selectedDate": format_timestamp(selected_date),
        "requestDate": format_timestamp(request_date),
        "timeSlot": Time_Slot,
        "reason": reason,
        
    }

    result = Leave.insert_one(new_leave)

    print("result", result)
    return "Leave request stored successfully"




def Otherleave_History_Details(userid):

    # Filter by userid and leaveType "Other"
    leave_history = list(Leave.find({"userid": userid, "leaveType": "Other Leave"}))

    # Convert ObjectId to string for JSON serialization
    for item in leave_history:
        item["_id"] = str(item["_id"])

    return leave_history

def normal_leave_details(userid):

    # Filter by userid and leaveType "Other"
    leave_history = list(Leave.find({"userid": userid,}))

    # Convert ObjectId to string for JSON serialization
    for item in leave_history:
        item["_id"] = str(item["_id"])

    return leave_history


def Permission_History_Details(userid):

    # Filter by userid and leaveType "Other"
    leave_history = list(Leave.find({"userid": userid, "leaveType": "Permission"}))

    # Convert ObjectId to string for JSON serialization
    for item in leave_history:
        item["_id"] = str(item["_id"])

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

def add_task_list(task:str, userid: str, today):
    task = {
        "task": task,
        "status": "Not completed",
        "date": today,
        "userid": userid,
    }
    result = Tasks.insert_one(task)
    return str(result.inserted_id)

def edit_the_task(userid, task, date, cdate, updated_task=None, status=None):
    update_fields = {}
    if updated_task and updated_task != "string":
        update_fields["task"] = updated_task
    if status and status != "string":
        update_fields["status"] = status
        update_fields["completed_date"] = cdate

    if update_fields:
        result = Tasks.update_one({"task": task, "date":date, "userid": userid}, {"$set": update_fields})
        if result.matched_count > 0:
            return "Task updated successfully"
        else:
            return "Task not found"
    else:
        return "No fields to update"


def delete_a_task(task: str, userid: str, date):
    try:
        result = Tasks.delete_one({"task": task, "date":date, "userid": userid})
        if result.deleted_count > 0:
            return "Deleted"
        return "Task not found"
    except Exception as e:
        return f"Error: {str(e)}"



def get_the_tasks(userid:str, date:str):
    tasks = list(Tasks.find({"userid":userid, "date":date}, {"_id":0}))
    task_list = []
    for task in tasks:
        task_data = {
            "task": task.get("task"),
            "status": task.get("status"),
            "date": task.get("date"),
            "userid": task.get("userid"),
        }
        task_list.append(task_data)  
    return task_list

def get_user_info(userid):
    result = Users.find_one({"_id":ObjectId(userid)},{"_id":0,"password":0})
    return result

def get_admin_info(adminid):
    result = admin.find_one({"_id":ObjectId(adminid)},{"_id":0,"password":0})
    return result

def add_an_employee(employee_data):
    try:
        # Insert the employee data into the Users collection
        result = Users.insert_one(employee_data)
        return {"message": "Employee details added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def add_a_manager(manager_data):
    try:
        result = Managers.insert_one(manager_data)
        return {"message": "Manager details added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def auto_approve_manager_leaves():
    Leave.update_many(
        {"position":"Manager", "status": "Recommend"},
        {"$set": {"status": "Approved"}}
    )

    return {"message": "Manager leave requests have been auto-approved where applicable."}