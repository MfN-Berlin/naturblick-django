function initMiniAudioPlayer(id) {
    const audio = document.getElementById(id);
    const button = document.getElementById(`${id}-toggle`);
    const toggleStoppedTemplate = document.getElementById(`${id}-toggle-stopped`);
    const togglePlayingTemplate = document.getElementById(`${id}-toggle-playing`);
    let state; // 1 stopped, 2 loading, 3 playing

    function updateState(newState) {
        switch(newState) {
        case 1:
            button.replaceChildren(
                document.importNode(toggleStoppedTemplate.content, true)
            );
            break;
        case 2:
            break;
        case 3:
            button.replaceChildren(
                document.importNode(togglePlayingTemplate.content, true)
            );
            break;
        }
        state = newState;
    }

    // Start stopped
    updateState(1);

    button.addEventListener("click", (event) => {
        switch(state) {
        case 1:
            audio
                .play()
                .then((_) => updateState(3), (_) => updateState(1));
            updateState(2);
            break;
        case 2:
            break;
        case 3:
            audio.pause();
            updateState(1);
            break;
        }
    });
}
