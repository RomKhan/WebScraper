import cv2
import numpy as np

# Загрузите изображение
image = cv2.imread('test.jpeg')

# Перевести изображение в формат HSV (Оттенок, Насыщенность, Яркость)
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Определите нижний и верхний диапазоны цветов для фона (в данном случае, белого цвета)
lower_white = np.array([0, 0, 200])
upper_white = np.array([255, 30, 255])

# Создайте маску на основе диапазонов цветов
mask = cv2.inRange(hsv_image, lower_white, upper_white)

# Найдите контуры в маске
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Используйте наибольший контур как область внутренней фотографии
if contours:
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Вырежьте внутреннюю фотографию
    inner_image = image[y:y+h, x:x+w]

    # Сохраните извлеченное изображение
    cv2.imwrite('внутренняя_фотография.jpg', inner_image)