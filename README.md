# EuroAge_IoT
EuroAge project with the objective of implementing IoT to elderly homes

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* ConBeeII
* MongoDB
* Docker (not required)

### Installing without docker

For PyProject 

```
sudo apt git
sudo apt python
sudo apt install python-pip
pip install pyserial
```

For EuroAge Project
```
Install MongoDB Community Edition
Install MongoDB Compass

In case of problems with mongod.service run: "sudo systemctl enable mongod.service"
```
Setting up the Server (If authentication required):
```
https://medium.com/founding-ithaka/setting-up-and-connecting-to-a-remote-mongodb-database-5df754a4da89

sudo service mongod start

Log in if authentication applied: mongo -u useradmin  127.0.0.1/admin
```

Install nodejs/npm and run:
```
npm run devStart
```

To make request just run the cmd to get the internal ip:
```
ip addr show
```

Commands for a new project(just a sidenote):
```
npm init

npm i express mongoose
npm i --save-dev dotenv nodemon
```
### Installing/running with docker
Install Docker
```
```

Install docker-compose
```
https://docs.docker.com/compose/install/
```

For RaspBian (only):
```
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
```

Create .env file with:
```
#Without Docker:
#DATABASE_URL=mongodb://new_user:euroage@localhost/euroage

#For Docker:
DATABASE_URL=mongodb://mongo:27017/euroage
```

Run
```
sudo docker-compose build
Start: sudo docker-compose up
Stop:  sudo docker-compose down
```
Access data:
```
sudo docker network ls
sudo docker network inspect euroage_iot_default
```

If mongodb and mosquitto installed:
```
sudo systemctl stop mosquitto
sudo service mongod stop
```

### Installing Mosquitto


### Installing Deconz

For Ubuntu 19.04
´´´
https://github.com/dresden-elektronik/deconz-rest-plugin
´´´
It might need the change from USB0 to ACM0

## Deployment

Add additional notes about how to deploy this on a live system

MongoDB
```
sudo service mongod start
mongodb-compass

```

Clear DB in docker
```
docker image prune -a -f
docker system prune --volumes -f
docker system df
```

## Acknowledgments
* **Billie Thompson** - *Template* - [PurpleBooth](https://github.com/PurpleBooth)


