#!/usr/bin/env python
# coding: utf-8

# # Misty Object Detection Websocket server
# This script needs to be run from the tensorflow object_detection library folder.
# For information on setting up the object_detection library visit
# https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md

# # Imports
import collections
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import base64
import re
from io import BytesIO
import asyncio
import websockets
import json

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
from object_detection.utils import ops as utils_ops

if StrictVersion(tf.__version__) < StrictVersion('1.12.0'):
  raise ImportError('Please upgrade your TensorFlow installation to v1.12.*.')


# ## Env setup

# ## Object detection imports
# Here are the imports from the object detection module.

from utils import label_map_util

from utils import visualization_utils as vis_util


# # Model preparation 

# ## Variables
# 
# Any model exported using the `export_inference_graph.py` tool can be loaded here simply by changing `PATH_TO_FROZEN_GRAPH` to point to a new .pb file.  
# 
# By default we use an "SSD with Mobilenet" model here. See the [detection model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) for a list of other models that can be run out-of-the-box with varying speeds and accuracies.

# What model to download.
MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')

SCREEN_CENTER_X = 320
SCRREN_CENTER_Y = 240

# ## Download Model
opener = urllib.request.URLopener()
opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
tar_file = tarfile.open(MODEL_FILE)
for file in tar_file.getmembers():
  file_name = os.path.basename(file.name)
  if 'frozen_inference_graph.pb' in file_name:
    tar_file.extract(file, os.getcwd())


# ## Load a (frozen) Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')


# ## Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)


# ## Helper code
def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


# # Detection

# use this when loading saved images
PATH_TO_TEST_IMAGES_DIR = 'test_images'
TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 3) ]

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)


def run_inference_for_single_image(image, graph):
  with graph.as_default():
    with tf.Session() as sess:
      # Get handles to input and output tensors
      ops = tf.get_default_graph().get_operations()
      all_tensor_names = {output.name for op in ops for output in op.outputs}
      tensor_dict = {}
      for key in [
          'num_detections', 'detection_boxes', 'detection_scores',
          'detection_classes', 'detection_masks'
      ]:
        tensor_name = key + ':0'
        if tensor_name in all_tensor_names:
          tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
              tensor_name)
      if 'detection_masks' in tensor_dict:
        # The following processing is only for single image
        detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
        detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
        # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
        real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
        detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
        detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            detection_masks, detection_boxes, image.shape[1], image.shape[2])
        detection_masks_reframed = tf.cast(
            tf.greater(detection_masks_reframed, 0.5), tf.uint8)
        # Follow the convention by adding back the batch dimension
        tensor_dict['detection_masks'] = tf.expand_dims(
            detection_masks_reframed, 0)
      image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

      # Run inference
      output_dict = sess.run(tensor_dict,
                             feed_dict={image_tensor: image})

      # all outputs are float32 numpy arrays, so convert types as appropriate
      output_dict['num_detections'] = int(output_dict['num_detections'][0])
      output_dict['detection_classes'] = output_dict[
          'detection_classes'][0].astype(np.int64)
      output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
      output_dict['detection_scores'] = output_dict['detection_scores'][0]
      if 'detection_masks' in output_dict:
        output_dict['detection_masks'] = output_dict['detection_masks'][0]
  return output_dict

def pure_pil_alpha_to_color(image, color=(255, 255, 255)):
    """Alpha composite an RGBA Image with a specified color.

    Source: http://stackoverflow.com/a/9459208/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """
    image.load()  # needed for split()
    background = Image.new('RGB', image.size, color)
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
    return background

