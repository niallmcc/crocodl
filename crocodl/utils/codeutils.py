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

import os.path
import re

def expand_imports(src,pattern,root_folder):
    lines = src.split("\n")
    for idx in range(len(lines)):
        line = lines[idx]
        matches = re.match(pattern,line)
        if matches:
            match = matches[1]
            filename = os.path.join(root_folder,*match.split("."))+".py"
            s = open(filename,"r").read()
            s = expand_imports(s,pattern,root_folder)
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