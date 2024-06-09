from opencv import *
from ObjectDetector import *
from PlayAI import PacManAI
from PathFinder import PathFinder

# VERSION USED ------------------------
# REFERENCE LINK: https://pytorch.org/get-started/locally/
# CUDA 1.2.1 
# Pytorch 2.3.1+cu121
# torchvision 0.18.1+cu121
# torchaudio 2.3.1+cu121
# -------------------------------------

# WARNING BEFORE RUNNING 
# 모델 로딩되는 동안 팩맨 게임을 시작하자마자 일시정지 시킨 상태로 벽을 감지해야 감지가 잘 됨 

# 팩맨 게임 창의 정확한 제목을 여기에 입력합니다
app_name = "VirtuaNES - pac"

# YOLOv5 model load with learned parameters best.pt
objDetector = ObjectDetector("best.pt")
pacman = PacManAI()
pathFinder = PathFinder()

isScreenProcessed = False
cells = []

while True:
    # 특정 어플리케이션 창 위치 및 크기 가져오기
    rect = get_window_rect(app_name)
    if not rect:
        print(f"No window found with title '{app_name}'")
        break
    x, y, x1, y1 = rect
    w = x1 - x
    h = y1 - y
    #print(f"Window position and size: x={x}, y={y}, w={w}, h={h}") # (width = 1916, height = 993) for hard coding

    screenshot = pyautogui.screenshot(region=(x,y,w,h))
    frame = np.array(screenshot)
    
    if w > 0 and h > 0:
        #app_frame = frame[y:y+h, x:x+w]
        app_frame = frame
        if app_frame.size > 0:
            h, w, _ = app_frame.shape # 행, 열 
            
            # 셀의 크기 계산 하드코딩;;
            cell_width = 60
            cell_height = 35
            
            if not isScreenProcessed: # Generate cell
                isScreenProcessed = True
                
                print(f"Window position and size: x={x}, y={y}, w={w}, h={h}") # (width = 1916, height = 993) for hard coding
                
                detectionFrame = cv2.cvtColor(app_frame, cv2.COLOR_RGB2BGR)
                
                cells = process_screen(detectionFrame, cell_width, cell_height)
                cell_info = [[np.mean(cell) for cell in row] for row in cells]
                draw_grid_classify(detectionFrame, cells, cell_width, cell_height) # draw cell on openCV screen, classifying walls. It needs color channel here 
                
                for y, row in enumerate(cells):
                    if y == 0 or y > 27: # 맨 윗줄 건너뛰기
                        continue
                    for x, cell in enumerate(row):
                        if x == 0 or x >21: # 왼쪽 열 건너뛰기
                            continue
                        classify_and_store_cell(cell, y-1, x-1)  # 인덱스 조정
                        
                # 배열 정보 출력
                update_direction_info()
                debug_cell_data()

            # Object Detection
            results = objDetector.ScoreFrame(app_frame)
            app_frame = objDetector.PlotBoxes(results, app_frame)
            
            # Player AI handling 
            if len(results[0]) > 0: # number of detected obj
                player_pos, ghosts_pos, edible_ghosts_pos, dots_pos, power_pellets_pos = objDetector.UpdateCellInfo(results, app_frame, cell_data)
                if player_pos == ():
                    print("No player detected")
                else:
                    pacman.UpdateAIInfo(cell_data, player_pos, ghosts_pos, edible_ghosts_pos, dots_pos, power_pellets_pos)
                    pacman.decide_next_pos()
                    pacman.GiveInput()
                    # next_pos = pathFinder.Run(player_pos, ghosts_pos, edible_ghosts_pos, dots_pos, power_pellets_pos, cell_data)
                    # pathFinder.GiveInput(player_pos, next_pos)
                
            # OpenCV 화면 보여주기
            cv2.imshow("YOLOV5 detection", app_frame)
        else:
            print("Extracted frame has size 0.")
    else:
        print("Invalid window size or position.")
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

# 'c' 키를 눌렀을 때 배열 초기화 및 벽 확인
if cv2.waitKey(1) & 0xFF == ord('c'):
    initialize_cell_data()
    for y, row in enumerate(cells):
        if y == 0 or y > 27: # 맨 윗줄 건너뛰기
            continue
        for x, cell in enumerate(row):
            if x == 0 or x >21: # 왼쪽 열 건너뛰기
                continue
            classify_and_store_cell(cell, y-1, x-1)  # 인덱스 조정
    # 배열 정보 출력
    update_direction_info()
    debug_cell_data()


