from rg_app.common.msg.base_model import BaseModel


class UnlockedRequest(BaseModel):
    user_id: int


class AccountDeleteRequest(BaseModel):
    user_id: int
