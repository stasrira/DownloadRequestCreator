from pathlib import Path


def get_project_root():
    # Returns project root folder.
    return Path(__file__).parent.parent


def file_exists(fn):
    try:
        with open(fn, "r"):
            return 1
    except IOError:
        return 0

def is_excel(file_path):
    ext = Path(file_path).suffix
    if 'xls' in ext:
        return True
    else:
        return False

def identify_delimeter_by_file_extension(file_path):
    ext = Path(file_path).suffix
    out_value = None

    if ext == 'csv':
        out_value = ','
    elif ext == 'tab':
        out_value = '   '
    elif 'xls' in ext:
        out_value = None
    else:
        out_value = ','

    return  out_value

def start_external_process_async (exec_path):
    from subprocess import Popen
    process = Popen(exec_path, shell=True)
    return process

def check_external_process(process):
    pr_out = process.poll()
    if pr_out is None:
        status = 'running'
        message = ''
    else:
        status = 'stopped'
        message = pr_out
    out = {'status': status, 'message': message}
    return out