def get_bounding_box_depth_data(output_dict, image_depth_data, image_width, image_height):
  # matches the detection threshold used
  # in visualize_boxes_and_labels_on_image_array
  detection_score_threshold = 0.5
  # each bounding_box_depth_data value will be the corresponding
  # depth data for a given detection box
  bounding_box_depth_data = []
  # each object detection box is an array whose values are in the form
  # (top-left-x, top-left-y, bottom-right-x, bottom-right-y)
  # each value is a range from 0 to 1
  # e.g. top-left-x = 0.5, image_width = 300px => pixel value is 150px
  detection_boxes = output_dict['detection_boxes']
  detection_scores = output_dict['detection_scores']
  for i in range(0, len(detection_boxes)):
    if detection_scores[i] <= detection_score_threshold:
      i = len(detection_boxes)
      break
    bounding_box_depth_data.append([])
    detection_box = detection_boxes[i]
    top_left_x = int(detection_box[0] * image_width)
    top_left_y = int(detection_box[1] * image_height)
    bottom_right_x = int(detection_box[2] * image_width)
    bottom_right_y = int(detection_box[3] * image_height)
    for y in range(top_left_y, bottom_right_y):
      for x in range(top_left_x, bottom_right_x):
        depth_value_index = (0 - x) + (y * image_width)
        if depth_value_index >= 0 and depth_value_index < len(image_depth_data):
          # these dicts are formatted to match the object schema used
          # to render the d3.js heatmap in Logging/src/views/takeDepthPicture.vue
          value = image_depth_data[depth_value_index]
          bounding_box_depth_data[i].append({
            x: x,
            y: y,
            value: value
          })
  
  return bounding_box_depth_data


def get_bounding_box_centroid_depth_data(output_dict, image_depth_data, image_width, image_height):
  # this threshold is set to match the threshold that
  # visualize_boxes_and_labels_on_image_array uses
  detection_score_threshold = 0.5
  bounding_box_centroid_depth_data = []
  detection_boxes = output_dict['detection_boxes']
  detection_scores = output_dict['detection_scores']
  for i in range(0, len(detection_boxes)):
    if detection_scores[i] <= detection_score_threshold:
      i = len(detection_boxes)
      break
    # set the centroid_depth to NaN by default because
    # we aren't sure whether the centroid will be within the bounds
    # of our depth data
    centroid_depth = "NaN"
    detection_box = detection_boxes[i]
    top_left_y = int(detection_box[0] * image_height)
    top_left_x = int(detection_box[1] * image_width)
    bottom_right_y = int(detection_box[2] * image_height)
    bottom_right_x = int(detection_box[3] * image_width)
    offset_direction = 0
    offset_magnitude = -1
    while centroid_depth == "NaN":
      centroid_x = (bottom_right_x - top_left_x) / 2
      centroid_y = (bottom_right_y - top_left_y) / 2
      offset_direction += 1
      offset_magnitude += 1
      if offset_direction > 4:
        offset_direction = 1
      if offset_direction == 1:
        # top
        centroid_y += offset_magnitude
      if offset_direction == 2:
        # right
        centroid_x += offset_magnitude
      if offset_direction == 3:
        # bottom
        centroid_y -= offset_magnitude
      if offset_direction == 4:
        # left
        centroid_x -= offset_magnitude
      centroid_index = (0 - centroid_x) + (centroid_y * image_width)
      # the centroid is outside the depth data
      if centroid_index >= 0 and centroid_index < len(image_depth_data):
        centroid_depth = -1
      else:
        centroid_depth = image_depth_data[centroid_index]
    bounding_box_centroid_depth_data.append(centroid_depth)

  return bounding_box_centroid_depth_data

def get_turn_direction(detection_box):
  turn_direction = "none"

  top_left_x = detection_box[1]
  bottom_right_x = detection_box[3]
  x_center = top_left_x + ((bottom_right_x - top_left_x) / 2)

  if x_center < 0.45:
    turn_direction = "left"
  if x_center > 0.55:
    turn_direction = "right"
  
  print('turn_direction : ')
  print(turn_direction)
  return turn_direction

