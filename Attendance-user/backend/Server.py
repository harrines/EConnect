from Mongo import Otherleave_History_Details,Permission_History_Details,normal_leave_details,store_Other_leave_request,get_approved_leave_history,get_remote_work_requests,attendance_details,leave_History_Details,Remote_History_Details,get_attendance_by_date,update_remote_work_request_status_in_mongo,updated_user_leave_requests_status_in_mongo,get_user_leave_requests, get_employee_id_from_db,store_Permission_request, get_all_users, get_admin_info, add_task_list, edit_the_task, delete_a_task, get_the_tasks, delete_leave, get_user_info, store_sunday_request, get_admin_info, add_an_employee, PreviousDayClockout, auto_clockout, add_a_manager, leave_update_notification, recommend_manager_leave_requests_status_in_mongo, get_manager_leave_requests, get_only_user_leave_requests, get_admin_page_remote_work_requests, update_remote_work_request_recommend_in_mongo, get_TL_page_remote_work_requests, users_leave_recommend_notification, managers_leave_recommend_notification,auto_approve_manager_leaves
from model import Item4,Item,Item2,Item3,Csvadd,Csvedit,Csvdel,CT,Item5,Item6,Item9,RemoteWorkRequest,Item7,Item8, Tasklist, Taskedit, Deletetask, Gettasks, DeleteLeave, Item9, AddEmployee
from fastapi import FastAPI, HTTPException,Path,Query, HTTPException,Form, Request
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI,Body
from auth.auth_bearer import JWTBearer
from http.client import HTTPException
from datetime import datetime, timedelta, date
from dateutil import parser
from typing import Union, Dict
import uvicorn
import Mongo
import pytz
from typing import List

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

# Start the scheduler
scheduler.start()

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
async def fetch_attendance_by_date(date: str = Query(...)):
    try:
        formatted_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format. Use yyyy-MM-dd")

    attendance_data = get_attendance_by_date(formatted_date)
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

# Leave Management

@app.post('/leave-request')
def leave_request(item: Item6):
    try:
        # Adjust parsing to handle both complete and date-only formats
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
        selected_date_str = item.selectedDate.rstrip('Z')
        request_date_str = item.requestDate.rstrip('Z')
        selected_date = parse_date(selected_date_str)
        request_date = parse_date(request_date_str)

        # Localize to UTC
        selected_date_utc = pytz.utc.localize(selected_date)
        request_date_utc = pytz.utc.localize(request_date)

        # Add request time in the desired timezone
        time = (datetime.now(pytz.timezone("Asia/Kolkata"))).strftime("%I:%M:%S %p")

        # Store the leave request in MongoDB
        result = Mongo.store_leave_request(
            item.userid,
            item.employeeName,
            time,
            item.leaveType,
            selected_date_utc,
            request_date_utc,
            item.reason,
            item.status,
        )

        return {"message": "Leave request stored successfully", "result": result}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post('/Bonus-leave-request')
