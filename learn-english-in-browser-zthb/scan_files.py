import os

""" Generate javavascript file to list all .jpg and mp3 files in current
    directory.
"""

_verbose_mode = False

FTYPE_NONE = -1
FTYPE_JPG = 0
FTYPE_MP3 = 1

JsFileName = 'file_list.js'

def log(msg):
    global _verbose_mode
    if _verbose_mode:
        print msg

def error(msg):
    print msg

def check_file_type(filePath):
    if filePath.endswith('.mp3') or filePath.endswith('.jpg'):
        return True
    elif filePath.endswith('.zip') or   \
         filePath.endswith('.tar') or   \
         filePath.endswith('.rar') or   \
         filePath.endswith('.html') or  \
         filePath.endswith('.js') or    \
         filePath.endswith('.py') or    \
         filePath.endswith('.pyc') or   \
         filePath.endswith('.txt'):
        return False
    else:
        error('Unknown file type %s' % filePath)
        return False

def get_file_index_type(fileName):
    index = -1 # -1 not set; 0 title
    start = -1
    end = -1
    ftype = FTYPE_NONE

    if fileName.endswith('_title_text.mp3'):
        index = 0
        ftype = FTYPE_MP3
    elif fileName.endswith('.jpg'):
        start = fileName.rfind('-')
        end = fileName.rfind('.jpg')
        if start != -1:
            start += 1
        ftype = FTYPE_JPG
    elif fileName.endswith('.mp3'):
        end = fileName.rfind('_text.mp3')
        start = fileName.rfind('_p', 0, end)
        if start != -1:
            start += 2
        ftype = FTYPE_MP3

    if start != -1 and end != -1:
        try:
            index = int(fileName[start : end])
            if index <= 0:
                index = -1
        except ValueError:
            pass

    if index == -1 or ftype == FTYPE_NONE:
        error('Unhandled file type: %s', fileName)

    return (index, ftype)

def add_to_file_map(m, baseDir, fileName, index, ftype):
    if not baseDir in m:
        m[baseDir] = {}
    if not index in m[baseDir]:
        m[baseDir][index] = ['', '']

    m[baseDir][index][ftype] = fileName

def output_to_js(m, workDir):
    global JsFileName
    f = open(os.path.join(workDir, JsFileName), 'wt')
    f.write('var DirFileLists = [\n')

    for baseDir, indexMap in sorted(m.iteritems()):
        f.write('{ dirBase : "%s/",\n' % baseDir)
        f.write('  fileLists : [\n')

        for index, files in indexMap.iteritems():
            f.write('    "%s", "%s",\n' % (files[FTYPE_JPG], files[FTYPE_MP3]))
        f.write(' ]\n')
        f.write('},\n')

    f.write('];\n')
    f.close()
    print 'Generated js file: %s' % JsFileName

def get_file_path_list(workDir):
    log(workDir)
    dirList = ["."]
    filePathList = []
    while dirList:
        curDir = dirList.pop()
        log('POP: ' + curDir)

        items = os.listdir(os.path.join(workDir, curDir))
        for item in items:
            log('ITEM: ' + item)
            if item == '.' or item == '..':
                continue
            itemPath = os.path.join(curDir, item)
            if os.path.isdir(os.path.join(workDir, itemPath)):
                dirList.append(itemPath)
            else:
                if check_file_type(itemPath):
                    # Convert \ to / for path on windows
                    filePathList.append(itemPath.replace('\\', '/'))
    return filePathList

def generate_js(filePathList, workDir):
    filePathList.sort()

    if False and _verbose_mode:
        for filePath in filePathList:
            log(filePath)

    # Generate dict.
    #   baseDirMap        : {baseDir -> indexMap}
    #   indexMap          : {index -> [JPG FILE, MP3 FILE]}
    #   index is parsed from file name.

    baseDirMap = {}
    for filePath in filePathList:
        (baseDir, fileName) = os.path.split(filePath)
        (index, ftype) = get_file_index_type(fileName)
        add_to_file_map(baseDirMap, baseDir, fileName, index, ftype)

    # Merge 'title' mp3 with first page if both are single.
    for baseDir, indexMap in sorted(baseDirMap.iteritems()):
        if 0 in indexMap and 1 in indexMap and not indexMap[1][FTYPE_MP3]:
            baseDirMap[baseDir][1][FTYPE_MP3] = baseDirMap[baseDir][0][FTYPE_MP3]
            del baseDirMap[baseDir][0]


    # Print dict
    if _verbose_mode:
        for baseDir, indexMap in sorted(baseDirMap.iteritems()):
            for index, files in indexMap.iteritems():
                log('[dict] %s -- %d, %s, %s' % (baseDir, index, files[FTYPE_JPG], files[FTYPE_MP3]))

    # Output from dict
    output_to_js(baseDirMap, workDir)

# main
if __name__ == '__main__':
    workDir = os.getcwd()
    filePathList = get_file_path_list(workDir)
    generate_js(filePathList, workDir)

