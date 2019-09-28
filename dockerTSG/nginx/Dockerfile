#Dockerfile to Create an Cenots environment to run my HTML Code
FROM centos

LABEL maintainer="bolajiagunbiade1@gmail.com"

#Make sure that Centos is fully updated and patched before Installing Apache on it
RUN yum update -y && yum install httpd -y

#Ensure to start the Apache2 Service & send stdout to /log as a sanity check
RUN service apache2 start > /log

#Get the code from Github to the /app Direcory
ADD https://raw.githubusercontent.com/ibrolord/myrepo/master/index.html /var/www/html/index.html

#Set the /app Directory as the Working Directory
WORKDIR /var/www/html/

#Give Appropriate Permissions
RUN chmod 644 index.html

#Expose Port 80 on Local Host
EXPOSE 80

#Start Apache2 in the Background so server does not go to sleep
ENTRYPOINT [ "/usr/sbin/httpd","-D","FOREGROUND" ]

