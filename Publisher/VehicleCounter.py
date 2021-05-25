"""
    Detekcja pojazdów
"""

import cv2
import dlib
import threading


def find_center(x, y, w, h):
    """
        Zwraca środek prostokąta, określonego poprzez jego położenie, długość i szerokość.
    """
    cx = int((x + w) / 2)
    cy = int((y + h) / 2)
    return cx, cy


def on_detect_test(direction):
    """
        Testowy callback detekcji pojazdów
    """
    print("Car detected, direction: " + direction)


def point_in_rectangle(x, y, w, h, cx, cy):
    """
        Sprawdza czy dany punkt, określony przez cx i cy, znajduje się w prostokącie o określonym położeniu, szerokości
        i wysokości.
    """
    if x < cx < x + w:
        if y < cy < y + h:
            return True
    else:
        return False


class VehicleCounter:
    """
        Klasa detekcji pojazdów
    """

    # URL strumienia wybranej kamery
    BRANIEWO_URL = 'http://kamery.tvbraniewo24.pl:5080/LiveApp/streams/853734119073868618727613.m3u8'

    def __init__(self, video=BRANIEWO_URL, preview=True):
        """
            Konstruktor obiektu detekcji.

            Parameters
            ----------
            viedo: str
                URL strumienia kamery

            preview: bool
                Czy podgląd ma być widoczny

        """
        self.__video = video
        self.__preview = preview
        self.on_detect = on_detect_test
        self.running = True

    def start(self):
        """
            Uruchomienie procesu detekcji pojazdów.
        """
        def thread():
            cap = cv2.VideoCapture(self.__video)
            background = cv2.bgsegm.createBackgroundSubtractorMOG()

            frames = 0
            frames_skip = 10
            cars_in = 0
            cars_out = 0
            trackers = []

            while self.running:
                ret, frame = cap.read()
                frame_r = cv2.resize(frame, (640, 480))
                frame_cropped = frame_r[200:640, 0:640]

                mask = background.apply(frame_cropped)
                mask = cv2.dilate(mask, (9, 9), 2)
                contours, h = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                trackers_to_del = []
                t_id = None

                for t_id, tracker_id in enumerate(trackers):
                    tracking_quality = tracker_id[0].update(frame_cropped)
                    if tracking_quality < 5:
                        trackers_to_del.append(tracker_id[0])
                try:
                    for _ in trackers_to_del:
                        if t_id:
                            trackers.pop(t_id)
                except IndexError:
                    pass

                if (frames % frames_skip) == 0:
                    for num, cnt in enumerate(contours):
                        area = cv2.contourArea(cnt)
                        if area in range(400, 8000):
                            x, y, w, h = cv2.boundingRect(cnt)
                            rect = dlib.rectangle(x, y, x + w, y + h)
                            tracking = False

                            for tracker_id in trackers:
                                pos = tracker_id[0].get_position()
                                start_x = int(pos.left())
                                start_y = int(pos.top())
                                end_x = int(pos.right())
                                end_y = int(pos.bottom())
                                tx, ty = find_center(start_x, start_y, end_x, end_y)
                                t_location_chk = point_in_rectangle(x, y, w, h, tx, ty)
                                if t_location_chk:
                                    tracking = True

                            if not tracking:
                                tracker = dlib.correlation_tracker()
                                tracker.start_track(frame_cropped, rect)
                                trackers.append([tracker, frame_cropped])

                for num, tracker_id in enumerate(trackers):
                    pos = tracker_id[0].get_position()
                    start_x = int(pos.left())
                    start_y = int(pos.top())
                    end_x = int(pos.right())
                    end_y = int(pos.bottom())
                    offset = 0
                    cv2.rectangle(frame_cropped, (start_x - offset, start_y - offset),
                                  (end_x + offset, end_y + offset), (0, 255, 250), 1)

                    if end_x < 320 and end_y >= 280:
                        cars_in += 1
                        self.on_detect("in")
                        trackers.pop(num)

                    if end_x > 320 and start_y < 0:
                        cars_out += 1
                        self.on_detect("out")
                        trackers.pop(num)

                frames += 1

                if self.__preview:
                    cv2.putText(frame_r, f"IN:{cars_in}",
                                (20, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(frame_r, f"OUT:{cars_out}",
                                (550, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

                    cv2.imshow('frame', frame_r)

                if cv2.waitKey(1) == 27:
                    break

            cap.release()
            cv2.destroyAllWindows()

        x = threading.Thread(target=thread)
        x.start()

    def stop(self):
        """
            Zatrzymanie procesu detekcji pojazdów.
        """
        self.running = False
