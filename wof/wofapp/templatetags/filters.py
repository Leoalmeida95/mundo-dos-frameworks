from django import template
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup
from pygments.styles import get_all_styles

register = template.Library()

@register.filter(is_safe=True)
def pygmentize(value):
    try:
        tree = BeautifulSoup(unescape_html(value))
        for code in tree.findAll('code'):
            if not code['class']: code['class'] = 'text'
            ling = code['class']

            try:
                lexer = get_lexer_by_name(ling[0], stripall=True)
            except ValueError:
                try:
                    lexer = guess_lexer(ling[0])
                except ValueError:
                    messages.error(request, 'Erro ao selecionar a linguagem')
                    return HttpResponseRedirect(reverse('wofapp:home'))

            styles = list(get_all_styles())
            new_content = highlight(code.contents[0], lexer, HtmlFormatter())
            code.replaceWith(BeautifulSoup(new_content))

        return tree
    except KeyError:
        return value

def unescape_html(html):
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&amp;', '&')
    return html