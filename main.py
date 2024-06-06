from opencv import *

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