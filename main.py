import cv2
import time
import random
import numpy as np
from face_detection import detection
from make_rectangle import make
from face_emotions import main

"""
/home/username/anaconda3/envs/deep36/lib/python3.6/site-packages/EmoPy/src/fermodel.py
60行目
        # self._print_prediction(prediction[0]) # past
        memo = self._print_prediction(prediction[0])  # add
        return memo  # add
60行目をコメントアウトし、後ろの2行を追加。

113行目に
        return [str(dominant_emotion), normalized_prediction[self.emotion_map[emotion]] * 100]
を追加。

実行結果が返ってくるように改良した。
"""


class Main:
    def __init__(self):
        self.ESC_KEY = 27
        self.INTERVAL = 33
        self.time_limit = 10

        self.odai_idx = [0, 1]
        self.odai_pred = ["happiness", "anger"]
        self.odai_list = ["Happy", "Angry"]
        self.odai_id = random.choice(self.odai_idx)
        # self.odai = random.choice(self.odai_list)

        self.ORG_WINDOW_NAME = "org"
        self.DEVICE_ID = 0

        self.cascade_file = "haarcascade_frontalface_alt.xml"
        self.cascade = cv2.CascadeClassifier(self.cascade_file)

        self.cap = cv2.VideoCapture(self.DEVICE_ID)

        # 初期フレームの読込
        self.end_flag, self.c_frame = self.cap.read()
        self.height, self.width, self.channels = self.c_frame.shape

        # ウィンドウの準備
        cv2.namedWindow(self.ORG_WINDOW_NAME)

        # flag
        self.face_flag = True

        self.rec = make(self.height, self.width)

        self.time_1 = time.time()
        self.last = self.time_1

        self.count = -1
        self.interval = 0

    def loop(self):
        while self.end_flag:
            # 画像の取得と顔の検出
            img2 = self.c_frame
            if self.face_flag:
                self.rec = make(self.height, self.width)
                self.face_flag = False
                self.interval = time.time() - self.last
                self.last = time.time()
                self.count += 1

            x, y, w, h = self.rec[0], self.rec[1], self.rec[2], self.rec[3]
            img3, face_list = detection(img2, self.cascade)
            cv2.rectangle(img2, (x, y), (w, h), (0, 200, 225), thickness=3)

            cv2.putText(img3,
                        "{0: .2f}sec {1}count {2}".format(self.interval, self.count, self.odai_list[self.odai_id]),
                        (20, 60),
                        fontFace=cv2.FONT_HERSHEY_COMPLEX,
                        fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_4)
            # print(face_list)
            if len(face_list) != 0:
                # print(x, y, w, h)
                if face_list[0][0] > x and face_list[0][1] > y and face_list[0][2] + face_list[0][0] < w \
                        and face_list[0][3] + face_list[0][1] < h:

                    file = "image_data/image.jpg"
                    # print(np.array(img2).shape)
                    save = np.array(img2)[face_list[0][1]:face_list[0][1] + face_list[0][3],
                           face_list[0][0]:face_list[0][0] + face_list[0][2], :]
                    # print(save.shape)
                    cv2.imwrite(file, save)
                    predict, ps = main()
                    if self.odai_pred[self.odai_id] == predict:
                        self.face_flag = True
                        self.odai_id = random.choice(self.odai_idx)
                        # self.odai = self.odai_list[self.odai_id]

            # Frame
            cv2.imshow(self.ORG_WINDOW_NAME, img3)

            # Escキーで終了 or Time Limit
            key = cv2.waitKey(self.INTERVAL)
            if key == self.ESC_KEY or time.time() - self.time_1 > self.time_limit:
                break

            # 次のフレーム読み込み
            self.end_flag, self.c_frame = self.cap.read()


if __name__ == '__main__':
    a = Main()
    a.loop()
