# Drone v-1
### Clone the repository
```shell
git clone https://github.com/riandrys/drone-v1.git
```
## Local Development

### First build only
1. `cp .env.example .env`
2. `docker-compose up -d --build`

### Daily development
1. `docker-compose up -d`


### Migrations with Alembic

Apply migrations
```shell
docker-compose exec api migrate
```
### API
Visit the api docs at http://172.88.0.3:8000/docs

Seed database at http://172.88.0.3:8000/drones/seed_db/

### Run test
```shell
docker-compose exec api runtest
```
