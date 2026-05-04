function fontZoomToggle() {
    const root = document.documentElement;
    const styles = getComputedStyle(root);
    const def = styles.getPropertyValue('--default-font-zoom').trim();
    const zoomed = styles.getPropertyValue('--zoomed-font-zoom').trim();
    const saved = localStorage.getItem('font-zoom');
    let next;
    if ((saved ?? def) === def) {
        next = zoomed
    } else {
        next = def
    }
    root.style.setProperty('--font-zoom', next);
    localStorage.setItem('font-zoom', next);
    initFontZoom();
}

function initFontZoom() {
    const root = document.documentElement;
    const styles = getComputedStyle(root);
    const def = styles.getPropertyValue('--default-font-zoom').trim();
    const zoomed = styles.getPropertyValue('--zoomed-font-zoom').trim();
    const saved = localStorage.getItem('font-zoom');
    if ((saved ?? def) === def) {
        root.style.setProperty('--font-zoom', def);
        document.documentElement.style.setProperty('--zoomed-color', "inherit");
        document.documentElement.style.setProperty('--unzoomed-color', "#ccc");
    } else {
        root.style.setProperty('--font-zoom', zoomed);
        document.documentElement.style.setProperty('--zoomed-color', "#ccc");
        document.documentElement.style.setProperty('--unzoomed-color', "inherit");
    }
}

initFontZoom();