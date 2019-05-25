import re 
import pygments 
from django import template 
from pygments import lexers 
from pygments import formatters 
 
register = template.Library() 
regex = re.compile(r'<pre(.*?)>(.*?)</pre>', re.DOTALL) 
 
@register.filter(is_safe=True) 
def pygmentize(value): 
    last_end = 0 
    to_return = '' 
    found = 0 
    for match_obj in regex.finditer(value): 
        code_class = match_obj.group(1) 
        code_string = match_obj.group(2) 
        if "<" and ">" and "</" in code_string:
            lexer = lexers.get_lexer_by_name('HTML', stripall=True) 
        elif code_class.find('id'): 
            language = re.split('id=', code_class)[1] 
            lexer = lexers.get_lexer_by_name(language, stripall=True)  
        else: 
            try: 
                lexer = lexers.guess_lexer(code_string, stripall=True) 
            except ValueError: 
                lexer = lexers.PythonLexer() 
        pygmented_string = pygments.highlight(code_string, lexer, formatters.HtmlFormatter(linenos=True, noclasses=True,style='emacs')) 
        to_return = to_return + value[last_end:match_obj.start(0)] + pygmented_string 
        last_end = match_obj.end(2) 
        found = found + 1 
    to_return = to_return + value[last_end:] 
    return to_return 