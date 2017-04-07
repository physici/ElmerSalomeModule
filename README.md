# ElmerSalome
Plugin for SALOME platform to access Elmer functionality 

##Requirements
* Elmer 8.2 with ElmerGui installed
* Salome 7.8 or 8.2

##Installation with custom plugin-directory
* create a plugin directory in the root path of SALOME or somewhere convenient, if not already using one
* copy ElmerSalome-directory into the plugin directory
* copy the salome_plugins.py-file in the plugin directory or modify the existing file 
* register the directory via the SALOME_PLUGINS_PATH system variable

##Installation with standard Salome-directories:
* put everything int (e.g Salome 7.8 on win64):
\SALOME-7.8.0-WIN64\MODULES\GUI\RELEASE\GUI_INSTALL\share\salome\plugins\gui\
* or use  ~/.config/salome/Plugins
  
##Usage:
*  In the 'Mesh'-module of Salome, the plugin is accessable via the 'Tools'-menu.
