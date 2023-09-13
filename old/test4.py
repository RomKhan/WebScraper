import cv2
import numpy as np

# Загрузите изображение
image = cv2.imread('test.jpeg')

# Перевести изображение в формат HSV
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Извлечь насыщенность (Saturation) из HSV изображения
saturation = np.mean(hsv_image, axis=0)

# Найдите точку, в которой насыщенность резко возрастает (например, первый пик)
threshold = 50  # Задайте порог насыщенности
separate_line = None
max_distance_saturation = 0
max_distance_brightness = 0

for row in [x for x in range(1, saturation.shape[0]) if x < saturation.shape[0] // 2 - 50 or x > saturation.shape[0] // 2 + 50]:
    if saturation[row, 1] > saturation[row-1, 1] and saturation[row, 1] - saturation[row-1, 1] >= 1.3 * max_distance_saturation\
            and saturation[row, 2] < saturation[row-1, 2] and saturation[row-1, 2] - saturation[row, 2] >= 1.3 * max_distance_brightness:
        separate_line = row
        max_distance_saturation = saturation[row, 1] - saturation[row-1, 1]
        max_distance_brightness = saturation[row - 1, 2] - saturation[row, 2]

if separate_line > saturation.shape[0] // 2:
    separate_line = saturation.shape[0] - separate_line
# Обрежьте изображение с учетом начальной строки, где насыщенность резко возрастает
if separate_line is not None:
    cropped_image = image[:, separate_line:-separate_line - 1]

    # Сохраните обрезанное изображение
    cv2.imwrite('обрезанное_изображение.jpg', cropped_image)
else:
    print("На изображении нет резкого возрастания насыщенности.")