import os
import platform
import sys

import maya.cmds as cmds


class DataDirectoryManager:
    """
    Manages data and preference paths for the Under Construction tools.
    Uses main Maya directory as the root location.
    Compatible with Python 2.7 and 3.x and different operating systems.
    """

    def __init__( self ):
        self.data_dir_name = 'under_construction_data'  # Name of main data directory
        self.prefs_dir_name = 'prefs'  # Name of preferences subdirectory
        self.root_dir = self._get_maya_main_directory()

    def _get_maya_main_directory( self ):
        """
        Get Maya's main directory path based on OS.
        This will be used as the root for data directory.
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

        # Get the scripts directory in the main Maya path
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

    def create_data_directory( self ):
        """
        Create the main data directory in Maya's scripts directory if it doesn't exist.
        Returns the full path to the data directory.
        """
        if self.root_dir:
            data_path = os.path.join( self.root_dir, self.data_dir_name )
            return self.ensure_directory_exists( data_path )
        return None

    def create_prefs_directory( self ):
        """
        Create the preferences directory inside the data directory.
        Returns the full path to the preferences directory.
        """
        data_dir = self.create_data_directory()
        if data_dir:
            prefs_path = os.path.join( data_dir, self.prefs_dir_name )
            return self.ensure_directory_exists( prefs_path )
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

    def get_data_file_path( self, filename, subdirectory = None ):
        """
        Get the full path for a data file.
        
        Args:
            filename (str): Name of the data file
            subdirectory (str, optional): Subdirectory within the data directory
            
        Returns:
            str: Full path to the data file
        """
        data_dir = self.create_data_directory()
        if data_dir:
            if subdirectory:
                subdir_path = os.path.join( data_dir, subdirectory )
                if self.ensure_directory_exists( subdir_path ):
                    return os.path.join( subdir_path, filename )
                return None
            return os.path.join( data_dir, filename )
        return None

    @staticmethod
    def ensure_directory_exists( directory ):
        """
        Ensure that a directory exists, create it if it doesn't.
        
        Args:
            directory (str): Path to directory
            
        Returns:
            str or None: Directory path if successful, None if failed
        """
        if not os.path.exists( directory ):
            try:
                os.makedirs( directory )
                message = "Created directory: {0}".format( directory )
                sys.stdout.write( message + "\n" )
                sys.stdout.flush()
            except OSError as e:
                message = "Error creating directory {0}: {1}".format( directory, e )
                sys.stderr.write( message + "\n" )
                sys.stderr.flush()
                return None
        return directory


# Create singleton instance
data_dir_manager = DataDirectoryManager()
