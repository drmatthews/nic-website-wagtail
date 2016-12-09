from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

from django.utils.safestring import mark_safe

code = 'for i in range(0,10):\n    print i'
src = code.strip('\n')
print src
lang = 'python'
lexer = get_lexer_by_name(lang)
formatter = get_formatter_by_name(
    'html',
    linenos=None,
    cssclass='highlight',
    style='colorful',
    noclasses=False,
)
print mark_safe(highlight(src, lexer, formatter))
