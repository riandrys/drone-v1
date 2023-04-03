# Drone v-1
### Clone the repository
```shell
git clone url_repository
```
### Install dependencies
Create and activate enviroment
```shell
$ cd /path/to/Drone
$ python -m venv myenv
$ source myenv/bin/activate
```


Install dependencies
```shell
pip install -r requirements.txt
```


### Run migrations
```shel
$ alembic upgrade head
```

### Run server locally
With the environment activeted run in folder root of the project:
```shell
$ uvicorn src.main:app --reload
```
