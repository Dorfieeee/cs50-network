// Initialize Popper tooltip list on window object
var tooltipList = [];

function displayPosts(posts) {
    const postsList = document.getElementById("postsList");
    const existingCards = postsList.children;
    const postsCards = posts.map((post) => PostCard(post));

    Array.from(existingCards).forEach((p) => p.remove());
    postsList.append(...postsCards);
}

async function getPosts(params = {}, url) {
    const URL = url || "/api/posts";
    const PARAMS = getQueryFrom(params);
    const SLASH = url ? "" : PARAMS ? "" : "/";
    const response = await fetch(URL + SLASH + PARAMS);

    if (!response.ok) {
        throw new Error("Something went wrong with getting posts");
    }

    const data = await response.json();

    return data;
}

async function editPost(id, text) {
    // PUT API call
    const response = await fetch("/api/posts/" + id + "/", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": Cookies.get("csrftoken"),
        },
        body: JSON.stringify(text),
    });

    if (!response.ok) {
        throw new Error("Something went wrong while editing");
    }

    const responseData = await response.json();

    return responseData;
}

async function deletePost(URL, postId) {
    const response = await fetch(URL, {
        method: "DELETE", // *GET, POST, PUT, DELETE, etc.
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": Cookies.get("csrftoken"),
        },
    });

    if (response.ok) {
        document.getElementById("post" + postId).remove();
    }
}

async function likePost(e, URL, postId) {
    e.preventDefault();

    // access post's like button
    let postCard = document.getElementById("post" + postId);
    let likeIconButton = postCard.querySelector("form button[data-like]");
    let likeCountEl = postCard.querySelector("small[data-like-count]");
    let likeTextEl = postCard.querySelector("small[data-like-count]+small");

    const reqMethod =
        likeIconButton.dataset.like === "true" ? "DELETE" : "POST";

    const response = await fetch(URL, {
        method: reqMethod, // *GET, POST, PUT, DELETE, etc.
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        headers: {
            "Content-Type": "application/json",
            "Content-Length": "0", // no body to be sent
            "X-CSRFToken": Cookies.get("csrftoken"),
        },
    });

    const responseData = await response.json(); // parses JSON response into native JavaScript objects

    if (response.ok) {
        // Get bool for post like = true => user likes it and vice versa
        // also get number of likes
        // Change data-like attribute value on post's like button
        // it also changes styling for that button
        likeIconButton.dataset.like = responseData.userLikesThis;
        likeCountEl.dataset.likeCount = responseData.numberOfLikes;
        likeCountEl.innerText = responseData.numberOfLikes;
        likeTextEl.innerText =
            responseData.numberOfLikes === 1 ? "like" : "likes";
    }
}

async function submitNewPost(e) {
    e.preventDefault();

    const postBody = document.getElementById("postBody");

    // silently abort
    if (postBody.value === "") return;

    const response = await fetch("/api/posts/", {
        method: "POST", // *GET, POST, PUT, DELETE, etc.
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": Cookies.get("csrftoken"),
        },
        body: JSON.stringify({
            postBody: postBody.value,
        }),
    });

    if (response.ok) {
        postBody.value = "";
        location.reload();
    }
}

function PostCard(post) {
    let card, row, avatarCol, avatar, contentCol;

    card = document.createElement("div");
    card.classList.add("card");
    card.id = `post${post.id}`;

    row = document.createElement("div");
    row.classList.add("row", "gx-0");

    avatarCol = document.createElement("div");
    avatarCol.classList.add("col-auto", "d-flex", "justify-content-center");
    avatarCol.style.width = "4em";

    avatar = document.createElement("i");
    avatar.classList.add("fas", "fa-user-circle", "fa-3x", "my-2");

    avatarCol.append(avatar);

    contentCol = document.createElement("div");
    contentCol.classList.add("col", "px-2");

    const header = PostHeader(post);
    const body = PostBody(post);
    const footer = PostFooter(post);

    contentCol.append(header, body, footer);

    row.append(avatarCol, contentCol);

    card.append(row);

    return card;
}

