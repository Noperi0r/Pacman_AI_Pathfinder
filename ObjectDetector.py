import torch
import cv2
import numpy as np 
#import time

class ObjectDetector:
    def __init__(self, model_name):
        self.model = self.LoadModel(model_name)
        self.classes = self.model.names # Get labels
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Using Device: ", self.device)
        
        
    def LoadModel(self, model_name):
        if model_name:
            model = torch.hub.load("ultralytics/yolov5", 'custom', path=model_name, force_reload=True)
        else:
            model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)    
        return model 
    
    def ScoreFrame(self, frame):
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame) # Frame passed through our model
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1] # Take labels from results, coordinates of bounding box
        return labels, cord
    
    def ClassToLabel(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]
    
    def PlotBoxes(self, results, frame):
        labels, coord = results # Unpack label coord
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]

        for i in range(n):
            row = coord[i]
            if row[4] >= 0.3: # Confidence threshold
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                bgr = (0, 255, 0)
                cv2.rectangle(frame, (x1,y1), (x2,y2), bgr, 2)
                cv2.putText(frame, self.ClassToLabel(labels[i]), (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr)
        return frame
    

    def __call__(self):
        """
        This function is called when class is executed, it runs the loop to read the video frame by frame, and write the output into a new file.
        """
        cap = self.FrameCapture()
        assert cap.isOpened() 
        
        while True:
            
            ret, frame = cap.read()
            assert ret
            
            frame = cv2.resize(frame, (416, 416)) # resize to the same size of data yolo used to train
            
            #start_time = time()
            results = self.ScoreFrame(frame)
            frame = self.PlotBoxes(results, frame)
            
            #end_time = time()
            #fps = 1/np.round(end_time - start_time, 2)
            #print(f"Frames per Second: {fps}")
            
            #cv2.putText(frame, f"FPS: {int(fps)}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
            cv2.imshow("YOLOv5 Detection", frame)
            
            if cv2.waitKey(5) & 0xFF == 27:
                break
            
        cap.release()
            
            
# detector = ObjectDetector()
# detector()