#ifndef LIBMCELL_H
#define LIBMCELL_H

#include "JSON.h"

typedef json_element data_model_element;

int mcell_set_iterations(int iters);
double mcell_set_time_step(double dt);


#endif

