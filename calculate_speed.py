from collections import defaultdict
from haversine import haversine
import cv2
import numpy as np
import math
from ultralytics import YOLO
from flask import Flask, request, render_template
import json

# custom dataset으로 fine-tunning한 YOLOv8 model
model = YOLO("best.pt")

# Open the video file: 광교중앙역 cctv영상을 https://www.utic.go.kr/map/map.do?menu=cctv 에서 녹화한 영상
video_path = "./video/video.mp4"
cap = cv2.VideoCapture(video_path)

# rack history 저장을 위한 dict
track_history = defaultdict(lambda: [])


IMAGE_H = 1152
IMAGE_W = 720


src = np.float32([[380.4, 613.6], [1058.4, 561.6], [363.2, 301.2], [666.4, 268.4]])
dst = np.float32([[37.289227, 127.050917], [37.289039, 127.050644], [37.288842, 127.051426], [37.288655, 127.051158]])
lat_long_dst = np.float32([[37.289227, 127.050917], [37.289039, 127.050644], [37.288842, 127.051426], [37.288655, 127.051158]])

# python의 haversine 라이브러리로 각 위경도 좌표간의 거리를 계산
dst = np.float32([haversine(dst[0], i, unit="m") for i in dst])
print(dst)  # [0, 31.943, 61.973, 67.023]

dst = np.float32([[0, 0], [31.943, 0], [0, 61.973], [31.943, 61.973]])

lat_long_M = cv2.getPerspectiveTransform(src, lat_long_dst)
M = cv2.getPerspectiveTransform(src, dst)  # The transformation matrix
print(f"M : {M}")
print(f"M : {lat_long_M}")

car_dict = defaultdict(list) # tracking되는 차별 id마다 변화되는 미터좌표계 저장
speed_dict = defaultdict(list) # 평균 속력 계산
lat_long_data = defaultdict(list)
frame_count = 0

fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Video FPS: {fps} frames per second") # 24 fps

# 속도 계산된 동영상 저장
fourcc = cv2.VideoWriter_fourcc(*'avc1')
output_video = cv2.VideoWriter('output_video.mp4', fourcc, fps, (IMAGE_W, IMAGE_H))

while cap.isOpened():
    # 비디오 프레임 읽기
    success, frame = cap.read()
    frame_count += 1

    if success:
        # Yolov8 tracking 이용
        results = model.track(frame, persist=True)

        # boxes와 track_ids
        boxes = results[0].boxes.xywh.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Plot the tracks
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y)))  # x, y center point
            x = x.tolist()
            y = y.tolist()
            src_coor = np.float32([[x], [y], [1]])
            lat_long_coor = np.dot(M, src_coor)
            lat_long_coor = np.array([lat_long_coor[i][0] / lat_long_coor[2][0] for i in range(3)])
            # print(f'lat_long_coor:{lat_long_coor}, track_id: {track_id}')

            real_coor = np.dot(lat_long_M, src_coor)
            np.set_printoptions(precision=15)
            # print(real_coor)
            real_coor = np.array([real_coor[i][0] / real_coor[2][0] for i in range(3)])
            # print(f'real_coor:{real_coor}, track_id: {track_id}')
            lat_long_data[track_id].append(real_coor[:-1].tolist())

            if not car_dict[track_id]:
                car_dict[track_id].append(lat_long_coor)
            else:
                car_dict[track_id].append(lat_long_coor)
                difference = car_dict[track_id][-2] - lat_long_coor
                distance = math.sqrt(difference[0] ** 2 + difference[1] ** 2)
                speed = distance * fps / 1000 * 3600 # 1초당 24fps -> 1frame당 1/24초, 거리/(1/24)*3600/1000 -> km/h로 변환
                # print("차이", difference)
                # print("프레임간 거리", distance)
                print("속도", speed, "km/h", 'id: ', track_id)

                speed_dict[track_id].append(speed)
                # 4 프레임의 평균 속도 계산
                if len(speed_dict[track_id]) > 4:
                    speed_dict[track_id].pop(0)
                elif len(speed_dict[track_id]) < 4: # 처음 4 프레임은 맨 처음 계산한 속도 출력
                    first_speed = speed_dict[track_id][0]
                    speed_text = f"Speed: {first_speed:.2f} km/h"
                    cv2.putText(annotated_frame, speed_text, (int(x), int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                
                # 처음 4 프레임이 지난 이후, 4 프레임의 평균 속도 계산하여 속도 오차 보정
                if len(speed_dict[track_id]) == 4:
                    avg_speed = sum(speed_dict[track_id]) / 4.0
                    speed_text = f"Speed: {avg_speed:.2f} km/h"
                    cv2.putText(annotated_frame, speed_text, (int(x), int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


            if len(track) > 30:
                track.pop(0)

            # Tracking line을 흰색 선으로 표시
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=3)

        # annotated frame 출력
        cv2.imshow("YOLOv8 Tracking", annotated_frame)
        #동영상 저장
        # output_video.write(annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break


# video capture object와 close the display window Release
cap.release()
cv2.destroyAllWindows()


# print(lat_long_data)
lat_long_data = dict(lat_long_data)

# 데이터를 저장할 파일 경로
data_file = 'lat_long_data.json'

# 데이터를 저장하는 함수
def save_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file)

save_data(lat_long_data)