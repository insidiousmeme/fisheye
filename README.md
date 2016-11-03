# fisheye
Convert dual fisheye image to equirectangular images for mp4 video files.


## How to Run on AWS Ubuntu

* ssh into AWS instance
* Ensure you have installed git, docker
* Clone repo `git clone git@github.com:insidiousmeme/fisheye.git`
* Pull latest docker image  prepared for fisheye project
`docker pull dmigous/fedora_fisheye`
* Go to repo folder `cd fisheye`
* Run ```docker run -i -t -p 80:80 -v `pwd`:/mnt dmigous/fedora_fisheye /bin/bash -c "source /root/.bashrc; /mnt/fisheye_webservice/util/prepare_apache.sh; /etc/httpd/run_apache_foreground"```

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

NOTE: this instructions only valid if you had __working correctly__ container
and then by some reason it stoped and you need to restart it. Run following command:

* cd into fisheye repo folder
```
cd workspace/fisheye
```
* kill all previous fisheye_webservice docker containers
```
docker rm `docker ps -a | grep "dmigous/fedora_fisheye" | awk '{print $1}'`
```
* Run ```docker run -i -t -p 80:80 -v `pwd`:/mnt dmigous/fedora_fisheye /bin/bash -c "source /root/.bashrc; /mnt/fisheye_webservice/util/prepare_apache.sh; /etc/httpd/run_apache_foreground"```


## F.A.Q.

###### 1. Why to use Docker and not run on AWS directly?
First, the project has very complex dependencies, and we tried to install needed
packages on CentOS, Ubuntu and had no luck. After all it worked only on Fedora
smoothly. So decision was to create docker container based on Fedora with
required projects. Having such docker image we are able to run our system on
any host that supports docker.


## Known issues