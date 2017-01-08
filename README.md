# ElmerSalome
Plugin for SALOME platform to access Elmer functionality 

##Requirements
* Elmer 8.2 with ElmerGui installed
* Salome 7.8

##Installation:
* create a 'plugins'-directory in the root path of SALOME or somewhere convenient
  * or use the GUI-'plugins'-folder -> $GUI_ROOT_DIR/share/salome/plugins/
* copy ElmerSalome-directory into the directory
* copy the salome_plugins.py-file in the in the same 'plugins'-directory, but outside the ElmerSalome-folder
  * alternatively, modify the existing file if you use other modules
* register the directory via the SALOME_PLUGIN_PATH system variable
