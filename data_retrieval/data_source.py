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

        ds_count = 0
        for loc_item in source_locations:
            ds_count +=1
            self.logger.info('Start processing data source #{}, path: "{}"'.format(ds_count, loc_item['path']))

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

            web_location = loc_item['web_location'] if 'web_location' in loc_item.keys() else None
            xpath = loc_item['xpath'] if 'xpath' in loc_item.keys() else '/' # default option - start with root element
            ds_path = loc_item['path']
            # make sure that web urls ends with "/", if not add the charcter
            if web_location and ds_path[-1:] != '/':
                ds_path += '/'

            # set default value for target_subfolder
            target_subfolder = ''
            # if target_subfolder value is provided in config, get it from there
            if 'target_subfolder' in loc_item.keys():
                target_subfolder = loc_item['target_subfolder'] if loc_item['target_subfolder'] else ''

            self.logger.info('Current data source config details: '
                             'web_location: "{}", '
                             'search_by: "{}", '
                             'search_deep_level_max: "{}", '
                             'exclude_folders: "{}", '
                             'file_ext: "{}", '
                             'soft_comparision (loose comparision): "{}", '
                             'aliquot_match: "{}", '
                             'target_subfolder: "{}"'
                             'xpath: "{}"'                             
                             ''.format((web_location if web_location else False),
                                       search_by,
                                       (search_deep_level if search_deep_level else 0 if web_location else 'No limit'),
                                       exclude_dirs,
                                       (ext_match if ext_match else ''),
                                       (soft_comparisions if soft_comparisions else ''),
                                       aliquot_match,
                                       target_subfolder,
                                       xpath))

            # start processing a source
            items = []
            if search_by == 'folder_name':
                if not web_location:
                    items = self.get_data_by_folder_name(ds_path, search_deep_level, exclude_dirs)
                else:
                    items = self.get_web_data(ds_path, xpath, exclude_dirs)
            elif search_by == 'file_name':
                if not web_location:
                    items = self.get_data_by_file_name(ds_path, search_deep_level, exclude_dirs, ext_match)
                else:
                    items = self.get_web_data(ds_path, xpath, exclude_dirs, ext_match)
            else:
                _str = 'Unexpected "search_by" configuration parameter "{}" was provided. ' \
                       'Skipping processing of the current source "{}"'.format(search_by, ds_path)
                self.logger.critical(_str)
                self.error.add_error(_str)
                continue

            if items and len(items) > 0:
                for item in items:
                    item_details = {'path': item if not web_location else ds_path + item,
                                    'name': os.path.basename(item) if not web_location else item,
                                    'target_subfolder': target_subfolder,
                                    'soft_comparisions': soft_comparisions,
                                    'aliquot_match': aliquot_match}
                    self.source_content_arr.append(item_details)
            else:
                self.logger.warning('No available files/folders were found in the current source. '
                                    'Configuration settings of the source might need to be reviewed.')

            self.logger.info('Processing data source #{} was completed. '
                             'Total number of files/folder available in the source = {}.'
                             .format(ds_count, len(items) if items else 0))
