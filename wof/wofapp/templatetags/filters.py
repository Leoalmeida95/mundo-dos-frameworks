from django import template
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup

register = template.Library()

@register.filter(is_safe=True)
def pygmentize(value):
    try:
        formatter = HtmlFormatter(linenos=True, noclasses=True,style='monokai')
        tree = BeautifulSoup(unescape_html(value))
        code = tree.find('pre')
        if not code['id']: code['id'] = 'text'
        ling = code['id']

        try:
            lexer = get_lexer_by_name(ling[0], stripall=True)
        except ValueError:
            try:
                lexer = guess_lexer(ling[0])
            except ValueError:
                messages.error(request, 'Erro ao selecionar a linguagem')
                return HttpResponseRedirect(reverse('wofapp:home'))

        new_content = highlight(code.contents[0], lexer, formatter)
        new_content += u"<style>%s</style>" % formatter.get_style_defs('.highlight')
        code.replaceWith(BeautifulSoup(new_content))

        return tree
    except KeyError:
        return value

def unescape_html(html):
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&amp;', '&')
    return html