function PostHeader(post) {
    let wrapper, userLink, postDate, spacer, divider, optionsMenu;

    wrapper = document.createElement("div");
    wrapper.classList.add("py-1", "d-flex", "align-items-center");

    userLink = document.createElement("a");
    userLink.classList.add("link-dark", "fw-bold");
    userLink.href = post.profileURL;
    userLink.innerText = post.author.username;

    postDate = document.createElement("a");
    postDate.classList.add("link-dark", "text-muted");
    postDate.href = "#";
    postDate.dataset.bsToggle = "tooltip";
    postDate.dataset.bsHtml = "true";
    postDate.title = `<b>${post.created.long}</b>`;
    postDate.innerText = post.created.short;

    window.tooltipList.push(new bootstrap.Tooltip(postDate));

    divider = document.createElement("span");
    divider.classList.add("card-title-divider", "text-muted");

    spacer = document.createElement("span");
    spacer.classList.add("spacer");

    wrapper.append(userLink, divider, postDate, spacer);

    if (post.userIsAuthor) {
        let toggleBtn,
            toggleBtnIcon,
            optionsList,
            editItem,
            deleteItem,
            editLink,
            deleteLink;

        const deleteListener = () => deletePost(post.postURL, post.id);
        const editListener = () => displayEditForm(post.id);

        optionsMenu = document.createElement("span");
        optionsMenu.classList.add("dropdown");

        toggleBtn = document.createElement("button");
        toggleBtn.classList.add("btn", "btn-sm");
        toggleBtn.id = `postOptionsMenu${post.id}`;
        toggleBtn.dataset.bsToggle = "dropdown";
        toggleBtn.setAttribute("aria-expanded", false);

        toggleBtnIcon = document.createElement("i");
        toggleBtnIcon.classList.add("fas", "fa-ellipsis-h");

        toggleBtn.append(toggleBtnIcon);

        optionsList = document.createElement("ul");
        optionsList.classList.add("dropdown-menu");
        optionsList.setAttribute(
            "aria-labelledby",
            `postOptionsMenu${post.id}`
        );

        editItem = document.createElement("li");
        editLink = document.createElement("a");
        editLink.classList.add("dropdown-item");
        editLink.href = "#";
        editLink.onclick = editListener;
        editLink.innerText = "Edit";
        editItem.append(editLink);

        deleteItem = document.createElement("li");
        deleteLink = document.createElement("a");
        deleteLink.classList.add("dropdown-item", "text-danger");
        deleteLink.href = "#";
        deleteLink.onclick = deleteListener;
        deleteLink.innerText = "Delete";
        deleteItem.append(deleteLink);

        optionsList.append(editItem, deleteItem);
        optionsMenu.append(toggleBtn, optionsList);

        wrapper.append(optionsMenu);
    }

    return wrapper;
}

function PostBody(post) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("py-1");
    wrapper.dataset.bodyText = post.body;

    const body = document.createElement("p");
    body.classList.add("card-text");
    body.innerText = post.body;

    wrapper.append(body);

    return wrapper;
}

function PostFooter(post) {
    const form = document.createElement("form");
    const input = document.createElement("input");

    const listener = (e) => likePost(e, post.likeURL, post.id);

    form.classList.add("py-1");
    form.onsubmit = listener;

    input.type = "submit";
    input.hidden = true;

    const likeBtn = LikeButton(listener, post.userIsAuthor, post.userLikesThis);
    const likeInfo = NumberOfLikes(post.numberOfLikes);

    form.append(likeBtn, input, likeInfo);

    return form;
}

function LikeButton(listener, isAuthor, isLike) {
    const btn = document.createElement("button");

    btn.classList.add("btn", "btn-sm", "rounded-circle", "text-danger");
    btn.dataset.like = isLike;
    btn.disabled = isAuthor;
    btn.onclick = !isAuthor && listener;

    return btn;
}

function NumberOfLikes(n) {
    let wrapper = document.createElement("span");
    let word = document.createElement("small");
    let number = document.createElement("small");

    wrapper.classList.add("card-text", "me-2");
    word.classList.add("text-muted", "ms-1");
    number.classList.add("text-muted");

    number.dataset.likeCount = n;

    word.innerText = "like" + (n !== 1 ? "s" : "");
    number.innerText = n;

    wrapper.append(number, word);

    return wrapper;
}

