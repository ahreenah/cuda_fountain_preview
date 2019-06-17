import os
import webbrowser
from cudatext import *
import urllib.request
from .node_proc import *

fn_script = os.path.join(os.path.dirname(__file__), 'runner.js')
fn_script_fountain = os.path.join(os.path.dirname(__file__), 'fountain_parser.js')
fn_ini = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_emmet.ini')
ini_section = 'setup'
ini_key_profile = 'profile'
text_quote = '%Q%'

lexers_xml = ['XML', 'XSL', 'XSLT']
lexers_css = ['CSS', 'SCSS', 'SASS', 'Sass', 'Stylus', 'LESS']

server_running=True

def get_syntax():
    lexer = ed.get_prop(PROP_LEXER_CARET)
    if lexer in lexers_xml:
        return 'xsl'
    elif lexer in lexers_css: 
        return 'css'
    else:
        return 'html'

    
def get_profile():
    return ini_read(fn_ini, ini_section, ini_key_profile, profiles[0])
      

def do_find_expand():
    x, y, x1, y1 = ed.get_carets()[0]
    text = ed.get_text_line(y)
    if not text: return
    text = text[:x]
    print('text: '+text)
    x,y=ed.get_carets()[0][0:2]
    ed.replace(0,y,x,y,do_parse_fountain(text))
    if not text: return

    try:
        return do_parse_fountain(text)
    except Exception as e:
        #msg_status(str(e))
        return

def do_find_expand_all():
    x, y, x1, y1 = ed.get_carets()[0]
    text = ed.get_text_all()
    if not text: return
    print('text_all: '+text)
    #x,y=ed.get_carets()[0][0:2]
    #ed.replace(0,y,x,y,do_parse_fountain(text))
    if not text: return

    try:
        return do_parse_fountain(text)
    except Exception as e:
        #msg_status(str(e))
        return
    
    
def do_insert_result(x0, y0, x1, y1, text, text_insert):
    if text_insert:
        for i in [1,2,3,4,5,6,7,8,9,0]:
            text_rep = '${'+str(i)+'}'
            if text_rep in text:
                text = text.replace(text_rep, '${'+str(i)+':'+text_insert+'}', 1)
                break
    
    ed.delete(x0, y0, x1, y1)
    ed.set_caret(x0, y0)
    
    lines = text.splitlines()
    insert_snip_into_editor(ed, lines)


def do_expand_abbrev(text_ab):
    msg_status('Expanding: %s (profile %s)' % (text_ab, get_profile()))
        
    try:
        text = do_parse_fountain(text_ab)
    except Exception as e:
        msg_box(str(e), MB_OK+MB_ICONERROR)
        return

    if not text or text=='?':
        msg_status('Cannot expand Fountain abbreviation: '+text_ab)
        return
        
    return text

def do_parse_fountain(text_to_parse):
    print('parsin`'+run_node('', [fn_script_fountain,text_to_parse]))
    return run_node('', [fn_script_fountain,text_to_parse])

class Command:

    def profiles(self):
        n = dlg_menu(MENU_LIST, '\n'.join(profiles))
        if n is None: return
        item = profiles[n]
        ini_write(fn_ini, ini_section, ini_key_profile, item)

    def help(self):
        webbrowser.open_new_tab(help_url)
        msg_status('Opened browser')

    def wrap_abbrev(self):
        x0, y0, x1, y1 = ed.get_carets()[0]
        #sort coords
        if (y1>y0) or ((y1==y0) and (x1>x0)):
            pass
        else:
            x0, y0, x1, y1 = x1, y1, x0, y0
        
        text_sel = ed.get_text_sel()
        if not text_sel:
            msg_status('Text not selected')
            return
            
        text_ab = dlg_input('Fountain abbreviation:', 'div')
        if not text_ab:
            return
        
        text = do_expand_abbrev(text_ab)
        if not text: return
                                               
        ed.insert(0,0,'abc')#(x0, y0, x1, y1, text, text_sel)
        

    def expand_abbrev(self):
        text = do_find_expand()
        if not text or ';' not in text:
            msg_status('Cannot find Fountain abbreviation')
            return
            
        slen, text = text.split(';', maxsplit=2)
        nlen = int(slen)
        x0, y0, x1, y1 = ed.get_carets()[0]
        xstart = max(0, x0-nlen)
        ed.insert(0,0,'abc')
       
    def expand_all(self):
        text = do_find_expand_all()
        print('all expanded: '+text)
        urllib.request.urlopen('http://127.0.0.1:5000/set/'+'%2501'.join(urllib.parse.quote(text).split('/')))
        #webbrowser.open('data:text/html,'+text)
        if not text or ';' not in text:
            msg_status('Cannot find Fountain abbreviation')
            return
            
        slen, text = text.split(';', maxsplit=2)
        nlen = int(slen)
        x0, y0, x1, y1 = ed.get_carets()[0]
        xstart = max(0, x0-nlen)
        ed.insert(0,0,'abc')        
        #ed.replace(xstart, y0, x0, y0, text, '')
        
    def on_change_slow(self, ed_self):
        self.expand_all()
        
    def stop_server(self):
        global server_running
        if server_running:
            global process
            process.kill()
            server_running=False 
        
    def start_server(self):
        global process
        global server_running
        if not server_running:
            os.chdir(os.path.dirname(__file__))
            try:
                process=Popen(['python3','server.py'])
                print('server started')
            except:
                try:
                    process=Popen(['python','server.py'])
                    print('server started')
                except:
                    print('error')
            finally:
                pass
            server_running=True 

'''
    def parse_fountain(self):
        print('parsin`')
        text_to_parse='*Finland*'
        print(do_parse_fountain(text_to_parse))
        
   '''     