// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.

let init = (app) => {

    // This is the Vue data.
    app.data = {
        reviews_list: [],
		adding_new_review: false,
		new_teacher: "",
		new_rating: "",
		new_review: "",
		author:"",
		current_user:""
    };

    app.set_add_status = function (new_status) {
		app.clear_new_post();
        app.vue.adding_new_review = new_status;
    };

    app.submit_review = function () {
        axios.post(submit_review_url+'/'+course_id,
            {
                teacher: app.vue.new_teacher,
				rating: app.vue.new_rating,
				review: app.vue.new_review,
            }).then(function (response) {
			app.get_reviews(course_id);
			app.enumerate(app.vue.reviews_list);
			app.clear_new_post();
			app.set_add_status(false);
        });
    };

    app.get_reviews = () => {
		axios.get(get_reviews_url+'/'+course_id).then(function (response) {
            app.vue.reviews_list = app.enumerate(response.data.the_reviews);
            app.vue.current_user=response.data.name;
        });


    };


    app.clear_new_post = () => {
        app.vue.new_review = "";
        app.vue.new_teacher = "";
        app.vue.new_rating = "";
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.delete_review = function(row_idx) {
        let id = app.vue.reviews_list[row_idx].id;
        axios.get(delete_review_url, {params: {id: id}}).then(function (response) {
            for (let i = 0; i < app.vue.reviews_list.length; i++) {
                if (app.vue.reviews_list[i].id === id) {
                    app.vue.reviews_list.splice(i, 1);
                    app.enumerate(app.vue.reviews_list);
                    break;
                }
            }
            });
    };

    // dictionary of all methods
    app.methods = {
        // API methods
        delete_review: app.delete_review,
		get_reviews: app.get_reviews,
		set_add_status: app.set_add_status,
		submit_review: app.submit_review,
        clear_new_post: app.clear_new_post,
		enumerate: app.enumerate,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        app.get_reviews();
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
init(app);