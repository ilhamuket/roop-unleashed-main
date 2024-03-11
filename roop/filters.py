import numpy as np
import cv2

c64_palette = np.array([
    [0, 0, 0],
    [255, 255, 255],
    [0x81, 0x33, 0x38],
    [0x75, 0xce, 0xc8],
    [0x8e, 0x3c, 0x97],
    [0x56, 0xac, 0x4d],
    [0x2e, 0x2c, 0x9b],
    [0xed, 0xf1, 0x71],
    [0x8e, 0x50, 0x29],
    [0x55, 0x38, 0x00],
    [0xc4, 0x6c, 0x71],
    [0x4a, 0x4a, 0x4a],
    [0x7b, 0x7b, 0x7b],
    [0xa9, 0xff, 0x9f],
    [0x70, 0x6d, 0xeb],
    [0xb2, 0xb2, 0xb2]
])

def fast_quantize_to_palette(image):
    # Simply round the color values to the nearest color in the palette
    palette = c64_palette / 255.0  # Normalize palette
    img_normalized = image / 255.0  # Normalize image

    # Calculate the index in the palette that is closest to each pixel in the image
    indices = np.sqrt(((img_normalized[:, :, None, :] - palette[None, None, :, :]) ** 2).sum(axis=3)).argmin(axis=2)
    # Map the image to the palette colors
    mapped_image = palette[indices]

    return (mapped_image * 255).astype(np.uint8)  # Denormalize and return the image


'''
knn = None

def quantize_to_palette(image, palette):
    global knn

    NumColors = 16
    quantized_image = None
    cv2.pyrMeanShiftFiltering(image, NumColors / 4, NumColors / 2, quantized_image, 1, cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 5, 1)

    palette = c64_palette
    X_query = image.reshape(-1, 3).astype(np.float32)

    if(knn == None):
        X_index = palette.astype(np.float32)
        knn = cv2.ml.KNearest_create()
        knn.train(X_index, cv2.ml.ROW_SAMPLE, np.arange(len(palette)))
    
    ret, results, neighbours, dist = knn.findNearest(X_query, 1)

    quantized_image = np.array([palette[idx] for idx in neighbours.astype(int)])
    quantized_image = quantized_image.reshape(image.shape)
    return quantized_image.astype(np.uint8)
'''
