''' Py-extensions for CudaText.
Authors:
    Andrey Kvichansky    (kvichans on github)
Version:
    '0.6.1 2017-02-09'
Wiki: github.com/kvichans/cudax_lib/wiki
ToDo: (see end of file)
'''

import  os, json, re, sys, collections

import  sw        as app
from    sw    import ed
#import sw_cmd    as cmds

# Overridden option tools:
APP_DEFAULT_OPTS    = {}
LAST_FILE_OPTS      = {}

# Localization
CONFIG_MSG_DONT_SET_FILE= 'Cannot set editor properties'
CONFIG_MSG_DONT_SET_PATH= 'Cannot set complex path'
NEED_NEWER_API          = 'Needs newer app version'
COMMENTING              = 'Commenting'
DUPLICATION             = 'Duplication'
ONLY_NORM_SEL_MODE      = '{} works only with normal selection'
CMT_NO_LINE_4LEX        = 'No line comment for lexer "{}"'
CMT_NO_STRM_4LEX        = 'No stream comment for lexer "{}"'
ONLY_SINGLE_CRT         = "{} doesn't work with multi-carets"

pass;                           # Logging
pass;                           import inspect  # stack
pass;                           from pprint import pformat
pass;                           pfrm15=lambda d:pformat(d,width=15)
pass;                           LOG = (-2==-2)  # Do or dont logging.
pass;                           log_gap = ''    # use only into log()

#################################################
## Common APP utils
def version(self):
    ''' Value from module doc
        Version:'value'
    '''
    return re.split('Version:', __doc__)[1].split("'")[1]

def _check_API(ver):
    if app.app_api_version()<ver:
        app.msg_status(NEED_NEWER_API)
        return False
    return True

def _json_loads(s, **kw):
    ''' Adapt s for json.loads
            Delete comments
            Delete unnecessary ',' from {,***,} and [,***,]
    '''
    s = re.sub(r'(^|[^:])//.*'  , r'\1', s)     # :// in http://
    s = re.sub(r'{\s*,'         , r'{' , s)
    s = re.sub(r',\s*}'         , r'}' , s)
    s = re.sub(r'\[\s*,'        , r'[' , s)
    s = re.sub(r',\s*\]'        , r']' , s)
    try:
        ans = json.loads(s, **kw)
    except:
        pass;                   LOG and log('FAIL: s={}',s)
        pass;                   LOG and log('sys.exc_info()={}',sys.exc_info())
        open(kw.get('log_file', _get_log_file()), 'a').write('_json_loads FAIL: s=\n'+s)
        ans = None
    return ans
#   return json.loads(s, **kw)
    #def _json_loads

LAST_FILE_OPTS      = {}
def _get_file_opts(opts_json, def_opts={}, **kw):
#   global LAST_FILE_OPTS
    if not os.path.exists(opts_json):
        pass;                  #LOG and log('no {}',os.path.basename(opts_json))
        LAST_FILE_OPTS.pop(opts_json, None)
        return def_opts
    mtime_os    = os.path.getmtime(opts_json)
    if opts_json not in LAST_FILE_OPTS:
        pass;                  #LOG and log('load "{}" with mtime_os={}',os.path.basename(opts_json), int(mtime_os))
        opts    = _json_loads(open(opts_json, encoding='utf8').read(), **kw)
        LAST_FILE_OPTS[opts_json]       = (opts, mtime_os)
    else:
        opts, mtime = LAST_FILE_OPTS[opts_json]
        if mtime_os > mtime:
            pass;              #LOG and log('reload "{}" with mtime, mtime_os={}',os.path.basename(opts_json), (int(mtime), int(mtime_os)))
            opts= _json_loads(open(opts_json, encoding='utf8').read(), **kw)
            LAST_FILE_OPTS[opts_json]   = (opts, mtime_os)
    return opts
   #def _get_file_opts

CONFIG_LEV_DEF      = 'def'
CONFIG_LEV_USER     = 'user'
CONFIG_LEV_LEX      = 'lex'
CONFIG_LEV_FILE     = 'file'
CONFIG_LEV_ALL      = 'dulf'
def get_opt(path, def_value=None, lev=None, ed_cfg=None):
    ''' Adapter for "Overridden options tool" from CudaText.
        Config pairs key:val are read from
            <app>/settings/user.json
        Params
            path        OptKey name
            def_value   If no OptKey into config file
            lev         (ignoreed)
            ed_cfg      (ignoreed)
        Return          Last found in config files default[/user[/lexer]] or def_value
    '''
    pass;                      #LOG and log('path, def_va, lev, ed_cfg={}',(path, def_value, lev, ed_cfg))
    usr_json    = os.path.join(app.app_ini_dir(), 'user.json')
#   if not os.path.exists(usr_json):
#       return def_value
    usr_opts    = _get_file_opts(usr_json)
    return usr_opts.get(path, def_value)
   #def get_opt

