# EuroAge_IoT
EuroAge project with the objective of implementing IoT to elderly homes

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

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

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

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

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc


