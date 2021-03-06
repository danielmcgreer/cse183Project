// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        query: "",
        results: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.complete = (results) => {
        // Initializes useful fields of rows.
        results.map((result) => {
            result.link_display_course = "../display_course/" + result.department + "/" + result.class_number;
        })
    };

    app.search = function () {
        let query = app.vue.query;
        if (query.length > 0) {
            axios.get(search_url, {params: {q: query}})
                .then(function (result) {
                    let results = result.data.results;
                    app.enumerate(results);
                    app.complete(results);
                    app.vue.results = results;
                });
        } else {
            app.vue.results = [];
        }
    }

    app.submit = function () {

        let query = app.vue.query;
        if (query.length > 0) {
            console.log("test!!");
            let encoded = encodeURI(query);
            console.log(encoded);
            window.location.href = '../display_courses/' + encoded;

//            axios.get(search_results_url, {params: {q: query}})
//                .then(function (result) {
//                    window.location.href = '../display_courses/' + result.data.department + '/' + result.data.numbers;
//                });
        }
    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        search: app.search,
        submit: app.submit,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