def set_opt(path, value, lev=None, ed_cfg=None):
    ''' Adapter for "Overridden options tool" from CudaText.
        Config pairs key:val are add/update/delete into
            <app>/settings/user.json
        Params
            path        OptKey name
            value       Value for setting or deleting
                            None        Delete pair (last key in path)
                            is not None Add or update pair value
            lev         (ignoreed)
            ed_cfg      (ignoreed)
        Return          The value (second param) or None if fail
    '''
    usr_json    = os.path.join(app.app_ini_dir(), 'user.json')
    pass;                      #LOG and log('path, value,usr_json={}',(path, value,usr_json))
    if not os.path.exists(usr_json)  and value is     None:
        pass;                  #LOG and log('no usr_json and del val',())
        return None #?? success or fail?
    if not os.path.exists(usr_json):#and value is not None
        # First pair for this file
        dct     = {path:value}
        open(usr_json, 'w', encoding='utf8').write(json.dumps(dct, indent=4))
        pass;                  #LOG and log('save body as dct={}',(dct))
        return value

    # Try to modify file
    body    = open(usr_json, encoding='utf8').read()
    value4js= json.dumps({'':value})[len('{"": '):-1]    # format for json
    # Assumptions:
    #    one key:val into one row
    re_key_val  = r'^\s*,?\s*"{}"\s*:.+'.format(re.escape(path))
    cre         = re.compile(re_key_val, re.MULTILINE)
    has_pair    = cre.search(body) is not None
    pass;                      #LOG and log('re_key_val, has_pair={}',(re_key_val,has_pair))
    if False:pass
    elif has_pair and value is None:
        # Delete!
        pass;                  #LOG and log('del!',)
        body    = cre.sub('', body)
    elif has_pair and value is not None:
        # Update!
        pass;                  #LOG and log('upd!',)
        body    = cre.sub('    "{}": {},'.format(path, value4js), body)
    elif not has_pair and value is None:
        # OK
        pass
    elif not has_pair:
        # Add! before end
        pass;                  #LOG and log('add!',)
        body    = body.rstrip(' \t\r\n')[:-1].rstrip(' \t\r\n')
        body= body+'{}\n    "{}": {},\n}}'.format(
                     '' if body[-1] in ',{' else ','
                   , path
                   , value4js)
    pass;                      #LOG and log('save body as \n{}',(body))
    open(usr_json, 'w', encoding='utf8').write(body)
    return value
   #def set_opt

def get_tab_by_id(tab_id):
    for h in app.ed_handles(): 
        try_ed  = app.Editor(h)
        if int(tab_id) == try_ed.get_prop(app.PROP_TAB_ID, ''):
            return try_ed
    return None

def get_groups_count():
    dct = {
        app.GROUPS_ONE      : 1,
        app.GROUPS_2VERT    : 2,
        app.GROUPS_2HORZ    : 2,
        app.GROUPS_3VERT    : 3,
        app.GROUPS_3HORZ    : 3,
        app.GROUPS_3PLUS    : 3,
        app.GROUPS_1P2VERT  : 3,
        app.GROUPS_1P2HORZ  : 3,
        app.GROUPS_4VERT    : 4,
        app.GROUPS_4HORZ    : 4,
        app.GROUPS_4GRID    : 4,
        app.GROUPS_6GRID    : 6
    }
    gr_mode = app.app_proc(app.PROC_GET_GROUPING, '')
    return dct.get(gr_mode, 1)

def get_enabled_lexers():
    all_lxrs  = app.lexer_proc(app.LEXER_GET_LIST, '') #.splitlines()
    enb_lxrs  = [lxr for lxr in all_lxrs if app.lexer_proc(app.LEXER_GET_ENABLED, lxr)]
    return enb_lxrs
def choose_avail_lexer(lxr_names):
    """ Choose from lxr_names first enabled lexer """
    all_lxrs  = get_enabled_lexers()
    for lxr in lxr_names:
        if lxr in all_lxrs:
            return lxr
    return ''

def _get_log_file():
    return os.path.join(app.app_ini_dir(), 'cudax.log')

def get_def_setting_dir():
    pass;                     #LOG and log('os.path.dirname(app.app_ini_dir())={}', os.path.dirname(app.app_ini_dir()))
    return os.path.join(
                os.path.dirname(app.app_ini_dir())
            ,   'settings_default' )
    #def get_def_setting_dir

def _opt_for_keys(dct_tree, keys=(), def_val=None):
    ''' Get opt as full dct_tree or sub-dict or single value
        Params
            keys    Path for dct_tree
                    (str1, str2, ...)
                    str
            def_val Default for return
        Return      dct_tree if keys==()
                    dct_tree[keys[0]][keys[1]][keys[2]]
                    def_val if any keys[*] not in [sub-]dict
    '''
    if isinstance(keys, str):
        return dct_tree.get(keys, def_val)
    ans     = dct_tree
    for k in keys:
        if not isinstance(ans, dict): return def_val
        if k not in ans:              return def_val
        ans = ans.get(k)
    return ans
    #def _opt_for_keys

def minmax(v1, v2):
    return min(v1, v2), max(v1, v2)

def int_to_html_color(n):
    """
    Convert int to HTML color '#rrggbb'
    """
    s = '%06x' % n
    r, g, b = s[4:], s[2:4], s[:2]
    return '#'+r+g+b
   #def int_to_html_color

