https://github.com/user-attachments/assets/6900ae77-6dd2-4d47-8ac7-bf090f33ad92

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.ru.md"><strong>Русский</strong></a> ·
  <a href="README.zh-CN.md">简体中文</a>
</p>

# 💜 Ame-chan для CanvasTTY

<p align="center">
  <strong>Анимированный пиксельный компаньон на вашем канвасе.</strong><br>
  ✨ 19 действий · 🎲 Случайная последовательность · 🪟 Windows · 🐧 Linux · 🍎 macOS<br>
  <a href="https://github.com/CLOSETTTY/canvastty-plugin-ame-chan/releases/latest">Последний релиз</a> ·
  <a href="INSTALL.md">Установка через AI-агента</a> ·
  <a href="NOTICE.md">Происхождение изображений</a>
</p>

Анимированный пиксельный персонаж для канваса [CanvasTTY](https://github.com/howdeploy/CanvasTTY). Аме-чан дышит, моргает, танцует, смотрит в телефон, делает селфи, слушает музыку и многое другое.

<p align="center">
  <img src="assets/preview.webp" width="300" alt="Анимированная Аме-чан на прозрачном фоне">
</p>

## ✨ Главное

| Параметр | Описание |
| --- | --- |
| Тип | Приложение на канвасе CanvasTTY |
| Версия | 1.0.2 |
| Анимация | 19 действий на выбор и режим **Всё подряд** |
| Разрешения | Не требуются |
| Платформа | CanvasTTY на Windows, Linux и macOS для Apple Silicon; патч прозрачной карточки для каждой системы |

В ожидании Аме-чан дышит, а действия воспроизводятся покадрово. Прозрачный фон позволяет разместить персонажа прямо на канвасе. Выберите одно действие для повтора или режим **Всё подряд** для случайной последовательности. Названия действий в меню — на русском.

## 🛠️ Технологии

| Часть | Технологии |
| --- | --- |
| Плагин | HTML, CSS, обычный JavaScript и Canvas 2D API |
| Анимация | Спрайт-листы WebP; кадры и тайминги заданы в JavaScript |
| Патч прозрачной карточки | CSS; PowerShell и Batch на Windows, Python 3 на Linux и macOS |

Это статическое приложение на канвасе CanvasTTY. Для плагина не нужны фреймворк, сборка или дополнительные разрешения.

## 🚀 Установка

Плагин устанавливается по ссылке на этот публичный репозиторий. CanvasTTY не устанавливает плагины по ссылкам на приватные репозитории.

1. Откройте **CanvasTTY → Settings → Plugins**.
2. Вставьте https://github.com/CLOSETTTY/canvastty-plugin-ame-chan и нажмите **Inspect**.
3. Проверьте манифест и разрешения, затем подтвердите **Install**.
4. Нажмите **Open** на карточке Ame-chan.

Действие выбирается в меню у правого верхнего края персонажа. Карточку можно перемещать и менять её размер на канвасе.

**Устанавливаете через Codex?** Отправьте ссылку на публичный репозиторий и попросите: «Установи Аме-чан в CanvasTTY и примени патч прозрачной карточки для моей ОС по INSTALL.md». Агенту нужен доступ к локальной установке CanvasTTY.

## 🫧 Прозрачная карточка

Анимация использует браузерные API CanvasTTY на Windows, Linux и macOS. У самого плагина прозрачный фон. CanvasTTY по умолчанию рисует вокруг любого плагина непрозрачную карточку, поэтому для вида как на скриншоте требуется локальный патч стилей CanvasTTY. Карточка, перемещение, изменение размера и кнопки при наведении остаются. Патч затрагивает только Аме-чан.

Перед применением патча закройте CanvasTTY. Без патча плагин тоже работает, но карточка будет со стандартным фоном и заголовком CanvasTTY.

### 🪟 Windows

1. Скачайте репозиторий как ZIP и распакуйте его.
2. Запустите `frameless\install-frameless.cmd`.
3. Снова откройте Ame-chan. Наведите указатель на персонажа, чтобы увидеть элементы управления.

Чтобы вернуть стандартную карточку, запустите `frameless\uninstall-frameless.cmd`. Для другой папки установки передайте каталог `resources` скрипту `frameless.ps1` через параметр `-Resources`.

### 🐧 Linux (.deb)

Скачайте и распакуйте репозиторий, затем из его корня выполните:

```sh
sudo python3 frameless/linux-transparent-card.py apply
```

Если CanvasTTY установлен в нестандартное место, добавьте `--resources /путь/к/CanvasTTY/resources`. Перезапустите CanvasTTY и откройте Аме-чан. Для возврата стандартной карточки закройте CanvasTTY и выполните `sudo python3 frameless/linux-transparent-card.py restore` с тем же аргументом `--resources`, если он использовался при установке.

### 🐧 Linux (AppImage)

Сохраните исходный AppImage. Из корня репозитория выполните:

```sh
python3 frameless/linux-transparent-card.py apply --appimage /path/to/CanvasTTY.AppImage
~/.local/bin/canvastty-ame-chan
```

Первая команда создаёт отдельную копию CanvasTTY с патчем в `~/.local/share/canvastty-ame-chan/`, вторая запускает её. Для прозрачной карточки запускайте CanvasTTY через этот ярлык. Для возврата к исходному AppImage выполните `python3 frameless/linux-transparent-card.py restore --appimage /path/to/CanvasTTY.AppImage` и запустите исходный AppImage.

### 🍎 macOS (Apple Silicon)

Сохраните исходный `CanvasTTY.app` и закройте его перед применением патча. Из корня репозитория выполните:

```sh
python3 frameless/mac-transparent-card.py apply --app /Applications/CanvasTTY.app
open "$HOME/Applications/CanvasTTY Ame-chan.app"
```

Скрипт создаёт копию CanvasTTY в `~/Applications`, применяет то же оформление Аме-чан, подписывает копию локальной ad-hoc подписью и проверяет её. Если CanvasTTY находится в другом месте, измените путь после `--app`. Для прозрачной карточки запускайте эту копию. Для возврата к исходному приложению закройте CanvasTTY, выполните `python3 frameless/mac-transparent-card.py restore` и запустите исходный `CanvasTTY.app`.

Патчи сохраняют `app.asar` как `app.asar.bak` в изменённой установке. После обновления CanvasTTY примените их снова. Файлы спрайтов плагина они не меняют. Плагин проверен в Chromium на Ubuntu; внешний вид в запущенном CanvasTTY на Linux и macOS пока не проверен на физических компьютерах.

## 🗂️ Структура репозитория

| Путь | Содержимое |
| --- | --- |
| canvastty.plugin.json, index.html | Манифест и стартовая страница плагина |
| ame.js, ame-frames.js, ame-*.webp | Проигрыватель анимации, тайминг и спрайты |
| assets/preview.webp | Анимированное превью персонажа |
| frameless/ | CSS и скрипты применения и отката прозрачной карточки для Windows, Linux и macOS |
| README.md, README.zh-CN.md | Английская и китайская версии руководства |
| [INSTALL.md](INSTALL.md) | Полная задача установки для Codex или другого локального агента |
| [NOTICE.md](NOTICE.md), [SECURITY.md](SECURITY.md) | Происхождение изображений, лицензия и сообщения об уязвимостях |
| tests/, .github/workflows/ | Проверки платформ и автоматическая валидация |

Это неофициальный фанатский проект. Аме-чан — персонаж игры *NEEDY STREAMER OVERLOAD*. Репозиторий не связан с создателями игры.

## 📜 Лицензия и безопасность

Оригинальный код и документация доступны по [лицензии MIT](LICENSE). Изображения персонажа и промоматериалы исключены; см. [права и область действия лицензии](NOTICE.md). Инструкции по сообщениям об уязвимостях находятся в [Security policy](SECURITY.md).
