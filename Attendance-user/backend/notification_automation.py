#!/usr/bin/env python3
"""
Enhanced Notification Automation System for E-Connect
Handles all automated notification triggers and scheduled tasks
"""

import asyncio
import pytz
from datetime import datetime, timedelta
from Mongo import (
    Tasks, Users, admin, Notifications, Clock, Leave, RemoteWork,
    create_notification_with_websocket, get_unread_notification_count,
    ObjectId
)
from websocket_manager import notification_manager

# Helper functions
def get_current_timestamp_ist():
    """Get current timestamp in IST timezone"""
    return datetime.now(pytz.timezone("Asia/Kolkata"))

def format_date_readable(date_str):
    """Convert DD-MM-YYYY to readable format"""
    try:
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        return dt.strftime("%B %d, %Y")
    except:
        return date_str

async def check_and_notify_overdue_tasks():
    """Check for overdue tasks and send notifications"""
    try:
        current_time = get_current_timestamp_ist()
        current_date = current_time.strftime("%d-%m-%Y")
        
        print(f"🔍 Checking overdue tasks for date: {current_date}")
        
        # Find all pending tasks
        overdue_tasks = list(Tasks.find({
            "status": {"$in": ["Pending", "In Progress", "pending", "in progress"]},
            "due_date": {"$exists": True, "$ne": ""}
        }))
        
        overdue_count = 0
        notifications_sent = 0
        
        for task in overdue_tasks:
            try:
                task_id = str(task["_id"])
                userid = task.get("userid")
                task_title = task.get("task", "Untitled Task")
                due_date_str = task.get("due_date")
                assigned_to = task.get("assigned_to", [])
                manager_id = task.get("manager_id")
                
                if not due_date_str:
                    continue
                
                # Parse due date
                due_date = datetime.strptime(due_date_str, "%d-%m-%Y")
                current_date_obj = datetime.strptime(current_date, "%d-%m-%Y")
                days_overdue = (current_date_obj - due_date).days
                
                if days_overdue > 0:
                    overdue_count += 1
                    
                    # Notify task owner/assignee
                    if userid:
                        await create_notification_with_websocket(
                            userid=userid,
                            title=f"⚠️ Task Overdue: {task_title}",
                            message=f"Task '{task_title}' is {days_overdue} day(s) overdue. Please complete it as soon as possible.",
                            notification_type="task_overdue",
                            priority="high",
                            action_url=f"/User/task",
                            related_id=task_id,
                            metadata={
                                "task_id": task_id,
                                "days_overdue": days_overdue,
                                "due_date": due_date_str
                            }
                        )
                        notifications_sent += 1
                    
                    # Notify assigned users
                    for assigned_user_id in assigned_to:
                        if assigned_user_id != userid:
                            await create_notification_with_websocket(
                                userid=assigned_user_id,
                                title=f"⚠️ Assigned Task Overdue: {task_title}",
                                message=f"Task '{task_title}' assigned to you is {days_overdue} day(s) overdue.",
                                notification_type="task_overdue",
                                priority="high",
                                action_url=f"/User/viewtask",
                                related_id=task_id,
                                metadata={
                                    "task_id": task_id,
                                    "days_overdue": days_overdue,
                                    "due_date": due_date_str
                                }
                            )
                            notifications_sent += 1
                    
                    # Notify manager about employee's overdue task
                    if manager_id and manager_id != userid:
                        # Get employee name
                        employee = Users.find_one({"_id": ObjectId(userid)}) if userid else None
                        employee_name = employee.get("name", "Employee") if employee else "Employee"
                        
                        await create_notification_with_websocket(
                            userid=manager_id,
                            title=f"🔔 Employee Task Overdue: {employee_name}",
                            message=f"{employee_name}'s task '{task_title}' is {days_overdue} day(s) overdue.",
                            notification_type="employee_task_overdue",
                            priority="high",
                            action_url=f"/admin/task",
                            related_id=task_id,
                            metadata={
                                "task_id": task_id,
                                "employee_id": userid,
                                "employee_name": employee_name,
                                "days_overdue": days_overdue
                            }
                        )
                        notifications_sent += 1
                        
            except Exception as e:
                print(f"❌ Error processing task {task.get('_id', 'unknown')}: {e}")
                continue
        
        print(f"✅ Overdue task check completed: {overdue_count} overdue tasks, {notifications_sent} notifications sent")
        return {"overdue_count": overdue_count, "notifications_sent": notifications_sent}
        
    except Exception as e:
        print(f"❌ Error in check_and_notify_overdue_tasks: {e}")
        return {"error": str(e)}

