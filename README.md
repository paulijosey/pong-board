# Pong Board
Pong Board is the ultimate leaderboard system for ping pong. The dream is to keep track of players previous games and ultimately provide a leaderboard with an ongoing ranking system. We all have to entertain our competitive nature... time to pong!
## Getting Started
The master branch is a simple skeleton of a containerized Django project using Docker. All development work is done in the development branch and ensuing feature branches.
### Development in Docker
To get started, [install Docker](https://docs.docker.com/install/) for your machine.
Once installed, we first need to build our images from the docker-compose file. To do this, simply navigate to the root folder of this repo, and run:
```
docker-compose build
```
Once the image is built, we can create a container using:
```
docker-compose up
```
This will spawn a continual process running in your current shell. To run the process in the background, you can use the `-d` option:
```
docker-compose up -d
```
Regardless, you can now access your Django web app at `http://localhost:8000`. Congrats!
You can also see your containers running by using:
```
docker ps
```
Lastly, to shut down your containers, simply use:
```
docker-compose down
```
That's it folks!