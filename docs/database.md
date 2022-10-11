# Database 

## connect

```python
from bali.core import db
# connect to database when app started
# db is a sqla-wrapper instance
db.connect('DATABASE_URI')  
  
```

## Declarative mode with sqla-wrapper

```python
class User(db.Model):
    __tablename__ "users"
    id = db.Column(db.Integer, primary_key=True)
    ...
db.create_all()
db.add(User(...))
db.commit()
todos = db.query(User).all()
```

More convenient usage, ref to [SQLA-Wrapper](https://github.com/jpsca/sqla-wrapper)


## Declare models inherit from convenient base models

*BaseModel*

```python
# using BaseModel
class User(db.BaseModel):
    __tablename__ "users"
    id = db.Column(db.Integer, primary_key=True)
    ...
```

```python
# BaseModel's source code 
class BaseModel(db.Model):
    __abstract__ = True
    created_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_time = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active = Column(Boolean(), default=True)
```

## Transaction

SQLA-wrapper default model behavior is auto commit, auto commit will be disabled with `db.transaction` context. 

```python
with db.transaction():
    item = Item.create(name='test1')
```

## Operators

Operators provided `get_filters_expr` to transform filters (dict) to SQLAlchemy expressions.  

```python
from bali.db.operators import get_filters_expr
from models import User
users = User.query().filter(*get_filters_expr(User, **filters)).all()
```

## Migrate

#### Migrate Config

In <4.0 versions, you should enable migrate first.

`ENABLE_MIGRATE` default value is `False` in <4.0, and will be `True` after 4.0 release. 

```python
class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///todo.sqlite'
    ENABLE_MIGRATE: bool = True
```

#### Migrate commands

```bash
python main.py db init
```
This will add a migrations folder to your application. 
The contents of this folder need to be added to version control along with your other source files.


```bash
python main.py db migrate
```
Generate migration, the migration script needs to be reviewed and edited, as Alembic currently does not detect every change you make to your models.


```bash
python main.py db upgrade
```
Apply the migration to the database


```bash
python main.py db --help
```
To see all the commands that are available run this command
