from data_retrieval import DataRetrieval
from pathlib import Path
import os
import tarfile
import hashlib
import subprocess
import shlex
import traceback
from utils import global_const as gc


class DataSource(DataRetrieval):

    def __init__(self, inquiry):
        self.source_content_arr = []
        # self.data_loc = None
        # self.cnf_data_source = None
        DataRetrieval.__init__(self, inquiry)

    def init_specific_settings(self):
        source_locations = self.conf_process_entity.get_value('Datasource/locations')
        search_by = self.conf_process_entity.get_value('Datasource/search_method/search_by')
        search_deep_level = self.conf_process_entity.get_value('Datasource/search_method/search_deep_level_max')
        exclude_dirs = self.conf_process_entity.get_value('Datasource/search_method/exclude_folders')
        ext_match = self.conf_process_entity.get_value('Datasource/search_method/file_ext')

        for loc_item in source_locations:
            if search_by == 'folder_name':
                items = self.get_data_by_folder_name(loc_item, search_deep_level, exclude_dirs)
            elif search_by == 'file_name':
                items = self.get_data_by_file_name(loc_item, search_deep_level, exclude_dirs, ext_match)

            for item in items:
                item_details = {'path': item, 'name': os.path.basename(item)}
                self.source_content_arr.append(item_details)

        pass

    """
    def get_data_by_file_name(self, data_loc, search_deep_level, exclude_dirs, ext_match):
        # it retrieves all files potentially qualifying to be a source and searches through each to match
        # the sub-aliquot name in the name of the file
        files = self.get_file_system_items(data_loc, search_deep_level, exclude_dirs, 'file', ext_match)
        return files
    """