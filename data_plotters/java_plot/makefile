PlotData.jar: PlotData.java makefile
	javac PlotData.java
	jar -cfe PlotData.jar PlotData PlotData.java *.class
	rm -f *.class

.PHONY: clean
clean:
	rm -f PlotData.jar