async def check_upcoming_deadlines():
    """Check for tasks due soon and send reminders"""
    try:
        current_time = get_current_timestamp_ist()
        today = current_time.strftime("%d-%m-%Y")
        tomorrow = (current_time + timedelta(days=1)).strftime("%d-%m-%Y")
        in_3_days = (current_time + timedelta(days=3)).strftime("%d-%m-%Y")
        
        print(f"🔍 Checking upcoming deadlines for: {today}, {tomorrow}, {in_3_days}")
        
        # Find tasks due today, tomorrow, or in 3 days
        upcoming_tasks = list(Tasks.find({
            "status": {"$in": ["Pending", "In Progress", "pending", "in progress"]},
            "due_date": {"$in": [today, tomorrow, in_3_days]}
        }))
        
        notifications_sent = 0
        
        for task in upcoming_tasks:
            try:
                task_id = str(task["_id"])
                userid = task.get("userid")
                task_title = task.get("task", "Untitled Task")
                due_date_str = task.get("due_date")
                assigned_to = task.get("assigned_to", [])
                
                if not due_date_str:
                    continue
                
                # Determine urgency
                if due_date_str == today:
                    urgency = "today"
                    priority = "high"
                    message = f"Task '{task_title}' is due TODAY. Please complete it before end of day."
                elif due_date_str == tomorrow:
                    urgency = "tomorrow"
                    priority = "medium"
                    message = f"Task '{task_title}' is due TOMORROW ({format_date_readable(due_date_str)}). Please prepare to complete it."
                else:
                    urgency = "soon"
                    priority = "medium"
                    message = f"Task '{task_title}' is due in 3 days ({format_date_readable(due_date_str)}). Please start working on it."
                
                # Notify task owner
                if userid:
                    await create_notification_with_websocket(
                        userid=userid,
                        title=f"⏰ Task Due {urgency.capitalize()}: {task_title}",
                        message=message,
                        notification_type="task_due_soon",
                        priority=priority,
                        action_url=f"/User/task",
                        related_id=task_id,
                        metadata={
                            "task_id": task_id,
                            "due_date": due_date_str,
                            "urgency": urgency
                        }
                    )
                    notifications_sent += 1
                
                # Notify assigned users
                for assigned_user_id in assigned_to:
                    if assigned_user_id != userid:
                        await create_notification_with_websocket(
                            userid=assigned_user_id,
                            title=f"⏰ Assigned Task Due {urgency.capitalize()}: {task_title}",
                            message=f"Task '{task_title}' assigned to you is due {urgency}.",
                            notification_type="task_due_soon",
                            priority=priority,
                            action_url=f"/User/viewtask",
                            related_id=task_id,
                            metadata={
                                "task_id": task_id,
                                "due_date": due_date_str,
                                "urgency": urgency
                            }
                        )
                        notifications_sent += 1
                        
            except Exception as e:
                print(f"❌ Error processing upcoming task {task.get('_id', 'unknown')}: {e}")
                continue
        
        print(f"✅ Upcoming deadline check completed: {notifications_sent} notifications sent")
        return {"notifications_sent": notifications_sent}
        
    except Exception as e:
        print(f"❌ Error in check_upcoming_deadlines: {e}")
        return {"error": str(e)}

async def check_missed_attendance():
    """Check for employees who haven't clocked in by 10 AM"""
    try:
        current_time = get_current_timestamp_ist()
        current_date = current_time.strftime("%d-%m-%Y")
        
        # Only check after 10 AM on weekdays
        if current_time.hour < 10 or current_time.weekday() >= 5:  # 0=Monday, 6=Sunday
            return {"message": "Not time for attendance check or weekend"}
        
        print(f"🔍 Checking missed attendance for date: {current_date}")
        
        # Get all active users
        all_users = list(Users.find({"status": {"$ne": "inactive"}}))
        notifications_sent = 0
        
        for user in all_users:
            try:
                userid = str(user["_id"])
                user_name = user.get("name", "Employee")
                
                # Check if user has clocked in today
                attendance_today = Clock.find_one({
                    "userid": userid,
                    "date": current_date,
                    "$or": [
                        {"clock_in_time": {"$exists": True, "$ne": ""}},
                        {"time": {"$exists": True, "$ne": ""}}
                    ]
                })
                
                if not attendance_today:
                    # Send missed clock-in notification
                    await create_notification_with_websocket(
                        userid=userid,
                        title="⏰ Missed Clock-In Reminder",
                        message=f"Hi {user_name}, you haven't clocked in today. Please clock in as soon as possible.",
                        notification_type="attendance",
                        priority="medium",
                        action_url="/User/Clockin_int",
                        metadata={
                            "date": current_date,
                            "type": "missed_clock_in"
                        }
                    )
                    notifications_sent += 1
                    
            except Exception as e:
                print(f"❌ Error checking attendance for user {user.get('_id', 'unknown')}: {e}")
                continue
        
        print(f"✅ Missed attendance check completed: {notifications_sent} notifications sent")
        return {"notifications_sent": notifications_sent}
        
    except Exception as e:
        print(f"❌ Error in check_missed_attendance: {e}")
        return {"error": str(e)}

