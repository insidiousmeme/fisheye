# fisheye
Convert dual fisheye image to equirectangular images for mp4 video files.


## How to Run on AWS Ubuntu
* ssh into AWS instance
* Ensure you have installed git, docker
* Clone repo `git clone git@github.com:insidiousmeme/fisheye.git`
* Pull latest docker image  prepared for fisheye project
`docker pull insidiousmeme/fedora_fisheye`

OR

* Build docker image from Dockerfile
`docker build -t insidiousmeme/fedora_fisheye .`


### Ubuntu 14.04 and Upstart
AWS has Ubuntu 14.04. So to start `fisheye_webserver` container on AWS host boot
we added Upstart config file. Before first usage you have to install it

##### Install Upstart script (executed only once)
* Go to repo folder `cd fisheye`
* Run `sudo ./fisheye_webservice/util/upstart/install_upstart_script.sh`

This will add relevant Upstart config to /etc/init folder.
NOTE: from now config has embedded path to repo folder. If you will move
repo folder on the file system to another place, then you have to re-invoke
`install_upstart_script.sh` script.

-----

After installation now you can run `fisheye_websever` using
`sudo service fisheye_webserver start`

And stop `fisheye_websever` using
`sudo service fisheye_webserver stop`


### Other systems
Upstart is supported only until Ubuntu 14.04. So if you want to run fisheye_webserver
on another system it is good to know what happends behind the scenes of Upstart config.

Here is instructions how to run `fisheye_webserver` docker container directly.

* Go to repo folder `cd fisheye`
* Run
```
docker run -d --name fisheye_webserver -i -t -p 80:80 -v `pwd`:/mnt insidiousmeme/fedora_fisheye /bin/bash -c "source /root/.bashrc; /mnt/fisheye_webservice/util/prepare_apache.sh; /etc/httpd/run_apache_foreground"
```


After that your server is UP!

If you want to run it from inside container and then fiddle with apache logs
or check something inside container you can do following:

* Run docker container
```docker run -i -t -p 80:80  -v `pwd`:/mnt fedora_fisheye bin/bash```.
Now you are inside docker container.
Inside /mnt folder you will find fisheye repo folder that is mounted inside
docker container from host AWS instance. All changes in this folder will
be seen in host also. The purpose of docker container in our case is just
* Run `/mnt/fisheye_webservice/util/prepare_apache.sh`. It will install inside
container all needed python dependencies and configure Apache to run fisheye
project. Our mounted `/mnt/fisheye_webservice` folder will be given to apache as
a soft link `/var/www/html/fisheye_webservice`. So all uploaded files while
service running will also appear in host filesystem in folders `uploads` and
`converted`
* The last step is to start web server by `/etc/httpd/run_apache_foreground`

### How to restart container?

If you had before __working correctly__ `fedora_fisheye` container
and then by some reason it stoped and you need to restart it, then
just run following command:

```
sudo docker start fisheye_webserver
```
It will take last running `fedora_fisheye` container start it.



If it doesn't worked you can do following procedure:

* cd into fisheye repo folder `cd workspace/fisheye`
* kill all previous fisheye_webservice docker containers
```
docker rm `docker ps -a | grep "insidiousmeme/fedora_fisheye" | awk '{print $1}'`
```
* Run
```
docker run -d --name fisheye_webserver -i -t -p 80:80 -v `pwd`:/mnt insidiousmeme/fedora_fisheye /bin/bash -c "source /root/.bashrc; /mnt/fisheye_webservice/util/prepare_apache.sh; /etc/httpd/run_apache_foreground"
```


## F.A.Q.

###### 1. Why to use Docker and not run on AWS directly?
First, the project has very complex dependencies, and we tried to install needed
packages on CentOS, Ubuntu and had no luck. After all it worked only on Fedora
smoothly. So decision was to create docker container based on Fedora with
required projects. Having such docker image we are able to run our system on
any host that supports docker.


###### 2. How to update DB?
```
sqlite3 ./fisheye_webservice/fisheye_webservice.db
insert into user(email, password, date_time, ip, payment_level) values('a@b.com', 'qwerty', (DATETIME('NOW')), '127.0.0.1', 1);
```



## Known issues