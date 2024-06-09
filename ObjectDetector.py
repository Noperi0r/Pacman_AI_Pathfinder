import torch
import cv2
import numpy as np 
#import time
import pathlib

IMGSIZE = 1280 # img size yolo used to train 

class ObjectDetector:
    def __init__(self, model_name):
        self.model = self.LoadModel(model_name)
        self.classes = self.model.names # Get labels
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Using Device: ", self.device)
        self.confidence = 0.3 
        
        
    def LoadModel(self, model_name):
        temp = pathlib.PosixPath
        pathlib.PosixPath = pathlib.WindowsPath
        if model_name:
            #model = torch.hub.load("ultralytics/yolov5", 'custom', path=model_name, force_reload=True)
            model = torch.hub.load("./yolov5", "custom", path=model_name, force_reload=True, source="local")
        else:
            model = torch.hub.load("ultralytics/yolov5", "custom", path=model_name, force_reload=True, source="local")
        pathlib.PosixPath = temp
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
        labels, cord = results # Unpack label coord
        x_shape, y_shape = frame.shape[1], frame.shape[0] # col, row 
        #print("Length of objects detected: ", len(labels))
        
        for i in range(len(labels)):
            row = cord[i]
            if row[4] >= self.confidence: # Confidence threshold
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                bgr = (0, 255, 0)
                cv2.rectangle(frame, (x1,y1), (x2,y2), bgr, 2)
                cv2.putText(frame, self.ClassToLabel(labels[i]), (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr)
        return frame
    
    def UpdateCellInfo(self, results, frame, cell_data):
        labels, cord = results
        x_shape, y_shape = frame.shape[1], frame.shape[0]

        player_pos, ghosts_pos, edible_ghosts_pos, dots_pos, power_pellets_pos = (), [], [], [], []
        
        for i in range(len(labels)):
            row = cord[i]
            if row[4] >= self.confidence: # confidence
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                center = ((y1+y2) // 2, (x1+x2) // 2) # y, x 

                idxRow, idxCol = center[0] // (frame.shape[0] // 27), center[1] // (frame.shape[1] // 21)
                objName = self.ClassToLabel(labels[i])
                if objName == "Player":
                    #player_pos.append((idxRow, idxCol))
                    player_pos = (idxRow, idxCol)
                    cell_data[idxRow][idxCol]["player"] = True
                else:
                    cell_data[idxRow][idxCol]["player"] = False
                
                if objName == "Ghost":
                    ghosts_pos.append((idxRow, idxCol))
                    cell_data[idxRow][idxCol]["ghost"] = True
                else:
                    cell_data[idxRow][idxCol]["ghost"] = False
                    
                if objName == "edible_ghost":
                    edible_ghosts_pos.append((idxRow, idxCol))
                    cell_data[idxRow][idxCol]["ghost_edible"] = True
                else:
                    cell_data[idxRow][idxCol]["ghost_edible"] = False
                    
                if objName == "s": # Small pellet
                    dots_pos.append((idxRow, idxCol))
                    cell_data[idxRow][idxCol]["food"] = True
                else:
                    cell_data[idxRow][idxCol]["food"] = False

                if objName == "b":
                    power_pellets_pos.append((idxRow, idxCol))
                    cell_data[idxRow][idxCol]["food"] = True
                else:
                    cell_data[idxRow][idxCol]["food"] = False
                    
                # frame shape: row, col >> 995(h), 1916(w)
                # celldata : 27(row, y) x 21(col, x) 
                
        return player_pos, ghosts_pos, edible_ghosts_pos, dots_pos, power_pellets_pos
  
    # def __call__(self):
    #     """
    #     This function is called when class is executed, it runs the loop to read the video frame by frame, and write the output into a new file.
    #     """
    #     cap = self.FrameCapture()
    #     assert cap.isOpened() 
        
    #     while True:
    #         ret, frame = cap.read()
    #         assert ret
            
    #         frame = cv2.resize(frame, (IMGSIZE, IMGSIZE)) # resize to the same size of data yolo used to train
            
    #         #start_time = time()
    #         results = self.ScoreFrame(frame)
    #         frame = self.PlotBoxes(results, frame)
            
    #         #end_time = time()
    #         #fps = 1/np.round(end_time - start_time, 2)
    #         #print(f"Frames per Second: {fps}")
            
    #         #cv2.putText(frame, f"FPS: {int(fps)}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
    #         cv2.imshow("YOLOv5 Detection", frame)
            
    #         if cv2.waitKey(5) & 0xFF == 27:
    #             break
    #     cap.release()