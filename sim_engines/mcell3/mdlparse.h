#ifndef MDLPARSE_H
#define MDLPARSE_H

#include <sys/types.h>

struct element_list {
  struct element_list *next;
  unsigned int begin;
  unsigned int end;
};

int mdlparse(void);
int mdlerror(char *str);

#endif
