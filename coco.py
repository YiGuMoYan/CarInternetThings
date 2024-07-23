import os
import time
import cv2
import numpy as np
import tritonclient.http as httpclient
import yaml
from PIL import ImageDraw, ImageFont, Image

with open("config.yaml", "r") as f:
    yaml_config = yaml.safe_load(f)

server_url = yaml_config["coco"]["server_url"]
input_name = yaml_config["coco"]["input_name"]
model_name = yaml_config["coco"]["model_name"]

triton_client = httpclient.InferenceServerClient(url=server_url)


def process_frame(frame):
    frame_resized = cv2.resize(frame, (512, 512))
    frame_normalized = frame_resized.astype(np.float32) / 255.0
    frame_transposed = np.transpose(frame_normalized, [2, 0, 1])
    frame_batched = np.expand_dims(frame_transposed, axis=0)
    return frame_batched


def _get_coco_label():
    return ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
            'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
            'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
            'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
            'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
            'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
            'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
            'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']


def _get_keywords():
    return ['person', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']


def post_process_image(frame, results, labels):
    output0 = results.as_numpy('boxes')
    output1 = results.as_numpy('labels')

    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    img = ImageDraw.Draw(image)
    x_size, y_size = image.size
    boxes = output0
    classes = output1

    for idx, label_class in enumerate(classes):
        box = boxes[idx]
        score = box[4]
        if score < 0.3:
            continue
        shape = [box[0] / 512 * x_size, box[1] / 512 * y_size, box[2] / 512 * x_size, box[3] / 512 * y_size]
        img.rectangle(shape, outline="red")
        label = labels[int(label_class)]
        show_txt = f"{label}:{score:.2f}"
        img.text((box[0] / 512 * x_size, box[1] / 512 * y_size), show_txt, fill=(0, 255, 0, 255))

    # 将 PIL 图像转换回 OpenCV 格式
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return frame


def real_time_inference(frame):
    request_images = process_frame(frame)
    inputs = [httpclient.InferInput(input_name, request_images.shape, "FP32")]
    inputs[0].set_data_from_numpy(request_images, binary_data=False)
    outputs = [
        httpclient.InferRequestedOutput("boxes", binary_data=False),
        httpclient.InferRequestedOutput("labels", binary_data=False)
    ]
    results = triton_client.infer(model_name, inputs=inputs, outputs=outputs)

    label_list = [output['name'] for output in results.get_output()]
    frame = post_process_image(frame, results, _get_coco_label())
    is_person = len([item for item in label_list if item in _get_keywords()]) > 0