def leave_request(item: Item9):
    try:
        # Helper function to parse dates
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                return datetime.strptime(date_str, "%Y-%m-%d")

        # Parse and localize dates
        selected_date = pytz.utc.localize(parse_date(item.selectedDate.rstrip('Z')))
        request_date = pytz.utc.localize(parse_date(item.requestDate.rstrip('Z')))
        time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")

        # Store leave request
        result = store_sunday_request(
            item.userid,
            item.employeeName,
            time,
            item.leaveType,
            selected_date,
            item.reason,
            request_date,
        )

        return {"message": "Combo request processed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# # Leave History

@app.get("/leave-History/{userid}")
async def get_leave_History(userid: str = Path(..., title="The userid of the user")):
    try:
        
        leave_history = Mongo.normal_leave_details(userid)
        return {"leave_history" : leave_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HR Page To Fetch Every Users Leave Requests
@app.get("/all_users_leave_requests/")
async def fetch_user_leave_requests(requestDate: str = Query(..., alias="requestDate"), selectedOption: str = Query(..., alias="selectedOption")):
    try:
        formatted_date = datetime.strptime(requestDate, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format. Use yyyy-MM-dd")

    user_leave_requests = get_user_leave_requests(formatted_date, selectedOption)
    if not user_leave_requests:
        raise HTTPException(status_code=404, detail="No leave data found for the selected date")

    return {"user_leave_requests": user_leave_requests}

# Admin Page To Fetch Only Managers Leave Requests 
@app.get("/manager_leave_requests/")
async def fetch_manager_leave_requests(requestDate: str = Query(..., alias="requestDate"), selectedOption: str = Query(..., alias="selectedOption")):
    try:
        formatted_date = datetime.strptime(requestDate, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format. Use yyyy-MM-dd")

    user_leave_requests = get_manager_leave_requests(formatted_date, selectedOption)
    if not user_leave_requests:
        raise HTTPException(status_code=404, detail="No leave data found for the selected date")

    return {"user_leave_requests": user_leave_requests}

#TL Page To Fetch Only Users Leave Requests Under Their Team
@app.get("/only_users_leave_requests/")
async def fetch_users_leave_requests(requestDate: str = Query(..., alias="requestDate"), selectedOption: str = Query(..., alias="selectedOption"), TL: str = Query(..., alias="TL")):
    try:
        formatted_date = datetime.strptime(requestDate, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format. Use yyyy-MM-dd")

    user_leave_requests = get_only_user_leave_requests(formatted_date, selectedOption, TL)
    if not user_leave_requests:
        raise HTTPException(status_code=404, detail="No leave data found for the selected date")

    return {"user_leave_requests": user_leave_requests}

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
        from_date_utc = parser.isoparse(request.fromDate)
        to_date_utc = parser.isoparse(request.toDate)
        request_date_utc = parser.isoparse(request.requestDate)

        from_date_utc = from_date_utc.astimezone(pytz.utc)
        to_date_utc = to_date_utc.astimezone(pytz.utc)
        request_date_utc = request_date_utc.astimezone(pytz.utc)
        
        # Add request time in the desired timezone
        time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")

        result = Mongo.store_remote_work_request(
            request.userid,
            request.employeeName,
            time,
            from_date_utc,
            to_date_utc,
            request_date_utc,
            request.reason,
        )
        return {"message": "Remote work request stored successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  

# Remote Work History    
@app.get("/Remote-History/{userid}")
async def get_Remote_History(userid:str = Path(..., title="The name of the user whose Remote History you want to fetch")):
    try:
        Remote_History = Remote_History_Details(userid)
        return{"Remote_History": Remote_History}
    except Exception as e:
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
@app.put("/updated_remote_work_requests")
async def update_remote_work_request_status(userid: str = Form(...), status: str = Form(...)):
    try:
        updated = update_remote_work_request_status_in_mongo(userid, status)
        if updated:
            return {"message": "Status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

update_remote_work_request_recommend_in_mongo
# HR Remote Work Responses
@app.put("/recommend_remote_work_requests")
async def update_remote_work_request_status(userid: str = Form(...), status: str = Form(...)):
    try:
        updated = update_remote_work_request_recommend_in_mongo(userid, status)
        if updated:
            return {"message": "Recommend status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Admin Page User Leave History
@app.get("/leave-history")
def get_leave_history():
    leave_history = get_approved_leave_history()
    return {"leave_history": list(leave_history)}

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


@app.post('/Other-leave-request')
def leave_request(item: Item7):
    try:
        def parse_date(date_str):
            # Remove 'Z' if present
            date_str = date_str[:-1] if date_str.endswith('Z') else date_str
            # Try parsing with full datetime format, fallback to date only
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                return datetime.strptime(date_str, "%Y-%m-%d")

        selected_date = parse_date(item.selectedDate)
        To_date = parse_date(item.ToDate)
        request_date = parse_date(item.requestDate)

        # Localize dates to UTC
        selected_date_utc = pytz.utc.localize(selected_date)
        To_date_utc = pytz.utc.localize(To_date)
        request_date_utc = pytz.utc.localize(request_date)

        # Add request time in the desired timezone
        time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")

        result = store_Other_leave_request(
            item.userid,
            item.employeeName,
            time,  # Use the generated time
            item.leaveType,
            selected_date_utc,
            To_date_utc,
            request_date_utc,
            item.reason,
        )

        return {"message": "Leave request stored successfully", "result": result}
    except Exception as e:
        raise HTTPException(400, str(e))

    
    
    
@app.post('/Permission-request')
def leave_request(item: Item8):
    try:
        selected_date_str = item.selectedDate[:-1] if item.selectedDate.endswith('Z') else item.selectedDate
        request_date_str = item.requestDate[:-1] if item.requestDate.endswith('Z') else item.requestDate
    

        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%dT%H:%M:%S.%f")
        request_date = datetime.strptime(request_date_str, "%Y-%m-%dT%H:%M:%S.%f")

        selected_date_utc = pytz.utc.localize(selected_date)
        request_date_utc = pytz.utc.localize(request_date)

      
        result = store_Permission_request(
                item.userid,
                item.employeeName,
                item.time,
                item.leaveType,
                selected_date_utc,
                request_date_utc,
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


# @app.post('/autoClockout')
# def auto_clockout(data: CT):
#     total_hours_worked = Mongo.Clockout(userid=data.userid, name=data.name, time=data.time)
#     return {"message": "Automatic clock out successful", "total_hours_worked": total_hours_worked}


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
        parsed_date = datetime.strptime(item.date, "%d-%m-%Y").strftime("%d-%m-%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use dd-mm-yyyy.")
    result = add_task_list(item.task, item.userid, parsed_date)
    return result


@app.post("/edit_task")
async def edit_task(item: Taskedit):
    today = datetime.today()
    formatted_date = today.strftime("%d-%m-%Y")
    try:
        # Parse the date to ensure it's in the correct format
        parsed_date = datetime.strptime(item.date, "%d-%m-%Y").strftime("%d-%m-%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use dd-mm-yyyy.")
    result = edit_the_task(item.userid, item.task, parsed_date, formatted_date, item.updated_task, item.status)
    return {"result": result}


@app.delete("/task_delete")
async def task_delete(item: Deletetask):
    try:
        # Parse the date to ensure it's in the correct format
        parsed_date = datetime.strptime(item.date, "%d-%m-%Y").strftime("%d-%m-%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use dd-mm-yyyy.")
    result = delete_a_task(item.task, item.userid, parsed_date)
    return {"result": result}



@app.get("/get_tasks/{userid}/{date}")
async def get_tasks(userid: str, date: str):
    try:
        # Parse the date to ensure it's in the correct format
        parsed_date = datetime.strptime(date, "%d-%m-%Y").strftime("%d-%m-%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use dd-mm-yyyy.")
    
    result = get_the_tasks(userid, parsed_date)
    if not result:
        return {"message": "No tasks found for the given user and date"}
    return result

@app.get("/get_user/{userid}")
def get_user(userid:str):
    result = get_user_info(userid)
    return result

@app.get("/get_admin/{userid}")
def get_admin(userid:str):
    result = get_admin_info(userid)
    return result 

@app.post("/add_employee")
def add_employee(item:AddEmployee):
    result = add_an_employee(item.dict())
    return result

@app.post("/add_manager")
def add_manager(item:AddEmployee):
    result = add_a_manager(item.dict())
    return result

@app.get("/auto_approve_manager_leaves")
async def trigger_auto_approval():
    result = auto_approve_manager_leaves()
    return result