function displayEditForm(id) {
    const postBody = document.querySelector(
        "#post" + id + " " + "[data-body-text]"
    );

    let isOpened = !postBody;

    if (isOpened) return;

    let initialValue = postBody.dataset.bodyText,
        form,
        formId = "editForm" + id,
        textarea,
        textareaId = "editFormInput" + id,
        textareaValue = initialValue,
        input,
        cancelBtn,
        confirmBtn,
        label;

    const confirmHandler = async () => {
        let currValue = textareaValue.trim();
        if (currValue !== initialValue && currValue)
            await editPost(id, currValue);
        closeForm(currValue);
    };
    const cancelHandler = () => {
        closeForm(initialValue);
    };
    const onChangeHandler = (e) => {
        textareaValue = e.target.value;
    };
    const closeForm = (textValue) => {
        form.removeEventListener("submit", confirmHandler);
        confirmBtn.removeEventListener("click", confirmHandler);
        cancelBtn.removeEventListener("click", cancelHandler);
        textarea.removeEventListener("keyup", onChangeHandler);

        isOpened = false;

        document
            .getElementById(formId)
            .replaceWith(PostBody({ body: textValue }));
    };

    form = document.createElement("form");
    form.id = formId;
    form.addEventListener("submit", confirmHandler);

    label = document.createElement("label");
    label.htmlFor = textareaId;
    label.classList.add("form-label");
    label.hidden = true;
    label.innerText = "Edit post";

    textarea = document.createElement("textarea");
    textarea.id = textareaId;
    textarea.classList.add("form-control");
    textarea.cols = 3;
    textarea.value = initialValue;
    textarea.addEventListener("keyup", onChangeHandler);

    input = document.createElement("input");
    input.type = "submit";
    input.hidden = true;

    cancelBtn = document.createElement("input");
    cancelBtn.type = "button";
    cancelBtn.name = "Discard";
    cancelBtn.value = "Discard";
    cancelBtn.classList.add("btn", "btn-sm", "btn-danger", "me-1", "my-1");
    cancelBtn.addEventListener("click", cancelHandler);

    confirmBtn = document.createElement("input");
    confirmBtn.type = "button";
    confirmBtn.name = "Confirm";
    confirmBtn.value = "Confirm";
    confirmBtn.classList.add("btn", "btn-sm", "btn-primary", "me-1", "my-1");
    confirmBtn.addEventListener("click", confirmHandler);

    form.append(label, textarea, input, confirmBtn, cancelBtn);

    postBody.replaceWith(form);
}

function useState(initialValue) {
    let state = initialValue;

    const getState = () => state;

    const setState = (nextState) => (state = nextState);

    return [getState, setState];
}

function getQueryFrom(params = {}) {
    let q = "",
        c = 0;
    if (!Object.entries(params).length) return q;
    q = "?";
    for (const [key, value] of Object.entries(params)) {
        q += c++ > 0 ? "&" : "";
        q += key;
        q += "=";
        q += value;
    }
    return q;
}

function displayPagination(curr, total, prev, next, setCurrPage) {
    let nav,
        ul,
        item,
        midItem = "",
        prevItem = "",
        nextItem = "",
        currPage = curr(),
        pag = document.getElementById("postsPagination");

    const nextListener = async (e) => {
        e.preventDefault();
        e.target.removeEventListener("click", nextListener);
        setCurrPage(currPage + 1);
        await loadPosts(curr, setCurrPage, {}, next);
    };

    const prevListener = async (e) => {
        e.preventDefault();
        e.target.removeEventListener("click", prevListener);
        setCurrPage(currPage - 1);
        await loadPosts(curr, setCurrPage, {}, prev);
    };

    item = (text, listener) => {
        let li = document.createElement("li");
        li.classList.add("page-item");
        listener && li.addEventListener("click", listener);

        let a = document.createElement("a");
        a.classList.add("page-link");
        a.href = "#";
        a.textContent = text || "";

        li.append(a);
        return li;
    };

    nav = document.createElement("nav");
    nav.setAttribute("aria-label", "Posts navigation");

    ul = document.createElement("ul");
    ul.classList.add("pagination", "justify-content-center");
    ul.id = "postsPagination";

    if (prev !== undefined) {
        prevItem = item("Previous", prevListener);
    }

    midItem = item(`${currPage} of ${total}`, (e) => e.preventDefault());

    if (next !== undefined) {
        nextItem = item("Next", nextListener);
    }

    ul.append(prevItem, midItem, nextItem);

    if (!pag) {
        nav.append(ul);
        document.querySelector("#postsList").parentElement.append(nav);
    } else {
        pag.replaceWith(ul);
    }
}

async function loadPosts(currPage, setCurrPage, params, url) {
    const data = await getPosts(params, url);
    const { posts, pageCount, nextPage, prevPage } = data;

    displayPosts(posts);
    displayPagination(currPage, pageCount, prevPage, nextPage, setCurrPage);
}

async function followUser(e) {
    let action = e.target.dataset.action;
    let username = e.target.dataset.username;
    console.log(action, username);
    let method = action === "follow" ? "POST" : action === "unfollow" ? "DELETE" : "";
    if (!method || !username) return;

    let response = await fetch("/api/followers/" + username + "/", {
        method: method,
        cache: "no-cache",
        headers: {
            "Content-Type": "application/json",
            "Content-Length": "0", // no body to be sent
            "X-CSRFToken": Cookies.get("csrftoken"),
        },
    })

    if (response.ok) {
        location.reload();
    }
}