function clone(obj) {
    return JSON.parse(JSON.stringify(obj));
}
// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
//let meow_get_users_url = "http://127.0.0.1:8000/meow/get_users";
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        rows: [],
        get_users_url: "http://127.0.0.1:8000/meow/get_users",
        text: "",
        status: "unfollow",
        setFollowUrl: "http://127.0.0.1:8000/meow/set_follow",
        posts: [], // Store posts of other users
        get_post_url: "http://127.0.0.1:8000/meow/get_posts",
        addPostUrl: "http://127.0.0.1:8000/meow/add_post",
        publish_reply_url: "http://127.0.0.1:8000/meow/publish_reply",
        get_replies_url: "http://127.0.0.1:8000/meow/get_replies",
        get_current_user_url: "http://127.0.0.1:8000/meow/get_current_user",
        get_recent_posts_url: "http://127.0.0.1:8000/meow/get_recent_posts",
        bodyText: "",
        showReplyForm: false, // For reply view
        showRecentPost: false,
        replyPost: null,
        replyText: "",
        selectedPost: null,
        replies: [],
        recentPost: []
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => { e._idx = k++; });
        return a;
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        reloadUsers() {
            this.text = ""; //Clear the text when x clicked
            //window.location.reload(); //reloads users
        },

        reloadPage() {
            //this.text = ""; //Clear the text when x clicked
            window.location.reload(); //reloads users
        },

        setFollow(username, status) {
            axios.post(app.data.setFollowUrl, { username, status })
                .then(function (response) {
                    if (response.data === "ok") {
                        const user = app.vue.rows.find((row) => row.username === username);
                        if (user) {
                            user.status = status;
                            window.location.reload(); //reloads users
                        }
                    }

                })
                .catch(function (error) {
                    console.error(error);
                });


        },

        publishPost() {
            const content = this.bodyText;
            if (content) {
                axios.post(app.data.addPostUrl, { content })
                    .then((response) => {
                        const newPost = response.data;
                        newPost.timestamp = Sugar.Date(newPost.timestamp + "Z").relative() //change format of time
                        // Add the new post to the posts array
                        app.vue.posts.unshift(newPost);
                        // Clear the text area
                        this.bodyText = "";
                    })
                    .catch((error) => {
                        console.error(error);
                    });
            }
        },

        remeowPost(post) {
            this.showRecentPost = false;
            const remeowContent = `RT ${post.author}: ${post.content}`;
            axios.post(app.data.addPostUrl, { content: remeowContent })
                .then((response) => {
                    const newPost = response.data;
                    newPost.timestamp = Sugar.Date(newPost.timestamp + "Z").relative() //change format of time
                    // Add the new post to the posts array
                    app.vue.posts.unshift(newPost);
                })
                .catch((error) => {
                    console.error(error);
                });
        },

        replyToPost(post) {
            this.replyPost = post;
            this.replyText = "";
            this.selectedPost = post;
            this.replyPost.replies = [];
            this.showRecentPost = false;
            
            axios.get(app.data.get_replies_url, { params: { postId: post.id } })
                .then((response) => {
                    const retrievedReplies = response.data.replies || [];
                    console.log(response.data.replies);
                    retrievedReplies.forEach((reply) => {
                        reply.timestamp = Sugar.Date(reply.timestamp + "Z").relative();
                    });
                    if (!this.replyPost.replies) {
                        this.replyPost.replies = [];
                    }

                    this.replyPost.replies = app.enumerate(retrievedReplies);
                    
                    this.showReplyForm = true;

                    
                })
                .catch((error) => {
                    console.error(error);
                });
                console.log(this.showRecentPost)
        },

        publishReply() {
            const replyContent = this.replyText;
            const originalPost = this.replyPost;
            const storedReplyText = this.replyText;
            this.replyText = "";
            
            axios.post(app.data.publish_reply_url, { content: replyContent, postId: originalPost.id })
                .then((response) => {
                    const newReply = response.data;
                    console.log(newReply)
                    newReply.timestamp = Sugar.Date(newReply.timestamp + "Z").relative();

                    if (!originalPost.replies) {
                        app.vue.posts[originalPost._idx].replies = [];
                    }

                    app.vue.posts[originalPost._idx].replies.unshift(newReply);

                    app.vue.posts[originalPost._idx].num_replies += 1;

                    this.replyText = storedReplyText;
                    this.replyText = "";

                    this.showRecentPost = false;
                })
                .catch((error) => {
                    console.error(error);
                });
        },

        displayUserPosts(username) {
            this.text = username;
        },

        displayYourPosts() {
            this.showReplyForm = false;
            this.showRecentPost = false;
            axios.get(app.data.get_current_user_url)
                .then((response) => {
                    const username = response.data.username;
                    //console.log(username)
                    app.vue.text = username;

                })
                .catch((error) => {
                    console.error(error);
                });
        },

        displayRecentMeow() {
            this.showReplyForm = false;
            this.showRecentPost = true;
            axios.get(app.data.get_recent_posts_url)
                .then((response) => {
                    const recentPosts = response.data.posts || [];
                    //console.log(recentPosts);

                    // sort the posts by timestamp 
                    recentPosts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

                    recentPosts.forEach((reply) => {
                        reply.timestamp = Sugar.Date(reply.timestamp + "Z").relative();
                    });
                    app.vue.recentPost = recentPosts; // store recent posts in the recentPost array
                    //console.log(recentPosts);
                    
                })
                .catch((error) => {
                    console.error(error);
                });
                
        },
        

    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.get(app.data.get_users_url)
            .then(function (response) {
                //console.log(response.data.users);
                if (response.data.users) {
                    const users = response.data.users.map((user) => ({
                        ...user,
                        status: "unfollow", // default status for each user
                    }));

                    const followStatus = response.data.follow_status;
                    //console.log(followStatus)
                    followStatus.forEach((status) => {
                        const user = users.find((user) => user.username === status.username);
                        if (user) {
                            user.status = status.status;
                        }
                    });

                    // sort users based on follow status
                    users.sort((a, b) => {
                        if (a.status === "follow" && b.status === "unfollow") {
                            return -1;
                        } else if (a.status === "unfollow" && b.status === "follow") {
                            return 1;
                        } else {
                            return 0;
                        }
                    });

                    app.vue.rows = app.enumerate(users);
                }
            })
            .catch(function (error) {
                console.error(error);
            });

        axios.get(app.data.get_post_url)
            .then(function (response) {
                const posts = response.data.posts;

                const followStatus = response.data.follow_status;

                posts.sort((a, b) => {
                    // sort posts based on follow status
                    const aStatus = (followStatus.find(status => status.username === a.author) || { status: "unfollow" }).status;
                    const bStatus = (followStatus.find(status => status.username === b.author) || { status: "unfollow" }).status;
                    // console.log("a.author:", a.author);
                    // console.log("b.author:", b.author);
                    // console.log("followStatus:", followStatus);
                    if (aStatus === "follow" && bStatus === "unfollow") {
                        return -1;
                    } else if (aStatus === "unfollow" && bStatus === "follow") {
                        return 1;
                    } else {
                        return 0;
                    }
                });

                // change format of time
                posts.forEach(post => {
                    post.timestamp = Sugar.Date(post.timestamp + "Z").relative();
                });

                app.vue.posts = app.enumerate(posts)
            })
            .catch(function (error) {
                console.error(error);
            });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
