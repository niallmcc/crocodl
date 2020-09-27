/*
Copyright (C) 2020 crocoDL developers

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

$ = function(s) {
    return document.getElementById(s);
}

class Runtime {

    constructor() {
    }

    upload(file, url, progress_id,cb) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', url+file.name, true);

        var progressBar = document.getElementById(progress_id);

        xhr.onload = function(e) {
            progressBar.setAttribute("style","display:none;");
            var result = JSON.parse(xhr.responseText);
            if (cb) {
                cb(result);
            }
        };

        progressBar.setAttribute("style","display:inline;");

        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                progressBar.value = (e.loaded / e.total) * 100;
                progressBar.textContent = progressBar.value;
            }
        };
        xhr.send(file);
    }
}