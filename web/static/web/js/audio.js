function init_audio(id) {
    const audio = document.getElementById(`${id}-audio`);
    const btn = document.getElementById(`${id}-playBtn`);
    const widther = document.getElementById(`${id}-widther`);
    const spec_cont = document.getElementById(`${id}-spectrogram_container`);
    const audio_start = document.getElementById(`${id}-audio_start`);
    const audio_end = document.getElementById(`${id}-audio_end`);
    const playTemplate = document.getElementById(`${id}-play-template`);
    const pauseTemplate = document.getElementById(`${id}-pause-template`);
    function formatTime(seconds) {
        const total = Math.round(seconds);
        const m = Math.floor(total / 60);
        const s = total % 60;

        return String(m).padStart(2, "0") + ":" +
               String(s).padStart(2, "0");
    }

    function updateTime(once = false) {
        newWidth = Number(audio.currentTime / audio.duration * 100).toFixed(2);
        widther.style = `width: ${newWidth}%`
        if (!once) {
            setTimeout( () => {
                if (audio.paused) {
                    return;
                }
                updateTime();
            }, 50)
        }
    }

    btn.replaceChildren(
        document.importNode(playTemplate.content, true)
    );

    audio.addEventListener('pause', () => {
        btn.replaceChildren(
            document.importNode(playTemplate.content, true)
        );
    });

    audio.addEventListener('play', () => {
        btn.replaceChildren(
            document.importNode(pauseTemplate.content, true)
        );
    });
    
    audio.addEventListener('timeupdate', () => {
        audio_start.innerHTML = formatTime(audio.currentTime);
    });

    audio.addEventListener("loadedmetadata", () => {
        audio_end.innerHTML = formatTime(audio.duration);
    });

    spec_cont.addEventListener('click', (event) => {
        const rect = spec_cont.getBoundingClientRect()

        const x = event.clientX - rect.left;
        new_value = Number((x / rect.width ) * audio.duration).toFixed(6);
        audio.currentTime = new_value;
        updateTime(true);
    });

    btn.addEventListener('click', () => {
      if (audio.paused == true) {
        audio.play();
        updateTime();
      } else {
        audio.pause();
      }
    });
}
