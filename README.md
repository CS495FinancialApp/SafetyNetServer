# SafetyNetServer
Simple server to facilitate payment processing in our app. Currently builds as a jar file which can be run.

## Building and Running the server
1. Build the .jar with maven
```bash
$ mvn package
```

2. Run the jar. Output to target/ directory
```bash
$ java -jar payments-jar-with-dependencies.jar
```

3. Use localhost at port 4567 to test
```bash
$ curl localhost:4567/hello/user
```