def html_color_to_int(s):
    """
    Convert HTML color '#RRGGBB' or '#RGB' to int
    """
    s = s.strip().lstrip('#')
#   while s[0] == '#': s = s[1:]
    if len(s)==3:
        s = s[0]*2 + s[1]*2 + s[2]*2
    if len(s)!=6:
        raise Exception('Incorrect color token: '+s)
    s = s[4:6] + s[2:4] + s[0:2]
    color = int(s, 16)
    return color
   #def html_color_to_int

def icase(*pars):
    """ Params    cond1,val1[, cond2,val2, ...[, valElse]...]
        Result    Value for first true cond in pairs otherwise last odd param or None
        Examples
            icase(1==2,'a', 3==3,'b') == 'b'
            icase(1==2,'a', 3==4,'b', 'c') == 'c'
            icase(1==2,'a', 3==4,'b') == None
    """
    for ppos in range(1,len(pars),2) :
        if pars[ppos-1] :
            return pars[ppos]
    return pars[-1] if 1==len(pars)%2 else None
    #def icase

def log(msg='', *args, **kwargs):
    """ en:
        Light print-logger. Commands are included into msg:
            >> << {{    Expand/Narrow/Cancel gap
        Execute msg.format(*args).  So you can insert Format String Syntax into msg.
        Replace '¬' to chr(9), '¶'to chr(10).

        Example.
        1    class C:
        2        def m():
        3            log('qwerty')
        4            log('>>more gap here')
        5            log('v1={}¶v2,v3¬{}',12,('ab',{}))
        6            log('<<less gap at next')
        7            log('QWERTY')
        output
            C.m:3 qwerty
                C.m:4 >>more gap here
                C.m:5 v1=12
            v2,v3    ('ab', {})
                C.m:6 <<less gap at next
            C.m:7 QWERTY
    """
    global log_gap
    lctn    = ''
    if -1==-1: # add "location"
        frCaller= inspect.stack()[1]    # 0-log, 1-need func
        try:
            cls = frCaller[0].f_locals['self'].__class__.__name__ + '.'
        except:
            cls = ''
        fun,ln  = (cls + frCaller[3]).replace('.__init__','()'), frCaller[2]
        lctn    = '{}:{} '.format(fun, ln)

    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    log_gap = log_gap + (chr(9) if '>>' in msg else '')
    msg     = log_gap + lctn + msg.replace('¬',chr(9)).replace('¶',chr(10))

    _out_h  = kwargs.pop('_out_h', None)
    _out_s  = kwargs.pop('_out_s', None)
    pass;                      #print('_out_h={}, _out_s={}'.format(_out_h, _out_s))
    if False:pass
    elif _out_h:
        _out_h.write(msg+chr(10))
    elif _out_s:
        with open(_out_s, 'a') as _out_h:
            _out_h.write(msg+chr(10))
    else:
        print(msg)

    log_gap = icase('<<' in msg, log_gap[:-1]
                   ,'{{' in msg, ''
                   ,             log_gap )
    #def log

'''
ToDo
[S][кто-кому][дата] Что сделать
    [S] Состояние: [ ] Не реализовано, [+] Сделано, [-] Не требуется, [?] Нужны уточнения
    [кто-кому] Автор-Исполнитель. Принимает значения: [kv] kvichans, [at] Alexey-T
    [дата] Когда придумано
---------------
[+][kv-kv][27oct15] full-line-if-no-sel for stream-cmt
[+][kv-at][27oct15] Дать способ вертикального перемещения каретки вниз
[+][kv-kv][27oct15] При Cmt1st не вставлять // перед пробелами, а заменять
[ ][kv-kv][27oct15] ! Разрешить Комм и Дубл для режима "много кареток"
[ ][kv-at][27oct15] Дать механизм для Localization
[-][kv-at][27oct15] Дать доступ из плагинов к командам из cudax_lib
[ ][kv-at][27oct15] Спрятать в меню Plugins команды из cudax_lib
[+][kv-kv][28oct15] Применять cmt_toggle_line_(1st|body) к каждой строке в выделении, решение по первой строке
[+][kv-at][28oct15] Включить настройки cudax_lib в общие default.json и user.json
[ ][kv-kv][28oct15] Контролировать, что выделенный фрагмент имеет один Лексер
[+][at-kv][29oct15] Вычислять по всему выделению оптимальную позицию для body - min(body_pos)
[+][kv-kv][29oct15] Брать/использовать комментарии из def_lexs.json\CommentsForLines
[?][kv-at][01nov15] (bug!) При быстром последовательном клике Ctrl+/ переход на новую строку не отрабатывает
[-][kv-kv][01nov15] Разделить set_opt на set_opt и del_opt
[+][kv-kv][02nov15] При stream-comm выделение направлять как исходное
[?][kv-at][02nov15] При stream-comm верт.выделении с неск каретками не давать ed.get_sel_mode()==SEL_COLUMN
[+][kv-kv][02nov15] При line-comm и добавлении/удалении символов перед выделением происходит смещение выделения. Избавиться!
'''
