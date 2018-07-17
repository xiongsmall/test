# -*-coding:utf-8-*-

import sys,os,re,six,shutil,multiprocessing,datetime,time,hashlib
from tornado import escape
import numpy, pandas

sys.path.insert(0, '.')
# import main_server
# assert not main_server.DEBUG, 'main_server 还是调试模式'

from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

CURRENT_FILE = os.path.abspath(__file__)
BASEDIR = os.path.dirname(CURRENT_FILE)
BASENAME  = os.path.basename(BASEDIR)
#BASEBINDIR = os.sep.join([os.path.dirname(BASEDIR),  BASENAME + '_bin'])

DATA_DIR = os.sep.join([BASEDIR,  'data'])
MODELS_DIR = os.sep.join([BASEDIR,  'models'])
MODELS_DEST_DIR = None

# assert os.path.exists('./__main__.py') and os.path.isfile('./__main__.py')
def find(dir, exts=None, starts=None, includes=None, excludes=None, abspath=False, withdir=False, _files=None):
    if _files is not None: # only first call
        files = _files
    else:
        files = []
        if exts is not None: #
            exts = [exts] if isinstance(exts, six.string_types) else exts
            for ext in exts:
                assert isinstance(ext, six.string_types)
        if starts is not None:
            starts = [starts] if isinstance(starts, six.string_types) else starts
            for start in starts:
                assert isinstance(start, six.string_types)
        if includes is not None:
            _includes = [includes] if isinstance(starts, six.string_types) else includes
            includes = []
            for include in _includes:
                assert isinstance(include, six.string_types)
                includes.append(re.compile(include, re.M))
        if excludes is not None:
            _excludes = [excludes] if isinstance(excludes, six.string_types) else excludes
            excludes = []
            for exclude in _excludes:
                assert isinstance(exclude, six.string_types)
                excludes.append(re.compile(exclude, re.M))

    if abspath:
        dir = os.path.abspath(dir)

    for f in os.listdir(dir):
        relative_path = os.sep.join([dir, f])

        if excludes is not None:
            missing = False

            for exclude in excludes:
                if exclude.search(f):
                    missing = True

            if missing:
                continue

        if os.path.isdir(relative_path):
            if withdir:
                files.append(relative_path)
            find(relative_path, exts=exts, starts=starts, includes=includes, excludes=excludes, abspath=abspath, withdir=withdir, _files=files)
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
    if len(sys.argv) > 1:
        mfile = sys.argv[1]
        try:
            cythonized_extension_modules = cythonize([mfile]) #, build_dir = BASEBINDIR, include_path = [numpy.get_include()], nthreads = int(1.5 * multiprocessing.cpu_count()),
                              #language = 'c++', # 默认为 C, 可以指定为 C++, 需要在编译成C++代码的.py / .pyx 文件里添加:  "# distutils: language=c++"
        except:
            #os.remove(finup_handler_file)
            #with open(finup_handler_file, 'wb') as fh:
            #    fh.write(finup_handler_str)
            #     fh.flush()
            raise
        sys.exit(0)

    elif len(sys.argv) == 1:
        sys.argv.extend(['build_ext',  '--inplace'])
    d = datetime.datetime.now()
    PARENTDIR = os.path.dirname(BASEDIR)
    TIMETAG = d.strftime('%Y%m%d%H%M%S')
    MODEL_SYMBOL = os.path.basename(BASEDIR) + '__' + TIMETAG
    PSRC_FILE = os.sep.join([PARENTDIR, MODEL_SYMBOL + '__py.tar.gz'])

    VERSIONDIR = os.sep.join([PARENTDIR, MODEL_SYMBOL + '__src'])
    TORNADODIR = os.sep.join([VERSIONDIR, 'tornado'])
    CMD = r"test -d %r && rm -rf %r; cp -prf %r %r; test -d %r && rm -rf %r" % (VERSIONDIR,VERSIONDIR,  BASEDIR,VERSIONDIR, TORNADODIR,TORNADODIR)
    os.system(CMD)
    CMD = r"find %r -name '*.pyc' -exec rm -f \{\} \;" % (VERSIONDIR) 
    os.system(CMD)
    RMDIRS =[shutil.rmtree(i) for i in [ os.sep.join([VERSIONDIR, d]) for d in ('logs', 'build', '.git', '.idea') ] if os.path.exists(i) ]
    os.makedirs(os.sep.join([VERSIONDIR, 'logs']))

    os.chdir(PARENTDIR)
    CMD = r'tar -cpzf %r %r' % (PSRC_FILE, os.path.basename(VERSIONDIR))
    os.system(CMD)
    PSRC_FILE_MD5 = hashlib.md5(open(PSRC_FILE,'rb').read()).hexdigest()
    PSRC_FILE_RELEASE = os.sep.join([PARENTDIR,  MODEL_SYMBOL + '__'+ PSRC_FILE_MD5 + '.tar.gz'])
    os.rename(PSRC_FILE, PSRC_FILE_RELEASE)
    os.chdir(VERSIONDIR)

    BASEBINDIR = os.sep.join([PARENTDIR, MODEL_SYMBOL])
    DATA_DEST_DIR = os.sep.join([BASEBINDIR,  'data'])
    MODELS_DEST_DIR = os.sep.join([BASEBINDIR,  'models'])
    os.makedirs(DATA_DEST_DIR)
    #os.makedirs(MODELS_DEST_DIR)
    print('BASEBINDIR: %s <<<<' % BASEBINDIR)

    pyfiles = find('.', exts=['.py'], excludes=['^\.', '^setup.py$', '^template.py$', '^dist.py$', '^build$', '^data$', '^logs$', '^tornado$'], withdir = True)
    print(pyfiles)

    buildfiles = [ ]
    for f in pyfiles:
        if f in ('./setup.py', './dist.py', './build'):
            continue

        if not f.endswith('.py'):
            assert os.path.isdir(f)
            fullpath = os.path.abspath( os.sep.join([BASEBINDIR, f]))
            if not os.path.exists(fullpath):
                os.makedirs(fullpath)
            continue

        dirname = os.path.dirname(f)
        basename = os.path.basename(f)
        if basename == '__init__.py' or basename == '__main__.py':
            init_dest =os.path.dirname( os.path.abspath(os.sep.join([BASEBINDIR, f])) )
            shutil.copy(f, init_dest)
            continue

        assert basename.rfind('.py') > 0

        c_file = os.sep.join([dirname, basename[:basename.rfind('.py')] + '.c'])
        c_file_dest = os.path.abspath(os.sep.join([BASEBINDIR, c_file]))

        so_file = os.sep.join([dirname, basename[:basename.rfind('.py')] + '.so'])
        so_file_dest = os.path.abspath(os.sep.join([BASEBINDIR, so_file]))

        buildfiles.append((f, (c_file, c_file_dest), (so_file, so_file_dest)))
    finup_handler_file = './handlers/finup_handler.py'
    finup_handler_str = None
    # main_server_file = './main_server.py'
    # main_server_str = None
    #
    # with open(finup_handler_file, 'rb') as fh:
    #     finup_handler_str = fh.read()
    # fh_new = finup_handler_str.replace(b"self.debug =False if self.get_query_argument('debug', None) is None else True", b"self.debug =False #### AUTO GENERATION FOR CYTHON")
    # os.remove(finup_handler_file)
    # with open(finup_handler_file, 'wb') as fh:
    #     fh.write(fh_new)
    #     fh.flush()
    # with open(main_server_file, 'rb') as fh:
    #     main_server_str = fh.read()
    # main_server_new = main_server_str.replace(b'DEBUG = True', b"DEBUG = False")
    # with open(main_server_file, 'wb') as fh:
    #     fh.write(main_server_new)
    #     fh.flush()

    try:
        cythonized_extension_modules = cythonize([py_file for py_file, (c_file, c_file_dest), (so_file, so_file_dest) in buildfiles],
                              build_dir = BASEBINDIR, include_path = [numpy.get_include()],
                              nthreads = int(1.5 * multiprocessing.cpu_count()),
                              #language = 'c++', # 默认为 C, 可以指定为 C++, 需要在编译成C++代码的.py / .pyx 文件里添加:  "# distutils: language=c++"
        )
    except:
        os.remove(finup_handler_file)
        with open(finup_handler_file, 'wb') as fh:
            fh.write(finup_handler_str)
            fh.flush()
        raise
    os.remove(finup_handler_file)
    with open(finup_handler_file, 'wb') as fh:
        fh.write(finup_handler_str)
        fh.flush()

    os.chdir(BASEBINDIR)
    extensions = []
    extension_files = []

    for py_f, (c_file, c_file_dest), (so_file, so_file_dest) in buildfiles:
        cont = b''
        with open(c_file, 'rb') as fh:
            cont  = fh.read()
            os.unlink(c_file)
        ## 移除comments里py源码, 增加反向工程生成原代码难度. 只要反向工程时间和人力成本，高于新创一个模型成本，目标就达成.
        while 1:
            comment_end = cont.find(b'*/')
            if comment_end < 0:
                break
            comment_start = cont.rfind(b'/*', 0, comment_end)
            if comment_start < 0:
                break
            cont = cont[:comment_start] + cont[comment_end+2:]

        with open(c_file_dest, 'wb') as fh:
            fh.seek(0)
            fh.write(cont)
            fh.flush()

        basename = os.path.basename(c_file)
        module_name = basename.partition('.')[0]
        extensions.append(Extension(module_name, [c_file]))

        module_dest_path = so_file.rpartition('.')[0]
        extension_files.append( (module_dest_path, c_file) )





    #cythonize(extensions)
    extensions_str = ',\n'.join( ['  (%r, %r)' % (module_dest_path, c_file)   for module_dest_path, c_file in  extension_files ] )
    with open('./dist.py', 'wb') as fh:
        fh.write( escape.utf8('''# -*-coding:utf-8-*-

import sys,os,re,six,shutil,multiprocessing ,numpy, pandas
sys.path.insert(0, '.')

from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

if len(sys.argv) > 1:
    cfile = sys.argv[1]
    sys.argv = [sys.argv[0], 'build_ext', '-i']
    modname, _, suffix = os.path.basename(cfile).rpartition('.')
    ext = Extension(name=modname, sources=[cfile])
    setup(ext_modules=cythonize(ext))
    sys.exit(0)

elif len(sys.argv) == 1:
    sys.argv.extend(['build_ext',  '--inplace'])

CURRENT_FILE = os.path.abspath(__file__)
BASEDIR = os.path.dirname(CURRENT_FILE)
BASENAME  = os.path.basename(CURRENT_FILE)
BASEBINDIR =BASENAME  if  BASENAME.endswith('_bin')  else  os.sep.join([BASEDIR,  BASENAME + '_bin'])

extension_files = [
%s
]

if six.PY3:
    extension_files = [(os.path.abspath(ext_modname), c_file) for ext_modname, c_file in extension_files]
cythonized_extensions = cythonize([  Extension(ext_modname, [c_file]) for ext_modname, c_file in extension_files  ])
setup( ext_modules=cythonized_extensions,
    libraries=[],
    include_dirs=[]
)

''' % extensions_str
    ))


    if os.path.exists(DATA_DIR) and os.path.isdir(DATA_DIR) and os.path.exists(DATA_DEST_DIR):
        #shutil.copytree(DATA_DIR, DATA_DEST_DIR, symlinks=False)
        filters_exts = ['.dat','.csv', '.json', '.gz', '.txt', '.sh']
        filters = find(DATA_DIR, exts=filters_exts, withdir = False)
        for f in filters:
            tgt = f.replace(DATA_DIR, DATA_DEST_DIR)
            dirname = os.path.dirname(tgt)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            ext = f[f.rfind('.'):]
            if ext in filters_exts and os.path.exists(f) and os.path.isfile(f):
                shutil.copyfile(f, tgt)


    for f in os.listdir(MODELS_DIR):
        if f.endswith('.dat'):
            abspath = os.path.abspath(os.sep.join([MODELS_DIR, f]))
            shutil.copy(abspath, MODELS_DEST_DIR)

    REQUIREMENTS_FILE = os.sep.join([VERSIONDIR, 'requirements.txt'])
    if os.path.exists(REQUIREMENTS_FILE) or os.path.isfile(REQUIREMENTS_FILE) and os.path.exists(BASEBINDIR):
        shutil.copy(REQUIREMENTS_FILE, os.sep.join([BASEBINDIR, 'requirements.txt']))

    LOGS_DIR = os.sep.join([BASEBINDIR, 'logs'])
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    #dist = setup( ext_modules = cythonized_extension_modules )

    os.chdir(PARENTDIR)
    CSRC_FILE = os.sep.join([PARENTDIR, MODEL_SYMBOL + '__cy.tar.gz'])
    CMD = r'tar -cpzf %r %r' % (CSRC_FILE, os.path.basename(BASEBINDIR))
    os.system(CMD)
    CSRC_FILE_MD5 = hashlib.md5(open(CSRC_FILE,'rb').read()).hexdigest()
    CSRC_FILE_RELEASE = os.sep.join([PARENTDIR,  MODEL_SYMBOL + '__'+ PSRC_FILE_MD5 + '__' + CSRC_FILE_MD5 + '.tar.gz'])
    os.rename(CSRC_FILE, CSRC_FILE_RELEASE)
#    shutil.rmtree(BASEBINDIR)
#    shutil.rmtree(VERSIONDIR)



#        setup(ext_modules = cythonize(f))
#        shutil.move(c_file, c_file_dest)
#        shutil.move(so_file, so_file_dest)


#    setup(ext_modules = cythonize("finup_model.py"))
#    setup(ext_modules = cythonize("main_server.py"))
#    setup(ext_modules = cythonize("otp.py"))
#    setup(ext_modules = cythonize("lru.py"))
