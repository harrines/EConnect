from Mongo import Otherleave_History_Details,Permission_History_Details, Users,admin,normal_leave_details,store_Other_leave_request,get_approved_leave_history,get_remote_work_requests,attendance_details,leave_History_Details,Remote_History_Details,get_attendance_by_date,update_remote_work_request_status_in_mongo,updated_user_leave_requests_status_in_mongo,get_user_leave_requests, get_employee_id_from_db,store_Permission_request, get_all_users, get_admin_info, add_task_list, edit_the_task, delete_a_task, get_the_tasks, delete_leave, get_user_info, store_sunday_request, get_admin_info, add_an_employee, PreviousDayClockout, auto_clockout, leave_update_notification, recommend_manager_leave_requests_status_in_mongo, get_manager_leave_requests, get_only_user_leave_requests, get_admin_page_remote_work_requests, update_remote_work_request_recommend_in_mongo, get_TL_page_remote_work_requests, users_leave_recommend_notification, managers_leave_recommend_notification,auto_approve_manager_leaves,edit_an_employee,get_managers,task_assign_to_multiple_users, get_team_members, manager_task_assignment, get_local_ip, get_public_ip, assigned_task, get_single_task, create_notification, get_notifications, mark_notification_read, mark_all_notifications_read, get_unread_notification_count, delete_notification, get_notifications_by_type, create_task_notification, create_leave_notification, create_wfh_notification, create_system_notification, create_attendance_notification, notify_leave_submitted, notify_leave_approved, notify_leave_rejected, notify_leave_recommended, notify_wfh_submitted, notify_wfh_approved, notify_wfh_rejected, store_leave_request, store_remote_work_request, get_admin_user_ids, get_hr_user_ids, get_user_position, notify_admin_manager_leave_request, notify_hr_recommended_leave, notify_hr_pending_leaves, notify_admin_pending_leaves, get_current_timestamp_iso, Notifications
from model import Item4,Item,Item2,Item3,Csvadd,Csvedit,Csvdel,CT,Item5,Item6,Item9,RemoteWorkRequest,Item7,Item8, Tasklist, Taskedit, Deletetask, Gettasks, DeleteLeave, Item9, AddEmployee,EditEmployee,Taskassign, SingleTaskAssign, NotificationModel, NotificationUpdate, NotificationFilter
from fastapi import FastAPI, HTTPException,Path,Query, HTTPException,Form, Request, WebSocket, WebSocketDisconnect
from websocket_manager import notification_manager
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI,Body
from auth.auth_bearer import JWTBearer
from http.client import HTTPException
from datetime import datetime, timedelta, date
from dateutil import parser
from typing import Union, Dict, List
from bson import ObjectId
from bson import json_util
import json
import uvicorn
import Mongo
import pytz
import os
import asyncio
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

# Initialize task scheduler on application startup
@app.on_event("startup")
async def startup_event():
    """Initialize task deadline scheduler when the application starts"""
    try:
        scheduler = Mongo.setup_task_scheduler()
        if scheduler:
            print("✅ Task deadline monitoring system initialized")
        else:
            print("⚠️ Failed to initialize task deadline scheduler")
    except Exception as e:
        print(f"❌ Error initializing task scheduler: {e}")

