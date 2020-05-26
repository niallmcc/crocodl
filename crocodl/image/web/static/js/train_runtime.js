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
    runtime = new ClassifierRuntime();
}

class ClassifierRuntime extends Runtime {

    constructor() {
        super();
        var that = this;
        this.fileInput = $("upload_data_file");
        this.dataInfo = $("data_info");
        this.modelInfo = $("model_info");
        this.architectures = $("architectures");
        this.train_button = $("train_button");
        this.modelInput = $("upload_model_file");
        this.createModelButton = $("create_model_button");
        this.trainingProgress = $("training_progress");
        this.trainingStatus = $("training_status");
        this.trainingGraph = $("training_graph");
        this.modelDownload = $("model_download");

        this.nr_epochs = $("nr_epochs");
        this.batch_size = $("batch_size");

        this.create_model = $("create_model");
        this.upload_model = $("upload_model");

        this.epoch = 0;

        this.fileInput.onchange = function() {
            that.setDataInfo("Uploading data...");
            var files = that.fileInput.files;
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, 'data_upload/', 'upload_data_progress',function(result) {
                    that.setDataInfo(JSON.stringify(result));
                    that.data_ready = true;
                    that.refreshControls();
                });
            }
        }

        this.modelInput.onchange = function() {
            var files = that.modelInput.files;
            that.setModelInfo("Uploading model...");
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, 'model_upload/', 'upload_model_progress',function(result) {
                    var details = result["model_details"]
                    var url = result["url"];
                    var filename = result["filename"];
                    that.updateDownloadLink(filename,url);
                    that.model_ready = true;
                    that.setModelInfo(JSON.stringify(details));
                    that.refreshTrainingGraph();
                    that.refreshControls();
                });
            }
        }

        this.architecture_names = [];
        fetch('configuration.json')
            .then((response) => {
                return response.json();
            })
              .then((config) => {
                that.configure(config);
              });

        this.createModelButton.onclick = function() {
            that.doCreateModel();
        }

        this.train_button.onclick = function() {
            that.doTrain();
        }
        this.create_model.onchange = function() {
            that.refreshControls();
        }
        this.upload_model.onchange = function() {
            that.refreshControls();
        }

        this.nr_epochs.onchange = function() {
            that.updateTrainingSettings();
        }

        this.batch_size.onchange = function() {
            that.updateTrainingSettings();
        }

        this.data_ready = false;
        this.model_ready = false;
        this.training = false;
        this.refreshControls();
        that.updateTrainingSettings();

    }

    settings() {
        var training = {};
        training["nr_epochs"] = Number.parseInt(this.nr_epochs.value);
        training["batch_size"] = Number.parseInt(this.batch_size.value);
        return training;
    }

    configure(config) {
        this.architecture_names = config["architectures"];
        architectures.innerHTML = "";
        for(var i=0; i<this.architecture_names.length; i++) {
            var n = this.architecture_names[i];
            var opt = document.createElement("option");
            opt.setAttribute("value",n);
            var tn = document.createTextNode(n);
            opt.appendChild(tn);
            this.architectures.appendChild(opt);
        }
    }

    refreshControls() {
        if (this.training) {
            this.train_button.setAttribute("class","");
            this.train_button.disabled = true;
            this.modelInput.disabled = true;
            this.architectures.disabled = true;
            this.fileInput.disabled = true;
            this.create_model.disabled = true;
            this.upload_model.disabled = true;
            this.createModelButton.disabled = true;
        } else {
            this.fileInput.disabled = false;
            this.create_model.disabled = !this.data_ready;
            this.upload_model.disabled = !this.data_ready;
            this.createModelButton.disabled = !this.data_ready;
            this.train_button.setAttribute("class","button-primary");
            this.train_button.disabled = !(this.data_ready && this.model_ready);
            this.modelInput.disabled = true;
            this.architectures.disabled = true;
            if (this.create_model.checked && this.data_ready) {
                this.architectures.disabled = false;
            }
            if (this.upload_model.checked && this.data_ready) {
                this.modelInput.disabled = false;
            }
        }
    }

    setModelInfo(text) {
        this.modelInfo.innerHTML="";
        this.modelInfo.appendChild(document.createTextNode(text));
    }

    setDataInfo(text) {
        this.dataInfo.innerHTML="";
        this.dataInfo.appendChild(document.createTextNode(text));
    }

    setTrainingStatus(text) {
        this.trainingStatus.innerHTML="";
        this.trainingStatus.appendChild(document.createTextNode(text));
    }

    updateTrainingSettings() {
        var batch_size = Number.parseInt(this.batch_size.value);
        var nr_epochs = Number.parseInt(this.nr_epochs.value);
        var that = this;
        fetch("update_training_settings.json", {
            method: 'POST',
            cache: 'no-cache',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({"batch_size":batch_size,"nr_epochs":nr_epochs})
        }).then((response) => {
                return response.json();
            })
            .then((update_status) => {
                that.refreshTrainingGraph();
            });
    }

    doCreateModel() {
        var that = this;
        this.epoch = 0;
        var architecture = this.architecture_names[this.architectures.selectedIndex];
        this.setModelInfo("Creating model...");
        fetch("create_model.json", {
            method: 'POST',
            cache: 'no-cache',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({"architecture":architecture})
        }).then((response) => {
                return response.json();
            })
            .then((create_status) => {
                var details = JSON.stringify(create_status["model_details"]);
                that.setModelInfo(details);
                var url = create_status["url"];
                var filename = create_status["filename"];
                that.updateDownloadLink(filename,url);
                that.refreshTrainingGraph();
                that.model_ready = true;
                that.refreshControls();
            });
    }

    doTrain() {
        var that = this;
        this.epoch = 0;
        fetch("launch_training.json", {
            method: 'POST',
            cache: 'no-cache',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.settings())
        }).then((response) => {
                return response.json();
            })
            .then((launch_status) => {
                that.checkProgress();
            });
    }

    checkProgress() {
        var that = this;
        fetch("training_progress.json")
            .then((response) => {
                return response.json();
            })
            .then((status) => {
                that.updateProgress(status);
                // if still training, schedule another check
                if (status["training"]) {
                    setTimeout(function() {
                        that.checkProgress();
                    },1000);
                }
            });
    }

    updateProgress(status) {
        this.training = status["training"];

        var completed_epochs = status["epoch"];

        if (this.training) {
            var batch = status["batch"];
            var msg = "Training... Epoch "+completed_epochs+" / Batch "+batch;
            this.setTrainingStatus(msg);
        } else {
            this.setTrainingStatus("Training Completed");
            this.refreshTrainingGraph();
        }
        this.trainingProgress.value = status["progress"] * 100;
        this.trainingProgress.textContent = this.trainingProgress.value;
        var that = this;

        if (this.training && completed_epochs != this.epoch) {
            this.refreshTrainingGraph();
            this.epoch = completed_epochs;
        }

        this.refreshControls();
    }

    refreshTrainingGraph() {
        this.trainingGraph.contentWindow.location.reload(true);
    }

    updateDownloadLink(filename,url) {
        this.modelDownload.setAttribute("href",url);
        this.modelDownload.innerHTML = "";
        this.modelDownload.appendChild(document.createTextNode(filename));
    }
}


