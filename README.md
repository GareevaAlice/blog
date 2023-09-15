Создаем директорию в `original_pages/` и сохраняем всю нужную информацию. Например `original_pages/example`.

Создаем зашифрованные страницы с помощью скрипта. Вписываем путь до директории без `original_pages/` и ключ, длиной 16. Если ключ не указан он генерируется рандомно.
```
pip install -r requirements.txt
python create_page.py --path example --key 1234567890123456
```

Полученные страницы сохраняются в `pages/`. Ссылки с ключами записываются в LINKS.txt.

```
http://localhost:63342/blog/pages/example/main.html?key=1234567890123456
https://gareevaalice.github.io/blog/pages/example/main.html?key=1234567890123456
```