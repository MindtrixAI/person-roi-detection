import cv2
import time
from ultralytics import YOLO
#............................................
model = YOLO("yolov8n.pt")
#cap = cv2.VideoCapture(0)
ROI = (0, 240, 640, 480)



#..................... frontend 
latest_stats = {
    "person_count": 0,
    "alert_count": 0,
    "fps": 0.0,
    "alert": False
}

#...............................functions
def is_box_in_roi(box, roi):
    x1, y1, x2, y2 = box
    rx1, ry1, rx2, ry2 = roi

    if x2 < rx1 or x1 > rx2:
        return False
    if y2 < ry1 or y1 > ry2:
        return False
    return True
#...............................................
def generate_frames():
    cap = cv2.VideoCapture(0)
    prev_time = time.time()
    #.......................................
    while True:
        ret,frame = cap.read()
    # print(frame.shape)
        if not ret:
            print("Failed to grab frame")
            break
    
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0 #....fps
        prev_time = curr_time

        rx1, ry1, rx2, ry2 = ROI
        cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), (0, 0, 255), 2)
        cv2.putText(frame, "Restricted Zone", (rx1, ry1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        results = model(frame, classes=[0], conf=0.5, verbose=False)

        person_count = 0
        alert_count = 0
        
        results = model(frame,classes=[0],conf=0.5,verbose=False)
        for result in results:
            for box in result.boxes:
             x1, y1, x2, y2 = map(int, box.xyxy[0])

            main_box = (x1, y1, x2, y2)
            alert = is_box_in_roi(main_box, ROI)#...alert
            color = (0, 0, 255) if alert else (45, 255, 150)
            label = "ALERT" if alert else "Person"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color,1)
            cv2.putText(frame, label, (x1, y1 - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

           
            # cls_id = int(box.cls[0])
            # conf = box.conf[0]
            #print(f"Class ID: {cls_id}, Confidence: {conf:.2f}")
            
            person_count += 1
            if alert:
                    alert_count += 1
                    print("ALERT: Person in restricted area")

        
        latest_stats["person_count"] = person_count
        latest_stats["alert_count"] = alert_count
        latest_stats["fps"] = round(fps, 1)
        latest_stats["alert"] = alert_count > 0

    
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()