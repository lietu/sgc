(function () {
    "use strict";

    /**
     * Convert argument to Array
     * @param items
     * @returns {Array.<T>}
     */
    var toArray = function (items) {
        return Array.prototype.slice.call(items);
    };

    /**
     * Log something if console is available
     */
    var log = function () {
        if (typeof console !== "undefined" && console.log) {
            console.log.apply(console, toArray(arguments));
        }
    };

    /**
     * Steam Game Chooser logic
     */
    var SGC = {
        form: null,
        listButton: null,
        listSection: null,
        listTemplate: null,
        gameTemplate: null,
        fields: [],

        choice: null,
        name: [],
        games: [],
        matches: [],
        game: [],
        review: [],
        hours: [],
        logo: [],
        appid: [],
        listData: {},
        listSort: "name",

        /**
         * Load up elements to cache, set up event listeners
         */
        start: function () {
            log("Starting up SGC");

            this.form = document.querySelector("form#chooser");
            this.listButton = document.querySelector("button#list");
            this.listSection = document.querySelector("section.list");
            this.gameTemplate = document.querySelector("#game-template");
            this.fields = toArray(document.querySelectorAll("form input"));
            this.username = document.querySelector("form #name");

            this.choice = document.querySelector(".choice");
            this.name = toArray(document.querySelectorAll(".name"));
            this.games = toArray(document.querySelectorAll(".games"));
            this.matches = toArray(document.querySelectorAll(".matches"));
            this.game = toArray(document.querySelectorAll(".game"));
            this.review = toArray(document.querySelectorAll(".review"));
            this.hours = toArray(document.querySelectorAll(".hours"));
            this.logo = toArray(document.querySelectorAll(".logo"));
            this.appid = toArray(document.querySelectorAll(".appid"));

            this.message = toArray(document.querySelectorAll(".message"));

            this.errormessage = document.querySelector(".error-message");
            this.loader = document.querySelector(".loader");

            if (document.activeElement && ["input", "button"].indexOf(document.activeElement.tagName) === -1) {
                this.username.focus();
            }

            this.form.addEventListener("submit", this._onSubmit.bind(this));
            this.listButton.addEventListener("click", this._onList.bind(this));
        },

        _getFormData: function () {
            var form_data = {
                name: null,
                reviews: [],
                hours_lt: null
            };

            var errors = false;

            this.fields.forEach(function (field) {
                if (field.name === "reviews") {
                    if (field.checked) {
                        form_data.reviews.push(field.value);

                        log("Review level " + field.value + " is included");
                    }
                } else {
                    if (field.name == "name" && !field.value) {
                        field.classList.add("error");
                        field.focus();

                        errors = true;

                        log("Missing username");
                    } else if (field.name == "hours_lt" && isNaN(Number(field.value))) {
                        field.classList.add("error");
                        field.focus();

                        errors = true;

                        log("Invalid hours (?)");
                    } else {
                        field.classList.remove("error");

                        log("No errors with field " + field.name);
                    }

                    form_data[field.name] = field.value;
                }
            });

            if (!errors) {
                return {
                    name: form_data.name,
                    reviews: (form_data.reviews ? form_data.reviews.join(",") : "null"),
                    hours_lt: (form_data.hours_lt ? form_data.hours_lt : "null")
                };
            } else {
                return null;
            }
        },

        /**
         * Triggered when "Choose a game" is clicked
         *
         * @param {Event} event
         * @private
         */
        _onSubmit: function (event) {
            log("Choose a game");

            var data = this._getFormData();

            if (data !== null) {
                log("No errors.");
                log("Data was:", data);

                this._getChoice(data);
            }

            event.preventDefault();
        },

        /**
         * Triggered when "Show list" is clicked
         *
         * @param {Event} event
         * @private
         */
        _onList: function (event) {
            log("Show list");

            var data = this._getFormData();

            if (data !== null) {
                log("No errors.");
                log("Data was:", data);

                this._getList(data);
            }

            event.preventDefault();
        },

        _getChoice: function (data) {
            var url = "/pick/" + data.name + "/" + data.reviews + "/" + data.hours_lt;

            log("Fetching " + url);

            this.choice.classList.remove("fetched");
            this.errormessage.classList.remove("visible");
            this.loader.classList.add("loading");

            var req = new XMLHttpRequest();
            req.addEventListener("load", this._getRequestHandler(req));
            req.open("GET", url);
            req.send();
        },

        _getList: function (data) {
            var url = "/list/" + data.name + "/" + data.reviews + "/" + data.hours_lt;

            log("Fetching " + url);

            this.listSection.classList.add("hidden");
            this.errormessage.classList.remove("visible");

            var req = new XMLHttpRequest();
            req.addEventListener("load", this._getRequestHandler(req));
            req.open("GET", url);
            req.send();
        },

        _getRequestHandler: function (req) {
            return function (event) {
                log("Load complete");
                log(req);
                log("Response status was " + req.status);

                if (req.status === 200) {
                    var response = JSON.parse(req.responseText);
                    log(response);

                    log("Result was: " + response.type);

                    if (response.type === "recommendation") {
                        this._setChoice(response);
                    } else if (response.type === "list") {
                        this.listData = response;
                        this._buildList();
                    } else {
                        this._setError(response);
                    }
                } else {
                    log("Response: " + req.responseText)
                }
            }.bind(this);
        },

        _setError: function (data) {
            for (var key in data) {
                if (!this[key]) {
                    continue;
                }

                log("Setting data for " + key);

                var elements = this[key];
                for (var i = 0, count = elements.length; i < count; i += 1) {
                    if (elements[i].tagName === "IMG") {
                        continue;
                    }
                    elements[i].innerText = String(data[key]);
                    elements[i].textContent = String(data[key]);
                }
            }

            this.loader.classList.remove("loading");
            this.choice.classList.remove("fetched");
            this.errormessage.classList.add("visible");
        },

        _capitalize: function (str) {
            return str.charAt(0).toUpperCase() + str.slice(1);
        },

        _setSort: function (event) {
            var text;
            if (event.target.innerText) {
                text = event.target.innerText;
            } else {
                text = event.target.textContent;
            }

            var key = text.toLowerCase().trim().replace(/ .*$/, "");

            log(key);

            if (key != "") {
                if (key == this.listSort) {
                    key = "!" + key;
                }

                log("Sorting is now by " + key);

                this.listSort = key;
                this._buildList();
            }
        },

        _buildList: function () {
            var i, count;

            if (!this.listTemplate) {
                this.listTemplate = Handlebars.compile(this.gameTemplate.innerHTML);
            }

            var key = this.listSort;
            var reversed = false;
            if (key[0] === "!") {
                reversed = true;
                key = key.substr(1);
            }

            var keys = ["name", "hours", "review"];
            for (i = 0, count = keys.length; i < count; i += 1) {
                var sortKey = this._capitalize(keys[i]);

                log(sortKey, key);
                if (sortKey.toLowerCase() === key) {
                    if (!reversed) {
                        this.listData["sortBy" + sortKey] = true;
                        this.listData["sortBy" + sortKey + "Rev"] = false;
                    } else {
                        this.listData["sortBy" + sortKey] = false;
                        this.listData["sortBy" + sortKey + "Rev"] = true;
                    }
                } else {
                    this.listData["sortBy" + sortKey] = false;
                    this.listData["sortBy" + sortKey + "Rev"] = false;
                }
            }

            log(this.listData);

            this.listData.name = this._capitalize(this.listData.name);

            this.listData.list.sort(function (a, b) {
                var first = a[key];
                var second = b[key];

                if (reversed) {
                    var tmp = second;
                    second = first;
                    first = tmp;
                }

                if (first < second) {
                    return -1;
                } else if (first > second) {
                    return 1;
                } else {
                    return 0;
                }
            });

            this.listSection.innerHTML = this.listTemplate(this.listData);

            this.listSection.classList.remove("hidden");
            var headers = this.listSection.querySelectorAll("th");
            for (i = 0, count = headers.length; i < count; i += 1) {
                headers[i].addEventListener("click", this._setSort.bind(this));
            }
        },

        _setChoice: function (data) {
            for (var key in data) {
                if (!this[key]) {
                    continue;
                }

                log("Setting data for " + key);
                var elements = this[key];
                for (var i = 0, count = elements.length; i < count; i += 1) {
                    if (key === "logo") {
                        elements[i].src = data[key];
                    } else if (key === "appid") {
                        elements[i].href = "steam://run/" + data[key] + "/";
                    } else {
                        elements[i].innerText = String(data[key]);
                        elements[i].textContent = String(data[key]);
                    }
                }
            }

            this.loader.classList.remove("loading");
            this.errormessage.classList.remove("visible");
            this.choice.classList.add("fetched");
        }
    };

    window.SGC = SGC;
    SGC.start();
})();