# file: runme.py

# This file illustrates the proxy class C++ interface generated
# by SWIG.

print ( "\n-------- Python -------- Python -------- Python -------- Python -------- Python -------- Python -------- Python --------\n" )

import libMCell

# ----- Object creation -----

print "Creating some objects:"
c = libMCell.Circle(10)
print "    Created circle", c
s = libMCell.Square(10)
print "    Created square", s

# ----- Access a static member -----

print "\nA total of", libMCell.cvar.Shape_nshapes, "shapes were created"

# ----- Member data access -----

# Set the location of the object

c.x = 20
c.y = 30

s.x = -10
s.y = 5

print "\nHere is their current position:"
print "    Circle = (%f, %f)" % (c.x, c.y)
print "    Square = (%f, %f)" % (s.x, s.y)

# ----- Call some methods -----

print "\nHere are some properties of the shapes:"
for o in [c, s]:
    print "   ", o
    print "        area      = ", o.area()
    print "        perimeter = ", o.perimeter()
# prevent o from holding a reference to the last object looked at
o = None

print "\nGuess I'll clean up now"

# Note: this invokes the virtual destructor
del c
del s

print libMCell.cvar.Shape_nshapes, "shapes remain"
print "Done with shapes!!"

root = libMCell.JSON_List_Element()

child = libMCell.JSON_Number_Element(111)
root.append_element ( child )

child = libMCell.JSON_Number_Element(2.222)
root.append_element ( child )

child = libMCell.JSON_Element()
root.append_element ( child )

rootsub1 = libMCell.JSON_List_Element()

grandchild = libMCell.JSON_Number_Element(0.1)
rootsub1.append_element ( grandchild );

grandchild = libMCell.JSON_Number_Element(0.2)
rootsub1.append_element ( grandchild )

grandchild = libMCell.JSON_Number_Element(0.3)
rootsub1.append_element ( grandchild )

root.append_element ( rootsub1 )

child = libMCell.JSON_Number_Element(99)
root.append_element ( child )

#print ( "List = " + libMCell.JSON_Element.chars_from_string(root.to_string()) )
root.print_self()




print ( "\n-------- Python -------- Python -------- Python -------- Python -------- Python -------- Python -------- Python --------\n" )

