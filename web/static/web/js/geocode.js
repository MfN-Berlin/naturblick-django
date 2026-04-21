async function getLocation(lat, lng) {
    const MAP_BOX_KEY = window.MAP_BOX_KEY;
    const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?access_token=${MAP_BOX_KEY}`;

    const res = await fetch(url);
    const obj = await res.json();

    const place =
        obj.features.find(x => x.place_type.includes('locality')) ||
        obj.features.find(x => x.place_type.includes('place'));

    if (!place) {
        return `[ ${lat}, ${lng} ]`;
    }

    return place.text;
}