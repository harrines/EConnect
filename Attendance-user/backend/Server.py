from Mongo import Leave, RemoteWork, Otherleave_History_Details,Permission_History_Details, Users,admin,normal_leave_details,store_Other_leave_request,get_approved_leave_history,get_remote_work_requests,attendance_details,leave_History_Details,Remote_History_Details,get_attendance_by_date,update_remote_work_request_status_in_mongo,updated_user_leave_requests_status_in_mongo,get_user_leave_requests, get_employee_id_from_db,store_Permission_request, get_all_users, get_admin_info, add_task_list, edit_the_task, delete_a_task, get_the_tasks, delete_leave, get_user_info, store_sunday_request, get_admin_info, add_an_employee, PreviousDayClockout, auto_clockout, leave_update_notification, recommend_manager_leave_requests_status_in_mongo, get_manager_leave_requests, get_only_user_leave_requests, get_admin_page_remote_work_requests, update_remote_work_request_recommend_in_mongo, get_TL_page_remote_work_requests, users_leave_recommend_notification, managers_leave_recommend_notification,auto_approve_manager_leaves,edit_an_employee,get_managers,task_assign_to_multiple_users, get_team_members, manager_task_assignment, get_local_ip, get_public_ip, assigned_task, get_single_task, insert_holidays, get_holidays, calculate_working_days, calculate_user_attendance_stats, get_user_attendance_dashboard, get_team_attendance_stats, get_department_attendance_stats, get_manager_team_attendance, update_daily_attendance_stats, get_user_leave_requests_with_history, get_manager_leave_requests_with_history, get_only_user_leave_requests_with_history, get_remote_work_requests_with_history, get_admin_page_remote_work_requests_with_history, get_TL_page_remote_work_requests_with_history
from model import Item4,Item,Item2,Item3,Csvadd,Csvedit,Csvdel,CT,Item5,Item6,Item9,RemoteWorkRequest,Item7,Item8, Tasklist, Taskedit, Deletetask, Gettasks, DeleteLeave, Item9, AddEmployee,EditEmployee,Taskassign, SingleTaskAssign, HolidayYear, Holiday
from fastapi import FastAPI, HTTPException,Path,Query, HTTPException,Form, Request
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI,Body
from auth.auth_bearer import JWTBearer
from http.client import HTTPException
from datetime import datetime, timedelta, date
from dateutil import parser
from typing import Union, Dict, List, Optional
from bson import ObjectId
from bson import json_util
import json
import uvicorn
import Mongo
import pytz
import os
from typing import List
import atexit


app = FastAPI()
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize APScheduler
scheduler = BackgroundScheduler()


# Schedule the auto-clockout task to run daily at 8:05 PM
scheduler.add_job(auto_clockout, 'cron', hour=9, minute=30)


# Add new job for daily attendance stats update
scheduler.add_job(
    update_daily_attendance_stats,
    'cron',
    hour=23,
    minute=59,  # Run at 11:59 PM daily
    id='daily_attendance_update'
)


# Add job to run attendance update at startup
scheduler.add_job(
    update_daily_attendance_stats,
    'date',  # Run once at startup
    id='startup_attendance_update'
)


# Start the scheduler
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post('/addjson',dependencies=[Depends(JWTBearer())])
def Addjson(item:Item4):
    a=Mongo.Adddata(item.data,item.id,item.filename)
    return {'data':a}


@app.post('/Editjson',dependencies=[Depends(JWTBearer())])
def editjson(item:Item4):
    a=Mongo.Editdata(item.data,item.id,item.filename)
    return {'data':a}


@app.post('/deljson',dependencies=[Depends(JWTBearer())])
def Deljson(item:Item3):
    a=Mongo.deletedata(item.id)
    return{'data':'Successfully Deleted'}


@app.post('/Addcsvjson')
async def Addcsvjson(Data:Csvadd):
    a=Mongo.addcsv(name=Data.name,data=Data.data,id=Data.fileid)
    return a


@app.post('/Getcsvjson')
async def Getcsvjson(item:Item3):
    a=Mongo.Getcsvdata(item.id)
    return a


@app.post('/Updatecsvjson')
async def Updatecsvjson(item:Csvedit):
    print(item)
    a=Mongo.Updatecsv(data=item.data,id=item.id,fileid=item.fileid,name=item.name)
    return a


@app.post('/deletecsvjson')
async def Deletecsv(item:Csvdel):
    a=Mongo.Deletecsv(fileid=item.fileid,id=item.id )
    return a


@app.post("/signup")
def Signup(item: Item):
    jwt=Mongo.Signup(item.email,item.password,item.name)
    print(jwt)
    return jwt


@app.post("/signin")
def Signup(item: Item2):
    c=Mongo.signin(item.email,item.password)
    return c


# Google Signin
@app.post("/Gsignin")
def Signup(item: Item5):
    jwt=Mongo.Gsignin(item.client_name,item.email)
    print(jwt)
    return jwt


# Userid
@app.post('/id',dependencies=[Depends(JWTBearer())])
def userbyid(item:Item3):
    a=Mongo.Userbyid(item.id)
    return {'data': a}


# Time Management
@app.post('/Clockin')
def clockin(Data: CT):
    print(Data)
    time = Data.current_time
    result = Mongo.Clockin(userid=Data.userid, name=Data.name, time=time)
    return {"message":result}


@app.post('/Clockout')
def clockout(Data: CT):
    time = Data.current_time
    result = Mongo.Clockout(userid=Data.userid, name=Data.name, time=time)
    return {"message":result}




@app.post('/PreviousDayClockout')
def previous_day_clockout(Data: CT):
    result = PreviousDayClockout(userid=Data.userid, name=Data.name)
    return {"message": result}




