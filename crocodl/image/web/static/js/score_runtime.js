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

runtime = null;
function boot_runtime() {
    runtime = new ScoreRuntime();
}

class ScoreRuntime extends Runtime {

    constructor() {
        super();
        var that = this;

        this.modelInfo = $("model_info");
        this.modelInput = $("upload_model_file");
        this.imageInput = $("upload_image_file");
        this.image = $("image");
        this.score_table_body = $("score_table_body");
        this.model_uploaded = false;
        this.image_uploaded = false;

        this.modelInput.onchange = function() {
            var files = that.modelInput.files;
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, 'model_upload/', 'upload_model_progress',function(result) {
                    that.modelInfo.innerHTML="";
                    that.modelInfo.appendChild(document.createTextNode(JSON.stringify(result)));
                    that.model_uploaded = true;
                    that.clearScores();
                    that.score();
                });
            }
        }

        this.imageInput.onchange = function() {
            var files = that.imageInput.files;
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, 'image_upload/', 'upload_image_progress',function(url) {
                    that.image.setAttribute("src",url);
                    that.image_uploaded = true;
                    that.clearScores();
                    that.score();
                });
            }
        }
    }

    score() {
        if (this.image_uploaded && this.model_uploaded) {
            var that = this;
            this.epoch = 0;
            fetch("score.json", {
                method: 'POST',
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            }).then((response) => {
                    return response.json();
                })
                .then((results) => {
                    that.showScores(results)
                });
        }
    }

    clearScores() {
        this.score_table_body.innerHTML = "";
    }

    showScores(results) {
        // alert(JSON.stringify(results));
        var scores = results["scores"];
        for(var i=0; i<scores.length; i++) {
            var cls = scores[i][0];
            var score = scores[i][1];
            var t1 = document.createTextNode(cls);
            var t2 = document.createTextNode(score.toFixed(3));
            var td1 = document.createElement("td"); td1.appendChild(t1);
            var td2 = document.createElement("td"); td2.appendChild(t2);
            var tr = document.createElement("tr");
            tr.appendChild(td1);
            tr.appendChild(td2);
            this.score_table_body.appendChild(tr);
        }
    }
}


