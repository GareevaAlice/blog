var params = (new URL(document.location)).searchParams;
var key = params.get("key")

document.title = decrypt(document.title, key);
document.body.innerHTML = decrypt(document.body.innerHTML, key);
