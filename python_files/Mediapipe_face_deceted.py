import cv2
import mediapipe as mp
from typing import List, Mapping, Optional, Tuple, Union
import math
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def _normalized_to_pixel_coordinates(
    normalized_x: float, normalized_y: float, image_width: int,
    image_height: int) -> Union[None, Tuple[int, int]]:
  """Converts normalized value pair to pixel coordinates."""
  # Checks if the float value is between 0 and 1.
  def is_valid_normalized_value(value: float) -> bool:
    return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                                      math.isclose(1, value))
  if not (is_valid_normalized_value(normalized_x) and
          is_valid_normalized_value(normalized_y)):
  # TODO: Draw coordinates even if it's outside of the image bounds.
    return None
  x_px = min(math.floor(normalized_x * image_width), image_width - 1)
  y_px = min(math.floor(normalized_y * image_height), image_height - 1)
  return x_px, y_px


def M_face():
  cap = cv2.VideoCapture(0)
  with mp_face_detection.FaceDetection(
    min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

      # Flip the image horizontally for a later selfie-view display, and convert
      # the BGR image to RGB.
      image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      image_rows, image_cols, _ = image.shape
      image.flags.writeable = False
      results = face_detection.process(image)

      # Draw the face detection annotations on the image.
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      
      if results.detections:
        for detection in results.detections:
          x = detection.location_data.relative_bounding_box.xmin
          y = detection.location_data.relative_bounding_box.ymin
          w = detection.location_data.relative_bounding_box.width
          h = detection.location_data.relative_bounding_box.height
          rect_start_point = _normalized_to_pixel_coordinates(
            x, y, image_cols, image_rows)
          rect_end_point = _normalized_to_pixel_coordinates(
            x + w, y + h, image_cols, image_rows)
          print(rect_start_point, rect_end_point, w * image_cols, h * image_rows)
          cv2.rectangle(image, rect_start_point, rect_end_point, (0, 255, 0), 2)
          #cv2.line(image, rect_start_point, rect_end_point, (0, 255, 0), 2)
          #mp_drawing.draw_detection(image, detection)
          
      cv2.imshow('MediaPipe Face Detection', image)
      if cv2.waitKey(5) & 0xFF == 27:
        break

  cap.release()


if __name__ == '__main__':
    M_face()