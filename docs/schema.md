# Schema

*model_to_schema*

```python
# generate pydantic schema from models
# `User` is a db.Model or db.BaseModel instance 
from bali.schemas import model_to_schema
UserSchema = model_to_schema(User)
```