def get_turn_speed(detection_box):
  turn_speed = 0

  top_left_x = detection_box[1]
  bottom_right_x = detection_box[3]
  x_center = top_left_x + ((bottom_right_x - top_left_x) / 2)

  if x_center < 0.1 or x_center > 0.9:
    turn_speed = 25
  if x_center < 0.2 or x_center > 0.8:
    turn_speed = 20
  if x_center < 0.3 or x_center > 0.7:
    turn_speed = 15
  else:
    turn_speed = 10
  
  print('turn_speed : ')
  print(turn_speed)
  return turn_speed


# parses a base64 image to a pil image
# then runs object detection on that image
# if it is a fisheye image derive turn direction and speed
async def process_image(websocket, message):
  parsed_message = json.loads(message)
  image_base_64 = parsed_message['image']
  image_height = parsed_message['image_height']
  image_width = parsed_message['image_width']
  image_depth_data = parsed_message['image_depth_data']
  is_fisheye_image = parsed_message['is_fisheye_image']
  get_depth_data = parsed_message['get_depth_data']

  # debugger
  # import pdb; pdb.set_trace()

  img = Image.open(BytesIO(base64.b64decode(image_base_64)))
  if is_fisheye_image:
    # remove the alpha channel, fisheye images are in rgba
    # and tensorflow just can't deal with that
    img = pure_pil_alpha_to_color(img)
  
  # the array based representation of the image will be used later in order to prepare the
  # result image with boxes and labels on it.
  image_np = load_image_into_numpy_array(img)
  # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
  image_np_expanded = np.expand_dims(image_np, axis=0)
  # Actual detection.
  output_dict = run_inference_for_single_image(image_np_expanded, detection_graph)
  # Visualization of the results of a detection.
  vis_util.visualize_boxes_and_labels_on_image_array(
      image_np,
      output_dict['detection_boxes'],
      output_dict['detection_classes'],
      output_dict['detection_scores'],
      category_index,
      instance_masks=output_dict.get('detection_masks'),
      use_normalized_coordinates=True,
      line_thickness=8)
  pil_img = Image.fromarray(image_np)
  buff = BytesIO()
  pil_img.save(buff, format="JPEG")
  processed_image_base_64 = base64.b64encode(buff.getvalue()).decode("utf-8")

  has_detections = len(output_dict['detection_boxes']) > 0
  turn_direction = None
  detection_boxes = output_dict['detection_boxes']
  turn_speed = 0
  if is_fisheye_image and has_detections:
    # get a turn direction based off of the detection box
    # with the greatest area
    largest_detection_box_index = 0
    largest_detection_box_value = 0
    for i in range(0, len(detection_boxes)):
      cur_box = detection_boxes[i]
      # box size = (top_left_x - bottom_right_x) * (top_left_y - bottom_right_y)
      cur_box_size = (cur_box[3] - cur_box[1]) * (cur_box[2] - cur_box[0])
      is_past_score_threshold = output_dict['detection_scores'][i] >= 0.5
      is_largest_box = cur_box_size > largest_detection_box_value
      # category index 1 correspods to a 'person' detection
      is_person = output_dict['detection_classes'][i] == 1
      if is_past_score_threshold and is_largest_box and is_person:
        largest_detection_box_value = cur_box_size
        largest_detection_box_index = i
    
    largest_detection_box = output_dict['detection_boxes'][largest_detection_box_index]
    turn_direction = get_turn_direction(largest_detetion_box)
    turn_speed = get_turn_speed(largest_detection_box)

  return_data = {}
  return_data['processed_image'] = processed_image_base_64
  return_data['turn_direction'] = turn_direction
  return_data['turn_speed'] = turn_speed
  print("image successfully processed")
  await websocket.send(json.dumps(return_data))

# Websocket logic 
# https://websockets.readthedocs.io/en/stable/intro.html

async def consumer_handler(websocket, path):
  async for message in websocket:
    print('recvd messg')
    await process_image(websocket, message)

# 132.178.227.12 is the bsu gpu ip
# start_server = websockets.serve(consumer_handler, 132.178.227.12, 8765)
start_server = websockets.serve(consumer_handler, "localhost", 8765)
print('Websocket listening on port 8765!')

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
