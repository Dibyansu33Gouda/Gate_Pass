import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

def clean_phone(v: str) -> str:
    cleaned = re.sub(r"[\s\-\(\)\+]", "", v.strip())
    if len(cleaned) == 12 and cleaned.startswith("91"):
        cleaned = cleaned[2:]
    if not (len(cleaned) == 10 and cleaned.isdigit()):
        raise ValueError("Phone number must be exactly 10 digits.")
    return cleaned

class PhoneModel(BaseModel):
    phone: str
    @field_validator("phone")
    @classmethod
    def check_phone(cls, v: str) -> str:
        return clean_phone(v)

class LoginForm(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)

class ResidentForm(PhoneModel):
    name: str = Field(..., min_length=2, max_length=100)
    flat_no: str = Field(..., min_length=1, max_length=10)
    email: Optional[str] = None

class StaffForm(PhoneModel):
    staff_name: str = Field(..., min_length=2, max_length=100)
    shift: str = Field(..., pattern=r"^(Morning|Evening|Night)$")

class DeliveryAgentForm(PhoneModel):
    agent_name: str = Field(..., min_length=2, max_length=100)
    courier_company: str = Field(..., min_length=2, max_length=80)

class VisitorRegisterForm(PhoneModel):
    visitor_name: str = Field(..., min_length=2, max_length=100)
    resident_id: int = Field(..., gt=0)
    purpose: str = Field(..., min_length=2, max_length=150)

class DeliveryForm(BaseModel):
    resident_id: int = Field(..., gt=0)
    agent_id: int = Field(..., gt=0)
    delivery_type: str = Field(..., pattern=r"^(Courier|Food|Other)$")
