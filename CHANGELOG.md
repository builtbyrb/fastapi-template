## 0.2.0 (2026-04-11)

### Feat

- **core/types**: added new type like OneUpercase etc
- **core**: added validatorFn
- **tests**: added tests setup
- **test**: added pytest
- **alembic**: added alembic to the project
- **logging**: added acces logging middleware
- **logging**: added logging setup

### Fix

- **users/typings**: fixed text too long
- **src/core/validators**: fixed contains_value fn
- **users**: fixed circular import
- **core**: fixed circular import
- **docker-compose-logs.yml**: fixed image
- **docker-compose-logs.yml**: fixed image
- **docker-compose-logs.yml**: fixed vector version
- **docker-compose**: fixed resources limit
- **docker-compose-logs**: fixed config loading
- **deploy**: fixed deploy worflows
- **flunt-bit**: fixed flunet-bit config
- **vector.toml**: fixed sinks.axiom
- **health-route**: Fixed health route response model
- **deploy**: removed history clear
- **workflows**: fixed github workflows
- **dockercompose**: fixed docker compose volumes
- **env**: deleted env file
- **gitignore**: fixed gitignore env file
- **redis**: fixed redis port
- **database**: fixed database port
- **dockerfile**: dockerfile fix
- **dockerfile**: fixed port
- **dockerfile**: fixed uvicorn
- **docker**: docker
- **fix-worker**: fix worker
- **dockerfile**: fix host
- **worker**: fixed config kwargs

### Refactor

- **users/typings**: added new types
- **src**: refactored all types folder
- **core**: updated resolve_ip_from_data function and added serialiser
- **users**: upgraded no email rules
- **src**: renamed validator_fn to predicate_fn
- **refresh_token**: moved interfaces file into type
- **users**: separed buisness rule logic and data
- **core**: refactored rules and export
- **docker-compose**: reogarnize files
- added stagging environement
- **loggingLevel**: Added logging level in env file
- **processors**: added drop_color_message_key processor
- **AccesLogging**: Added a message in the acces logging middleware
- **color_message**: remove drop_color_message processor
- **deploy**: updated inputs to secrets
- **deploy.yml**: added logs
- **environment**: added prod environement
- **auth**: added run_in_threadpool
- **docker-compose-app**: changed app host
- **dockerfile**: remove workers
- **dockerfile**: added workers
- **database**: switch to nullPool
- **dockerfile**: removed healtcheck

### Perf

- updated pool settings
- **dockerfile**: remplace gunicorn for uvicorn
