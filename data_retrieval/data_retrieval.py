from pathlib import Path
import os
import glob
# from utils import common as cm
from lxml import html
import requests
import traceback


class DataRetrieval:

    def __init__(self, inquiry):
        # self.path_sub_aliqs = {}
        self.inq_obj = inquiry  # reference to the current inquiry object
        self.error = self.inq_obj.error
        self.logger = self.inq_obj.logger
        self.conf_process_entity = inquiry.conf_process_entity
        # self.data_loc = None
        self.init_specific_settings()

    def init_specific_settings(self):
        # should be overwritten in classed that inherit this one
        pass

    def get_data_by_folder_name(self, data_loc, search_deep_level, exclude_dirs):
        # retrieves data for each sub-aliquot listed in the inquiry file based on presence
        # of aliquot id key in the name of the folder
        dirs = self.find_locations_by_folder(data_loc, search_deep_level, exclude_dirs)
        return dirs

    def get_data_by_file_name(self, data_loc, search_deep_level, exclude_dirs, ext_match):
        # it retrieves all files potentially qualifying to be a source and searches through each to match
        # the sub-aliquot name in the name of the file
        files = self.get_file_system_items(data_loc, search_deep_level, exclude_dirs, 'file', ext_match)
        return files

    def get_data_for_aliquot(self, sa, directory):
        # this retrieves data related to the purpose of the current class - raw data or attachment info.
        # should be overwritten in classes that inherit this one
        pass

    def find_locations_by_folder(self, loc_path, search_deep_level, exclude_dirs):
        # get directories of the top level and filter out any directories to be excluded
        dirs_top = self.get_top_level_dirs(loc_path, exclude_dirs)
        dirs = []  # holds final list of directories
        dirs.extend(dirs_top)

        # if deeper than top level search is required, proceed here
        if search_deep_level > 0:
            for d in dirs_top:
                dirs.extend(self.get_file_system_items(d, search_deep_level-1, exclude_dirs, 'dir'))

        return dirs

    def get_top_level_dirs(self, path, exclude_dirs=None):
        if exclude_dirs is None:
            exclude_dirs = []
        if Path(path).exists():
            itr = os.walk(Path(path))
            _, dirs, _ = next(itr)
            if not dirs:
                dirs = []
            dirs = list(set(dirs) - set(exclude_dirs))  # remove folders to be excluded from the list of directories
            dirs_path = [str(Path(path + '/' + dr)) for dr in dirs]
        else:
            self.logger.warning('Expected to exist directory "{}" is not present - reported from "DataRetrieval" '
                                'class, "get_top_level_dirs" function'.format (path))
            dirs_path = []
        return dirs_path

    @staticmethod
    def get_file_system_items(dir_cur, search_deep_level, exclude_dirs=None, item_type='dir', ext_match=None):
        # base_loc = self.data_loc / dir_cur
        if ext_match is None:
            ext_match = []
        if exclude_dirs is None:
            exclude_dirs = []
        deep_cnt = 0
        cur_lev = ''
        items = []
        while deep_cnt <= search_deep_level:
            cur_lev = cur_lev + '/*'
            items_cur = glob.glob(str(Path(str(dir_cur) + cur_lev)))

            if item_type == 'dir':
                items_clean = [fn for fn in items_cur if
                               Path.is_dir(Path(fn)) and not os.path.basename(fn) in exclude_dirs]
            elif item_type == 'file':
                items_clean = []
                for ext in ext_match:
                    items_found = [fn for fn in items_cur if not Path.is_dir(Path(fn))
                                   and (len(ext_match) == 0 or fn.endswith(ext))]
                                    # and (len(ext_match) == 0 or os.path.splitext(fn)[1] in ext_match)]
                    if items_found:
                        items_clean.extend(items_found)
            else:
                items_clean = None
            items.extend(items_clean)
            deep_cnt += 1
        return items

    def get_web_data(self, url, str_xpath, exclude_entries=None, ext_match=None):
        items = []
        if not exclude_entries:
            exclude_entries = []
        try:
            page = requests.get(url)
        except Exception as ex:
            # report error during opening a web location
            _str = 'Unexpected Error "{}" occurred during opening web location at: "{}"\n{} ' \
                .format(ex, url, traceback.format_exc())
            self.logger.critical(_str)
            self.error.add_error(_str)
            return items

        content = html.fromstring(page.content)

        try:
            entries = content.xpath(str_xpath)
        except Exception as ex:
            # report error at attempt of applying xpath
            _str = 'Unexpected Error "{}" occurred during applying xpath value "{}" against content of URL "{}"\n{} ' \
                .format(ex, str_xpath, url, traceback.format_exc())
            self.logger.critical(_str)
            self.error.add_error(_str)
            return items

        for entry in entries:
            if not entry in exclude_entries:
                if (ext_match and Path(entry).endswith(ext_match)) or (not ext_match):
                    items.append(entry)
                    # print (entry)
        return items

