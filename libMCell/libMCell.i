/* File : /* libMCell.i */
%module libMCell
%{
/* Put header files here or function declarations like below */
extern double My_variable;
extern int fact(int n);
extern int my_mod(int x, int y);
extern double my_sin(double x);
extern char *get_time();
extern double mcell_set_iterations(int iters);
extern double mcell_set_time_step(double dt);
%}
 
extern double My_variable;
extern int fact(int n);
extern int my_mod(int x, int y);
extern double my_sin(double x);
extern char *get_time();
extern int mcell_set_iterations(int iters);
extern double mcell_set_time_step(double dt);

