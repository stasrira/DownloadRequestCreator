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
        self.source_locations = None
        # self.data_loc = None
        # self.cnf_data_source = None
        DataRetrieval.__init__(self, inquiry)

    def init_specific_settings(self):
        source_locations = self.conf_process_entity.get_value('Datasource/locations')
        self.source_locations = source_locations
        # default search_by parameters from source config file
        search_by_default = self.conf_process_entity.get_value('Datasource/search_method_default/search_by')
        search_deep_level_defalult = self.conf_process_entity.get_value(
            'Datasource/search_method_default/search_deep_level_max')
        exclude_dirs_defalult = self.conf_process_entity.get_value('Datasource/search_method_default/exclude_folders')
        ext_match_defalult = self.conf_process_entity.get_value('Datasource/search_method_default/file_ext')
        soft_comparisions_default = self.conf_process_entity.get_value(
            'Datasource/search_method_default/soft_comparision')
        aliquot_match_default = self.conf_process_entity.get_value('Datasource/search_method_default/aliquot_match')

        for loc_item in source_locations:
            # check if a current source has specific search_by parameters, otherwise use default ones
            src_sm = loc_item['search_method'] if 'search_method' in loc_item.keys() else None
            search_by = src_sm['search_by'] \
                if src_sm and 'search_by' in src_sm.keys() else search_by_default
            search_deep_level = src_sm['search_deep_level_max'] \
                if src_sm and 'search_deep_level_max' in src_sm.keys() else search_deep_level_defalult
            exclude_dirs = src_sm['exclude_folders'] \
                if src_sm and 'exclude_folders' in src_sm.keys() else exclude_dirs_defalult
            ext_match = src_sm['file_ext'] \
                if src_sm and 'file_ext' in src_sm.keys() else ext_match_defalult
            soft_comparisions = src_sm['soft_comparision'] \
                if src_sm and 'soft_comparision' in src_sm.keys() else soft_comparisions_default
            aliquot_match = src_sm['aliquot_match'] \
                if src_sm and 'aliquot_match' in src_sm.keys() else aliquot_match_default


            # start processing a source
            items = []
            if search_by == 'folder_name':
                items = self.get_data_by_folder_name(loc_item['path'], search_deep_level, exclude_dirs)
            elif search_by == 'file_name':
                items = self.get_data_by_file_name(loc_item['path'], search_deep_level, exclude_dirs, ext_match)
            else:
                # TODO: report an error that unexpected search_by parameter was provided
                pass

            # set default value for target_subfolder
            target_subfolder = ''
            # if target_subfolder value is provided in config, get it from there
            if 'target_subfolder' in loc_item.keys():
                target_subfolder = loc_item['target_subfolder'] if loc_item['target_subfolder'] else ''

            for item in items:
                item_details = {'path': item,
                                'name': os.path.basename(item),
                                'target_subfolder': target_subfolder,
                                'soft_comparisions': soft_comparisions,
                                'aliquot_match': aliquot_match}
                self.source_content_arr.append(item_details)

        pass
