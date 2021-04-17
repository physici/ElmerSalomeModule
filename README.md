# ElmerSalome
Plugin for SALOME platform to access Elmer functionality 

## Requirements
* Elmer 9.x with ElmerGui installed
* Salome 9.x

## Installation with custom plugin-directory
* create a plugin directory in the root path of SALOME or somewhere convenient, if not already using one
* copy ElmerSalome-directory into the plugin directory
* copy the salome_plugins.py-file in the plugin directory or modify the existing file 
* register the directory via the SALOME_PLUGINS_PATH system variable

## Installation with standard Salome-directories:
* put everything int (e.g Salome 9.6 on win64):
\SALOME-9.6.0\W64\GUI\share\salome\plugins\gui\demo
* or use  ~/.config/salome/Plugins
  
## Usage:
* In the 'Mesh'-module of Salome, the plugin is accessable via the 'Tools'-menu.
* Here is a small demo: https://youtu.be/D2-dp4UxblY
* Avoid any blanks (" ")in file and directory names as likely to happen in Windows
