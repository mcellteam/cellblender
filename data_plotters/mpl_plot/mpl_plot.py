#!/usr/bin/env python

''' Plot files '''

'''
This is the current plan for a simple plotting syntax:

 Basic Command line arguments:
  page : start a new page (new figure)
  plot : start a new plot on a page
  f=name : add file "name" to the current plot

 Additional Command line arguments that apply to all subsequent files until over-ridden:

  color=clr : set color
  xaxis=label : set label for x axis
  yaxis=label : set label for y axis
'''

from numpy import *
from scipy import *
from pylab import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


if (len(sys.argv)<2):
  print('')
  print('\nUsage: %s filename'%(sys.argv[0]))
  print('          Plots this file using rc parameters.')
  print('')
  exit(1)





#################
# set rc params #
#################

mpl.rcdefaults()

# mpl.rcParams['backend'] = MacOSX

mpl.rcParams['figure.figsize'] = (11.0, 8.5)
mpl.rcParams['figure.dpi'] = 80
mpl.rcParams['figure.facecolor'] = 'white'
mpl.rcParams['figure.subplot.wspace'] = 0.4
mpl.rcParams['figure.subplot.hspace'] = 0.45

mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.style'] = 'normal'
mpl.rcParams['font.variant'] = 'normal'
mpl.rcParams['font.weight'] = 'medium'
mpl.rcParams['font.stretch'] = 'normal'
mpl.rcParams['font.size'] = 18.0
mpl.rcParams['font.serif'] = 'Palatino'
mpl.rcParams['font.sans-serif'] = 'Arial'
mpl.rcParams['font.cursive'] = ['Apple Chancery', 'Textile', 'Zapf Chancery']
mpl.rcParams['font.fantasy'] = ['Comic Sans MS', 'Chicago', 'Charcoal', 'Impact', 'Western']
mpl.rcParams['font.monospace'] = ['Andale Mono', 'Bitstream Vera Sans Mono', 'Nimbus Mono L', 'Courier New', 'Courier']

mpl.rcParams['mathtext.cal'] = 'cursive'
mpl.rcParams['mathtext.rm'] = 'sans'
mpl.rcParams['mathtext.tt'] = 'monospace'
mpl.rcParams['mathtext.it'] = 'sans:italic'
mpl.rcParams['mathtext.bf'] = 'sans:bold'
mpl.rcParams['mathtext.sf'] = 'sans'
mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.default'] = 'rm'

mpl.rcParams['axes.titlesize'] = 'large'
mpl.rcParams['axes.labelsize'] = 'medium'
mpl.rcParams['axes.unicode_minus'] = True
#mpl.rcParams['axes.formatter.use_mathtext'] = False

mpl.rcParams['xtick.major.size'] = 5
mpl.rcParams['xtick.minor.size'] = 2.5
mpl.rcParams['xtick.labelsize'] = 'medium'
mpl.rcParams['ytick.major.size'] = 5
mpl.rcParams['ytick.minor.size'] = 2.5
mpl.rcParams['ytick.labelsize'] = 'medium'

#################
#################

title = ''
xlabel = None
ylabel = None

# Get a list of just the parameters (excluding the program name itself)
params = sys.argv[1:]

# Separate the commands into a list of lists (one list per page)

def subdivide ( l, sep ):
  nl = []
  c = []
  for s in l:
    if s==sep:
      if len(c) > 0:
        nl = nl + [c]
        c = []
    else:
      c = c + [s]
  if len(c) > 0:
    nl = nl + [c]
  return nl

pages = subdivide ( params, "page" )

plot_cmds = []
for page in pages:
  pc = subdivide ( page, "plot" )
  if len(pc) > 0:
    plot_cmds = plot_cmds + [pc]


print plot_cmds


# Draw each plot

for page in plot_cmds:
  print "Plotting " + str(page)
  
  num_plots = len(page)

  print "This figure has " + str(num_plots) + " plots"

  num_cols = math.trunc(math.ceil(math.sqrt(num_plots)))
  num_rows = math.trunc(math.ceil(num_plots*1.0/num_cols))
  
  print "This figure will be " + str(num_rows) + "x" + str(num_cols)

  fig = plt.figure()
  fig.subplots_adjust(top=0.85)
  fig.subplots_adjust(bottom=0.15)
  fig.suptitle("TITLE GOES HERE",fontsize=18.5)

  row = 1
  col = 1
  plot_num = 1
  
  for plot in page:
    print "  Plotting " + str(plot)
    
    #majorLocator   = MultipleLocator(20)
    #majorFormatter = FormatStrFormatter('%d')
    minorLocatorY   = MultipleLocator(5)
    minorLocatorX   = MultipleLocator(0.1)

    ax = fig.add_subplot(num_rows,num_cols,plot_num) # (r,c,n): r=num_rows, c=num_cols, n=this_plot_number

    for cmd in plot:
      if cmd[0:2] == "c=":
        print "Color command: " + cmd
      elif cmd[0:2] == "f=":
        print "File command: " + cmd
        fn = cmd[2:]
        print "  File name = " + fn
        data = loadtxt(fn)

        x = data[:,0]
        y = data[:,1]
        ax.plot(x,y)
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        #ax.set_xscale('log')
        #ax.axis([0.001,1.0,0.0,70.0])
        if xlabel != None:
          ax.set_xlabel(xlabel)
        if ylabel != None:
          ax.set_ylabel(ylabel)
        #ax.yaxis.set_minor_locator(minorLocatorY)
    plot_num = plot_num + 1

plt.show()


