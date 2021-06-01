// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.

let init = (app) => {

    // This is the Vue data.
    app.data = {
        reviews_list: [],
        avg_rating: "",
        avg_difficulty: "",
        avg_workload: "",
		adding_new_review: false,
		new_teacher: "",
		new_rating: 0,
		new_workload: 0,
		new_difficulty: 0,
		new_review: "",
		author:"",
		current_user:"",

		
		not_logged_in_wanring: false,
		no_teacher_warning: false,
		no_rating_warning: false,
		no_workload_warning: false,
		no_difficulty_warning: false,
		no_review_warning: false
    };

    app.set_add_status = function (new_status) {
		if(app.vue.current_user == null){
			app.vue.not_logged_in_wanring = true;
			return;
		}
		else{
			not_logged_in_wanring = false;
		}
		app.clear_new_post();
        app.vue.adding_new_review = new_status;
    };

    app.submit_review = function () {
		let fail = false;
		
		if(app.vue.new_teacher == ""){
			fail = true;
			app.vue.no_teacher_warning = true;
		}
		else{
			app.vue.no_teacher_warning = false;
		}
		if(app.vue.new_rating == 0){
			fail = true;
			app.vue.no_rating_warning = true;
		}
		else{
			app.vue.no_rating_warning = false;
		}
		if(app.vue.new_workload == 0){
			fail = true;
			app.vue.no_workload_warning = true;
		}
		else{
			app.vue.no_workload_warning = false;
		}
		if(app.vue.new_difficulty == 0){
			fail = true;
			app.vue.no_difficulty_warning = true;
		}
		else{
			app.vue.no_difficulty_warning = false;
		}
		if(app.vue.new_review == ""){
			fail = true;
			app.vue.no_review_warning = true;
		}
		else{
			app.vue.no_review_warning = false;
		}
		if(fail){
			return;
		}
			
        axios.post(submit_review_url+'/'+course_id,
            {
                teacher: app.vue.new_teacher,
				rating: app.vue.new_rating,
				workload: app.vue.new_workload,
				difficulty: app.vue.new_difficulty,
				review: app.vue.new_review,
				_state: {teacher: "clean", review: "clean"},
            }).then(function (response) {
			app.get_reviews(course_id);
			app.enumerate(app.vue.reviews_list);
			app.clear_new_post();
			app.set_add_status(false);
        });
    };

    app.get_reviews = () => {
		axios.get(get_reviews_url+'/'+course_id).then(function (response) {
            app.vue.reviews_list = app.decorate(app.enumerate(response.data.the_reviews));
            app.vue.current_user=response.data.name;
            app.vue.avg_rating=response.data.avg_review;
            app.vue.avg_difficulty=response.data.avg_difficulty;
            app.vue.avg_workload=response.data.avg_workload;

        });
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
            }).then(() => {
                app.get_reviews();
            });
    };


    app.clear_new_post = () => {
        app.vue.new_review = "";
        app.vue.new_teacher = "";
        app.vue.new_rating = 0;
		app.vue.new_workload = 0;
        app.vue.new_difficulty = 0;
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };
    app.decorate = (a) => {
        a.map((e) => {e._state = {teacher: "clean", review: "clean"} ;});
        return a;
    }

    // Star Rating
    app.stars_out = () => {
        app.vue.new_rating = new_rating;
    };

    app.stars_over = (num_stars) => {
        app.vue.new_rating = num_stars;
    };

    app.set_stars = (num_stars) => {
        new_rating = num_stars;
        // Sets the stars on the server.
    };
    
    // Difficulty Rating
    app.bombs_out = () => {
        app.vue.new_difficulty = new_difficulty;
    };

    app.bombs_over = (num_bombs) => {
        app.vue.new_difficulty = num_bombs;
    };

    app.set_bombs = (num_bombs) => {
        new_difficulty = num_bombs;
        // Sets the bombs on the server.
    };
    
    // Workload
    app.planes_out = () => {
        app.vue.new_workload = new_workload;
    };

    app.planes_over = (num_planes) => {
        app.vue.new_workload = num_planes;
    };

    app.set_planes = (num_planes) => {
        new_workload = num_planes;
        // Sets the planes on the server.
    };

    // dictionary of all methods
    app.methods = {
        // API methods
        delete_review: app.delete_review,
        set_stars: app.set_stars,
        stars_over: app.stars_over,
        stars_out: app.stars_out,
        
        set_bombs: app.set_bombs,
        bombs_over: app.bombs_over,
        bombs_out: app.bombs_out,
        
        set_planes: app.set_planes,
        planes_over: app.planes_over,
        planes_out: app.planes_out,

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
		new_rating=0;
        new_workload=0;
		new_difficulty=0;
		not_logged_in_wanring=false;
		no_teacher_warning= false;
		no_rating_wanring= false;
		no_workload_warning= false;
		no_difficulty_warning= false;
		no_review_wanring= false;
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
init(app);