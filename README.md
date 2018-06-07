# Pong Board
Pong Board is the ultimate leaderboard system for ping pong. The dream is to keep track of players previous games and ultimately provide a leaderboard with an ongoing ranking system. We all have to entertain our competitive nature... time to pong!
## Getting Started
The master branch is the most recent version and represents stable deployments. All development work is done in the development branch and ensuing feature branches.
### Using Docker
The app is containerized in Docker. Currently, this is only used to get apps up and running easily locally, but the thought one day is that this will be used for deployments. Eventually, we hope to also do all development work in Docker, although we first need to enable virtual Selenium functional tests in our Docker container. 
In the meantime, let's get started with the basics of Docker, and [install Docker](https://docs.docker.com/install/) for your machine.
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
### Deployment with Heroku
Pong Board is Heroku compatible for quick and easy deployment. All [Django settings](pongboard/settings.py), required Heroku files (such as the [Procfile](Procfile) and [runtime file](runtime.txt), and [required python packages](requirements.txt) needed for deployment to Heroku are already provided. All that remains to deploy the app yourself is a Heroku account and client installed. After this is done, we can create our Heroku app by running:
```
heroku create
```
(where after `create` you can optionally name your Heroku app. The name you provide is used as a subdomain for its Heroku deployment; if you don't provide a name a randomly gnerated one is given to you).

Next, get your app running on Heroku:
```
git push heroku master
```
This assumes that you're pushing code from your master branch. If instead you were to push from another branch `branch-name`, use:
```
git push heroku branch-name:master
```
At this point, your app should be up and running on Heroku! For more detailed information, see Heroku's [deployment tutorial](https://devcenter.heroku.com/articles/getting-started-with-python#introduction).
