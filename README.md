How to make my own nodes
########################

### Overview
To create your own node you have to follow 2 simple steps:

1. Copy the file of an existing node and change to you needs.
2. Register the node in the _nodes/mn_node_list.py_ file.

All node files are in the subdirectories of the Folder named _nodes_.

### the class
The Code itself is very self-explanatory. 
You have to change:
* the class Name too something that fits the purpose of your node
* the _bl_idname_ variable: you Need this later to Register the node
* the _bl_label_ variable: the user will see this in the add menu

### _init_
The _init_ function is for defining the sockets. In other nodes you see exactly how this has to look like. 
There are a few different types of sockets (the list will probably get longer over time):
* StringSocket -> Text
* ObjectSocket -> Object names
* IntegerSocket -> Whole Numbers
* FloatSocket -> All Numbers
* VectorSocket -> Vector with an x, y and z component
* GenericSocket -> allows all types

### execute
Here you add the code that executes when the node is used. 
It gets a variable named _input_ as Parameter. This is a dictionary which contains your input socket names as keys. 
This function always returns a dictionary that should be called _output_. The keys of this dictionary are equivalent to the output socket names you defined in the _init_ function.

### Registration
Open the _mn_node_list.py_ file and write your _bl_idname_ in the corresponding category or define you own category. This shouldn't be more than a one-line-change.

### summary
The best way to implement new nodes is to look at the existing ones :D

