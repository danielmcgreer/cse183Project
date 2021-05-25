// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.

let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        posts: [],
        post_teacher: '',
        post_rating: '',
        post_text: '', 
        new_post_showing: false, 
        refresh: false,
        hover_post: null,
    };

    app.refresh = () => {
        let temp = app.vue.hover_post;
        app.vue.hover_post = null;
        app.vue.hover_post = temp;
    };

    app.toggle_hover_post = (post_id) => {
        app.vue.hover_post = post_id;
    };

    app.send_post = () => { 
        axios.post(add_post_url, {post_text : app.vue.post_text, 
                                    post_teacher : app.vue.post_teacher, 
                                    post_rating : app.vue.post_rating}).then((result) => {
            let post = app.format_thumbs(result.data.post); 
            app.vue.posts = app.reindex([post, ...app.vue.posts]);
            app.clear_new_post();
        })
        .catch((e) => alert("Error Sending New Post:", e));
 
    };

    app.send_thumb = (post_id, rating) => {
        axios.post(thumb_post_url, {
            post_id,
            rating,
        }).then((result) => {
            let post = app.format_thumbs(result.data.post);
            let index = app.vue.posts.findIndex((post) => post.id === post_id);
            app.vue.posts[index] = post;
            app.vue.posts = app.reindex(app.vue.posts);
            app.refresh();
        });
    };

    app.get_posts = () => {
        axios.get(get_posts_url).then((result) => {
            let posts = result.data.posts.map((post) => app.format_thumbs(post)); // map returns new array
            app.vue.posts = app.reindex(posts);
        })
        .catch((e) => alert("Error Getting Post:", e));

    };

    app.delete_post = (post_id) => {
        axios.post(delete_post_url, {
            post_id,
        }).then(() => {
            app.vue.posts = app.vue.posts.filter((post) => post.id !== post_id);
        });
    };

    // happens only in get_posts or send_post (a new one)
    app.format_thumbs = (post) => {
        post.likes = [];
        post.dislikes = [];
        post.thumbs.forEach((thumb) => {
            let info = {
                name: thumb.name, 
                user_email: thumb.user_email,
            };
            if (thumb.rating === 1) {
                post.likes.push(info);
            } else if (thumb.rating === -1) {
                post.dislikes.push(info); 
            }
        });
        return post;
    };

    app.user_thumb_on_post = (post, rating) => {
        if(rating === 0) {
            return false;
        } else {
            let arr;
            if (rating === 1) {
                arr = post.likes;
            } else {
                arr = post.dislikes;
            }
            let index = arr.findIndex((user) => user.user_email === user_email);
            return index !== -1; 
        }
    };

    app.toggle_new_post = () => { 
        app.vue.new_post_showing = !app.vue.new_post_showing;
    };

    app.clear_new_post = () => { 
        app.vue.post_text = "";
        app.vue.post_teacher = "";
        app.vue.post_rating = "";
    };


    // Use this function to reindex the posts, when you get them, and when
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
        send_post: app.send_post, 
        send_thumb: app.send_thumb,
        delete_post: app.delete_post,
        // other methods
        toggle_new_post: app.toggle_new_post,
        toggle_hover_post: app.toggle_hover_post,
        clear_new_post: app.clear_new_post,
        user_thumb_on_post: app.user_thumb_on_post,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        app.get_posts();

    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
init(app);