# Store scheduler reference for potential cleanup
task_scheduler = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup scheduler when application shuts down"""
    global task_scheduler
    if task_scheduler:
        try:
            task_scheduler.shutdown()
            print("✅ Task scheduler shut down successfully")
        except Exception as e:
            print(f"⚠️ Error shutting down scheduler: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize APScheduler
scheduler = BackgroundScheduler()

# Import notification automation
from notification_automation import (
    run_all_automated_checks, 
    check_and_notify_overdue_tasks,
    check_upcoming_deadlines,
    check_missed_attendance,
    check_pending_approvals
)

# Schedule the auto-clockout task to run daily at 9:30 AM
scheduler.add_job(auto_clockout, 'cron', hour=9, minute=30, id='auto_clockout')

# Schedule notification automation tasks
# Morning checks at 8:00 AM (upcoming deadlines, missed attendance)
scheduler.add_job(
    lambda: asyncio.create_task(check_upcoming_deadlines()),
    'cron', hour=8, minute=0, id='morning_deadline_check'
)

scheduler.add_job(
    lambda: asyncio.create_task(check_missed_attendance()),
    'cron', hour=10, minute=0, id='missed_attendance_check'
)

# Midday overdue tasks check at 12:00 PM
scheduler.add_job(
    lambda: asyncio.create_task(check_and_notify_overdue_tasks()),
    'cron', hour=12, minute=0, id='midday_overdue_check'
)

# Evening comprehensive check at 6:00 PM
scheduler.add_job(
    lambda: asyncio.create_task(run_all_automated_checks()),
    'cron', hour=18, minute=0, id='evening_comprehensive_check'
)

# Pending approvals check twice daily (10 AM and 3 PM)
scheduler.add_job(
    lambda: asyncio.create_task(check_pending_approvals()),
    'cron', hour=10, minute=30, id='morning_approvals_check'
)

scheduler.add_job(
    lambda: asyncio.create_task(check_pending_approvals()),
    'cron', hour=15, minute=0, id='afternoon_approvals_check'
)

# Start the scheduler
scheduler.start()
print("✅ Enhanced notification automation scheduler started with comprehensive checks")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test")
def test_connection():
    return {"status": "Backend is connected", "timestamp": datetime.now().isoformat()}

@app.get("/notification-system-status")
async def notification_system_status():
    """Check the status of the enhanced notification system"""
    try:
        from websocket_manager import notification_manager
        from notification_automation import get_current_timestamp_ist
        
        # Get current timestamp
        current_time = get_current_timestamp_ist()
        
        # Check active WebSocket connections
        active_users = notification_manager.get_active_users()
        total_connections = sum(notification_manager.get_user_connection_count(user_id) for user_id in active_users)
        
        # Check notification database
        total_notifications = Notifications.count_documents({})
        
        # Check recent notifications (last 24 hours)
        yesterday = current_time - timedelta(hours=24)
        recent_notifications = Notifications.count_documents({
            "created_at": {"$gte": yesterday.isoformat()}
        })
        
        # Check scheduler status
        scheduler_status = "running" if scheduler.running else "stopped"
        
        # Get some sample stats
        notification_types = {}
        for notif_type in ["task", "leave", "wfh", "attendance", "system"]:
            count = Notifications.count_documents({"type": notif_type})
            notification_types[notif_type] = count
        
        return {
            "status": "operational",
            "timestamp": current_time.isoformat(),
            "websocket": {
                "active_users": len(active_users),
                "total_connections": total_connections,
                "active_user_ids": active_users[:10]  # Show first 10
            },
            "notifications": {
                "total": total_notifications,
                "recent_24h": recent_notifications,
                "by_type": notification_types
            },
            "scheduler": {
                "status": scheduler_status,
                "jobs": len(scheduler.get_jobs()) if scheduler.running else 0
            },
            "automation": {
                "enabled": True,
                "modules": [
                    "overdue_tasks_check",
                    "upcoming_deadlines_check", 
                    "missed_attendance_check",
                    "pending_approvals_check"
                ]
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Enhanced notification testing and automation endpoints
@app.get("/test-notifications/{userid}")
async def test_notifications(userid: str):
    """Test endpoint to create a sample notification"""
    try:
        # Create a test notification with WebSocket
        notification_id = create_notification(
            userid=userid,
            title="🧪 Test Notification",
            message="This is a test notification to verify the enhanced system is working perfectly!",
            notification_type="system",
            priority="medium",
            metadata={"test": True, "timestamp": get_current_timestamp_iso()}
        )
        
        # Send via WebSocket if user is connected
        if notification_id:
            notification_data = {
                "_id": notification_id,
                "userid": userid,
                "title": "🧪 Test Notification",
                "message": "This is a test notification to verify the enhanced system is working perfectly!",
                "type": "system",
                "priority": "medium",
                "metadata": {"test": True, "timestamp": get_current_timestamp_iso()},
                "is_read": False,
                "created_at": get_current_timestamp_iso()
            }
            await notification_manager.send_personal_notification(userid, notification_data)
        
        return {
            "status": "success",
            "message": "Test notification sent successfully",
            "notification_id": notification_id,
            "userid": userid,
            "timestamp": get_current_timestamp_iso()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/run-automation-checks")
async def run_automation_checks():
    """Manually trigger all automated notification checks"""
    try:
        from notification_automation import run_all_automated_checks
        result = await run_all_automated_checks()
        return {
            "status": "success",
            "message": "Automation checks completed",
            "results": result,
            "timestamp": get_current_timestamp_iso()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/check-overdue-tasks")
async def manual_overdue_check():
    """Manually check for overdue tasks"""
    try:
        from notification_automation import check_and_notify_overdue_tasks
        result = await check_and_notify_overdue_tasks()
        return {
            "status": "success",
            "message": "Overdue tasks check completed",
            "result": result,
            "timestamp": get_current_timestamp_iso()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/notification-stats/{userid}")
async def get_notification_stats(userid: str):
    """Get notification statistics for a user"""
    try:
        total_notifications = Notifications.count_documents({"userid": userid})
        unread_count = get_unread_notification_count(userid)
        read_count = total_notifications - unread_count
        
        # Get notifications by type
        type_stats = {}
        for notification_type in ["task", "leave", "wfh", "attendance", "system"]:
            count = Notifications.count_documents({"userid": userid, "type": notification_type})
            type_stats[notification_type] = count
        
        return {
            "userid": userid,
            "total_notifications": total_notifications,
            "unread_count": unread_count,
            "read_count": read_count,
            "by_type": type_stats,
            "timestamp": get_current_timestamp_iso()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        # Create notification in database
        result = create_notification(notification_data)
        
        # Send real-time notification if user is connected
        asyncio.create_task(notification_manager.send_personal_notification(userid, notification_data))
        
        return {"status": "Test notification created", "notification": result}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

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

# Test endpoint for attendance notifications
@app.post('/test-attendance-notification')
def test_attendance_notification():
    """Test endpoint to create sample attendance notifications"""
    try:
        # Create test notifications for the first user found
        user = Mongo.Users.find_one()
        if user:
            userid = str(user["_id"])
            
            # Test clock-in notification
            create_attendance_notification(
                userid=userid,
                message="Test clock-in notification - System working correctly!",
                priority="low",
                attendance_type="clock_in"
            )
            
            # Test auto clock-out notification  
            create_attendance_notification(
                userid=userid,
                message="Test auto clock-out notification - System working correctly!",
                priority="medium", 
                attendance_type="auto_clock_out"
            )
            
            # Test missed clock-out notification
            create_attendance_notification(
                userid=userid,
                message="Test missed clock-out notification - System working correctly!",
                priority="high",
                attendance_type="missed_clock_out"
            )
            
            return {"message": f"Test notifications created for user {userid}"}
        else:
            return {"message": "No users found"}
    except Exception as e:
        return {"message": f"Error creating test notifications: {e}"}


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
async def leave_request(item: Item6):
    try:
        print(f"📩 Processing leave request from user: {item.userid}")
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

        # Check if result is a conflict or other business logic issue
        if isinstance(result, str):
            if "Conflict" in result or "already has" in result:
                # This is a business logic conflict, not a request error
                return {
                    "success": False,
                    "status": "conflict",
                    "message": "Request processed successfully, but a scheduling conflict was detected.",
                    "details": result,
                    "suggestion": "Please select a different date or check your existing requests."
                }
            elif result == "Leave request stored successfully":
                # Success case - notify employee and appropriate approver
                try:
                    # 1. Notify employee about successful submission
                    await notify_leave_submitted(
                        userid=item.userid,
                        leave_type=item.leaveType,
                        leave_id=None
                    )
                    print(f"✅ Employee notification sent for leave submission")
                    
                    # 2. Check if the user is a manager and send appropriate notifications
                    user_position = await Mongo.get_user_position(item.userid)
                    
                    if user_position == "Manager":
                        # Manager leave request - notify admin
                        admin_ids = await Mongo.get_admin_user_ids()
                        if admin_ids:
                            await Mongo.notify_admin_manager_leave_request(
                                manager_name=item.employeeName,
                                manager_id=item.userid,
                                leave_type=item.leaveType,
                                leave_date=item.selectedDate,
                                leave_id=None
                            )
                            print(f"✅ Admin notification sent for manager leave request")
                        else:
                            print(f"⚠️ No admin found, skipping admin notification")
                    else:
                        # Regular employee leave request - notify manager
                        manager_id = await Mongo.get_user_manager_id(item.userid)
                        if manager_id:
                            await Mongo.notify_manager_leave_request(
                                employee_name=item.employeeName,
                                employee_id=item.userid,
                                leave_type=item.leaveType,
                                leave_date=item.selectedDate,
                                manager_id=manager_id,
                                leave_id=None
                            )
                            print(f"✅ Manager notification sent for employee leave approval request")
                        else:
                            print(f"⚠️ No manager found for user {item.userid}, skipping manager notification")
                        
                except Exception as notification_error:
                    print(f"⚠️ Notification error: {notification_error}")
                
                return {
                    "success": True,
                    "status": "submitted",
                    "message": "Leave request submitted successfully",
                    "details": result
                }
            else:
                # Other validation errors (Sunday, invalid dates, etc.)
                return {
                    "success": False,
                    "status": "validation_error",
                    "message": "Request validation failed",
                    "details": result,
                    "suggestion": "Please check your request details and try again."
                }

        return {"message": "Leave request processed", "result": result}
    except Exception as e:
        print(f"❌ Error in leave request: {e}")
        # Only return 500 for actual server errors, not business logic issues
        return {
            "success": False,
            "status": "error",
            "message": "An unexpected error occurred while processing your request",
            "details": str(e),
            "suggestion": "Please try again later or contact support if the issue persists."
        }

@app.post('/Bonus-leave-request')
async def bonus_leave_request(item: Item9):
    try:
        print(f"📩 Processing bonus leave request from user: {item.userid}")
        
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

        if result and result != "No bonus leave available" and "Conflict" not in str(result):
            # For successful requests, create notifications
            try:
                # 1. Notify employee about successful submission
                await Mongo.notify_leave_submitted(
                    userid=item.userid,
                    leave_type=item.leaveType,
                    leave_id=None  # No specific ID for bonus leave
                )
                print(f"✅ Employee notification sent for bonus leave submission")
                
                # 2. Check if the user is a manager and send appropriate notifications
                user_position = await Mongo.get_user_position(item.userid)
                
                if user_position == "Manager":
                    # Manager bonus leave request - notify admin
                    admin_ids = await Mongo.get_admin_user_ids()
                    if admin_ids:
                        await Mongo.notify_admin_manager_leave_request(
                            manager_name=item.employeeName,
                            manager_id=item.userid,
                            leave_type=item.leaveType,
                            leave_date=item.selectedDate,
                            leave_id=None
                        )
                        print(f"✅ Admin notification sent for manager bonus leave request")
                    else:
                        print(f"⚠️ No admin found, skipping admin notification")
                else:
                    # Regular employee bonus leave request - notify manager
                    manager_id = await Mongo.get_user_manager_id(item.userid)
                    if manager_id:
                        await Mongo.notify_manager_leave_request(
                            employee_name=item.employeeName,
                            employee_id=item.userid,
                            leave_type=item.leaveType,
                            leave_date=item.selectedDate,
                            manager_id=manager_id,
                            leave_id=None
                        )
                        print(f"✅ Manager notification sent for employee bonus leave approval request")
                    else:
                        print(f"⚠️ No manager found for user {item.userid}, skipping manager notification")
                
            except Exception as notification_error:
                print(f"⚠️ Notification error: {notification_error}")

        return {"message": "Bonus leave request processed", "result": result}
    except Exception as e:
        print(f"❌ Error in bonus leave request: {e}")
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

# HR page - Notify HR about pending leave approvals
@app.get("/hr_leave_notification_reminder")
async def fetch_hr_pending_leaves():
    result = await notify_hr_pending_leaves()
    return result

# HR page - Force refresh HR notifications for recommended leaves
@app.post("/hr_force_notification_refresh")
async def force_hr_notification_refresh():
    """Force refresh HR notifications for all pending recommended leaves"""
    try:
        result = await Mongo.notify_hr_pending_leaves()
        return {"success": True, "result": result}
    except Exception as e:
        print(f"Error in force HR notification refresh: {e}")
        return {"success": False, "error": str(e)}

# Admin page - Notify admin about pending manager leave approvals
@app.get("/admin_leave_notification_reminder")
async def fetch_admin_pending_leaves():
    """Notify admin about all pending manager leave requests"""
    result = await Mongo.notify_admin_pending_leaves()
    return result

# Admin page - Force refresh admin notifications for pending manager leaves
@app.post("/admin_force_notification_refresh")
async def force_admin_notification_refresh():
    """Force refresh admin notifications for all pending manager leave requests"""
    try:
        result = await Mongo.notify_admin_pending_leaves()
        return {"success": True, "result": result}
    except Exception as e:
        print(f"Error in force admin notification refresh: {e}")
        return {"success": False, "error": str(e)}

# HR Page Leave Responses
@app.put("/updated_user_leave_requests")
async def updated_user_leave_requests_status(leave_id: str = Form(...), status: str = Form(...)):
    try:
        response = updated_user_leave_requests_status_in_mongo(leave_id, status)
        
        # Create notification for leave status update
        if response and "userid" in response:
            # Properly handle different status values
            status_lower = status.lower()
            if status_lower == "approved":
                action = "Approved"
                priority = "high"
            elif status_lower in ["rejected", "reject"]:
                action = "Rejected"
                priority = "high"
            elif status_lower in ["recommended", "recommend"]:
                action = "Recommended"
                priority = "medium"
            else:
                action = status  # Use the original status for any other case
                priority = "medium"
            
            create_leave_notification(
                userid=response["userid"],
                leave_type=response.get("leave_type", "Leave"),
                action=action,
                leave_id=leave_id,
                priority=priority
            )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Admin And TL Leave Recommendation Responses
@app.put("/recommend_users_leave_requests")
async def recommend_managers_leave_requests_status(leave_id: str = Form(...), status: str = Form(...)):
    try:
        response = recommend_manager_leave_requests_status_in_mongo(leave_id, status)
        
        # Create notification for leave recommendation
        if response and "userid" in response:
            action = "Recommended" if status.lower() in ["recommended", "recommend"] else "Not Recommended"
            recommender_name = response.get("recommender_name", "Admin")
            
            # Notify the employee about the recommendation
            create_leave_notification(
                userid=response["userid"],
                leave_type=response.get("leave_type", "Leave"),
                action=action,
                leave_id=leave_id,
                priority="medium",
                manager_name=recommender_name
            )
            
            # If the leave is recommended, also notify HR for final approval
            if status.lower() in ["recommended", "recommend"]:
                try:
                    # Get employee details for HR notification
                    employee_name = response.get("employee_name", "Unknown Employee")
                    leave_type = response.get("leave_type", "Leave")
                    leave_date = response.get("leave_date", "Unknown Date")
                    recommender_name = response.get("recommender_name", "Manager/Admin")
                    
                    await Mongo.notify_hr_recommended_leave(
                        employee_name=employee_name,
                        employee_id=response["userid"],
                        leave_type=leave_type,
                        leave_date=leave_date,
                        recommended_by=recommender_name,
                        leave_id=leave_id
                    )
                    print(f"✅ HR notification sent for recommended leave: {employee_name}")
                    
                except Exception as hr_notification_error:
                    print(f"⚠️ Error sending HR notification: {hr_notification_error}")
        
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
async def remote_work_request(request: RemoteWorkRequest):
    try:
        print(f"📩 Processing WFH request from user: {request.userid}")
        
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
        
        # Check if result is a dictionary (success) or string (error/conflict)
        if isinstance(result, dict) and result.get("success"):
            # Success case - notify employee and manager
            try:
                wfh_id = result.get("wfh_id")
                from_date = result.get("from_date")
                to_date = result.get("to_date")
                
                # 1. Notify employee about successful submission
                await Mongo.notify_wfh_submitted(
                    userid=request.userid,
                    request_date=from_date,
                    wfh_id=wfh_id
                )
                print(f"✅ Employee notification sent for WFH submission with ID: {wfh_id}")
                
                # 2. Check if user is a manager and handle notifications accordingly
                user = Mongo.Users.find_one({"_id": Mongo.ObjectId(request.userid)})
                if user and user.get("position") == "Manager":
                    # If manager is submitting WFH, notify admin
                    try:
                        await Mongo.notify_admin_manager_wfh_request(
                            manager_name=request.employeeName,
                            manager_id=request.userid,
                            request_date_from=from_date,
                            request_date_to=to_date,
                            wfh_id=wfh_id
                        )
                        print(f"✅ Admin notification sent for manager WFH request")
                    except Exception as admin_notification_error:
                        print(f"⚠️ Admin notification error: {admin_notification_error}")
                else:
                    # Regular employee - notify their manager
                    manager_id = await Mongo.get_user_manager_id(request.userid)
                    if manager_id:
                        await Mongo.notify_manager_wfh_request(
                            employee_name=request.employeeName,
                            employee_id=request.userid,
                            request_date_from=from_date,
                            request_date_to=to_date,
                            manager_id=manager_id,
                            wfh_id=wfh_id
                        )
                        print(f"✅ Manager notification sent for WFH approval request")
                    else:
                        print(f"⚠️ No manager found for user {request.userid}, skipping manager notification")
                    
            except Exception as notification_error:
                print(f"⚠️ Notification error: {notification_error}")
                import traceback
                traceback.print_exc()
            
            return {
                "success": True,
                "status": "submitted",
                "message": result.get("message", "Remote work request submitted successfully"),
                "details": result,
                "wfh_id": wfh_id
            }
        elif isinstance(result, str):
            if "Conflict" in result or "already has" in result:
                # This is a business logic conflict, not a request error
                return {
                    "success": False,
                    "status": "conflict",
                    "message": "Request processed successfully, but a scheduling conflict was detected.",
                    "details": result,
                    "suggestion": "Please select different dates or check your existing requests."
                }
            elif "successfully" in result:
                # Old format success - fallback
                try:
                    # 1. Notify employee about successful submission
                    await Mongo.notify_wfh_submitted(
                        userid=request.userid,
                        request_date=request.fromDate,
                        wfh_id=None
                    )
                    print(f"✅ Employee notification sent for WFH submission (fallback)")
                    
                    # 2. Check if user is a manager and handle notifications accordingly
                    user = Mongo.Users.find_one({"_id": Mongo.ObjectId(request.userid)})
                    if user and user.get("position") == "Manager":
                        # If manager is submitting WFH, notify admin
                        try:
                            await Mongo.notify_admin_manager_wfh_request(
                                manager_name=request.employeeName,
                                manager_id=request.userid,
                                request_date_from=request.fromDate,
                                request_date_to=request.toDate,
                                wfh_id=None
                            )
                            print(f"✅ Admin notification sent for manager WFH request (fallback)")
                        except Exception as admin_notification_error:
                            print(f"⚠️ Admin notification error: {admin_notification_error}")
                    else:
                        # Regular employee - notify their manager
                        manager_id = await Mongo.get_user_manager_id(request.userid)
                        if manager_id:
                            await Mongo.notify_manager_wfh_request(
                                employee_name=request.employeeName,
                                employee_id=request.userid,
                                request_date_from=request.fromDate,
                                request_date_to=request.toDate,
                                manager_id=manager_id,
                                wfh_id=None
                            )
                            print(f"✅ Manager notification sent for WFH approval request")
                        else:
                            print(f"⚠️ No manager found for user {request.userid}, skipping manager notification")
                        
                except Exception as notification_error:
                    print(f"⚠️ Notification error: {notification_error}")
                
                return {
                    "success": True,
                    "status": "submitted",
                    "message": "Remote work request submitted successfully",
                    "details": result
                }
            else:
                # Other validation errors (Sunday, too many days, etc.)
                return {
                    "success": False,
                    "status": "validation_error",
                    "message": "Request validation failed",
                    "details": result,
                    "suggestion": "Please check your request details and try again."
                }
        
        return {"message": "WFH request processed", "result": result}
    except Exception as e:
        print(f"❌ Error in WFH request: {e}")
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
            # Send notification to the user about the status update
            try:
                wfh_request = Mongo.RemoteWork.find_one({"_id": Mongo.ObjectId(id)})
                if wfh_request:
                    from_date = wfh_request.get("fromDate")
                    from_date_str = from_date.strftime("%Y-%m-%d") if from_date else None
                    
                    if status.lower() == "approved":
                        await Mongo.notify_wfh_approved(userid, from_date_str, id)
                        print(f"✅ WFH approved notification sent to user {userid}")
                    elif status.lower() == "rejected":
                        await Mongo.notify_wfh_rejected(userid, from_date_str, id, reason="Not specified")
                        print(f"✅ WFH rejected notification sent to user {userid}")
            except Exception as notification_error:
                print(f"⚠️ Notification error: {notification_error}")
            
            return {"message": "Status updated successfully"}
        else:
            return {"message": "Failed to update status"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# HR Remote Work Responses
@app.put("/recommend_remote_work_requests")
async def update_remote_work_request_status(userid: str = Form(...), status: str = Form(...), id: str = Form(...)):
    try:
        print(f"WFH recommendation update - User: {userid}, Status: {status}, ID: {id}")
        updated = update_remote_work_request_recommend_in_mongo(userid, status, id)
        if updated and status.lower() == "recommend":
            # Send notification to HR when WFH is recommended
            try:
                wfh_request = Mongo.RemoteWork.find_one({"_id": Mongo.ObjectId(id)})
                if wfh_request:
                    employee_name = wfh_request.get("employeeName", "Unknown Employee")
                    employee_id = wfh_request.get("userid")  # This is the actual employee ID
                    from_date = wfh_request.get("fromDate")
                    to_date = wfh_request.get("toDate")
                    from_date_str = from_date.strftime("%d-%m-%Y") if from_date else "Unknown Date"
                    to_date_str = to_date.strftime("%d-%m-%Y") if to_date else "Unknown Date"
                    
                    # Get the employee's manager name (who is doing the recommendation)
                    employee = Mongo.Users.find_one({"_id": Mongo.ObjectId(employee_id)})
                    manager_name = employee.get("TL", "Manager") if employee else "Manager"
                    
                    await Mongo.notify_hr_recommended_wfh(
                        employee_name=employee_name,
                        employee_id=employee_id,
                        request_date_from=from_date_str,
                        request_date_to=to_date_str,
                        recommended_by=manager_name,
                        wfh_id=id
                    )
                    print(f"✅ HR notification sent for recommended WFH: {employee_name} (recommended by {manager_name})")
            except Exception as notification_error:
                print(f"⚠️ HR notification error: {notification_error}")
        
        if updated:
            return {"message": "Recommend status updated successfully"}
        else:
            return {"message": "Failed to update recommend status"}
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
async def other_leave_request(item: Item7):
    try:
        print(f"📩 Processing other leave request from user: {item.userid}")
        
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

        # Check if result is a conflict or other business logic issue
        if isinstance(result, str):
            if "Conflict" in result or "already has" in result:
                # This is a business logic conflict, not a request error
                return {
                    "success": False,
                    "status": "conflict",
                    "message": "Request processed successfully, but a scheduling conflict was detected.",
                    "details": result,
                    "suggestion": "Please select different dates or check your existing requests."
                }
            elif result == "Leave request stored successfully":
                # Success case - notify employee and manager
                try:
                    # 1. Notify employee about successful submission
                    await Mongo.notify_leave_submitted(
                        userid=item.userid,
                        leave_type=item.leaveType,
                        leave_id=None  # No specific ID for other leave
                    )
                    print(f"✅ Employee notification sent for other leave submission")
                    
                    # 2. Check if the user is a manager and send appropriate notifications
                    user_position = await Mongo.get_user_position(item.userid)
                    
                    if user_position == "Manager":
                        # Manager other leave request - notify admin
                        admin_ids = await Mongo.get_admin_user_ids()
                        if admin_ids:
                            date_range = f"{item.selectedDate} to {item.ToDate}" if item.selectedDate != item.ToDate else item.selectedDate
                            await Mongo.notify_admin_manager_leave_request(
                                manager_name=item.employeeName,
                                manager_id=item.userid,
                                leave_type=item.leaveType,
                                leave_date=date_range,
                                leave_id=None
                            )
                            print(f"✅ Admin notification sent for manager other leave request")
                        else:
                            print(f"⚠️ No admin found, skipping admin notification")
                    else:
                        # Regular employee other leave request - notify manager
                        manager_id = await Mongo.get_user_manager_id(item.userid)
                        if manager_id:
                            date_range = f"{item.selectedDate} to {item.ToDate}" if item.selectedDate != item.ToDate else item.selectedDate
                            await Mongo.notify_manager_leave_request(
                                employee_name=item.employeeName,
                                employee_id=item.userid,
                                leave_type=item.leaveType,
                                leave_date=date_range,
                                manager_id=manager_id,
                                leave_id=None
                            )
                            print(f"✅ Manager notification sent for employee other leave approval request")
                        else:
                            print(f"⚠️ No manager found for user {item.userid}, skipping manager notification")
                        
                except Exception as notification_error:
                    print(f"⚠️ Notification error: {notification_error}")
                
                return {
                    "success": True,
                    "status": "submitted",
                    "message": "Other leave request submitted successfully",
                    "details": result
                }
            else:
                # Other validation errors (Sunday, too many days, etc.)
                return {
                    "success": False,
                    "status": "validation_error",
                    "message": "Request validation failed",
                    "details": result,
                    "suggestion": "Please check your request details and try again."
                }

        return {"message": "Leave request processed", "result": result}
    except Exception as e:
        print(f"❌ Error in other leave request: {e}")
        raise HTTPException(400, str(e))
    
@app.post('/Permission-request')
async def permission_request(item: Item8):
    try:
        print(f"📩 Processing permission request from user: {item.userid}")
        
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

        # Check if result is a conflict or other business logic issue
        if isinstance(result, str):
            if "Conflict" in result or "already has" in result:
                # This is a business logic conflict, not a request error
                return {
                    "success": False,
                    "status": "conflict",
                    "message": "Request processed successfully, but a scheduling conflict was detected.",
                    "details": result,
                    "suggestion": "Please select different dates or check your existing requests."
                }
            elif result == "Leave request stored successfully":
                # Success case - notify employee and manager
                try:
                    # 1. Notify employee about successful submission
                    await Mongo.notify_leave_submitted(
                        userid=item.userid,
                        leave_type=item.leaveType,
                        leave_id=None  # No specific ID for permission
                    )
                    print(f"✅ Employee notification sent for permission submission")
                    
                    # 2. Check if the user is a manager and send appropriate notifications
                    user_position = await Mongo.get_user_position(item.userid)
                    
                    if user_position == "Manager":
                        # Manager permission request - notify admin
                        admin_ids = await Mongo.get_admin_user_ids()
                        if admin_ids:
                            permission_details = f"{item.selectedDate} ({item.timeSlot})"
                            await Mongo.notify_admin_manager_leave_request(
                                manager_name=item.employeeName,
                                manager_id=item.userid,
                                leave_type=item.leaveType,
                                leave_date=permission_details,
                                leave_id=None
                            )
                            print(f"✅ Admin notification sent for manager permission request")
                        else:
                            print(f"⚠️ No admin found, skipping admin notification")
                    else:
                        # Regular employee permission request - notify manager
                        manager_id = await Mongo.get_user_manager_id(item.userid)
                        if manager_id:
                            permission_details = f"{item.selectedDate} ({item.timeSlot})"
                            await Mongo.notify_manager_leave_request(
                                employee_name=item.employeeName,
                                employee_id=item.userid,
                                leave_type=item.leaveType,
                                leave_date=permission_details,
                                manager_id=manager_id,
                                leave_id=None
                            )
                            print(f"✅ Manager notification sent for employee permission approval request")
                        else:
                            print(f"⚠️ No manager found for user {item.userid}, skipping manager notification")
                        
                except Exception as notification_error:
                    print(f"⚠️ Notification error: {notification_error}")
                
                return {
                    "success": True,
                    "status": "submitted",
                    "message": "Permission request submitted successfully",
                    "details": result
                }
            else:
                # Other validation errors (Sunday, too many days, etc.)
                return {
                    "success": False,
                    "status": "validation_error",
                    "message": "Request validation failed",
                    "details": result,
                    "suggestion": "Please check your request details and try again."
                }

        return {"message": "Permission request processed", "result": result}
    except Exception as e:
        print(f"❌ Error in permission request: {e}")
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
    
    # Enhanced notification for task assignment
    if result:
        task_titles = ", ".join(item.task) if isinstance(item.task, list) else str(item.task)
        
        # Create self-assignment notification (user creating their own task)
        await Mongo.create_task_created_notification(
            userid=item.userid,
            task_title=task_titles,
            creator_name="You",  # Self-created
            due_date=due_date,
            priority="medium"
        )
        
        # Also create assignment notification for consistency
        await Mongo.create_task_assignment_notification(
            userid=item.userid,
            task_title=task_titles,
            assigner_name="Admin",  # Since this is admin task assignment
            due_date=due_date,
            priority="high"
        )
    
    return result

@app.post("/manager_task_assign")
async def task_assign(item:SingleTaskAssign):
    # Parse the date to ensure it's in the correct format
    parsed_date = datetime.strptime(item.date, "%Y-%m-%d").strftime("%d-%m-%Y")
    due_date = datetime.strptime(item.due_date, "%Y-%m-%d").strftime("%d-%m-%Y")
    result = manager_task_assignment(item.task, item.userid, item.TL, parsed_date, due_date)
    
    # Enhanced notification for manager task assignment
    if result:
        task_titles = ", ".join(item.task) if isinstance(item.task, list) else str(item.task)
        
        # Use specific manager assignment notification
        await Mongo.create_task_manager_assigned_notification(
            userid=item.userid,
            task_title=task_titles,
            manager_name=item.TL,  # Manager/TL name
            task_id=result,
            due_date=due_date,
            priority="high"
        )
    
    return result


@app.put("/edit_task")
async def edit_task(item: Taskedit):
    today = datetime.today()
    formatted_date = today.strftime("%d-%m-%Y")
    
    # Get current task details before updating
    current_task = Mongo.Tasks.find_one({"_id": ObjectId(item.taskid)})
    
    # Track changes for detailed notifications
    changes = {}
    if current_task:
        if item.updated_task and item.updated_task != current_task.get("task"):
            changes["title_changed"] = True
            changes["old_title"] = current_task.get("task")
            changes["new_title"] = item.updated_task
        
        if item.due_date and item.due_date != current_task.get("due_date"):
            changes["due_date_changed"] = True
            changes["old_due_date"] = current_task.get("due_date")
            changes["new_due_date"] = item.due_date
        
        if item.status and item.status != current_task.get("status"):
            changes["status_changed"] = True
            changes["old_status"] = current_task.get("status")
            changes["new_status"] = item.status
    
    result = edit_the_task(item.taskid, item.userid, formatted_date, item.due_date, item.updated_task, item.status)
    
    # Enhanced notifications based on task updates
    if result:
        task_title = item.updated_task or current_task.get("task", "Task") if current_task else "Task"
        
        # Check if task was marked as completed
        if item.status and item.status.lower() == "completed":
            # Get TL name from current task
            tl_name = current_task.get("TL") if current_task else None
            
            # Notify manager/TL about task completion
            await Mongo.notify_task_completion(
                userid=item.userid,
                task_title=task_title,
                task_id=item.taskid,
                tl_name=tl_name
            )
            
            # Create completion notification for user
            user = Mongo.Users.find_one({"_id": ObjectId(item.userid)}) if ObjectId.is_valid(item.userid) else None
            user_name = user.get("name", "User") if user else "User"
            
            await Mongo.create_task_assignment_notification(
                userid=item.userid,
                task_title=f"✅ Task Completed: {task_title}",
                assigner_name="System",
                task_id=item.taskid,
                priority="medium"
            )
        else:
            # Enhanced task update notification with detailed changes
            if changes:
                await Mongo.create_task_updated_notification(
                    userid=item.userid,
                    task_title=task_title,
                    updater_name="You",  # Assuming user is updating their own task
                    changes=changes,
                    task_id=item.taskid,
                    priority="medium"
                )
            else:
                # Fallback for minor updates
                action = "Updated"
                if item.status:
                    action = f"Status changed to {item.status}"
                
                create_task_notification(
                    userid=item.userid,
                    task_title=task_title,
                    action=action,
                    task_id=item.taskid,
                    priority="medium"
                )
    
    return {"result": result}


@app.delete("/task_delete/{taskid}")
async def task_delete(taskid: str):
    result = delete_a_task(taskid)
    return {"result": result}

# Enhanced Task Notification Endpoints
@app.post("/trigger_deadline_check")
async def trigger_deadline_check():
    """Manually trigger deadline checking for testing/immediate needs"""
    try:
        overdue_count = await Mongo.check_and_notify_overdue_tasks()
        upcoming_count = await Mongo.check_upcoming_deadlines_enhanced()
        
        return {
            "status": "success",
            "overdue_notifications_sent": overdue_count,
            "upcoming_deadline_notifications_sent": upcoming_count,
            "message": f"Processed {overdue_count} overdue tasks and {upcoming_count} upcoming deadline reminders"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking deadlines: {str(e)}")

@app.get("/task_notification_stats/{userid}")
async def get_task_notification_stats(userid: str):
    """Get task notification statistics for a user"""
    try:
        # Get task-related notification counts
        total_task_notifications = Mongo.Notifications.count_documents({
            "userid": userid,
            "type": {"$in": ["task", "task_created", "task_updated", "task_manager_assigned", "task_due_soon", "task_overdue", "task_completed"]}
        })
        
        unread_task_notifications = Mongo.Notifications.count_documents({
            "userid": userid,
            "type": {"$in": ["task", "task_created", "task_updated", "task_manager_assigned", "task_due_soon", "task_overdue", "task_completed"]},
            "is_read": False
        })
        
        # Get active tasks
        active_tasks = Mongo.Tasks.count_documents({
            "userid": userid,
            "status": {"$ne": "Completed"}
        })
        
        # Get overdue tasks
        current_date = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
        current_date_obj = datetime.strptime(current_date, "%d-%m-%Y")
        
        overdue_tasks = list(Mongo.Tasks.find({
            "userid": userid,
            "status": {"$ne": "Completed"}
        }))
        
        overdue_count = 0
        for task in overdue_tasks:
            due_date_str = task.get("due_date")
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%d-%m-%Y")
                    if due_date < current_date_obj:
                        overdue_count += 1
                except ValueError:
                    continue
        
        return {
            "userid": userid,
            "total_task_notifications": total_task_notifications,
            "unread_task_notifications": unread_task_notifications,
            "active_tasks": active_tasks,
            "overdue_tasks": overdue_count,
            "notification_types": {
                "task_assigned": Mongo.Notifications.count_documents({"userid": userid, "type": "task_manager_assigned"}),
                "task_created": Mongo.Notifications.count_documents({"userid": userid, "type": "task_created"}),
                "task_updated": Mongo.Notifications.count_documents({"userid": userid, "type": "task_updated"}),
                "task_due_soon": Mongo.Notifications.count_documents({"userid": userid, "type": "task_due_soon"}),
                "task_overdue": Mongo.Notifications.count_documents({"userid": userid, "type": "task_overdue"}),
                "task_completed": Mongo.Notifications.count_documents({"userid": userid, "type": "task_completed"})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task notification stats: {str(e)}")
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
async def task_assign(item: Taskassign):
    print(item.Task_details)
    
    # Get assigner name from the request or use default
    assigner_name = item.assigner_name or "Manager"
    
    # Use the enhanced function with notifications
    result = await Mongo.task_assign_to_multiple_users_with_notification(
        task_details=item.Task_details,
        assigner_name=assigner_name,
        single_notification_per_user=item.single_notification_per_user
    )
    
    return {"inserted_ids": result}

# Debug endpoint to check recent notifications for a user
@app.get("/debug/notifications/{userid}")
async def debug_notifications(userid: str):
    try:
        # Get recent notifications for the user
        recent_notifications = list(Mongo.Notifications.find(
            {"userid": userid}
        ).sort("created_at", -1).limit(10))
        
        # Convert ObjectId to string and format dates
        for notif in recent_notifications:
            notif["_id"] = str(notif["_id"])
            if "created_at" in notif:
                notif["created_at"] = notif["created_at"].isoformat() if hasattr(notif["created_at"], 'isoformat') else str(notif["created_at"])
            if "updated_at" in notif:
                notif["updated_at"] = notif["updated_at"].isoformat() if hasattr(notif["updated_at"], 'isoformat') else str(notif["updated_at"])
        
        return {
            "userid": userid,
            "recent_notifications": recent_notifications,
            "total_notifications": Mongo.Notifications.count_documents({"userid": userid}),
            "unread_count": Mongo.get_unread_notification_count(userid)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching debug info: {str(e)}")

# Task deadline management endpoints
@app.post("/tasks/check-overdue")
async def manually_check_overdue_tasks():
    """Manually trigger overdue task check"""
    try:
        overdue_count = await Mongo.check_and_notify_overdue_tasks()
        return {
            "message": f"Checked overdue tasks successfully",
            "overdue_tasks_found": overdue_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking overdue tasks: {str(e)}")

@app.post("/tasks/check-upcoming-deadlines")
async def manually_check_upcoming_deadlines():
    """Manually trigger upcoming deadline check"""
    try:
        upcoming_count = await Mongo.check_upcoming_deadlines()
        return {
            "message": f"Checked upcoming deadlines successfully",
            "upcoming_tasks_found": upcoming_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking upcoming deadlines: {str(e)}")

@app.get("/tasks/overdue-summary")
async def get_overdue_tasks_summary():
    """Get summary of all overdue tasks"""
    try:
        current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
        current_date = current_time.strftime("%d-%m-%Y")
        
        # Find all incomplete tasks
        incomplete_tasks = list(Mongo.Tasks.find({"status": {"$ne": "Completed"}}))
        overdue_tasks = []
        upcoming_tasks = []
        
        for task in incomplete_tasks:
            due_date_str = task.get("due_date")
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%d-%m-%Y")
                    current_date_obj = datetime.strptime(current_date, "%d-%m-%Y")
                    tomorrow = current_date_obj + timedelta(days=1)
                    
                    task_info = {
                        "task_id": str(task["_id"]),
                        "userid": task.get("userid"),
                        "task": task.get("task"),
                        "due_date": due_date_str,
                        "status": task.get("status"),
                        "TL": task.get("TL")
                    }
                    
                    if due_date < current_date_obj:
                        overdue_tasks.append(task_info)
                    elif due_date.strftime("%d-%m-%Y") == tomorrow.strftime("%d-%m-%Y"):
                        upcoming_tasks.append(task_info)
                        
                except ValueError:
                    pass
        
        return {
            "current_date": current_date,
            "overdue_tasks": overdue_tasks,
            "upcoming_tasks": upcoming_tasks,
            "overdue_count": len(overdue_tasks),
            "upcoming_count": len(upcoming_tasks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task summary: {str(e)}")

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

# Notification System Endpoints
@app.post("/notifications/create")
async def create_notification_endpoint(notification: NotificationModel):
    """Create a new notification"""
    try:
        result = create_notification(
            userid=notification.userid,
            title=notification.title,
            message=notification.message,
            notification_type=notification.type,
            priority=notification.priority,
            action_url=notification.action_url,
            related_id=notification.related_id,
            metadata=notification.metadata
        )
        if result:
            return {"message": "Notification created successfully", "notification_id": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to create notification")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications/{userid}")
async def get_user_notifications(
    userid: str,
    type: str = None,
    priority: str = None,
    is_read: bool = None,
    limit: int = 50
):
    """Get notifications for a user with optional filters"""
    try:
        notifications = get_notifications(
            userid=userid,
            notification_type=type,
            priority=priority,
            is_read=is_read,
            limit=limit
        )
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/notifications/{notification_id}/read")
async def mark_notification_as_read(notification_id: str, update: NotificationUpdate):
    """Mark a notification as read/unread"""
    try:
        success = mark_notification_read(notification_id, update.is_read)
        if success:
            return {"message": "Notification updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/notifications/{userid}/mark-all-read")
async def mark_all_user_notifications_read(userid: str):
    """Mark all notifications as read for a user"""
    try:
        count = mark_all_notifications_read(userid)
        return {"message": f"Marked {count} notifications as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications/{userid}/unread-count")
async def get_user_unread_count(userid: str):
    """Get count of unread notifications for a user"""
    try:
        count = get_unread_notification_count(userid)
        return {"unread_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/notifications/{notification_id}")
async def delete_notification_endpoint(notification_id: str):
    """Delete a notification"""
    try:
        success = delete_notification(notification_id)
        if success:
            return {"message": "Notification deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications/{userid}/type/{notification_type}")
async def get_notifications_by_type_endpoint(userid: str, notification_type: str):
    """Get notifications by type for a user"""
    try:
        notifications = get_notifications_by_type(userid, notification_type)
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoint to create sample notifications
@app.post("/notifications/test/{userid}")
async def create_test_notification(userid: str):
    """Create a test notification - useful for testing the system"""
    try:
        from websocket_manager import notification_manager
        
        # Create test notification in database
        notification_id = create_notification(
            userid=userid,
            title="Test Notification",
            message="This is a test notification to verify the system is working correctly.",
            notification_type="system",
            priority="low",
            action_url="/User/notifications",
            metadata={"test": True}
        )
        
        if notification_id:
            # Send via WebSocket if connected
            notification_data = {
                "_id": notification_id,
                "userid": userid,
                "title": "Test Notification",
                "message": "This is a test notification to verify the system is working correctly.",
                "type": "system",
                "priority": "low",
                "action_url": "/User/notifications",
                "metadata": {"test": True},
                "is_read": False,
                "created_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()
            }
            
            await notification_manager.send_personal_notification(userid, notification_data)
            
            # Update unread count
            unread_count = get_unread_notification_count(userid)
            await notification_manager.send_unread_count_update(userid, unread_count)
            
        return {"message": "Test notification created successfully", "notification_id": notification_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time notifications
@app.websocket("/ws/notifications/{userid}")
async def websocket_endpoint(websocket: WebSocket, userid: str):
    print(f"WebSocket connection attempt for user: {userid}")
    try:
        await notification_manager.connect(websocket, userid)
        print(f"WebSocket connected successfully for user: {userid}")
        
        # Send existing unread notifications on connection
        try:
            notifications = get_notifications(userid, is_read=False, limit=10)
            if notifications:
                for notification in notifications:
                    if websocket.client_state.value == 1:  # WebSocketState.CONNECTED
                        await websocket.send_text(json.dumps({
                            "type": "notification",
                            "data": notification
                        }))
        except Exception as e:
            print(f"Error sending initial notifications: {e}")
        
        # Keep the connection alive
        while True:
            try:
                # Check if connection is still open
                if websocket.client_state.value != 1:  # Not CONNECTED
                    break
                    
                # Receive any message (ping/pong or other client messages)
                data = await websocket.receive_text()
                print(f"Received message from {userid}: {data}")
                
                # Only send response if connection is still open
                if websocket.client_state.value == 1:  # WebSocketState.CONNECTED
                    await websocket.send_text(json.dumps({"type": "pong", "message": "Connection alive"}))
                    
            except WebSocketDisconnect:
                print(f"WebSocket disconnect for user: {userid}")
                break
            except Exception as e:
                print(f"WebSocket receive error for user {userid}: {e}")
                break
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnect for user: {userid}")
    except Exception as e:
        print(f"WebSocket error for user {userid}: {e}")
    finally:
        # Ensure cleanup happens
        notification_manager.disconnect(websocket, userid)

@app.post("/test-notification")
async def create_test_notification(data: dict):
    """Test endpoint to create a notification with current timestamp"""
    try:
        userid = data.get("userid", "test_user")
        title = data.get("title", "Test Notification")
        message = data.get("message", "Testing timestamp display")
        
        # Create notification using the fixed create_notification function
        notification_id = Mongo.create_notification(
            userid=userid,
            title=title,
            message=message,
            notification_type="test",
            priority="medium"
        )
        
        if notification_id:
            # Also send via WebSocket for real-time display
            await notification_manager.send_personal_notification(
                userid=userid,
                notification_data={
                    "_id": notification_id,
                    "userid": userid,
                    "title": title,
                    "message": message,
                    "type": "test",
                    "priority": "medium",
                    "is_read": False,
                    "created_at": Mongo.get_current_timestamp_iso()
                }
            )
            
            return {"success": True, "notification_id": notification_id, "message": "Test notification created with current timestamp"}
        else:
            return {"success": False, "message": "Failed to create notification"}
            
    except Exception as e:
        print(f"Error creating test notification: {e}")
        return {"success": False, "error": str(e)}

# Enhanced Leave and WFH Notification Endpoints

@app.post("/notifications/leave/submitted")
async def notify_leave_submitted_endpoint(data: dict):
    """Create leave submitted notification"""
    try:
        userid = data.get("userid")
        leave_type = data.get("leave_type", "Leave")
        leave_id = data.get("leave_id")
        
        if not userid:
            raise HTTPException(status_code=400, detail="userid is required")
        
        result = await Mongo.notify_leave_submitted(userid, leave_type, leave_id)
        return {"success": True, "notification_id": result, "message": "Leave submitted notification sent"}
        
    except Exception as e:
        print(f"Error creating leave submitted notification: {e}")
        return {"success": False, "error": str(e)}

@app.post("/notifications/leave/approved")
async def notify_leave_approved_endpoint(data: dict):
    """Create leave approved notification"""
    try:
        userid = data.get("userid")
        leave_type = data.get("leave_type", "Leave")
        leave_id = data.get("leave_id")
        
        if not userid:
            raise HTTPException(status_code=400, detail="userid is required")
        
        result = await Mongo.notify_leave_approved(userid, leave_type, leave_id)
        return {"success": True, "notification_id": result, "message": "Leave approved notification sent"}
        
    except Exception as e:
        print(f"Error creating leave approved notification: {e}")
        return {"success": False, "error": str(e)}

@app.post("/notifications/leave/rejected")
async def notify_leave_rejected_endpoint(data: dict):
    """Create leave rejected notification"""
    try:
        userid = data.get("userid")
        leave_type = data.get("leave_type", "Leave")
        leave_id = data.get("leave_id")
        reason = data.get("reason")
        
        if not userid:
            raise HTTPException(status_code=400, detail="userid is required")
        
        result = await Mongo.notify_leave_rejected(userid, leave_type, leave_id, reason)
        return {"success": True, "notification_id": result, "message": "Leave rejected notification sent"}
        
    except Exception as e:
        print(f"Error creating leave rejected notification: {e}")
        return {"success": False, "error": str(e)}

@app.post("/notifications/leave/recommended")
async def notify_leave_recommended_endpoint(data: dict):
    """Create leave recommended notification"""
    try:
        userid = data.get("userid")
        leave_type = data.get("leave_type", "Leave")
        manager_name = data.get("manager_name")
        leave_id = data.get("leave_id")
        
        if not userid or not manager_name:
            raise HTTPException(status_code=400, detail="userid and manager_name are required")
        
        result = await Mongo.notify_leave_recommended(userid, leave_type, manager_name, leave_id)
        return {"success": True, "notification_id": result, "message": "Leave recommended notification sent"}
        
    except Exception as e:
        print(f"Error creating leave recommended notification: {e}")
        return {"success": False, "error": str(e)}

@app.post("/notifications/wfh/submitted")
async def notify_wfh_submitted_endpoint(data: dict):
    """Create WFH submitted notification"""
    try:
        userid = data.get("userid")
        request_date = data.get("request_date")
        wfh_id = data.get("wfh_id")
        
        if not userid:
            raise HTTPException(status_code=400, detail="userid is required")
        
        result = await Mongo.notify_wfh_submitted(userid, request_date, wfh_id)
        return {"success": True, "notification_id": result, "message": "WFH submitted notification sent"}
        
    except Exception as e:
        print(f"Error creating WFH submitted notification: {e}")
        return {"success": False, "error": str(e)}

@app.post("/notifications/wfh/approved")
async def notify_wfh_approved_endpoint(data: dict):
    """Create WFH approved notification"""
    try:
        userid = data.get("userid")
        request_date = data.get("request_date")
        wfh_id = data.get("wfh_id")
        
        if not userid:
            raise HTTPException(status_code=400, detail="userid is required")
        
        result = await Mongo.notify_wfh_approved(userid, request_date, wfh_id)
        return {"success": True, "notification_id": result, "message": "WFH approved notification sent"}
        
    except Exception as e:
        print(f"Error creating WFH approved notification: {e}")
        return {"success": False, "error": str(e)}

@app.post("/notifications/wfh/rejected")
async def notify_wfh_rejected_endpoint(data: dict):
    """Create WFH rejected notification"""
    try:
        userid = data.get("userid")
        request_date = data.get("request_date")
        wfh_id = data.get("wfh_id")
        reason = data.get("reason")
        
        if not userid:
            raise HTTPException(status_code=400, detail="userid is required")
        
        result = await Mongo.notify_wfh_rejected(userid, request_date, wfh_id, reason)
        return {"success": True, "notification_id": result, "message": "WFH rejected notification sent"}
        
    except Exception as e:
        print(f"Error creating WFH rejected notification: {e}")
        return {"success": False, "error": str(e)}

@app.post("/test/notifications/manager-workflow/{userid}")
async def test_manager_workflow_notifications(userid: str):
    """Test endpoint for complete leave/WFH manager notification workflow"""
    try:
        # Get user details
        user = Mongo.Users.find_one({"_id": Mongo.ObjectId(userid)})
        if not user:
            return {"error": "User not found"}
        
        user_name = user.get("name", "Test User")
        
        results = []
        
        # Test 1: Leave submission notification to employee
        result1 = await Mongo.notify_leave_submitted(userid, "Test Leave", "test_leave_001")
        results.append({"test": "Employee Leave Notification", "result": result1})
        
        # Test 2: WFH submission notification to employee  
        result2 = await Mongo.notify_wfh_submitted(userid, "2025-09-10", "test_wfh_001")
        results.append({"test": "Employee WFH Notification", "result": result2})
        
        # Test 3: Manager notifications (if manager exists)
        manager_id = await Mongo.get_user_manager_id(userid)
        if manager_id:
            # Test leave manager notification
            result3 = await Mongo.notify_manager_leave_request(
                employee_name=user_name,
                employee_id=userid,
                leave_type="Test Leave",
                leave_date="10-09-2025",
                manager_id=manager_id,
                leave_id="test_leave_001"
            )
            results.append({"test": "Manager Leave Approval Notification", "result": result3})
            
            # Test WFH manager notification
            result4 = await Mongo.notify_manager_wfh_request(
                employee_name=user_name,
                employee_id=userid,
                request_date_from="2025-09-15",
                request_date_to="2025-09-15",
                manager_id=manager_id,
                wfh_id="test_wfh_001"
            )
            results.append({"test": "Manager WFH Approval Notification", "result": result4})
        else:
            results.append({"test": "Manager Notifications", "result": "No manager found for user"})
        
        return {
            "message": "Manager workflow notification test completed",
            "user": user_name,
            "manager_id": manager_id,
            "results": results
        }
        
    except Exception as e:
        print(f"Error testing manager workflow notifications: {e}")
        return {"error": str(e)}

@app.post("/test/enhanced-notifications/{userid}")
async def test_enhanced_notifications_endpoint(userid: str):
    """Test endpoint for enhanced leave and WFH notifications"""
    try:
        results = []
        
        # Test Leave Notifications
        result1 = await Mongo.notify_leave_submitted(userid, "Annual Leave", "leave_test_001")
        results.append(f"Leave submitted: {result1}")
        
        await asyncio.sleep(0.5)  # Brief delay between notifications
        
        result2 = await Mongo.notify_leave_recommended(userid, "Annual Leave", "John Smith", "leave_test_001")
        results.append(f"Leave recommended: {result2}")
        
        await asyncio.sleep(0.5)
        
        result3 = await Mongo.notify_leave_approved(userid, "Annual Leave", "leave_test_001")
        results.append(f"Leave approved: {result3}")
        
        # Test WFH Notifications
        await asyncio.sleep(0.5)
        
        result4 = await Mongo.notify_wfh_submitted(userid, "2025-09-10", "wfh_test_001")
        results.append(f"WFH submitted: {result4}")
        
        await asyncio.sleep(0.5)
        
        result5 = await Mongo.notify_wfh_approved(userid, "2025-09-10", "wfh_test_001")
        results.append(f"WFH approved: {result5}")
        
        # Test rejection scenarios
        await asyncio.sleep(0.5)
        
        result6 = await Mongo.notify_leave_rejected(userid, "Sick Leave", "leave_test_002", "Insufficient documentation")
        results.append(f"Leave rejected: {result6}")
        
        await asyncio.sleep(0.5)
        
        result7 = await Mongo.notify_wfh_rejected(userid, "2025-09-15", "wfh_test_002", "Team meeting scheduled")
        results.append(f"WFH rejected: {result7}")
        
        return {
            "success": True, 
            "message": "Enhanced notification test completed",
            "results": results,
            "total_notifications": len(results)
        }
        
    except Exception as e:
        print(f"Error testing enhanced notifications: {e}")
        return {"success": False, "error": str(e)}

@app.post("/test/admin-notifications")
async def test_admin_notifications():
    """Test endpoint for admin notification system"""
    try:
        results = []
        
        # Test 1: Check if admin IDs can be retrieved
        admin_ids = await Mongo.get_admin_user_ids()
        results.append(f"Admin IDs found: {admin_ids}")
        
        if not admin_ids:
            return {
                "success": False,
                "message": "No admin users found - this is why admin is not getting notifications!",
                "results": results
            }
        
        # Test 2: Test admin notification for a sample manager leave
        result1 = await Mongo.notify_admin_manager_leave_request(
            manager_name="Test Manager",
            manager_id="test_manager_001",
            leave_type="Test Leave",
            leave_date="10-09-2025",
            leave_id="test_leave_admin_001"
        )
        results.append(f"Admin manager leave notification: {result1}")
        
        # Test 3: Test admin pending leaves notification
        result2 = await Mongo.notify_admin_pending_leaves()
        results.append(f"Admin pending leaves notification: {result2}")
        
        return {
            "success": True,
            "message": "Admin notification test completed",
            "results": results,
            "admin_count": len(admin_ids)
        }
        
    except Exception as e:
        print(f"Error testing admin notifications: {e}")
        return {"success": False, "error": str(e)}

@app.get("/debug/admin-data")
async def debug_admin_data():
    """Debug endpoint to check admin user data and potential issues"""
    try:
        results = {}
        
        # Check admin collection
        admin_users = list(Mongo.admin.find({}, {"_id": 1, "name": 1, "email": 1}))
        results["admin_collection"] = {
            "count": len(admin_users),
            "users": admin_users[:5]  # Show first 5 for debugging
        }
        
        # Check Users collection for admin positions
        admin_position_users = list(Mongo.Users.find(
            {"position": {"$in": ["Admin", "Administrator", "CEO", "Director"]}}, 
            {"_id": 1, "name": 1, "position": 1, "email": 1}
        ))
        results["users_collection_admins"] = {
            "count": len(admin_position_users),
            "users": admin_position_users[:5]  # Show first 5 for debugging
        }
        
        # Check all positions in Users collection
        all_positions = list(Mongo.Users.distinct("position"))
        results["all_positions"] = all_positions
        
        # Test admin ID retrieval
        admin_ids = await Mongo.get_admin_user_ids()
        results["retrieved_admin_ids"] = admin_ids
        
        # Check for pending manager leaves
        manager_users = list(Mongo.Users.find({"position": "Manager"}, {"_id": 1, "name": 1}))
        manager_ids = [str(manager["_id"]) for manager in manager_users]
        
        pending_manager_leaves = list(Mongo.Leave.find({
            "userid": {"$in": manager_ids},
            "Recommendation": {"$exists": False},
            "status": {"$exists": False}
        }, {"_id": 1, "employeeName": 1, "leaveType": 1, "selectedDate": 1}))
        
        results["manager_data"] = {
            "manager_count": len(manager_users),
            "pending_leaves_count": len(pending_manager_leaves),
            "sample_pending_leaves": pending_manager_leaves[:3]
        }
        
        return {
            "success": True,
            "debug_results": results
        }
        
    except Exception as e:
        print(f"Error in admin debug: {e}")
        return {"success": False, "error": str(e)}

@app.post("/test/hr-wfh-notifications")
async def test_hr_wfh_notifications():
    """Test endpoint for HR WFH notification system"""
    try:
        results = []
        
        # Test HR notification for pending WFH requests
        result1 = await Mongo.notify_hr_pending_wfh()
        results.append(f"HR pending WFH notifications: {result1}")
        
        # Test individual HR recommended WFH notification
        result2 = await Mongo.notify_hr_recommended_wfh(
            employee_name="Test Employee",
            employee_id="test_employee_id",
            request_date_from="15-09-2025",
            request_date_to="15-09-2025",
            recommended_by="Test Manager",
            wfh_id="test_wfh_001"
        )
        results.append(f"HR recommended WFH notification: {result2}")
        
        return {
            "success": True,
            "message": "HR WFH notification test completed",
            "results": results,
            "note": "Check HR users for new notifications"
        }
        
    except Exception as e:
        print(f"Error in HR WFH notification test: {e}")
        return {"success": False, "error": str(e)}

@app.post("/test/admin-wfh-notifications")
async def test_admin_wfh_notifications():
    """Test endpoint for admin WFH notification system"""
    try:
        results = []
        
        # Test admin notification for pending WFH requests
        result1 = await Mongo.notify_admin_pending_wfh()
        results.append(f"Admin pending WFH notifications: {result1}")
        
        # Test individual admin manager WFH notification
        result2 = await Mongo.notify_admin_manager_wfh_request(
            manager_name="Test Manager",
            manager_id="test_manager_id",
            request_date_from="2025-09-15",
            request_date_to="2025-09-15",
            wfh_id="test_wfh_001"
        )
        results.append(f"Admin manager WFH notification: {result2}")
        
        return {
            "success": True,
            "message": "Admin WFH notification test completed",
            "results": results,
            "note": "Check admin users for new notifications"
        }
        
    except Exception as e:
        print(f"Error in admin WFH notification test: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Get absolute paths to the SSL certificate and key files
    key_file_path = os.path.join(os.path.dirname(__file__), '../certificates/key.pem')
    cert_file_path = os.path.join(os.path.dirname(__file__), '../certificates/cert.pem')

    # Temporarily run without SSL for WebSocket testing
    uvicorn.run(
        "Server:app",  # Replace with your actual file/module name
        host="0.0.0.0",  # Listen on all network interfaces (public access)
        port=8000,  # Or another port like 4433 if needed
        # ssl_keyfile=key_file_path,  # Path to your private key
        # ssl_certfile=cert_file_path  # Path to your certificate
    )