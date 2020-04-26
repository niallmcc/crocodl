/*
 Copyright 2020 Niall McCarroll

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
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