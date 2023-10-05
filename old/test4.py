import base64
from io import BytesIO
from PIL import Image

# Ваша строка данных Base64
base64_data = "data:image/png;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAASABgDASIAAhEBAxEB/8QAGAABAQEBAQAAAAAAAAAAAAAAAAYFBAj/xAApEAACAQQBAwIGAwAAAAAAAAABAgMABAURBhIhMRNBBwgiMkJxUWGC/8QAFwEAAwEAAAAAAAAAAAAAAAAAAQIDBP/EACIRAAIBAQgDAAAAAAAAAAAAAAABAhEEBRIhMTM0QWGBsf/aAAwDAQACEQMRAD8AubniAbBxZWKL0HkiWR4X7aJG9fumC5Zk8Hxt7BMbZJBeyLCks6qXLMDpR37k6OqiMp8wDXDR2mH4/LdW06toyShZH7e3lV/1us7jTPyHMWdrb2d3ZMQ10FvL31zHKgPSFRQB9rMSd/x2qXVRnFxeGWT8lollj4I2vs3e2dlFskLNdRxdevPdj4/QJpXFyLh8HJcBY8VyczpMyTRGZW10u52G6SD1686JGteaUY0a1C0zz1xdm62+o/iPP91sZa4nijkeKeWNgOzK5BHelKnZ9o33zzpeviKn4b5C/fLsXvrliIXIJlY6IBI9/YgGlKUrMJ//2Q=="

# Извлечение данных Base64 без префикса
base64_data = base64_data.split(',')[1]

# Декодирование Base64 в бинарные данные
binary_data = base64.b64decode(base64_data)

# Загрузка изображения в объект Pillow
image = Image.open(BytesIO(binary_data))

# Получение размеров изображения после обработки
width, height = image.size

# Вывод размеров
print(f"Ширина: {width}, Высота: {height}")