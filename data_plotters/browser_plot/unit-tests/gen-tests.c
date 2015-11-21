#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>

#define TESTDIR "tests"

void genRandomMols(int, int, int, int);
void genDefaultMols(int, int);

char *badFormatMsg = "Usage: ./gen-tests [-d <directory name>] [-n <number of molecules>] [-t <number of iterations>] [-r <if random>] [-g <if add to git repo>]";

int main(int argc, char **argv) {
    int argNum;
    int numMols = 0;
    int numIter = 0;
    int isRand = 1; // no option for now
	char *dirName = NULL;

	int yMin = -500;
	int yMax = 2000;

    for (argNum = 1; argNum < argc; argNum++) {
		if (strcmp(argv[argNum], "-d") == 0 && argNum + 1 < argc) {
			dirName = argv[++argNum];
		} else if (strcmp(argv[argNum], "-n") == 0 && argNum + 1 < argc) {
            numMols = atoi(argv[++argNum]);
        } else if (strcmp(argv[argNum], "-t") == 0 && argNum + 1 < argc) {
            numIter = atoi(argv[++argNum]);
        } else {
            fprintf(stderr, "%s\n", badFormatMsg);
			fprintf(stderr, "Bad argument %s\n", argv[argNum]);
            exit(1);
        }
    }

    if (numMols <= 0 || numIter <= 0) {
        fprintf(stderr, "%s\n", badFormatMsg);
		fprintf(stderr, "Number of molecules and timepoints must be positive.\n");
        exit(1);
    }

	chdir(TESTDIR);
	struct stat st = {0};
	if (dirName == NULL) {
		fprintf(stderr, "%s\n", badFormatMsg);
		fprintf(stderr, "No directory provided.\n");
		exit(1);
	} else if (stat(dirName, &st) != -1) {
		fprintf(stderr, "%s\n", badFormatMsg);
		fprintf(stderr, "Directory \"%s\" in use.\n", dirName);
		exit(1);
	}

	fprintf(stderr, "Writing tests to directory \"%s\"\n", dirName);
    fprintf(stderr, "Number of molecules: %d\n", numMols);
    fprintf(stderr, "Number of iterations: %d\n", numIter);
    fprintf(stderr, "Random: %d\n", isRand);

	mkdir(dirName, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
	chdir(dirName);

	if (isRand) {
    		genRandomMols(numMols, numIter, yMin, yMax);
	} else {
		genDefaultMols(numMols, numIter);
	}

    return 0;
}

void genRandomMols(int numMols, int numIter, int yMin, int yMax) {
	srand(time(0));

	for (int i = 0; i < numMols; i++) {
		char fileName[25] = {0};
		sprintf(fileName, "mol%d.txt", i);

		FILE *dataFile = fopen(fileName, "w");
		if (dataFile == NULL) {
			fprintf(stderr, "Write to %s failed!\n", fileName);
			continue;
		}

		for (int t = 0; t <= numIter; t++) {
			int molCount = rand() % (yMax - yMin) + yMin;
			fprintf(dataFile, "%lf %d\n", 1.0 * t / numIter, molCount);
		}

		fclose(dataFile);
	}
}

void genDefaultMols(int numMols, int numIter) {
	fprintf(stderr, "Default tests unavailable.\n");
}
