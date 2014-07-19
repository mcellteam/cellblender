//#include <windows.h>
#include <GL/gl.h>
#include <GL/glu.h>
#include <GL/glut.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int w, h;
//const
int font; // = (int)GLUT_BITMAP_9_BY_15;

char s[30];

double t;

FILE *subprocess_pipe;

typedef struct a_line_struct {
  char *line;
  struct a_line_struct* next;
} a_line;

a_line *line_list = NULL;
a_line *last_line = NULL;

static void resize(int width, int height)
{
  const float ar = (float) width / (float) height;
  w = width;
  h = height;
  glViewport(0, 0, width, height);
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  glFrustum(-ar, ar, -1.0, 1.0, 2.0, 100.0);
  glMatrixMode(GL_MODELVIEW);
  glLoadIdentity() ;
}

void setOrthographicProjection() {
  glMatrixMode(GL_PROJECTION);
  glPushMatrix();
  glLoadIdentity();
  gluOrtho2D(0, w, 0, h);
  glScalef(1, -1, 1);
  glTranslatef(0, -h, 0);
  glMatrixMode(GL_MODELVIEW);
}

void resetPerspectiveProjection() {
  glMatrixMode(GL_PROJECTION);
  glPopMatrix();
  glMatrixMode(GL_MODELVIEW);
}

void renderBitmapString(float x, float y, void *font,const char *string){
  const char *c;
  glRasterPos2f(x, y);
  for (c=string; *c != '\0'; c++) {
      glutBitmapCharacter(font, *c);
  }
}

static void display(void){
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  glColor3d(0.0, 1.0, 0.0);
  setOrthographicProjection();
  glPushMatrix();
  glLoadIdentity();
  renderBitmapString(200,200,(void *)font,"Font Rendering - Programming Techniques");
  renderBitmapString(300,220, (void*)font, s);
  renderBitmapString(300,240,(void *)font,"Esc - Quit");
  glPopMatrix();
  resetPerspectiveProjection();
  glutSwapBuffers();
}

void update(int value){
  char buffer[1010];
  a_line *new_line;
  if (subprocess_pipe != NULL) {
    char *buf = fgets ( buffer, 1000, subprocess_pipe );
    if (buf != NULL) {
      printf ( "Input: %s", buf );
      new_line = (a_line *) malloc ( sizeof(a_line) );
      new_line->next = NULL;
      new_line->line = (char *) malloc ( 1+strlen(buf) );
      strcpy ( new_line->line, buf );
      if (line_list == NULL) {
        line_list = new_line;
        last_line = new_line;
      } else {
        last_line->next = new_line;
        last_line = last_line->next;
      }
      
    }
  }
  t = glutGet(GLUT_ELAPSED_TIME) / 10.0;
  int time = (int)t;
  sprintf(s, "TIME : %2d Sec", time);
  glutTimerFunc(10, update, 0);
  glutPostRedisplay();
}

int main(int argc, char *argv[])
{
  printf ( "Simulation Control Program ...\n" );
  int command_length = 1; // Allow for the null terminator
  for (int i=1; i<argc; i++) {
    printf ( "Arg %d = %s\n", i, argv[i] );
    command_length += 1 + strlen(argv[i]); // Allow for spaces between arguments
  }
  char *cmd;
  cmd = (char *) malloc ( command_length + 1 );  // Allow for mistakes!!
  cmd[0] = '\0';
  for (int i=1; i<argc; i++) {
    strcat ( cmd, argv[i] );
    if (i < (argc-1) ) {
      strcat ( cmd, " " );
    }
  }
  printf ( "Command: %s\n", cmd );
  
  subprocess_pipe = popen ( cmd, "r" );
  
  free(cmd);
  
  
  font=(int)GLUT_BITMAP_9_BY_15;
  glutInit(&argc, argv);
  glutInitWindowSize(640,480);
  glutInitWindowPosition(10,10);
  glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH);
  glutCreateWindow("Font Rendering Using Bitmap Font - Programming Techniques0");
  glutReshapeFunc(resize);
  glutDisplayFunc(display);
  glutTimerFunc(25, update, 0);
  glutMainLoop();
  return EXIT_SUCCESS;
}
