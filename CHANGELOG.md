# Change Log
> All notable changes to this project will be documented in this file.
> 
> This project adheres to [Semantic Versioning](http://semver.org/).
> 
> includes Added / Changed / Fixed
> 

## [3.5.2] UNRELEASED

## [3.5.1] 2023-09-03
### Added
- Allows custom http host/port and rpc host/port [PR#172](https://github.com/bali-framework/bali/pull/172)

## [3.5.0] 2023-03-08
### Added
- Hybrid property to dict [PR#168](https://github.com/bali-framework/bali/pull/168)
- Enhanced Bali.register() make http/rpc register optinal [PR#170](https://github.com/bali-framework/bali/pull/170)
### Changed
- Created a typing.py file dedicated to storing type annotations
- Make response code more appropriate for Resource create route

## [3.4.1] 2022-12-24
### Fixed
- Fixed ParseDict/MessageToDict utils compatible in protobuf>=3.20

## [3.4.0] 2022-11-10
### Added
- Multi ENV Configuration [PR#153](https://github.com/bali-framework/bali/pull/153)
- Added Python 3.11 to the officially supported versions

### Changed
- Upgraded requirements and removed `decamelize` dependency
- Updated docs about using cases

### Breaking changes

If your project uses an outdated protobuf you may need to rebuild because all dependencies have been updated

## [3.3.0] 2022-10-11
### Added
- Integrated database migrate by `FastAPI-Migrate`
- Declarative API simple resource version (Major feature in 4.0)

### Changed
- upgrade grpc plugin versions

### Fixed
- Fixed importlib-metadata 5.0 conflict with kombu

## [3.2.2] 2022-07-11
### Fixed
- Fixed event stacking when no handler matched [PR#139](https://github.com/bali-framework/bali/pull/139)

## [3.2.1] 2022-07-05
### Added
- Event handler support class style
- Added bali.Environments

### Changed
- Removed dependency python-jose[cryptography]==3.2.0

### Fixed
- Fixed event handler message queue message stacking
- Fixed generic rpc schema find issue when it been override

## [3.2.0] 2022-06-16
### Added
- The concept of `manager` is introduced 🥂
- New elegant model API methods 🥂 [PR#122](https://github.com/bali-framework/bali/pull/122)
- Added `db.Base` declarative_base
- Application add `__clear__` for the convenience of unit testing
- Generated gRPC servicer for register resources 🍕 [PR#125](https://github.com/bali-framework/bali/pull/125)
- Introduce `pytest-grpc` for RPC service testing

### Changed
- Removed deprecated `connection.retry_on_deadlock_decorator`
- Removed deprecated `connection.close_connection`
- Updated related projects link comes from bali framework organization
- Removed deprecated `bali.schema`, use `bali.schemas` instead
- Marked `GRPCTestBase` as deprecated, will removed in v3.5
- Add more unit tests to ensure project quality 🏄‍

### Fixed
- Fixed initialize http service every requests
- Optimized and fixed ModelResource in resource register style

## [3.1.0 ~ 3.1.6] 2020-04-30 ~ 2020-05-23
### Added
- `Event` supported
- RabbitMQ fanout exchange support
### Fixed
- Compatible legacy SQLA-Wrapper SessionProxy

## [3.0.0] 2022-04-24
### Added
- Upgraded to sql-wrapper v5.0.0
- Supported uvicorn 0.15
- Model support asynchronous
- Resource support asynchronous
### Changed
- Removed main.py default launch behavior

## [2.1.3] 2021-11-19
### Added
- timezone added `localtime`/`localdate`

## [2.1.0] 2021-10-14
### Changed
- Adjusted version range dependency packages

## [2.0.0] 2021-05-26
### Added
- Resource layer base class, support elegant RESTful CRUD
- Refactor core layer, support multi dotenv variables
- Handle metadata or context

## [1.2.1] 2021-03-22
### Changed
- Added custom route class support clear SQLAlchemy scoped session

## [1.2.0] 2021-03-21
### Changed
- Added custom APIRouter support clear SQLAlchemy scoped session

## [1.1.2] 2021-03-20
### Fixed
- Fixed close and remove session when FastAPI request completed
### Changed
- Added SQLAlchemy pool_recycle setting, default value is 2 hours

## [1.1.0] 2021-03-03
### Added
- Added timezone settings and utility
- RPC logging when defined log handler
- New model method bind to BaseModel: count() and get_fields()

## [1.0.3] 2021-02-20
### Fixed
- locked uvicorn version (0.12.3) to fixed runtime error

## [1.0.0] 2021-01-26
### Added
- Added db stub file to improve code intelligence
- Ensure db remove even though exception raised
### Fixed
- gRPC base tests lost `ProcessInterceptor`

## [0.7.3] 2021-01-14
### Added
- Added FastAPI Request GZip decompression

## [0.7.2] 2021-01-14
### Added
- GZipMiddleware

## [0.7.1] 2021-01-07
### Added
- Added gRPC interceptor process setup & teardown
- Added FastAPI middleware process setup & teardown

## [0.7.0] 2020-12-18
### Added
- Added cache backend with Redis
- Added dateparse utility
### Fixed
- Fixed add_XXXServiceServicer_to_server in GRPCTestBase

## [0.6.0] 2020-11-26
### Added
- Added bali Application Wrapper

## [0.5.3] 2020-11-23
### Added
- Added `to_dict()` method to BaseModel

## [0.5.2] 2020-11-23
### Fixed
- Fixed lost package `pydantic-sqlalchemy`

## [0.5.1] 2020-11-19
### Fixed
- Fixed BaseModel's updated_time

## [0.5.0] 2020-11-19
### Added
- Added model utility `BaseModel`
- Added convenient way to generate Pydantic model

## [0.4.1] 2020-11-12
### Changed
- Removed `NextBase` replaced by `db.Model`

## [0.4.0] 2020-11-11
### Added
- Added `NextBase` enhanced declarative base

## [0.3.0] 2020-11-02
### Added
-- Added gRPC service unit test base class
### Fixed
- Fixed MAXIMUM_RETRY_ON_DEADLOCK not defined issue

## [0.2.1] 2020-10-23
### Added
- Added SQLAlchemy declarative Base

## [0.2.0] 2020-10-23
### Added
- Added code formatter `yapf`.
- Added sqla-wrapper
- Migrated db layer to core
- Added gRPC service mixin to close database connection

## [0.1.0] 2020-10-13
### Added
- Added gRPC / FastAPI stack requirements
