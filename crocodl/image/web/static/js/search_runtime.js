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
    runtime = new SearchRuntime();
}

class SearchRuntime extends Runtime {

    constructor() {
        super();
        var that = this;

        this.loading = false;
        this.searching = false;
        this.image_uploaded = false;
        this.database_ready = false;
        this.search_ready = false;

        this.loadInfo = $("load_info");
        this.loadInput = $("upload_images_file");
        this.loadImage = $("load_image");
        this.loadMonitor = $("load_monitor");
        this.loadFileName = $("load_file_name");
        this.imageInput = $("upload_image_file");
        this.image = $("image");
        this.searchTableBody = $("search_table_body");
        this.searchButton = $("search_btn");
        this.searchInfo = $("search_info");

        this.createDatabase = $("create_database");
        this.uploadDatabase = $("upload_database");
        this.databaseInput = $("upload_database_file");
        this.databaseInfo = $("database_info");
        this.databaseLink = $("database_link");
        this.architectures = $("architectures");
        this.createDatabaseButton = $("create_database_button");

        this.loadInput.onchange = function() {
            that.setLoadInfo("Adding images...");
            var files = that.loadInput.files;
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, 'images_upload/', 'upload_images_progress',function(result) {
                    that.loading = true;
                    that.refreshControls();
                    that.checkStatus();
                });
            }
        }

        this.imageInput.onchange = function() {
            var files = that.imageInput.files;
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, 'image_upload/', 'upload_image_progress',function(result) {
                    that.clearSearchResults();
                    that.checkStatus();
                });
            }
        }

        this.databaseInput.onchange = function() {
            var files = that.databaseInput.files;
            that.setDatabaseInfo("Uploading database...");
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                that.upload(file, 'upload_database/', 'upload_database_progress',function(result) {
                    that.checkStatus();
                });
            }
        }

        this.searchButton.onclick = function() {
            that.search();
        }

        this.createDatabaseButton.onclick = function() {
            that.doCreateDatabase();
        }

        this.createDatabase.onchange = function() {
            that.refreshControls();
        }

        this.uploadDatabase.onchange = function() {
            that.refreshControls();
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
    }

    search() {
        this.clearSearchResults();
        if (!this.loading && !this.searching) {
            this.setSearchInfo("Starting search...");
            var that = this;
            this.searching = true;
            this.refreshControls();
            fetch("search_image", {
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

    doCreateDatabase() {
        var that = this;
        this.epoch = 0;
        var architecture = this.architecture_names[this.architectures.selectedIndex];
        this.setDatabaseInfo("Creating database...");
        fetch("create_database", {
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
                that.checkStatus();
            });
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

    setLoadInfo(txt,latest_image,latest_filename) {
        this.loadInfo.innerHTML="";
        this.loadInfo.appendChild(document.createTextNode(txt));
        this.loadImage.setAttribute("src",latest_image);
        this.loadFileName.innerHTML = "";
        this.loadFileName.appendChild(document.createTextNode(latest_filename));
    }

    checkStatus() {
        var that = this;
        fetch("status")
            .then((response) => {
                return response.json();
            })
            .then((status) => {
                that.updateStatus(status);
                // if still loading or searching, schedule another check
                if (status["loading"] || status["searching"]) {
                    setTimeout(function() {
                        that.checkStatus();
                    },1000);
                }
            });
    }

    updateStatus(status) {
        this.loading = status["loading"];
        this.searching = status["searching"];
        this.image_uploaded = status["image_uploaded"];
        this.database_ready = status["database_ready"];
        this.search_ready = status["search_ready"];

        this.setDatabaseInfo(status["database_info"]);
        this.databaseLink.setAttribute("href",status["database_url"]);

        var search_status = status["search_progress"];
        this.setSearchInfo(search_status);

        var load_status = status["load_progress"];
        var load_image = "";
        var load_file_name = "";
        if (this.loading && status["latest_load_image"] && status["latest_load_path"]) {
            load_image = status["latest_load_image"];
            load_file_name = status["latest_load_path"];
            this.loadMonitor.setAttribute("style","display:block;");
        } else {
            this.loadMonitor.setAttribute("style","display:none;");
        }

        this.setLoadInfo(load_status,load_image,load_file_name);

        if (status["search_results"]) {
            this.showSearchResults(status["search_results"]);
        }

        if (status["search_image_url"]) {
            this.image.setAttribute("src",status["search_image_url"]);
        }

        this.refreshControls();
    }

    refreshControls() {
        if (this.loading || this.searching) {
            /* database controls */
            this.databaseInput.disabled = true;
            this.createDatabase.disabled = true;
            this.uploadDatabase.disabled = true;
            this.createDatabaseButton.disabled = true;
            this.architectures.disabled = true;

            /* loading controls */
            this.loadInput.disabled = true;

            /* search controls */
            this.searchButton.setAttribute("class","");
            this.searchButton.disabled = true;
            this.imageInput.disabled = true;
            this.databaseLink.setAttribute("style","display:none;");
        } else {
            /* database controls */
            this.createDatabase.disabled = false;
            this.uploadDatabase.disabled = false;
            this.createDatabaseButton.disabled = !this.createDatabase.checked;
            this.architectures.disabled = !this.createDatabase.checked;
            this.databaseInput.disabled = !this.uploadDatabase.checked;

            if (this.database_ready) {
                this.databaseLink.setAttribute("style","display:span;");
            } else {
                this.databaseLink.setAttribute("style","display:none;");
            }

            /* loading controls */
            console.log(this.database_ready);
            this.loadInput.disabled = !this.database_ready;

            /* search controls */
            this.imageInput.disabled = false;
            if (this.image_uploaded && this.search_ready) {
                this.searchButton.setAttribute("class","button-primary");
                this.searchButton.disabled = false;
            } else {
                this.searchButton.setAttribute("class","");
                this.searchButton.disabled = true;
            }
        }
    }
}


