import cv2
import numpy as np
import pyautogui
import win32gui

# 팩맨 게임 창의 정확한 제목을 여기에 입력합니다
app_name = "VirtuaNES - pac"



def initialize_cell_data():
    global cell_data
    cell_data = [[{'is_wall': True, 'E': 0, 'W': 0, 'S': 0, 'N': 0} for _ in range(21)] for _ in range(27)]

def classify_and_store_cell(cell, row, col):
    cell_type = classify_cell(cell)
    if cell_type == 'wall':
        cell_data[row][col]['is_wall'] = True
    else:
        cell_data[row][col]['is_wall'] = False

def update_direction_info():
    for row in range(27):
        for col in range(21):
            if not cell_data[row][col]['is_wall']:
                # 동쪽 확인
                if col < 20 and not cell_data[row][col+1]['is_wall']:
                    cell_data[row][col]['E'] = 1
                # 서쪽 확인
                if col > 0 and not cell_data[row][col-1]['is_wall']:
                    cell_data[row][col]['W'] = 1
                # 남쪽 확인
                if row < 26 and not cell_data[row+1][col]['is_wall']:
                    cell_data[row][col]['S'] = 1
                # 북쪽 확인
                if row > 0 and not cell_data[row-1][col]['is_wall']:
                    cell_data[row][col]['N'] = 1



def print_cell_data():
    direction_symbols = {('E', 'N', 'S', 'W'): '┼', 
                         ('E', 'S', 'W'): '┯', 
                         ('E', 'N', 'W'): '┴',
                         ('E', 'N', 'S'): '├',
                         ('N', 'S', 'W'): '┤',
                         ('E', 'W'): '─',
                         ('E', 'S'): '┌',
                         ('E', 'N'): '└',
                         ('S', 'W'): '┓',
                         ('N', 'W'): '┘',
                         ('N', 'S'): '│',
                         ('E',): '→',
                         ('W',): '←',
                         ('S',): '↓',
                         ('N',): '↑',
                         (): ' '}
    
    for row in cell_data:
        row_symbols = []
        for cell in row:
            if cell['is_wall']:
                row_symbols.append('■')
            else:
                directions = tuple(sorted([k for k, v in cell.items() if v == 1 and k in 'EWNS']))
                row_symbols.append(direction_symbols[directions])
        print(' '.join(row_symbols))
    print("\n" + "="*60 + "\n")


def get_window_rect(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        # Get client area rectangle
        client_rect = win32gui.GetClientRect(hwnd)
        
        # Convert client area rectangle to screen coordinates
        client_point = win32gui.ClientToScreen(hwnd, (client_rect[0], client_rect[1]))
        client_point2 = win32gui.ClientToScreen(hwnd, (client_rect[2], client_rect[3]))
        client_rect = (client_point[0], client_point[1], client_point2[0], client_point2[1])
        
        return client_rect
    else:
        return None

def process_screen(image, cell_width, cell_height):
    height, width, _ = image.shape
    cells = []
    for y in range(0, height, cell_height):
        row = []
        for x in range(0, width, cell_width):
            cell = image[y:y+cell_height, x:x+cell_width]
            row.append(cell)
        cells.append(row)
    return cells

COLOR_TARGETS = {
    'wall': (248, 96, 64),  # 파란색
    'food': (0, 160, 255),  # 주황색 (먹이)
}

def classify_cell(cell):
    cell_hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)  # HSV로 변환하여 색상 검출 정확도를 높임
    for item, target_color in COLOR_TARGETS.items():
        lower = np.array(target_color) - 10
        upper = np.array(target_color) + 10
        mask = cv2.inRange(cell, lower, upper)
        ratio = cv2.countNonZero(mask) / (cell.shape[0] * cell.shape[1])
        if ratio > 0.1 and ratio < 0.3:  # 특정 색상이 셀의 일정 퍼센트 이상일 때 해당 항목으로 분류
            return item
    return 'empty' #기본값.

def draw_grid_and_text(image, cells, cell_width, cell_height):
    height, width, _ = image.shape
    for y, row in enumerate(cells):
        for x, cell in enumerate(row):
            # Draw cell boundaries
            top_left = (x * cell_width, y * cell_height)
            bottom_right = (top_left[0] + cell_width, top_left[1] + cell_height)
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 1)

            # Classify the cell
            cell_type = classify_cell(cell)

            # Define the text to be displayed
            text = cell_type[:3]  # 첫 3글자만 표시
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            text_x = top_left[0] + (cell_width - text_size[0]) // 2
            text_y = top_left[1] + (cell_height + text_size[1]) // 2

            # Put the text on the image
            cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

while True:
    # 특정 어플리케이션 창 위치 및 크기 가져오기
    rect = get_window_rect(app_name)
    if not rect:
        print(f"No window found with title '{app_name}'")
        break

    x, y, x1, y1 = rect
    w = x1 - x
    h = y1 - y

    

    # 화면 캡처
    screenshot = pyautogui.screenshot()

    # PIL 이미지에서 numpy 배열로 변환
    frame = np.array(screenshot)

    # BGR로 변환 (OpenCV는 BGR을 사용)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

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
        print_cell_data()


    # 영역이 유효한지 확인
    if w > 0 and h > 0:
        app_frame = frame[y:y+h, x:x+w]

        # 이미지 크기 확인
        if app_frame.size > 0:
            h, w, _ = app_frame.shape


            # 셀의 크기 계산 하드코딩;;
            cell_width = 60
            cell_height = 35

            

            # 게임 스크린을 셀로 나누기
            cells = process_screen(app_frame, cell_width, cell_height)

            # 각 셀의 정보를 2차원 배열로 출력 (셀의 평균 색상 값)
            cell_info = [[np.mean(cell) for cell in row] for row in cells]

            # 각 셀의 경계선 및 텍스트를 그림
            draw_grid_and_text(app_frame, cells, cell_width, cell_height)

            # OpenCV 화면 보여주기
            cv2.imshow(app_name, app_frame)


            
        
    else:
        print("Invalid window size or position.")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()