(function() {
    "use strict";

    /**
     * Convert argument to Array
     * @param items
     * @returns {Array.<T>}
     */
    var toArray = function(items) {
        return Array.prototype.slice.call(items);
    };

    /**
     * Log something if console is available
     */
    var log = function() {
        if (typeof console !== "undefined" && console.log) {
            console.log.apply(console, toArray(arguments));
        }
    };

    /**
     * Steam Game Chooser logic
     */
    var SGC = {
        form: null,
        fields: [],

        choice: null,
        name: [],
        games: [],
        matches: [],
        game: [],
        review: [],
        hours: [],
        logo: [],

        /**
         * Load up elements to cache, set up event listeners
         */
        start: function() {
            log("Starting up SGC");

            this.form = document.querySelector("form#chooser");
            this.fields = toArray(document.querySelectorAll("form input"));
            this.form.addEventListener("submit", this._onSubmit.bind(this));

            this.choice = document.querySelector(".choice");
            this.name = toArray(document.querySelectorAll(".name"));
            this.games = toArray(document.querySelectorAll(".games"));
            this.matches = toArray(document.querySelectorAll(".matches"));
            this.game = toArray(document.querySelectorAll(".game"));
            this.review = toArray(document.querySelectorAll(".review"));
            this.hours = toArray(document.querySelectorAll(".hours"));
            this.logo = toArray(document.querySelectorAll(".logo"));

            this.loader = document.querySelector(".loader");
        },

        /**
         * Triggered when "Choose a game" is clicked
         *
         * @param {Event} event
         * @private
         */
        _onSubmit: function(event) {
            log("Form submitted");
            var form_data = {
                name: null,
                reviews: [],
                hours_lt: null
            };

            var errors = false;

            this.fields.forEach(function(field) {
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
                log("No errors.");
                log("Data was:", form_data);

                var data = {
                    name: form_data.name,
                    reviews: (form_data.reviews ? form_data.reviews.join(",") : "null"),
                    hours_lt: (form_data.hours_lt ? form_data.hours_lt : "null")
                };

                this._getChoice(data);
            }

            event.preventDefault();
        },

        _getChoice: function(data) {
            var url = "/pick/" + data.name + "/" + data.reviews + "/" + data.hours_lt;

            log("Fetching " + url);

            this.choice.classList.remove("fetched");
            this.loader.classList.add("loading");

            var req = new XMLHttpRequest();
            req.addEventListener("load", this._getChoiceHandler(req));
            req.open("GET", url);
            req.send();
        },

        _getChoiceHandler: function(req) {
            return function(event) {
                log("Load complete");
                log(req);
                log("Response status was " + req.status);

                if (req.status === 200) {
                    var response = JSON.parse(req.responseText);
                    log(response);

                    this._setChoice(response);
                } else {
                    log("Response: " + req.responseText)
                }
            }.bind(this);
        },

        _setChoice: function(data) {
            for (var key in data) {
                log("Setting data for " + key);
                var elements = this[key];
                for (var i = 0, count = elements.length; i < count; i+=1) {
                    if (key === "logo") {
                        elements[i].src = data[key];
                    } else {
                        elements[i].innerText = String(data[key]);
                    }
                }
            }

            this.loader.classList.remove("loading");
            this.choice.classList.add("fetched");
        }
    };

    SGC.start();
})();