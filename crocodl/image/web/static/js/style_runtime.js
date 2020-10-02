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

runtime = null;
function boot() {
    runtime = new StyleRuntime();
}

class StyleRuntime extends Runtime {

    constructor() {
        super();
        this.restyleInfo = $("restyle_info");
        this.restyleButton = $("restyle_button");
        this.restyleProgress = $("restyle_progress");
        this.restyleSelect = $("restyle_select");
        this.restyleSelectParent = $("restyle_select_parent");
        this.restyleImage = $("restyle_image");
        this.restyling = false;
        this.nrIterations = $("nr_iterations");
        this.restyleSelectOptions = [];
        this.restyledImages = {};
        this.completedIterations = 0;
        this.totalIterations = 0;

        var that = this;

        this.baseImageInput = $("upload_base_image_file");
        this.baseImage = $("base_image");
        this.base_image_uploaded = false;

        this.baseImageInput.onchange = function() {
            var files = that.baseImageInput.files;
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, 'base_image_upload/', 'upload_base_image_progress',function(result) {
                    that.baseImage.setAttribute("src",result["url"]);
                    that.base_image_uploaded = true;
                    that.refreshControls();
                });
            }
        }

        this.styleImageInput = $("upload_style_image_file");
        this.styleImage = $("style_image");
        this.style_image_uploaded = false;

        this.styleImageInput.onchange = function() {
            var files = that.styleImageInput.files;
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, 'style_image_upload/', 'upload_style_image_progress',function(result) {
                    that.styleImage.setAttribute("src",result["url"]);
                    that.style_image_uploaded = true;
                    that.refreshControls();
                });
            }
        }

        this.restyleButton.onclick = function() {
            if (that.restyling) {
                that.cancel();
                that.restyling = false;
                that.restyleButton.value = "Start restyling";
            } else {
                that.restyle();
                that.restyling = true;
                that.restyleButton.value = "Cancel restyling";
            }
        }

        this.setRestyleOptions([]);
        this.restyleSelect.onchange = function() {
            that.updateResultImage();
        }

        this.checkStatus();
    }

    restyle() {
        var that = this;
        var nr_iterations = parseInt(this.nrIterations.value);
        this.restyleImage.setAttribute("src","");
        this.setRestyleOptions([]);
        this.restylingCompletedIterations = 0;
        this.restyledImages = {};
        if (this.base_image_uploaded && this.style_image_uploaded) {
            fetch("restyle", {
                method: 'POST',
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ "nr_iterations":nr_iterations})
            }).then((response) => {
                return response.json();
            })
            .then((status) => {
                that.checkStatus();
            });
        }
    }

    cancel() {
        var that = this;

        fetch("cancel", {
            method: 'POST',
            cache: 'no-cache',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        }).then((response) => {
            return response.json();
        })
        .then((status) => {
            if (status["cancelled"]) {
                alert("Cancelled");
            };
        });
    }

    checkStatus() {
        var that = this;
        fetch("status")
            .then((response) => {
                return response.json();
            })
            .then((status) => {
                that.updateStatus(status);
                // if still restyling, schedule another check in 10s
                if (status["restyling"]) {
                    setTimeout(function() {
                        that.checkStatus();
                    },10000);
                }
            });
    }

    setRestyleInfo(txt) {
        this.restyleInfo.innerHTML="";
        this.restyleInfo.appendChild(document.createTextNode(txt));
    }

    setRestyleOptions(options) {
        if (options.length > 0) {
            if (options == this.restyleSelectOptions) {
                return;
            }
            this.restyleSelectParent.setAttribute("style","visbility:visible;");
            var orig_value = "";
            if (this.restyleSelect.selectedIndex >= 0) {
                var orig_value = this.restyleSelect.options[this.restyleSelect.selectedIndex].value;
            }
            this.restyleSelect.innerHTML = "";
            var selected_index = -1;
            for(var i=0; i<options.length; i++) {
                var value = options[i];
                if (orig_value == value) {
                    selected_index = i;
                }
                var option = document.createElement("option");
                option.setAttribute("value",value);
                option.appendChild(document.createTextNode("After iteration "+value));
                this.restyleSelect.appendChild(option);
            }
            if (selected_index >= 0) {
                this.restyleSelect.selectedIndex = selected_index;
            } else {
                this.restyleSelect.selectedIndex = 0;
            }
            this.restyleSelectOptions = options;
        } else {
            this.restyleSelect.innerHTML = "";
            this.restyleSelectParent.setAttribute("style","visibility:hidden;");
        }
    }

    updateResultImage() {
        var iteration_key = "";
        if (this.completedIterations >= 0) {
            iteration_key = ""+this.completedIterations;
        }
        if (this.restyleSelect.selectedIndex >= 0) {
            var selected_iteration = this.restyleSelect.options[this.restyleSelect.selectedIndex].value;
            if (selected_iteration != "<latest>") {
                iteration_key = selected_iteration;
            }
        }
        if (iteration_key != "" && iteration_key in this.restyledImages) {
            var url = "restyled_image/"+this.restyledImages[iteration_key];
            if (url != this.restyleImage.getAttribute("src")) {
                this.restyleImage.setAttribute("src",url);
            }
        } else {
            this.restyleImage.setAttribute("src","");
        }
    }

    updateStatus(status) {
        console.log(JSON.stringify(status))
        this.restyling = status["restyling"];
        this.base_image_uploaded = status["base_image_uploaded"];
        this.style_image_uploaded = status["style_image_uploaded"];
        this.setRestyleInfo(status["restyling_info"]);
        var restyled_images = status["restyled_images"];
        var completed_iterations = status["completed_iterations"];
        var iterations = status["iterations"];

        this.baseImage.setAttribute("src",status["base_image_url"]);
        this.styleImage.setAttribute("src",status["style_image_url"]);

        this.restyledImages = restyled_images;
        this.completedIterations = completed_iterations;
        this.totalIterations = iterations;

        this.updateResultImage();
        var restyle_options = [];
        if (completed_iterations>0) {
            restyle_options.push("<latest>");
            for(var i=1; i<=completed_iterations; i++) {
                restyle_options.push(""+i);
            }
        }
        this.setRestyleOptions(restyle_options);

        if (this.restyling) {
            this.restyleProgress.setAttribute("style","visibility:visible;");
            var pct = (completed_iterations/iterations) * 100;
            this.restyleProgress.value = pct;
            this.restyleProgress.textContent = ""+ pct.toFixed(0) + " %";
        } else {
            this.restyleProgress.setAttribute("style","visibility:hidden;");
        }
        this.refreshControls();
    }

    refreshControls() {
        if (this.restyling || (this.style_image_uploaded && this.base_image_uploaded)) {
            this.restyleButton.setAttribute("class","button-primary");
            this.restyleButton.disabled = false;
        } else {
            this.restyleButton.setAttribute("class","");
            this.restyleButton.disabled = true;
        }
        if (this.restyling) {
            this.baseImageInput.disabled = true;
            this.styleImageInput.disabled = true;
        } else {
            this.baseImageInput.disabled = false;
            this.styleImageInput.disabled = false;
        }
    }

}