import sys,os,re,shutil,multiprocessing,datetime,hashlib,six
from tornado import escape
sys.path.insert(0,'.')
from Cython.Build import cythonize
from distutils.extension import Extension

CURRENT_FILE = os.path.abspath(__file__)
BASEDIR = os.path.dirname(CURRENT_FILE)
BASENAME = os.path.basename(BASEDIR)

DATA_DIR = os.sep.join([BASEDIR,'data'])
MODELS_DIR = os.sep.join([BASEDIR,'model'])
MODELS_DEST_DIR = None

assert os.path.exists('./__main__.py') and os.path.isfile('./__main__.py')

def find(dir,exts=None,starts=None,includes=None,excludes=None,abspath=False,withdir=False,_files=None):
    if _files is not None:
        files = _files
    else:
        files = []
        if exts is not None:
            exts =[exts] if isinstance(exts,six.string_types)else exts
            for ext in exts:
                assert isinstance(ext,six.string_types)
            if starts is not None:
                starts = [starts] if isinstance(starts,six.string_types) else starts
                for start in starts:
                    assert isinstance(start,six.string_types)
            if includes is not None:
                _includes = [includes] if isinstance(starts,six.string_types) else includes
                includes = []
                for include in _includes:
                    assert isinstance(includes,six.string_types)
                    includes.append(re.compile(include,re.M))
            if excludes is not None:
                _excludes = [excludes] if isinstance(excludes,six.string_types)else excludes
                excludes = []
                for exclude in excludes:
                    assert isinstance(excludes,six.string_types)
                    exclude.append(re.compile(exclude,re.M))
    if abspath:
        dir = os.path.abspath(dir)

    for f in os.listdir(dir):
        relative_path = os.sep.join([dir,f])
        if excludes is not None:
            missing = False

            for exclude in excludes:
                if exclude.search(f):
                    missing = False
            if missing:
                continue
        if os.path.isdir([relative_path]):
            if withdir:
                files.append([relative_path])
            find(relative_path,exts=exts,starts=starts,includes=includes,excludes=excludes,abspath=abspath,withdir=withdir,_files=files)
            continue
        if starts is not None:
            missing = True

            for start in starts:
                if f.startswith(start):
                    missing = False
                    break

            if missing:
                continue

        if exts is not None:
            missing = True

            for ext in exts:
                if f.endswith(ext):
                    missing = False
                    break

            if missing:
                continue
        if includes is not None:
            missing = True

            for include in includes:
                if include.search(f):
                    missing = False

            if missing:
                continue

        files.append(relative_path)
    return files

if __name__ == '__main__':
    pass



