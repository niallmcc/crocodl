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

        this.training = false;
        this.searching = false;

        this.databaseInfo = $("database_info");
        this.trainInfo = $("train_info");
        this.trainInput = $("upload_images_file");
        this.trainImage = $("train_image");
        this.trainMonitor = $("train_monitor");
        this.trainFileName = $("train_file_name");
        this.imageInput = $("upload_image_file");
        this.image = $("image");
        this.searchTableBody = $("search_table_body");
        this.searchButton = $("search_btn");
        this.searchInfo = $("search_info");

        this.architectures = $("architectures");
        this.clearButton = $("clear_btn");

        this.image_uploaded = false;

        this.trainInput.onchange = function() {
            that.setTrainInfo("Adding images...");
            var files = that.trainInput.files;
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, '/images_upload/', 'upload_images_progress',function(result) {
                    that.training = true;
                    that.refreshControls();
                    that.checkStatus();
                });
            }
        }

        this.imageInput.onchange = function() {
            var files = that.imageInput.files;
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, '/image_upload/', 'upload_image_progress',function(url) {
                    that.image.setAttribute("src",url);
                    that.image_uploaded = true;
                    that.clearSearchResults();
                });
            }
        }

        this.searchButton.onclick = function() {
            that.search();
        }

        this.clearButton.onclick = function() {
            that.clearDatabase();
        }

        this.architecture_names = [];
        fetch('configuration.json')
            .then((response) => {
                return response.json();
            })
              .then((config) => {
                that.configure(config);
              });

        this.checkStatus();
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
        var that = this;
        this.architectures.onchange = function() {
            that.configureDatabase();
        }
    }

    search() {
        this.clearSearchResults();
        this.setSearchInfo("Starting search...");
        if (!this.training && !this.searching) {
            var that = this;
            this.searching = true;
            this.refreshControls();
            fetch("/search_image", {
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
                    that.checkStatus();
                });
        }
    }

    clearDatabase() {
        if (!this.training && !this.searching) {
            var that = this;
            this.searching = true;
            this.refreshControls();
            fetch("/clear_database", {
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
                    that.checkStatus();
                });
        }
    }

    configureDatabase() {
        if (!this.training && !this.searching) {
            var that = this;
            this.searching = true;
            this.refreshControls();
            var architecture = this.architecture_names[this.architectures.selectedIndex];
            fetch("/configure_database", {
                method: 'POST',
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({"architecture":architecture})
            }).then((response) => {
                    return response.json();
                })
                .then((results) => {
                    that.checkStatus();
                });
        }
    }

    clearSearchResults() {
        this.searchTableBody.innerHTML = "";
    }

    showSearchResults(search_results) {
        console.log(JSON.stringify(search_results));
        this.clearSearchResults();
        for(var i=0; i<search_results.length; i++) {
            var filename = search_results[i]["filename"];
            var similarity = search_results[i]["similarity"];
            var image_data_uri = search_results[i]["image"];
            var t1 = document.createTextNode(filename);
            var t2 = document.createTextNode(similarity.toFixed(3));
            var t3 = document.createElement("img");
            t3.setAttribute("src",image_data_uri);
            var td1 = document.createElement("td"); td1.appendChild(t1);
            var td2 = document.createElement("td"); td2.appendChild(t2);
            var td3 = document.createElement("td"); td3.appendChild(t3);
            var tr = document.createElement("tr");
            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.appendChild(td3);
            this.searchTableBody.appendChild(tr);
        }
    }

    setDatabaseInfo(txt) {
        this.databaseInfo.innerHTML="";
        this.databaseInfo.appendChild(document.createTextNode(txt));
    }

    setSearchInfo(txt) {
        this.searchInfo.innerHTML="";
        this.searchInfo.appendChild(document.createTextNode(txt));
    }

    setTrainInfo(txt,latest_image,latest_filename) {
        this.trainInfo.innerHTML="";
        this.trainInfo.appendChild(document.createTextNode(txt));
        this.trainImage.setAttribute("src",latest_image);
        this.trainFileName.innerHTML = "";
        this.trainFileName.appendChild(document.createTextNode(latest_filename));
    }

    checkStatus() {
        var that = this;
        fetch("status")
            .then((response) => {
                return response.json();
            })
            .then((status) => {
                that.updateStatus(status);
                // if still training or searching, schedule another check
                if (status["training"] || status["searching"]) {
                    setTimeout(function() {
                        that.checkStatus();
                    },1000);
                }
            });
    }

    updateStatus(status) {
        this.training = status["training"];
        this.searching = status["searching"];
        this.setDatabaseInfo(status["database_info"]);

        var search_status = "";
        if (this.searching) {
            search_status = status["search_progress"];
        }
        this.setSearchInfo(search_status);

        var train_status = "";
        if (this.training) {
            train_status = status["train_progress"];
        }

        var train_image = "";
        var train_file_name = "";
        if (this.training && status["train_image"] && status["train_file_name"]) {
            train_image = status["train_image"];
            train_file_name = status["train_file_name"];
            this.trainMonitor.setAttribute("style","display:block;");
        } else {
            this.trainMonitor.setAttribute("style","display:none;");
        }

        this.setTrainInfo(train_status,train_image,train_file_name);


        if (status["search_results"]) {
            this.showSearchResults(status["search_results"]);
        }

        this.refreshControls();
    }

    refreshControls() {
    }
}