async def check_pending_approvals():
    """Check for pending leave/WFH approvals that need attention"""
    try:
        current_time = get_current_timestamp_ist()
        notifications_sent = 0
        
        print("🔍 Checking pending approvals...")
        
        # Check pending leave requests
        pending_leaves = list(Leave.find({
            "status": {"$in": ["Pending", "pending", "Recommended"]}
        }))
        
        for leave in pending_leaves:
            try:
                leave_id = str(leave["_id"])
                userid = leave.get("userid")
                employee_name = leave.get("name", "Employee")
                leave_type = leave.get("leave_type", "Leave")
                from_date = leave.get("from_date")
                to_date = leave.get("to_date")
                status = leave.get("status", "Pending")
                
                # Get admin/HR users to notify
                admin_users = list(admin.find({}, {"_id": 1}))
                hr_users = list(Users.find({
                    "$or": [
                        {"position": {"$regex": "HR", "$options": "i"}},
                        {"department": {"$regex": "HR", "$options": "i"}}
                    ]
                }, {"_id": 1}))
                
                approval_users = admin_users + hr_users
                
                for approver in approval_users:
                    approver_id = str(approver["_id"])
                    
                    await create_notification_with_websocket(
                        userid=approver_id,
                        title=f"📋 Pending Leave Approval: {employee_name}",
                        message=f"{employee_name} has requested {leave_type} from {from_date} to {to_date}. Status: {status}",
                        notification_type="leave_approval_required",
                        priority="medium",
                        action_url="/admin/leaveapproval",
                        related_id=leave_id,
                        metadata={
                            "leave_id": leave_id,
                            "employee_id": userid,
                            "employee_name": employee_name,
                            "leave_type": leave_type,
                            "from_date": from_date,
                            "to_date": to_date
                        }
                    )
                    notifications_sent += 1
                    
            except Exception as e:
                print(f"❌ Error processing leave {leave.get('_id', 'unknown')}: {e}")
                continue
        
        # Check pending WFH requests
        pending_wfh = list(RemoteWork.find({
            "status": {"$in": ["Pending", "pending", "Recommended"]}
        }))
        
        for wfh in pending_wfh:
            try:
                wfh_id = str(wfh["_id"])
                userid = wfh.get("userid")
                employee_name = wfh.get("name", "Employee")
                from_date = wfh.get("from_date")
                to_date = wfh.get("to_date")
                status = wfh.get("status", "Pending")
                
                # Get admin/HR users to notify
                admin_users = list(admin.find({}, {"_id": 1}))
                hr_users = list(Users.find({
                    "$or": [
                        {"position": {"$regex": "HR", "$options": "i"}},
                        {"department": {"$regex": "HR", "$options": "i"}}
                    ]
                }, {"_id": 1}))
                
                approval_users = admin_users + hr_users
                
                for approver in approval_users:
                    approver_id = str(approver["_id"])
                    
                    await create_notification_with_websocket(
                        userid=approver_id,
                        title=f"🏠 Pending WFH Approval: {employee_name}",
                        message=f"{employee_name} has requested Work From Home from {from_date} to {to_date}. Status: {status}",
                        notification_type="wfh_approval_required",
                        priority="medium",
                        action_url="/admin/wfh",
                        related_id=wfh_id,
                        metadata={
                            "wfh_id": wfh_id,
                            "employee_id": userid,
                            "employee_name": employee_name,
                            "from_date": from_date,
                            "to_date": to_date
                        }
                    )
                    notifications_sent += 1
                    
            except Exception as e:
                print(f"❌ Error processing WFH {wfh.get('_id', 'unknown')}: {e}")
                continue
        
        print(f"✅ Pending approvals check completed: {notifications_sent} notifications sent")
        return {"notifications_sent": notifications_sent}
        
    except Exception as e:
        print(f"❌ Error in check_pending_approvals: {e}")
        return {"error": str(e)}

# Main automation runner
async def run_all_automated_checks():
    """Run all automated notification checks"""
    try:
        print("🚀 Starting automated notification checks...")
        
        results = {}
        
        # Run all checks concurrently
        overdue_result = await check_and_notify_overdue_tasks()
        upcoming_result = await check_upcoming_deadlines()
        attendance_result = await check_missed_attendance()
        approval_result = await check_pending_approvals()
        
        results["overdue_tasks"] = overdue_result
        results["upcoming_deadlines"] = upcoming_result
        results["missed_attendance"] = attendance_result
        results["pending_approvals"] = approval_result
        
        total_notifications = (
            overdue_result.get("notifications_sent", 0) +
            upcoming_result.get("notifications_sent", 0) +
            attendance_result.get("notifications_sent", 0) +
            approval_result.get("notifications_sent", 0)
        )
        
        print(f"✅ Automated checks completed. Total notifications sent: {total_notifications}")
        return results
        
    except Exception as e:
        print(f"❌ Error in run_all_automated_checks: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Run the automation checks
    asyncio.run(run_all_automated_checks())
