FROM openjdk:8

MAINTAINER "Jeremy <jjmccormick@crimson.ua.edu>"

#COPY server* /usr/local/tomcat/conf/
#COPY tomcat-users* /usr/local/tomcat/conf/
#COPY ojdbc6* /usr/local/tomcat/lib/
#COPY safetynet* /usr/local/tomcat/webapps/
RUN apt -y update
RUN apt -y install maven
#RUN apt -y install openjdk-8-jre-headless
WORKDIR /code
ADD . /code

RUN ["mvn", "dependency:resolve"]
#RUN ["mvn", "verify"]
RUN ["mvn","package"]

EXPOSE 4567
CMD ["/usr/lib/jvm/java-8-openjdk-amd64/bin/java", "-jar", "target/payments-jar-with-dependencies.jar"]
