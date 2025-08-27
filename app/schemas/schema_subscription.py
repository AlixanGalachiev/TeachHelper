from pydantic import BaseModel
import uuid
from app.models.model_subscription import SubscriptionType


class SubscriptionCreate(BaseModel):
	type: SubscriptionType
	price: int
	description: str

class SubscriptionRead(SubscriptionCreate):
	id: uuid.UUID

class SubscriptionUpdate(BaseModel):
	id:          uuid.UUID
	price:       int               | None = None
	description: str               | None = None
	type:        SubscriptionType  | None = None
