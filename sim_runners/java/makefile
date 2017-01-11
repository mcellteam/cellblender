SimControl.jar: SimControl.java
	-rm -f *.class
	-javac SimControl.java
	-touch -t 201407160000 *.class
	-zip $(ZIPOPTS) SimControl.jar META-INF/MANIFEST.MF SimControl.java *.class
	-rm -f *.class

.PHONY: clean
clean:
	-rm -f SimControl.jar

