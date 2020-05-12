#ifndef MDLPARSE_H
#define MDLPARSE_H

#include <sys/types.h>

#define YY_DECL int mdllex \
  (YYSTYPE * yylval_param , yyscan_t yyscanner)

struct element_list {
  struct element_list *next;
  unsigned int begin;
  unsigned int end;
};


#endif
