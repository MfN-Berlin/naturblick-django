function init_youtube(element_id, src_url) {
    const youtube = document.getElementById(element_id);
    youtube.addEventListener("click", (event) => {
        const iframe = document.createElement("iframe");
        iframe.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
        iframe.setAttribute("allowfullscreen", true);
        iframe.setAttribute("type", "text/html");
        iframe.setAttribute("frameborder", "0");
        iframe.setAttribute("src", src_url);
        youtube.replaceChildren(iframe);
    }, { once: true });
}
