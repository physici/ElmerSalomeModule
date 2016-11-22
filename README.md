# ElmerSalome
Plugin for SALOME platform to access Elmer functionality 

##Requirements
* Elmer 8.2 with ElmerGui installed
* Salome 7.8

##Installation:
* create a plugin directory in the root path of SALOME or somewhere convenient, if not already using one
* copy ElmerSalome-directory into the plugin directory
* copy the salome_plugins.py-file in the plugin directory or modify the existing file 
* register the directory via the SALOME_PLUGIN_PATH system variable
  
##ToDo:
*  check whether registration via system variables can be bypassed by using the env.bat batch file that starts SALOME
