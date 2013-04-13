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



# Figure out how many files are in the command line

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

num_files = len(sys.argv) - 1
num_cols = math.trunc(math.ceil(math.sqrt(num_files)))
num_rows = math.trunc(math.ceil(num_files*1.0/num_cols))

arg_num = 1

separate_windows = False

if separate_windows:
  print "Plotting " + str(num_files) + " files in separate windows"
else:
  print "Plotting " + str(num_files) + " files as " + str(num_rows) + "x" + str(num_cols)
  fig = plt.figure()
  fig.subplots_adjust(top=0.85)
  fig.subplots_adjust(bottom=0.15)
  fig.suptitle(title,fontsize=18.5)


for r in range(0,num_rows):
  for c in range(0,num_cols):
    if arg_num < len(sys.argv):
      data_fn = sys.argv[arg_num]
      print "Plotting " + data_fn
      
      title = data_fn

      #majorLocator   = MultipleLocator(20)
      #majorFormatter = FormatStrFormatter('%d')
      minorLocatorY   = MultipleLocator(5)
      minorLocatorX   = MultipleLocator(0.1)

      if separate_windows:
        fig = plt.figure()
        fig.subplots_adjust(top=0.85)
        fig.subplots_adjust(bottom=0.15)

        fig.suptitle(title,fontsize=18.5)
        ax = fig.add_subplot(1,1,1) # (r,c,n): r=num_rows, c=num_cols, n=this_plot_number
      else:
        ax = fig.add_subplot(num_rows,num_cols,arg_num,title=title) # (r,c,n): r=num_rows, c=num_cols, n=this_plot_number

      data = loadtxt(data_fn)
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
      arg_num = arg_num + 1
      print ("Bottom of loop")

plt.show()

