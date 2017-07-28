#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "mdlparse.h"
#include "mdlmesh_parser.h"
#include "mdlparse.bison.h"
#include "mdllex.flex.h"

char *curr_file;
int line_num;
struct object *root_objp;

struct object *mdl_parser(char *filename)
{
  FILE *mdlin;
  yyscan_t mdl_scanner;

  line_num = 0;
  root_objp = NULL;
  curr_file = filename;
  mdlin = NULL;

	fprintf(stdout,"mdlmesh_parser: opening file: %s\n",filename);
	if ((mdlin=fopen(filename,"r"))==NULL) {
	  fprintf(stderr,"mdlmesh_parser: error opening file: %s\n",filename);
	  fflush(stdout);
	  return(NULL);
	} 

	fprintf(stdout,"mdlmesh_parser: initializing mdl scanner\n");
  mdllex_init(&mdl_scanner);
	fprintf(stdout,"mdlmesh_parser: setting infile stream\n");
  mdlset_in(mdlin, mdl_scanner);

	fprintf(stdout,"mdlmesh_parser: parsing begins...\n");
	if (mdlparse(mdl_scanner)) {
	  fprintf(stderr,"mdlmesh_parser: error parsing file: %s\n",filename);
	  fclose(mdlin);
    mdllex_destroy(mdl_scanner);
	  return(NULL);
	} 
	fprintf(stdout,"mdlmesh_parser: parsing complete.\n");

	fclose(mdlin);
	fprintf(stdout,"mdlmesh_parser: destroying mdl scanner\n");
  mdllex_destroy(mdl_scanner);

	fprintf(stdout,"mdlmesh_parser: returning root object %s\n", root_objp->name);
	return(root_objp);
}
