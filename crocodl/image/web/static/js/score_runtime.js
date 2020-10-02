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

score_runtime = null;
function boot_score_runtime(embedded_in_train) {
    score_runtime = new ScoreRuntime(embedded_in_train);
}

class ScoreRuntime extends Runtime {

    constructor(embedded_in_train) {
        super();
        var that = this;
        this.embedded_in_train = embedded_in_train;
        if (this.embedded_in_train) {
            this.modelInfo = null;
            this.modelInput = null;
        } else {
            this.modelInfo = $("model_info");
            this.modelInput = $("upload_model_file");
        }
        this.imageInput = $("upload_image_file");
        this.image = $("image");
        this.score_table = $("score_table");
        this.score_table_body = $("score_table_body");
        this.score_status = $("score_status");

        this.distance_table = $("distance_table");
        this.distance_table_body = $("distance_table_body");
        this.model_uploaded = false;
        this.image_uploaded = false;
        if (this.modelInput) {
            this.modelInput.onchange = function () {
                var files = that.modelInput.files;
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];
                    that.upload(file, 'model_upload/', 'upload_model_progress', function (result) {
                        that.modelInfo.innerHTML = "";
                        that.modelInfo.appendChild(document.createTextNode(JSON.stringify(result)));
                        that.model_uploaded = true;
                        that.clearScores();
                        that.score();
                    });
                }
            }
        } else {
            this.model_uploaded = true;
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

    startScoring() {
        if (self.score_status) {
            self.score_status.innerHTML = "Fetching Scores...";
        }
    }

    score() {
        if (this.image_uploaded && this.model_uploaded) {
            this.startScoring();
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
                    that.endScoring();
                    that.showScores(results);
                });
        }
    }

    endScoring() {
        if (self.score_status) {
            self.score_status.innerHTML = "";
        }
    }

    clearScores() {
        this.score_table_body.innerHTML = "";
        this.score_table.setAttribute("style","display:none;");
        this.distance_table_body.innerHTML = "";
        this.distance_table.setAttribute("style","display:none;");
    }

    showScores(results) {
        if (results["distance"] != undefined) {
            this.distance_table.setAttribute("style","display:block;");
            var t1 = document.createTextNode(results["distance"].toFixed(3));
            var td1 = document.createElement("td");
            td1.appendChild(t1);
            var tr = document.createElement("tr");
            tr.appendChild(td1);
            this.distance_table_body.appendChild(tr);
        } else if (results["scores"]) {
            this.score_table.setAttribute("style","display:block;");
            var scores = results["scores"];
            for (var i = 0; i < scores.length; i++) {
                var cls = scores[i][0];
                var score = scores[i][1];
                var t1 = document.createTextNode(cls);
                var t2 = document.createTextNode(score.toFixed(3));
                var td1 = document.createElement("td");
                td1.appendChild(t1);
                var td2 = document.createElement("td");
                td2.appendChild(t2);
                var tr = document.createElement("tr");
                tr.appendChild(td1);
                tr.appendChild(td2);
                this.score_table_body.appendChild(tr);
            }
        }
    }
}