# @app.post('/Clockout')
# def clockout(Data: CT):
#     total_hours_worked = Mongo.Clockout(userid=Data.userid,name=Data.name, time=Data.time)
#     return {"message": f"Total hours worked today: {total_hours_worked} hours"}


# Clockin Details
@app.get("/clock-records/{userid}")
async def get_clock_records(userid: str = Path(..., title="The name of the user whose clock records you want to fetch")):
    try:
        clock_records = attendance_details(userid)
        return {"clock_records": clock_records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Admin Dashboard Attendance
@app.get("/attendance/")
async def fetch_attendance_by_date():
    attendance_data = get_attendance_by_date()
    if not attendance_data:
        return "No attendance data found for the selected date"


    return {"attendance": attendance_data}


# Employee ID
@app.get("/get_EmployeeId/{name}")
async def get_employee_id(name: str = Path(..., title="The username of the user")):
    try:
        employee_id = get_employee_id_from_db(name)
        if employee_id:
            return {"Employee_ID": employee_id}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(500, str(e))




#Leave-request
#Leave-request
@app.post('/leave-request')
def leave_request(item: Item6):
    try:
       
        print(item.selectedDate)
        print(item.requestDate)


        # Add request time in the desired timezone
        time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")


        # Store the leave request in MongoDB
        result = Mongo.store_leave_request(
            item.userid,
            item.employeeName,
            time,
            item.leaveType,
            item.selectedDate,  # Formatted as DD-MM-YYYY
            item.requestDate,  # Formatted as DD-MM-YYYY
            item.reason,
        )


        return {"message": "Leave request stored successfully", "result": result}
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post('/Bonus-leave-request')
def bonus_leave_request(item: Item9):
    try:
        # Get the current time in IST
        time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")


        # Store bonus leave request
        result = store_sunday_request(
            item.userid,
            item.employeeName,
            time,
            item.leaveType,
            item.selectedDate,  # Formatted as DD-MM-YYYY
            item.reason,
            item.requestDate,  # Formatted as DD-MM-YYYY
        )


        return {"message": "Bonus leave request stored successfully", "result": result}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


# Leave History
@app.get("/leave-History/{userid}")
async def get_leave_History(userid: str = Path(..., title="The userid of the user")):
    try:
       
        leave_history = Mongo.normal_leave_details(userid)
        return {"leave_history" : leave_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# HR Page To Fetch Every Users Leave Requests
# HR endpoint - Uses get_user_leave_requests
@app.get("/all_users_leave_requests/")
async def fetch_user_leave_requests(selectedOption: str = Query(..., alias="selectedOption")):
    user_leave_requests = get_user_leave_requests(selectedOption) # HR sees recommended
    return {"user_leave_requests": user_leave_requests or []}


# Admin Page To Fetch Only Managers Leave Requests
# @app.get("/manager_leave_requests/")
# async def fetch_manager_leave_requests(selectedOption: str = Query(..., alias="selectedOption")):
#     user_leave_requests = get_manager_leave_requests(selectedOption)
#     if not user_leave_requests:
#         raise HTTPException(status_code=404, detail="No leave data found for the selected date")


#     return {"user_leave_requests": user_leave_requests}


# Admin Page To Fetch Only Managers Leave Requests
@app.get("/manager_leave_requests/")
async def fetch_manager_leave_requests(selectedOption: str = Query(..., alias="selectedOption")):
    user_leave_requests = get_manager_leave_requests(selectedOption) # Admin sees manager requests
    return {"user_leave_requests": user_leave_requests or []}


#TL,Manager Page To Fetch Only Users Leave Requests Under Their Team
@app.get("/only_users_leave_requests/")
async def fetch_users_leave_requests(selectedOption: str = Query(..., alias="selectedOption"), TL: str = Query(..., alias="TL")):
    user_leave_requests = get_only_user_leave_requests(selectedOption, TL) # Manager sees new requests
    return {"user_leave_requests": user_leave_requests or []}


#HR page
@app.get("/leave_update_reminder")
async def fetch_pending_leave():
    result = leave_update_notification()
    return result


#Admin page
@app.get("/managers_leave_recommend_reminder")
async def fetch_pending_leave():
    result = managers_leave_recommend_notification()
    return result


#TL page
@app.get("/leave_update_reminder")
async def fetch_pending_leave(TL: str = Query(..., alias="TL")):
    result = users_leave_recommend_notification(TL)
    return result


# HR Page Leave Responses
@app.put("/updated_user_leave_requests")
async def updated_user_leave_requests_status(leave_id: str = Form(...), status: str = Form(...)):
    try:
        response = updated_user_leave_requests_status_in_mongo(leave_id, status)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
# Admin And TL Leave Recommendation Responses
@app.put("/recommend_users_leave_requests")
async def recommend_managers_leave_requests_status(leave_id: str = Form(...), status: str = Form(...)):
    try:
        response = recommend_manager_leave_requests_status_in_mongo(leave_id, status)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete_leave_request")
async def delete_leave_request(item:DeleteLeave):
    try:
        def parse_date(date_str):
            try:
                # Attempt to parse as full timestamp with time and microseconds
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                try:
                    # Fallback to parsing as date-only
                    return datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"Invalid date format: {date_str}")


        # Parse selectedDate and requestDate
        selected_date_str = item.fromDate.rstrip('Z')
        request_date_str = item.requestDate.rstrip('Z')
        selected_date = parse_date(selected_date_str)
        request_date = parse_date(request_date_str)


        # Localize to UTC
        selected_date_utc = pytz.utc.localize(selected_date)
        request_date_utc = pytz.utc.localize(request_date)


        result = delete_leave(item.userid, selected_date_utc, request_date_utc, item.leavetype)
        return result


    except Exception as e:
        raise HTTPException(400, str(e))




# Remote Work Request


@app.post("/remote-work-request")
def remote_work_request(request: RemoteWorkRequest):
    try:
        # Add request time in IST
        time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")


        result = Mongo.store_remote_work_request(
            request.userid,
            request.employeeName,
            time,
            request.fromDate,
            request.toDate,
            request.requestDate,
            request.reason,
            request.ip
        )
        return result  # ✅ structured dict returned directly
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


 


# Remote Work History    
@app.get("/Remote-History/{userid}")
async def get_Remote_History(userid:str = Path(..., title="The name of the user whose Remote History you want to fetch")):
    try:
        Remote_History = Remote_History_Details(userid)
        return{"Remote_History": Remote_History}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


# HR Page User Remote Work Requests
@app.get("/remote_work_requests")
async def fetch_remote_work_requests():
    remote_work_requests = get_remote_work_requests()
    return {"remote_work_requests": remote_work_requests}


# Admin Page User Remote Work Requests
@app.get("/admin_page_remote_work_requests")
async def fetch_remote_work_requests():
    remote_work_requests = get_admin_page_remote_work_requests()
    return {"remote_work_requests": remote_work_requests}


# TL Page User Remote Work Requests
@app.get("/TL_page_remote_work_requests")
async def fetch_remote_work_requests(TL: str = Query(..., alias="TL")):
    remote_work_requests = get_TL_page_remote_work_requests(TL)
    return {"remote_work_requests": remote_work_requests}




# HR Remote Work Responses
@app.put("/update_remote_work_requests")
async def update_remote_work_request_status(userid: str = Form(...), status: str = Form(...), id: str = Form(...)):
    try:
        updated = update_remote_work_request_status_in_mongo(userid, status, id)
        if updated:
            return {"message": "Status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HR Remote Work Responses
@app.put("/recommend_remote_work_requests")
async def update_remote_work_request_status(userid: str = Form(...), status: str = Form(...), id: str = Form(...)):
    try:
        print(id)
        updated = update_remote_work_request_recommend_in_mongo(userid, status, id)
        if updated:
            return {"message": "Recommend status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
# Admin Page User Leave History
@app.get("/approved-leave-history/{name}")
def get_leave_history(name: str = Path(..., title= "Team lead name")):
    leave_history = get_approved_leave_history(name)
    return {"leave_history": leave_history}


# Admin ID
@app.post('/id',dependencies=[Depends(JWTBearer())])
def adminid(item:Item3):
    a=Mongo.adminbyid(item.id)
    return {'data': a}


@app.post("/admin_signup")
def adminid_Signup(item: Item):
    jwt=Mongo.admin_Signup(item.email,item.password,item.name,item.phone,item.position,item.date_of_joining)
    return jwt


@app.post("/admin_signin")
def admin_Signup(item: Item2):
    jwt=Mongo.admin_signin(item.email,item.password)
    email = jwt.get('email')
    admin = get_admin_info(email)
    print(jwt)
    return { "jwt": jwt, "Name": admin.get('name'), "Email": admin.get('email'), "Phone no": admin.get('phone'), "Position": admin.get('position'), "Date of joining": admin.get('date_of_joining')}


# Admin Signin
@app.post("/admin_Gsignin")
def admin_signup(item: Item5):
    print(item.dict())
    jwt=Mongo.admin_Gsignin(item.client_name,item.email)
    print(jwt)
    return jwt




from datetime import datetime
import pytz
from fastapi import HTTPException


def parse_and_format_date(date_str):
    """Parses various date formats and converts them to DD-MM-YYYY format."""
    if not date_str:
        return None


    date_str = date_str.rstrip('Z')  # Remove 'Z' if present
    formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]  # Possible formats


    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%d-%m-%Y")  # Convert to DD-MM-YYYY
        except ValueError:
            continue  # Try next format if parsing fails


    raise ValueError(f"Invalid date format: {date_str}")


@app.post('/Other-leave-request')
def leave_request(item: Item7):
    try:
        # Add request time in the desired timezone
        time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")


        # Store the leave request in MongoDB
        result = store_Other_leave_request(
            item.userid,
            item.employeeName,
            time,  # Use the generated time
            item.leaveType,
            item.selectedDate,  # Formatted as DD-MM-YYYY
            item.ToDate,  # Formatted as DD-MM-YYYY
            item.requestDate,  # Formatted as DD-MM-YYYY
            item.reason,
        )


        return {"message": "Leave request stored successfully", "result": result}
    except Exception as e:
        raise HTTPException(400, str(e))
   
@app.post('/Permission-request')
def leave_request(item: Item8):
    try:
        result = store_Permission_request(
                item.userid,
                item.employeeName,
                item.time,
                item.leaveType,
                item.selectedDate,
                item.requestDate,
                item.timeSlot,
                item.reason,
            )


        return {"message": "Leave request stored successfully", "result": result}
    except Exception as e:
        raise HTTPException(400, str(e))
   
@app.get("/Other-leave-history/{userid}")
async def get_other_leave_history(userid: str = Path(..., title="The ID of the user")):
    try:
        # Call your function to get the leave history for the specified user
        leave_history = Otherleave_History_Details(userid)


        # Return the leave history
        return {"leave_history": leave_history}
    except Exception as e:
        # If an exception occurs, return a 500 Internal Server Error
        raise HTTPException(status_code=500, detail=str(e))
   
   
@app.get("/Permission-history/{userid}")
async def get_Permission_history(userid: str = Path(..., title="The ID of the user")):
    try:
        # Call your function to get the leave history for the specified user
        leave_history = Permission_History_Details(userid)


        # Return the leave history
        return {"leave_history": leave_history}
    except Exception as e:
        # If an exception occurs, return a 500 Internal Server Error
        raise HTTPException(status_code=500, detail=str(e))

# ============== LEAVE DETAILS ENDPOINTS ==============

@app.get("/leave_details/user/{userid}")
async def get_user_leave_details(
    userid: str,
    status_filter: str = Query("All", alias="statusFilter"),
    leave_type_filter: str = Query("All", alias="leaveTypeFilter")
):
    """Get all leave details for a specific user"""
    try:
        match_conditions = {"userid": userid}
        
        if status_filter and status_filter != "All":
            if status_filter == "Pending":
                match_conditions["status"] = {"$exists": False}
            else:
                match_conditions["status"] = status_filter
        
        if leave_type_filter and leave_type_filter != "All":
            match_conditions["leaveType"] = leave_type_filter
        
        leave_details = list(Leave.find(match_conditions))
        
        # Convert ObjectId and format dates
        for leave in leave_details:
            leave["_id"] = str(leave["_id"])
            if "selectedDate" in leave and leave["selectedDate"]:
                leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            if "requestDate" in leave and leave["requestDate"]:
                leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
            if "ToDate" in leave and leave["ToDate"]:
                leave["ToDate"] = leave["ToDate"].strftime("%d-%m-%Y")
        
        return {"leave_details": leave_details}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== REMOTE WORK ENDPOINTS ==============

@app.get("/remote_work_details/user/{userid}")
async def get_user_remote_work_details(
    userid: str,
    status_filter: str = Query("All", alias="statusFilter")
):
    """Get all remote work details for a specific user"""
    try:
        match_conditions = {"userid": userid}
        
        if status_filter and status_filter != "All":
            if status_filter == "Pending":
                match_conditions["status"] = {"$exists": False}
                match_conditions["Recommendation"] = {"$exists": False}
            elif status_filter == "Recommended":
                match_conditions["Recommendation"] = "Recommend"
            else:
                match_conditions["status"] = status_filter
        
        remote_work_details = list(RemoteWork.find(match_conditions))
        
        # Convert ObjectId and format dates
        for remote_work in remote_work_details:
            remote_work["_id"] = str(remote_work["_id"])
            if "fromDate" in remote_work and remote_work["fromDate"]:
                remote_work["fromDate"] = remote_work["fromDate"].strftime("%d-%m-%Y")
            if "toDate" in remote_work and remote_work["toDate"]:
                remote_work["toDate"] = remote_work["toDate"].strftime("%d-%m-%Y")
            if "requestDate" in remote_work and remote_work["requestDate"]:
                remote_work["requestDate"] = remote_work["requestDate"].strftime("%d-%m-%Y")
        
        return {"remote_work_details": remote_work_details}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========all
@app.get("/manager/leave_details/{user_id}")
async def get_manager_team_leave_details(
    user_id: str,
    statusFilter: Optional[str] = Query(None),
    leaveTypeFilter: Optional[str] = Query(None),
    departmentFilter: Optional[str] = Query(None)
):
    """Get leave details for team members under a specific manager"""
    try:
        # First, verify the manager exists and get their info
        manager = Users.find_one({"_id": ObjectId(user_id)})
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        manager_name = manager.get("name")
        if not manager_name:
            raise HTTPException(status_code=400, detail="Manager name not found")
        
        # Build the aggregation pipeline
        pipeline = []
        
        # Convert userid to ObjectId if it's a string
        pipeline.append({
            "$addFields": {
                "userid_as_objectid": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$userid"}, "objectId"]},
                        "then": "$userid",
                        "else": {"$toObjectId": "$userid"}
                    }
                }
            }
        })
        
        # Join with Users collection
        pipeline.append({
            "$lookup": {
                "from": "Users",
                "localField": "userid_as_objectid",
                "foreignField": "_id",
                "as": "user_info"
            }
        })
        
        # Unwind the user_info array
        pipeline.append({"$unwind": "$user_info"})
        
        # Filter to only show team members under this manager
        base_match = {
            "user_info.TL": manager_name,  # Team members have this manager as TL
            "user_info.position": {"$ne": "Manager"}  # Exclude other managers
        }
        
        # Add additional filters
        if departmentFilter and departmentFilter != "All":
            base_match["user_info.department"] = departmentFilter
        
        if statusFilter and statusFilter != "All":
            if statusFilter == "Pending":
                base_match["status"] = {"$exists": False}
            else:
                base_match["status"] = statusFilter
        
        if leaveTypeFilter and leaveTypeFilter != "All":
            base_match["leaveType"] = leaveTypeFilter
        
        # Apply the match conditions
        pipeline.append({"$match": base_match})
        
        # Add employee info fields to output
        pipeline.append({
            "$addFields": {
                "employeeName": "$user_info.name",
                "position": "$user_info.position",
                "department": "$user_info.department",
                "email": "$user_info.email",
                "teamLeader": "$user_info.TL"
            }
        })
        
        # Remove temporary fields
        pipeline.append({
            "$project": {
                "user_info": 0,
                "userid_as_objectid": 0
            }
        })
        
        # Sort by request date (most recent first)
        pipeline.append({
            "$sort": {"requestDate": -1}
        })
        
        # Execute aggregation
        leave_details = list(Leave.aggregate(pipeline))
        
        # Format dates and ObjectIds
        for leave in leave_details:
            leave["_id"] = str(leave["_id"])
            if "selectedDate" in leave and leave["selectedDate"]:
                leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            if "requestDate" in leave and leave["requestDate"]:
                leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
            if "ToDate" in leave and leave["ToDate"]:
                leave["ToDate"] = leave["ToDate"].strftime("%d-%m-%Y")
        
        return {
            "manager_info": {
                "user_id": user_id,
                "manager_name": manager_name
            },
            "leave_details": leave_details,
            "total_count": len(leave_details),
            "filters_applied": {
                "status": statusFilter or "All",
                "leave_type": leaveTypeFilter or "All",
                "department": departmentFilter or "All"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/manager/remote_work_details/{user_id}")
async def get_manager_team_remote_work_details(
    user_id: str,
    statusFilter: Optional[str] = Query(None),
    departmentFilter: Optional[str] = Query(None)
):
    """Get remote work details for team members under a specific manager"""
    try:
        # First, verify the manager exists and get their info
        manager = Users.find_one({"_id": ObjectId(user_id)})
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        manager_name = manager.get("name")
        if not manager_name:
            raise HTTPException(status_code=400, detail="Manager name not found")
        
        # Build the aggregation pipeline
        pipeline = []
        
        # Convert userid to ObjectId if it's a string
        pipeline.append({
            "$addFields": {
                "userid_as_objectid": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$userid"}, "objectId"]},
                        "then": "$userid",
                        "else": {"$toObjectId": "$userid"}
                    }
                }
            }
        })
        
        # Join with Users collection
        pipeline.append({
            "$lookup": {
                "from": "Users",
                "localField": "userid_as_objectid",
                "foreignField": "_id",
                "as": "user_info"
            }
        })
        
        # Unwind the user_info array
        pipeline.append({"$unwind": "$user_info"})
        
        # Filter to only show team members under this manager
        base_match = {
            "user_info.TL": manager_name,  # Team members have this manager as TL
            "user_info.position": {"$ne": "Manager"}  # Exclude other managers
        }
        
        # Add additional filters
        if departmentFilter and departmentFilter != "All":
            base_match["user_info.department"] = departmentFilter
        
        if statusFilter and statusFilter != "All":
            if statusFilter == "Pending":
                base_match["status"] = {"$exists": False}
                base_match["Recommendation"] = {"$exists": False}
            elif statusFilter == "Recommended":
                base_match["Recommendation"] = "Recommend"
            else:
                base_match["status"] = statusFilter
        
        # Apply the match conditions
        pipeline.append({"$match": base_match})
        
        # Add employee info fields to output
        pipeline.append({
            "$addFields": {
                "employeeName": "$user_info.name",
                "position": "$user_info.position",
                "department": "$user_info.department",
                "email": "$user_info.email",
                "teamLeader": "$user_info.TL"
            }
        })
        
        # Remove temporary fields
        pipeline.append({
            "$project": {
                "user_info": 0,
                "userid_as_objectid": 0
            }
        })
        
        # Sort by request date (most recent first)
        pipeline.append({
            "$sort": {"requestDate": -1}
        })
        
        # Execute aggregation
        remote_work_details = list(RemoteWork.aggregate(pipeline))
        
        # Format dates and ObjectIds
        for remote_work in remote_work_details:
            remote_work["_id"] = str(remote_work["_id"])
            if "fromDate" in remote_work and remote_work["fromDate"]:
                remote_work["fromDate"] = remote_work["fromDate"].strftime("%d-%m-%Y")
            if "toDate" in remote_work and remote_work["toDate"]:
                remote_work["toDate"] = remote_work["toDate"].strftime("%d-%m-%Y")
            if "requestDate" in remote_work and remote_work["requestDate"]:
                remote_work["requestDate"] = remote_work["requestDate"].strftime("%d-%m-%Y")
        
        return {
            "manager_info": {
                "user_id": user_id,
                "manager_name": manager_name
            },
            "remote_work_details": remote_work_details,
            "total_count": len(remote_work_details),
            "filters_applied": {
                "status": statusFilter or "All",
                "department": departmentFilter or "All"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/manager/team_members/{user_id}")
async def get_manager_team_members(user_id: str):
    """Get list of team members under a specific manager"""
    try:
        # Get manager info
        manager = Users.find_one({"_id": ObjectId(user_id)})
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        manager_name = manager.get("name")
        
        # Get team members under this manager
        team_members = list(Users.find(
            {
                "TL": manager_name,
                "position": {"$ne": "Manager"}
            },
            {
                "_id": 1,
                "name": 1,
                "email": 1,
                "position": 1,
                "department": 1,
                "phone": 1,
                "status": 1
            }
        ))
        
        # Format the response
        formatted_members = []
        for member in team_members:
            formatted_members.append({
                "userid": str(member["_id"]),
                "name": member.get("name"),
                "email": member.get("email"),
                "position": member.get("position"),
                "department": member.get("department"),
                "phone": member.get("phone"),
                "status": member.get("status", "Active")
            })
        
        return {
            "manager_info": {
                "user_id": user_id,
                "manager_name": manager_name
            },
            "team_members": formatted_members,
            "total_count": len(formatted_members)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/leave_details/user/")
async def get_all_users_leave_details(
    statusFilter: Optional[str] = Query(None),
    leaveTypeFilter: Optional[str] = Query(None),
    positionFilter: Optional[str] = Query(None),
    departmentFilter: Optional[str] = Query(None)
):
    """Get leave details for ALL users (no specific userid required)"""
    try:
        # Build the aggregation pipeline with flexible userid matching
        pipeline = []
        
        # Convert userid to ObjectId if it's a string
        pipeline.append({
            "$addFields": {
                "userid_as_objectid": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$userid"}, "objectId"]},
                        "then": "$userid",
                        "else": {"$toObjectId": "$userid"}
                    }
                }
            }
        })
        
        # Join with Users collection
        pipeline.append({
            "$lookup": {
                "from": "Users",
                "localField": "userid_as_objectid",
                "foreignField": "_id",
                "as": "user_info"
            }
        })
        
        # Handle cases where user info might not be found
        pipeline.append({
            "$addFields": {
                "user_info": {
                    "$cond": {
                        "if": {"$eq": [{"$size": "$user_info"}, 0]},
                        "then": [{"name": "Unknown User", "position": "Unknown", "department": "Unknown", "email": "Unknown", "TL": "Unknown"}],
                        "else": "$user_info"
                    }
                }
            }
        })
        
        # Unwind the user_info array
        pipeline.append({"$unwind": "$user_info"})
        
        # Build match conditions for filtering
        match_conditions = {}
        
        if positionFilter and positionFilter != "All":
            match_conditions["user_info.position"] = positionFilter
            
        if departmentFilter and departmentFilter != "All":
            match_conditions["user_info.department"] = departmentFilter
        
        if statusFilter and statusFilter != "All":
            if statusFilter == "Pending":
                match_conditions["status"] = {"$exists": False}
            else:
                match_conditions["status"] = statusFilter
        
        if leaveTypeFilter and leaveTypeFilter != "All":
            match_conditions["leaveType"] = leaveTypeFilter
        
        # Add match stage if there are conditions
        if match_conditions:
            pipeline.append({"$match": match_conditions})
        
        # Add employee info fields to output
        pipeline.append({
            "$addFields": {
                "employeeName": "$user_info.name",
                "position": "$user_info.position",
                "department": "$user_info.department",
                "email": "$user_info.email",
                "teamLeader": "$user_info.TL"
            }
        })
        
        # Remove temporary fields
        pipeline.append({
            "$project": {
                "user_info": 0,
                "userid_as_objectid": 0
            }
        })
        
        # Sort by request date (most recent first)
        pipeline.append({
            "$sort": {"requestDate": -1}
        })
        
        # Execute aggregation
        leave_details = list(Leave.aggregate(pipeline))
        
        # Format dates and ObjectIds
        for leave in leave_details:
            leave["_id"] = str(leave["_id"])
            if "selectedDate" in leave and leave["selectedDate"]:
                leave["selectedDate"] = leave["selectedDate"].strftime("%d-%m-%Y")
            if "requestDate" in leave and leave["requestDate"]:
                leave["requestDate"] = leave["requestDate"].strftime("%d-%m-%Y")
            if "ToDate" in leave and leave["ToDate"]:
                leave["ToDate"] = leave["ToDate"].strftime("%d-%m-%Y")
        
        return {
            "leave_details": leave_details,
            "total_count": len(leave_details),
            "filters_applied": {
                "position": positionFilter or "All",
                "status": statusFilter or "All",
                "leave_type": leaveTypeFilter or "All",
                "department": departmentFilter or "All"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/remote_work_details/user/")
async def get_all_users_remote_work_details(
    statusFilter: Optional[str] = Query(None),
    positionFilter: Optional[str] = Query(None),
    departmentFilter: Optional[str] = Query(None)
):
    """Get remote work details for ALL users (no specific userid required)"""
    try:
        # Build the aggregation pipeline with flexible userid matching
        pipeline = []
        
        # Convert userid to ObjectId if it's a string
        pipeline.append({
            "$addFields": {
                "userid_as_objectid": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$userid"}, "objectId"]},
                        "then": "$userid",
                        "else": {"$toObjectId": "$userid"}
                    }
                }
            }
        })
        
        # Join with Users collection
        pipeline.append({
            "$lookup": {
                "from": "Users",
                "localField": "userid_as_objectid",
                "foreignField": "_id",
                "as": "user_info"
            }
        })
        
        # Handle cases where user info might not be found
        pipeline.append({
            "$addFields": {
                "user_info": {
                    "$cond": {
                        "if": {"$eq": [{"$size": "$user_info"}, 0]},
                        "then": [{"name": "Unknown User", "position": "Unknown", "department": "Unknown", "email": "Unknown", "TL": "Unknown"}],
                        "else": "$user_info"
                    }
                }
            }
        })
        
        # Unwind the user_info array
        pipeline.append({"$unwind": "$user_info"})
        
        # Build match conditions for filtering
        match_conditions = {}
        
        if positionFilter and positionFilter != "All":
            match_conditions["user_info.position"] = positionFilter
            
        if departmentFilter and departmentFilter != "All":
            match_conditions["user_info.department"] = departmentFilter
        
        if statusFilter and statusFilter != "All":
            if statusFilter == "Pending":
                match_conditions["status"] = {"$exists": False}
                match_conditions["Recommendation"] = {"$exists": False}
            elif statusFilter == "Recommended":
                match_conditions["Recommendation"] = "Recommend"
            else:
                match_conditions["status"] = statusFilter
        
        # Add match stage if there are conditions
        if match_conditions:
            pipeline.append({"$match": match_conditions})
        
        # Add employee info fields to output
        pipeline.append({
            "$addFields": {
                "employeeName": "$user_info.name",
                "position": "$user_info.position",
                "department": "$user_info.department",
                "email": "$user_info.email",
                "teamLeader": "$user_info.TL"
            }
        })
        
        # Remove temporary fields
        pipeline.append({
            "$project": {
                "user_info": 0,
                "userid_as_objectid": 0
            }
        })
        
        # Sort by request date (most recent first)
        pipeline.append({
            "$sort": {"requestDate": -1}
        })
        
        # Execute aggregation
        remote_work_details = list(RemoteWork.aggregate(pipeline))
        
        # Format dates and ObjectIds
        for remote_work in remote_work_details:
            remote_work["_id"] = str(remote_work["_id"])
            if "fromDate" in remote_work and remote_work["fromDate"]:
                remote_work["fromDate"] = remote_work["fromDate"].strftime("%d-%m-%Y")
            if "toDate" in remote_work and remote_work["toDate"]:
                remote_work["toDate"] = remote_work["toDate"].strftime("%d-%m-%Y")
            if "requestDate" in remote_work and remote_work["requestDate"]:
                remote_work["requestDate"] = remote_work["requestDate"].strftime("%d-%m-%Y")
        
        return {
            "remote_work_details": remote_work_details,
            "total_count": len(remote_work_details),
            "filters_applied": {
                "position": positionFilter or "All",
                "status": statusFilter or "All",
                "department": departmentFilter or "All"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_all_users")
async def get_all_users_route():
        # Fetch all users using the function from Mongo.py
        users = get_all_users()
        if users:
            return users  # Return the list of users
        else:
            raise HTTPException(status_code=404, detail="No users found")


@app.post("/add_task")
async def add_task(item:Tasklist):
    try:
        # Parse the date to ensure it's in the correct format
        parsed_date = datetime.strptime(item.date, "%Y-%m-%d").strftime("%d-%m-%Y")
        due_date = datetime.strptime(item.due_date, "%Y-%m-%d").strftime("%d-%m-%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use dd-mm-yyyy.")
    result = add_task_list(item.task, item.userid, parsed_date, due_date)
    return result


@app.post("/manager_task_assign")
async def task_assign(item:SingleTaskAssign):
    # Parse the date to ensure it's in the correct format
    parsed_date = datetime.strptime(item.date, "%Y-%m-%d").strftime("%d-%m-%Y")
    due_date = datetime.strptime(item.due_date, "%Y-%m-%d").strftime("%d-%m-%Y")
    result = manager_task_assignment(item.task, item.userid, item.TL, parsed_date, due_date)
    return result




@app.put("/edit_task")
async def edit_task(item: Taskedit):
    today = datetime.today()
    formatted_date = today.strftime("%d-%m-%Y")
    result = edit_the_task(item.taskid, item.userid, formatted_date, item.due_date, item.updated_task, item.status)
    return {"result": result}




@app.delete("/task_delete/{taskid}")
async def task_delete(taskid: str):
    result = delete_a_task(taskid)
    return {"result": result}


@app.get("/get_tasks/{userid}")
async def get_tasks(userid: str):
    result = get_the_tasks(userid)
    if not result:
        return {"message": "No tasks found for the given user"}
    return result


@app.get("/get_tasks/{userid}/{date}")
async def get_tasks(userid: str, date: str):
    result = get_the_tasks(userid, date)
    if not result:
        return {"message": "No tasks found for the given user/date"}
    return result




@app.get("/get_single_task/{taskid}")
async def get_task(taskid : str):
    result = get_single_task(taskid)
    if not result:
        return {"message": "No tasks found for the given task id"}
    return result




# @app.get("/get_user/{userid}")
# def get_user(userid: str):
#     result = get_user_info(userid)
#     if result:
#         return result
#     return {"error": "User not found", "userid": userid}


@app.get("/get_user/{userid}")
def get_user(userid: str):
    print("Searching user ID:", userid, "in collection:", Users.name)


    try:
        obj_id = ObjectId(userid)
    except Exception as e:
        return JSONResponse(content={"error": f"Invalid ID format: {str(e)}", "userid": userid})


    user = Users.find_one({"_id": obj_id}, {"password": 0})


    if user:
        # Convert ObjectId to string for JSON
        user["_id"] = str(user["_id"])
        return JSONResponse(content=user)
    else:
        print("User not found in collection!")
        return JSONResponse(content={"error": "User not found", "userid": userid})


# @app.put("/edit_employee")
# def add_employee(item:EditEmployee):
#  result = edit_an_employee(item.dict())
#  return result


@app.put("/edit_employee")
def edit_employee(item: EditEmployee):
    try:
        # Convert Pydantic model to dict
        employee_dict = item.dict()
       
        # Call the edit function
        result = edit_an_employee(employee_dict)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in edit_employee endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/get_managers_list")
async def fetch_managers():
 result = get_managers()
 return result




@app.get("/get_admin/{userid}")
def get_admin(userid: str):
    result = Mongo.get_admin_information(userid)
    return result


@app.post("/add_employee")
def add_employee(item:AddEmployee):
    result = add_an_employee(item.dict())
    return result




@app.get("/auto_approve_manager_leaves")
async def trigger_auto_approval():
    result = auto_approve_manager_leaves()
    return result


@app.get("/get_team_members")
def get_members(TL: str = Query(..., alias="TL")):
    result = get_team_members(TL)
    return result


@app.post("/task_assign_to_multiple_members")
def task_assign(item: Taskassign):
    print(item.Task_details)
    result = task_assign_to_multiple_users(item.Task_details)
    return {"inserted_ids": result}


@app.get("/get_assigned_task")
def get_assigned_tasks(TL: str = Query(..., alias="TL"), userid: str | None = Query(None, alias = "userid")):
    result = assigned_task(TL, userid)
    return result


@app.get("/ip-info")
def fetch_ip_info():
    return {
        "public_ip": get_public_ip(),
        "local_ip": get_local_ip()
}


if __name__ == "__main__":
    # Get absolute paths to the SSL certificate and key files
    key_file_path = os.path.join(os.path.dirname(__file__), '../certificates/key.pem')
    cert_file_path = os.path.join(os.path.dirname(__file__), '../certificates/cert.pem')


    uvicorn.run(
        "Server:app",  # Replace with your actual file/module name
        host="0.0.0.0",  # Listen on all network interfaces (public access)
        port=8000,  # Or another port like 4433 if needed
        ssl_keyfile=key_file_path,  # Path to your private key
        ssl_certfile=cert_file_path  # Path to your certificate
    )


#---------------------------------------------------------------------------------------------------------




# Holiday Management Endpoints
@app.post("/api/holidays/{year}")
def add_holidays(year: int, body: HolidayYear):
    """Admin only - Add holidays for a specific year"""
    if body.year != year:
        raise HTTPException(status_code=400, detail="Year mismatch between path and body")
   
    insert_holidays(year, [h.dict() for h in body.holidays])
    return {"message": f"Holidays saved for {year}"}


@app.get("/api/holidays/{year}")
def get_holidays_for_year(year: int):
    holiday_doc = get_holidays(year)
    if not holiday_doc:
        return {"year": year, "holidays": []}
   
    # Convert ObjectId to string if exists
    if "_id" in holiday_doc:
        holiday_doc["_id"] = str(holiday_doc["_id"])
   
    return holiday_doc




@app.get("/working-days/{year}")
def get_working_days(year: int):
    """Get working days calculation for a year"""
    holiday_doc = get_holidays(year)
    if not holiday_doc:
        raise HTTPException(status_code=404, detail=f"No holidays defined for {year}")
   
    holidays = holiday_doc["holidays"]
    working_days = calculate_working_days(year, holidays)
   
    return {
        "year": year,
        "totalWorkingDays": len(working_days),
        "workingDays": working_days,
        "holidays": holidays
    }

@app.get("/attendance/user/{userid}/year/{year}")
async def get_user_attendance_by_year(userid: str, year: int):
    """User can see their attendance stats for a specific year"""
    try:
        stats = calculate_user_attendance_stats(userid, year)
        user = Users.find_one({"_id": ObjectId(userid)}, {"name": 1, "email": 1})
        
        return {
            "user_info": {
                "userid": userid,
                "name": user.get("name", "Unknown") if user else "Unknown",
                "email": user.get("email", "") if user else ""
            },
            "attendance_stats": stats,
            "year": year
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


@app.get("/attendance/team/{team_leader}")
async def get_team_attendance(team_leader: str, year: int = Query(None)):
    """Team Leader can see their team members' attendance"""
    try:
        if year is None:
            year = date.today().year
        
        team_stats = get_team_attendance_stats(team_leader, year)
        return team_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        
# User Level Endpoints (Lowest Level - Own Data Only)
@app.get("/attendance/user/{userid}")
async def get_user_attendance(userid: str):
    """User can see only their own attendance statistics"""
    try:
        dashboard_data = get_user_attendance_dashboard(userid)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/attendance/team/{team_leader}/member/{userid}")
async def get_team_member_attendance(team_leader: str, userid: str, year: int = Query(None)):
    """Team Leader can see specific team member's attendance"""
    try:
        if year is None:
            year = date.today().year
       
        # Verify that the user belongs to this team leader
        user = Users.find_one({"_id": ObjectId(userid), "TL": team_leader})
        if not user:
            raise HTTPException(status_code=403, detail="User is not in your team")
       
        stats = calculate_user_attendance_stats(userid, year)
        stats["user_info"] = {
            "name": user.get("name"),
            "email": user.get("email"),
            "department": user.get("department"),
            "position": user.get("position")
        }
       
        return {
            "team_leader": team_leader,
            "member_stats": stats,
            "year": year
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Manager Level Endpoints
@app.get("/attendance/manager/{manager_userid}")
async def get_manager_attendance_overview(manager_userid: str, year: int = Query(None)):
    """Manager can see all teams under them"""
    try:
        if year is None:
            year = date.today().year
       
        manager_stats = get_manager_team_attendance(manager_userid, year)
        return manager_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/attendance/department/{department}")
async def get_department_attendance(department: str, year: int = Query(None)):
    """Manager can see department-wise attendance"""
    try:
        if year is None:
            year = date.today().year
       
        dept_stats = get_department_attendance_stats(department, year)
        return dept_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Admin Level Endpoints (Highest Level - Can See Everything)
@app.get("/attendance/admin/overview")
async def get_admin_attendance_overview(year: int = Query(None)):
    """Admin can see company-wide attendance statistics"""
    try:
        if year is None:
            year = date.today().year
       
        company_stats = get_department_attendance_stats(year=year)  # All departments
        return company_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Utility Endpoints
@app.post("/attendance/refresh-stats")
async def refresh_attendance_stats():
    """Manually trigger attendance statistics refresh (Admin only)"""
    try:
        updated_count = update_daily_attendance_stats()
        return {"message": f"Successfully updated attendance stats for {updated_count} users"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/attendance/summary/{userid}")
async def get_attendance_summary(userid: str):
    """Get a quick summary of user's attendance (for dashboard cards)"""
    try:
        current_year = date.today().year
        stats = calculate_user_attendance_stats(userid, current_year)
       
        return {
            "userid": userid,
            "current_year": current_year,
            "attendance_percentage": stats["attendance_percentage"],
            "present_days": stats["present_days"],
            "total_working_days": stats["total_working_days"],
            "leave_days_taken": stats["leave_days_taken"],
            "leave_percentage": stats["leave_percentage"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Role-based access endpoint
@app.get("/attendance/dashboard/{userid}")
async def get_role_based_attendance_dashboard(userid: str, year: int = Query(None)):
    """Get attendance dashboard based on user's role"""
    try:
        if year is None:
            year = date.today().year
       
        # Get user info to determine role
        user = Users.find_one({"_id": ObjectId(userid)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
       
        position = user.get("position", "User").lower()
       
        if position == "admin":
            return await get_admin_attendance_overview(year)
        elif position == "hr":
            return await get_hr_attendance_analytics(year)
        elif position == "manager":
            return await get_manager_attendance_overview(userid, year)
        elif position == "tl" or position == "team lead":
            team_leader_name = user.get("name")
            return await get_team_attendance(team_leader_name, year)
        else:  # Regular user
            return await get_user_attendance(userid)
           
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
