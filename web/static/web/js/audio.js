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
            if (!running) {
                return;
            }
            updateTime();
        }, 50)
    }
}

running = false;

function init_audio(audio) {
    const btn = document.getElementById('playBtn');
    const widther = document.getElementById('widther');
    const spec_cont = document.getElementById('spectrogram_container');
    const audio_start = document.getElementById('audio_start');
    const audio_end = document.getElementById('audio_end');

    audio.onpause = function() {
        running = false;
    }

    audio.addEventListener('timeupdate', () => {
        audio_start.innerHTML = formatTime(audio.currentTime);
    })

    audio.addEventListener("loadedmetadata", () => {
        audio_end.innerHTML = formatTime(audio.duration);
    });

    spec_cont.addEventListener('click', (event) => {
        const rect = spec_cont.getBoundingClientRect()

        const x = event.clientX - rect.left;
        new_value = Number((x / rect.width ) * audio.duration).toFixed(6);
        audio.currentTime = new_value;
        updateTime(true);
    })

    btn.addEventListener('click', () => {
      if (audio.paused == true) {
        audio.play();
        running = true;
        updateTime();
      } else {
        audio.pause();
        running = false;
      }
    });
}
