function font_zoom_toggle() {
    const root = document.documentElement;
    const styles = getComputedStyle(root);
    const def = styles.getPropertyValue('--default-font-zoom').trim();
    const zoomed = styles.getPropertyValue('--zoomed-font-zoom').trim();
    const saved = localStorage.getItem('font-zoom');
    let next;
    if ((saved ?? def) === def) {
        next = zoomed
        root.style.setProperty('--zoomed-color', "#ccc");
        root.style.setProperty('--unzoomed-color', "inherit");
    } else {
        next = def
        root.style.setProperty('--font-zoom', next);
        root.style.setProperty('--zoomed-color', "inherit");
        root.style.setProperty('--unzoomed-color', "#ccc");
    }
    root.style.setProperty('--font-zoom', next);
    localStorage.setItem('font-zoom', next);
}