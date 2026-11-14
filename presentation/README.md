# Презентация и демонстрационные материалы

| Путь | Что это |
|---|---|
| `КлассОнлайн_презентация.pptx` | готовая презентация, 13 слайдов, 16:9 |
| `screenshots/start.png` | экран «Главное меню» |
| `screenshots/form.png` | экран «Заполнение заявки» |
| `screenshots/success.png` | экран «Заявка принята» |
| `screenshots/admin.png` | экран «Статистика администратора» |
| `demo/telegram_mock.html` | HTML-макет телефона, из которого сделаны экраны |
| `preview/СлайдN.PNG` | экспорт слайдов для проверки вёрстки |

## Сборка презентации

```bash
pip install -r requirements-tools.txt
python tools/build_presentation.py
```

Файл перезаписывается по пути `presentation/КлассОнлайн_презентация.pptx`.

## Сборка экранов

Экраны сделаны из HTML-макета в стиле Telegram. Макет открывается в браузере с параметром `?screen=`:

```text
presentation/demo/telegram_mock.html?screen=start
presentation/demo/telegram_mock.html?screen=form
presentation/demo/telegram_mock.html?screen=success
presentation/demo/telegram_mock.html?screen=admin
```

Для скриншотов использовался headless Chrome:

```powershell
chrome --headless=new --disable-gpu --hide-scrollbars `
  --default-background-color=00000000 --force-device-scale-factor=2 `
  --window-size=720,1560 --screenshot=start.png `
  "http://127.0.0.1:8765/presentation/demo/telegram_mock.html?screen=start"
```

Диалог в макете соответствует текстам и сценарию бота, данные взяты из `data/demo.db`.

## Экспорт слайдов в PNG

В Windows с установленным PowerPoint:

```powershell
$ppt = New-Object -ComObject PowerPoint.Application
$deck = $ppt.Presentations.Open((Resolve-Path "presentation\КлассОнлайн_презентация.pptx").Path, $true, $false, $false)
$deck.Export((Join-Path (Resolve-Path "presentation").Path "preview"), "PNG", 1600, 900)
$deck.Close()
$ppt.Quit()
```

В LibreOffice:

```bash
soffice --headless --convert-to pdf presentation/КлассОнлайн_презентация.pptx
```

## Текст защиты

Речь по слайдам и ответы на возможные вопросы — в [`docs/PRESENTATION.md`](../docs/PRESENTATION.md).
