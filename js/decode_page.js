function crypt_image (imgElement, key) {
    const divElement = document.createElement('div');
    divElement.id = imgElement.src;
    imgElement.replaceWith(divElement);

    const encoder = new TextEncoder();
    const byteKey = encoder.encode(key);

    fetch(imgElement.src)
      .then(response => response.arrayBuffer())
      .then(arrayBuffer => {
        const data = new Uint8Array(arrayBuffer);

        for (let i = 0; i < data.length; i++) {
          data[i] = data[i] ^ byteKey[i % byteKey.length];
        }

        const modifiedArrayBuffer = data.buffer;
        const modifiedBlob = new Blob([modifiedArrayBuffer], { type: 'image/png' });
        const modifiedURL = URL.createObjectURL(modifiedBlob);
        const imageElement = document.createElement('img');
        imageElement.src = modifiedURL;

        const imageContainer = document.getElementById(imgElement.src);
        imageContainer.appendChild(imageElement);
      })
      .catch(error => console.error(error));
}

var params = (new URL(document.location)).searchParams;
var key = params.get("key")

document.title = decrypt(document.title, key);
document.body.innerHTML = decrypt(document.body.innerHTML, key);

const imgElements = document.querySelectorAll('img');
imgElements.forEach((imgElement) => {
  crypt_image(imgElement, key)
});
