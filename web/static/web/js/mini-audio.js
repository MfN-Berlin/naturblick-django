function initMiniAudioPlayer(id) {
    const audio = document.getElementById(id);
    const button = document.getElementById(`${id}-toggle`);
    const toggleStoppedTemplate = document.getElementById(`${id}-toggle-stopped`);
    const togglePlayingTemplate = document.getElementById(`${id}-toggle-playing`);

    audio.addEventListener("play", (_) => {
        button.replaceChildren(
            document.importNode(togglePlayingTemplate.content, true)
        );
    });

    audio.addEventListener("pause", (_) => {
        button.replaceChildren(
            document.importNode(toggleStoppedTemplate.content, true)
        );
    });

    // Start stopped
    button.replaceChildren(
        document.importNode(toggleStoppedTemplate.content, true)
    );

    button.addEventListener("click", (event) => {
        if(audio.paused) {
            audio.play();
        } else {
            audio.pause();
        }
    });
}
