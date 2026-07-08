import os
import sys
from PIL import Image, ImageDraw, ImageOps

# Flag to check if we can use advanced detection libraries
HAS_MEDIAPIPE = False
HAS_OPENCV = False

try:
    import mediapipe as mp
    import numpy as np
    HAS_MEDIAPIPE = True
except ImportError:
    pass

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    pass

def crop_to_circle(img: Image.Image) -> Image.Image:
    """Crops an image into a circle with transparency."""
    # Ensure square size
    size = min(img.size)
    img_square = ImageOps.fit(img, (size, size), Image.Resampling.LANCZOS)
    
    # Create circular mask
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    # Create output image with alpha channel
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(img_square, (0, 0), mask)
    
    # Resize to standard size (e.g. 200x200) for game use
    return output.resize((200, 200), Image.Resampling.LANCZOS)

def process_face(input_path: str, output_path: str) -> bool:
    """
    Detects a face in the input image, crops it with padding,
    makes it a circle, and saves it to the output path.
    """
    try:
        img = Image.open(input_path).convert('RGB')
        width, height = img.size
    except Exception as e:
        print(f"Error opening image: {e}")
        return False

    cropped_face = None

    # --- Method 1: MediaPipe Face Detection ---
    if HAS_MEDIAPIPE:
        try:
            print("Attempting face detection using MediaPipe...")
            # Convert PIL image to numpy array (RGB) for MediaPipe
            img_np = np.array(img)
            
            mp_face_detection = mp.solutions.face_detection
            with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.4) as face_detection:
                results = face_detection.process(img_np)
                
                if results.detections:
                    print("Face detected by MediaPipe!")
                    # Use the first detected face
                    detection = results.detections[0]
                    bbox = detection.location_data.relative_bounding_box
                    
                    # Convert relative coordinates to pixels
                    xmin = int(bbox.xmin * width)
                    ymin = int(bbox.ymin * height)
                    box_width = int(bbox.width * width)
                    box_height = int(bbox.height * height)
                    
                    # Expand box to include hair/ears/chin (face detection boxes are usually tight)
                    pad_w = int(box_width * 0.3)
                    pad_h = int(box_height * 0.4)
                    
                    # Compute coordinates with padding
                    x1 = max(0, xmin - pad_w)
                    y1 = max(0, ymin - pad_h)
                    x2 = min(width, xmin + box_width + pad_w)
                    y2 = min(height, ymin + box_height + pad_h)
                    
                    # Make crop area square
                    crop_w = x2 - x1
                    crop_h = y2 - y1
                    side = min(crop_w, crop_h)
                    
                    # Center the square
                    cx, cy = x1 + crop_w // 2, y1 + crop_h // 2
                    x1 = max(0, cx - side // 2)
                    y1 = max(0, cy - side // 2)
                    x2 = min(width, x1 + side)
                    y2 = min(height, y1 + side)
                    
                    cropped_face = img.crop((x1, y1, x2, y2))
        except Exception as e:
            print(f"MediaPipe processing failed: {e}")

    # --- Method 2: OpenCV Haar Cascades Fallback ---
    if cropped_face is None and HAS_OPENCV:
        try:
            print("Attempting face detection using OpenCV Haar Cascades...")
            # Convert PIL image to OpenCV BGR format
            img_cv = cv2.imread(input_path)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            # Note: OpenCV's built-in cascades dir is cv2.data.haarcascades
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
            
            if len(faces) > 0:
                print("Face detected by OpenCV!")
                x, y, w, h = faces[0]
                
                # Expand box slightly
                pad_w = int(w * 0.2)
                pad_h = int(h * 0.3)
                
                x1 = max(0, x - pad_w)
                y1 = max(0, y - pad_h)
                x2 = min(width, x + w + pad_w)
                y2 = min(height, y + h + pad_h)
                
                # Make square
                side = min(x2 - x1, y2 - y1)
                cx, cy = x1 + (x2 - x1) // 2, y1 + (y2 - y1) // 2
                x1 = max(0, cx - side // 2)
                y1 = max(0, cy - side // 2)
                x2 = min(width, x1 + side)
                y2 = min(height, y1 + side)
                
                cropped_face = img.crop((x1, y1, x2, y2))
        except Exception as e:
            print(f"OpenCV processing failed: {e}")

    # --- Method 3: Center Crop Fallback (Guaranteed to work) ---
    if cropped_face is None:
        print("Using Center Crop Fallback...")
        side = min(width, height)
        x1 = (width - side) // 2
        y1 = (height - side) // 2
        x2 = x1 + side
        y2 = y1 + side
        cropped_face = img.crop((x1, y1, x2, y2))

    # Apply circular mask & resize
    try:
        final_avatar = crop_to_circle(cropped_face)
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        final_avatar.save(output_path, format="PNG")
        print(f"Avatar successfully saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving circular cropped avatar: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2:
        process_face(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python face_processor.py <input_image_path> <output_image_path>")
