/* File : /* libMCell.i */
%module libMCell
%{
/* Put header files here or function declarations like below */
extern double mcell_set_iterations(int iters);
extern double mcell_set_time_step(double dt);
%}
 
extern int mcell_set_iterations(int iters);
extern double mcell_set_time_step(double dt);

