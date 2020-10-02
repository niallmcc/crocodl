#    Copyright (C) 2020 crocoDL developers
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this software
#   and associated documentation files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all copies or
#   substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
#   BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os.path
import re

def specialise_imports(model_factory,code):
    (module_name,class_name) = model_factory.getModelUtilsModule()
    return code.replace("from crocodl.runtime.model_utils import createModelUtils",
    					"from %s import %s\ncreateModelUtils = %s.createModelUtils"%(module_name,class_name,class_name))

def expand_imports(src,pattern,root_folder,expanded_filenames=set()):
    lines = src.split("\n")
    for idx in range(len(lines)):
        line = lines[idx]
        matches = re.match(pattern,line)
        if matches:
            match = matches[1]
            filename = os.path.join(root_folder,*match.split("."))+".py"
            if filename not in expanded_filenames:
                expanded_filenames.add(filename)
                s = open(filename,"r").read()
                s = expand_imports(s,pattern,root_folder,expanded_filenames)
                slines = s.split("\n")
                for jdx in range(len(slines)):
                    if not slines[jdx].startswith("#"):
                        break
                s = "\n".join(slines[jdx:])
                lines[idx] = s
    return "\n".join(lines)

if __name__ == '__main__':
    xpanded = expand_imports(open("/crocodl/image/autoencoder/train_autoencoder.py").read(), re.compile("from (crocodl\.utils\.[^ ]*) import .*"))
    open("/tmp/test.py","w").write(xpanded)