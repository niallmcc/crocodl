# Copyright 2020 Niall McCarroll
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from pygments import highlight
from pygments.lexers.python import Python3Lexer
from pygments.formatters.html import HtmlFormatter

class CodeFormatter(object):

    def __init__(self):
        pass

    def formatHTML(self,code):
        fmt = HtmlFormatter(style='colorful')
        html = highlight(code, Python3Lexer(), fmt)
        style = fmt.get_style_defs('.highlight')
        return "<html>\n<head>\n<style>\n" + style + "\n</style>\n<body>\n" + html + "\n</body>\n</html>"

if __name__ == '__main__':
    cf = CodeFormatter()
    code = open(__file__).read()
    html = cf.formatHTML(code)
    open("/tmp/test.html","w").write(html)