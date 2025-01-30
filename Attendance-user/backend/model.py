from datetime import datetime
import pytz
import re
from pydantic import BaseModel, validator, ValidationError
from typing import Optional, List, Dict, Union
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
    
    @validator("password")
    def validate_password(cls, value):
        if not value:
            raise ValueError("Password must be provided.")
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number.")
        if not re.search(r"[@#$%&]", value):
            raise ValueError("Password must contain at least one special character (@#$%&).")
        return value
    
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
    selectedDate: str
    requestDate: str 
    status:str

class Item7(BaseModel):
    userid: str
    employeeName: str
    leaveType: str
    reason: str
    selectedDate: str
    ToDate : str
    requestDate: str 
    
class Item8(BaseModel):
    userid: str
    employeeName: str
    time: str
    leaveType: str
    selectedDate: str
    requestDate: str 
    timeSlot :str 
    reason: str   

class Item9(BaseModel):
    userid: str
    employeeName: str
    leaveType: str
    selectedDate: str
    reason: str
    requestDate: str 

class Tasklist(BaseModel):
    task: str
    userid: str
    date:str

class Taskedit(BaseModel):
    userid: str
    task: str
    updated_task: Optional[str] = None
    status: Optional[str] = None
    date:str

class Gettasks(BaseModel):
    userid: str
    date: str

class Deletetask(BaseModel):
    task: str
    userid: str
    date: str

class RemoteWorkRequest(BaseModel):
    userid: str
    employeeName: str
    fromDate: str
    toDate: str
    requestDate: str
    reason: str

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
    # education: List[str]  # Changed to List for an array of strings
    # skills: List[dict]    
    education: List[Dict[str, Union[str,int]]]  # A list of educational qualifications
    skills: List[Dict[str, Union[str, int]]]  # A list of skills with 'name' and 'level'
    TL: str

   
class Settings(BaseModel):
    authjwt_secret_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJhZG1pbl9pZCIsInJvbGUiOiJhZG1pbiIsImV4cGlyZXMiOjE3MDk3MTM2NjEuMjc5ODk4NH0.DwYyZBkO20Kicz5vvqxpCrxZ7279uHRlLttNDBVO-_E"
    authjwt_algorithm: str = "HS256"

