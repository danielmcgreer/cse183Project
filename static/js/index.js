// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.

let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        reviews: [], 
        review_text: '', 
        new_review_showing: false, 
        refresh: false,
        hover_review: null,
    };

    app.refresh = () => {
        let temp = app.vue.hover_review;
        app.vue.hover_review = null;
        app.vue.hover_review = temp;
    };

    app.toggle_hover_review = (review_id) => {
        app.vue.hover_review = review_id;
    };

    app.send_review = () => { 
        axios.review(add_review_url, {review_text : app.vue.review_text}).then((result) => {
            let review = app.format_thumbs(result.data.review); 
            app.vue.reviews = app.reindex([review, ...app.vue.reviews]);
            app.clear_new_review();
        })
        .catch((e) => alert("Error Sending New review:", e));
 
    };

    app.send_thumb = (review_id, thumb_rating) => {
        axios.review(thumb_review_url, {
            review_id,
            thumb_rating,
        }).then((result) => {
            let review = app.format_thumbs(result.data.review);
            let index = app.vue.reviews.findIndex((review) => review.id === review_id);
            app.vue.reviews[index] = review;
            app.vue.reviews = app.reindex(app.vue.reviews);
            app.refresh();
        });
    };

    app.get_reviews = () => {
        axios.get(get_reviews_url).then((result) => {
            let reviews = result.data.reviews.map((review) => app.format_thumbs(review)); // map returns new array
            app.vue.reviews = app.reindex(reviews);
        })
        .catch((e) => alert("Error Getting review:", e));

    };

    app.delete_review = (review_id) => {
        axios.review(delete_review_url, {
            review_id,
        }).then(() => {
            app.vue.reviews = app.vue.reviews.filter((review) => review.id !== review_id);
        });
    };

    // happens only in get_reviews or send_review (a new one)
    app.format_thumbs = (review) => {
        review.likes = [];
        review.dislikes = [];
        review.thumbs.forEach((thumb) => {
            let info = {
                name: thumb.name, 
                user_email: thumb.user_email,
            };
            if (thumb.thumb_rating === 1) {
                review.likes.push(info);
            } else if (thumb.thumb_rating === -1) {
                review.dislikes.push(info); 
            }
        });
        return review;
    };

    app.user_thumb_on_review = (review, thumb_rating) => {
        if(thumb_rating === 0) {
            return false;
        } else {
            let arr;
            if (thumb_rating === 1) {
                arr = review.likes;
            } else {
                arr = review.dislikes;
            }
            let index = arr.findIndex((user) => user.user_email === user_email);
            return index !== -1; 
        }
    };

    app.toggle_new_review = () => { 
        app.vue.new_review_showing = !app.vue.new_review_showing;
    };

    app.clear_new_review = () => { 
        app.vue.review_text = "";
    };


    // Use this function to reindex the reviews, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a) => {
        let idx = 0;
        for (p of a) {
            p._idx = idx++;
        }
        return a;
    };

    // dictionary of all methods
    app.methods = {
        // API methods
        send_review: app.send_review, 
        send_thumb: app.send_thumb,
        delete_review: app.delete_review,
        // other methods
        toggle_new_review: app.toggle_new_review,
        toggle_hover_review: app.toggle_hover_review,
        clear_new_review: app.clear_new_review,
        user_thumb_on_review: app.user_thumb_on_review,
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