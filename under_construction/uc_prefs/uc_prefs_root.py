import os
import platform
import sys

import maya.cmds as cmds


class PrefsDirectoryManager:
    """
    Manages preference paths and directories for the Under Construction tools.
    Uses main Maya directory as the root location for preferences.
    Compatible with Python 2.7 and 3.x and different operating systems.
    """

    def __init__( self ):
        self.prefs_dir_name = 'under_construction_prefs'  # Name of preferences directory
        self.root_dir = self._get_maya_main_directory()

    def _get_maya_main_directory( self ):
        """
        Get Maya's main directory path based on OS.
        This will be used as the root for preferences.
        Returns the main scripts directory path.
        """
        system = platform.system().lower()

        if system == 'windows':
            maya_app_dir = os.environ.get( 'MAYA_APP_DIR' )
            if maya_app_dir:
                base_path = maya_app_dir
            else:
                base_path = os.path.join( os.environ.get( 'USERPROFILE', '' ), 'Documents', 'maya' )

        elif system == 'darwin':  # macOS
            base_path = os.path.expanduser( '~/Library/Preferences/Autodesk/maya' )

        elif system == 'linux':
            base_path = os.path.expanduser( '~/maya' )

        else:
            message = "Unsupported operating system: {0}".format( system )
            sys.stderr.write( message + "\n" )
            sys.stderr.flush()
            return None

        # Get the scripts directory in the main Maya path (not version specific)
        scripts_path = os.path.join( base_path, 'scripts' )

        # Ensure scripts directory exists
        if not os.path.exists( scripts_path ):
            try:
                os.makedirs( scripts_path )
                message = "Created Maya scripts directory: {0}".format( scripts_path )
                sys.stdout.write( message + "\n" )
                sys.stdout.flush()
            except OSError as e:
                message = "Error creating Maya scripts directory: {0}".format( e )
                sys.stderr.write( message + "\n" )
                sys.stderr.flush()
                return None

        return scripts_path

    def create_prefs_directory( self ):
        """
        Create the preferences directory in Maya's main scripts directory if it doesn't exist.
        Returns the full path to the preferences directory.
        """
        if self.root_dir:
            prefs_path = os.path.join( self.root_dir, self.prefs_dir_name )

            if not os.path.exists( prefs_path ):
                try:
                    os.makedirs( prefs_path )
                    message = "Created preferences directory at: {0}".format( prefs_path )
                    sys.stdout.write( message + "\n" )
                    sys.stdout.flush()
                except OSError as e:
                    message = "Error creating preferences directory: {0}".format( e )
                    sys.stderr.write( message + "\n" )
                    sys.stderr.flush()
                    return None

            return prefs_path
        return None

    def get_pref_file_path( self, filename ):
        """
        Get the full path for a preferences file.
        
        Args:
            filename (str): Name of the preferences file
            
        Returns:
            str: Full path to the preferences file
        """
        prefs_dir = self.create_prefs_directory()
        if prefs_dir:
            return os.path.join( prefs_dir, filename )
        return None

    @staticmethod
    def ensure_directory_exists( directory ):
        """
        Ensure that a directory exists, create it if it doesn't.
        
        Args:
            directory (str): Path to directory
            
        Returns:
            bool: True if directory exists or was created successfully
        """
        if not os.path.exists( directory ):
            try:
                os.makedirs( directory )
                return True
            except OSError as e:
                message = "Error creating directory {0}: {1}".format( directory, e )
                sys.stderr.write( message + "\n" )
                sys.stderr.flush()
                return False
        return True


# Create singleton instance
prefs_dir_manager = PrefsDirectoryManager()
