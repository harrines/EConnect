from datetime import datetime
import pytz
import re
from pydantic import BaseModel, validator, ValidationError
from typing import Optional, List, Dict, Union
from datetime import date

class Item(BaseModel):
    email: str
    # password: str
    name: str

class Item2(BaseModel):
    email: str
    # password: str
    name:str

class Item(BaseModel):
    email: str
    password: str
    name: str
    phone: str
    position: str
    date_of_joining: str

    # @validator("email")
    # def validate_email(cls, value):
    #     if not value:
    #         raise ValueError("Email must be provided.")
    #     # if (("@rbg" not in value) and ('.ai' not in value)):
    #     #     raise ValueError("Invalid email.")
    
    #@validator("password")
    #def validate_password(cls, value):
     #   if not value:
      #      raise ValueError("Password must be provided.")
       # if len(value) < 8:
        #    raise ValueError("Password must be at least 8 characters long.")
        #if not re.search(r"[0-9]", value):
         #   raise ValueError("Password must contain at least one number.")
        #if not re.search(r"[@#$%&]", value):
         #   raise ValueError("Password must contain at least one special character (@#$%&).")
        #return value*/
    
    @validator("name")
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name must be provided.")
        return value

class Item2(BaseModel):
    email: str
    password: str

class Item3(BaseModel):
    id: str
    
class Item4(BaseModel):
    data: str 
    id:str
    filename:str
    
class Item5(BaseModel):
    client_name: str 
    email:str

class Item9(BaseModel):
    client_name: str 
    email:str
    userid:str
    password:str
    
class Csvadd(BaseModel):
    data :str
    name:str
    fileid:str

class Csvedit(BaseModel):
    data:str
    name:str
    id:int
    fileid:str

class Csvdel(BaseModel):
    id:int
    fileid:str

class CT(BaseModel):
    name:str
    userid:str

    @property
    def current_time(self) -> str:
        now  = datetime.now(pytz.timezone("Asia/Kolkata"))
        return now.strftime("%I:%M:%S %p")
    
class UserId(BaseModel):
    user_id: str

class Item6(BaseModel):
    userid: str
    employeeName: str
    leaveType: str
    reason: str
    selectedDate: Union[date, str]
    requestDate: Union[date, str]
    time: Optional[str] = None
    status: Optional[str] = ""
    
    @validator('selectedDate', pre=True)
    def parse_selected_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('selectedDate must be in YYYY-MM-DD format')
        return v
    
    @validator('requestDate', pre=True)
    def parse_request_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('requestDate must be in YYYY-MM-DD format')
        return v 

class Item7(BaseModel):
    userid: str
    employeeName: str
    leaveType: str
    reason: str
    selectedDate: Union[date, str]
    ToDate: Union[date, str]
    requestDate: Union[date, str]
    
    @validator('selectedDate', pre=True)
    def parse_selected_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('selectedDate must be in YYYY-MM-DD format')
        return v
    
    @validator('ToDate', pre=True)
    def parse_to_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('ToDate must be in YYYY-MM-DD format')
        return v
    
    @validator('requestDate', pre=True)
    def parse_request_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('requestDate must be in YYYY-MM-DD format')
        return v
    
class Item8(BaseModel):
    userid: str
    employeeName: str
    time: str
    leaveType: str
    selectedDate: Union[date, str]
    requestDate: Union[date, str]
    timeSlot: str 
    reason: str
    
    @validator('selectedDate', pre=True)
    def parse_selected_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('selectedDate must be in YYYY-MM-DD format')
        return v
    
    @validator('requestDate', pre=True)
    def parse_request_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('requestDate must be in YYYY-MM-DD format')
        return v   

class Item9(BaseModel):
    userid: str
    employeeName: str
    leaveType: str
    selectedDate: Union[date, str]
    reason: str
    requestDate: Union[date, str]
    
    @validator('selectedDate', pre=True)
    def parse_selected_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('selectedDate must be in YYYY-MM-DD format')
        return v
    
    @validator('requestDate', pre=True)
    def parse_request_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('requestDate must be in YYYY-MM-DD format')
        return v

class Tasklist(BaseModel):
    task: List
    userid: str
    date:str
    due_date: str

class SingleTaskAssign(BaseModel):
    task: List
    userid: str
    due_date: str
    date:str
    TL: str

class Taskedit(BaseModel):
    userid: str
    updated_task: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    taskid: str

class Gettasks(BaseModel):
    userid: str
    date: str

class Deletetask(BaseModel):
    taskid: str

class RemoteWorkRequest(BaseModel):
    userid: str
    employeeName: str
    fromDate: date
    toDate: date
    requestDate: date
    reason: str
    ip: str

class DeleteLeave(BaseModel):
    userid: str
    fromDate: str
    requestDate: str
    leavetype: str

class AddEmployee(BaseModel):
    name: str
    email: str
    phone: str
    position: str
    department: str
    address: str
    date_of_joining: str
    education: List[Dict[str, Union[str,int]]]  # A list of educational qualifications
    skills: List[Dict[str, Union[str, int]]]  # A list of skills with 'name' and 'level'
    TL: str
    personal_email: str
    resume_link: str
    status: str
    ip: str
    


class EditEmployee(BaseModel):
    userid: str
    name: str
    email: str
    phone: str
    position: str
    department: str
    address: str 
    date_of_joining: str  # Changed from dateOfJoining
    education: List[Dict[str, Union[str, int]]]
    skills: List[Dict[str, Union[str, int]]]
    TL: str
    personal_email: str
    resume_link: str
    status: str
    ip: str
    
    @validator('skills')
    def validate_skills(cls, v):
        """Ensure skill levels are integers"""
        for skill in v:
            if 'level' in skill:
                try:
                    skill['level'] = int(skill['level'])
                except (ValueError, TypeError):
                    skill['level'] = 0
        return v

# class EditEmployee(BaseModel):
#  userid: str
#  name: str
#  email: str
#  phone: str
#  position: str
#  department: str
#  address: str 
#  education: List[Dict[str, Union[str,int]]] # A list of educational qualifications
#  skills: List[Dict[str, Union[str, int]]] # A list of skills with 'name' and 'level'
#  TL: str
#  personal_email: str
#  resume_link:str
#  status: str
#  ip:str


class Taskassign(BaseModel):
    Task_details: List[Dict[str, Union[str, int, List[str]]]]
    assigner_name: Optional[str] = None  # Name of the person assigning tasks
    assigner_id: Optional[str] = None    # ID of the person assigning tasks
    single_notification_per_user: Optional[bool] = True  # Send one notification per user instead of per task
    
class Settings(BaseModel):
    authjwt_secret_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJhZG1pbl9pZCIsInJvbGUiOiJhZG1pbiIsImV4cGlyZXMiOjE3MDk3MTM2NjEuMjc5ODk4NH0.DwYyZBkO20Kicz5vvqxpCrxZ7279uHRlLttNDBVO-_E"
    authjwt_algorithm: str = "HS256"

class NotificationModel(BaseModel):
    userid: str
    title: str
    message: str
    type: str
    priority: Optional[str] = "medium"
    action_url: Optional[str] = None

class NotificationUpdate(BaseModel):
    is_read: bool

class NotificationFilter(BaseModel):
    userid: Optional[str] = None
    type: Optional[str] = None
    is_read: Optional[bool] = None


