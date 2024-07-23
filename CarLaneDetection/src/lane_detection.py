import cv2
import numpy as np
from moviepy.editor import VideoFileClip


class LaneDetection:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.blur_ksize = 5  # Gaussian blur kernel size
        self.canny_lthreshold = 50  # Canny edge detection low threshold
        self.canny_hthreshold = 150  # Canny edge detection high threshold

        # Hough transform parameters
        self.rho = 1
        self.theta = np.pi / 180
        self.threshold = 15
        self.min_line_length = 40
        self.max_line_gap = 20

    def roi_mask(self, img, vertices):
        mask = np.zeros_like(img)

        # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
        if len(img.shape) > 2:
            channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
            mask_color = (255,) * channel_count
        else:
            mask_color = 255

        cv2.fillPoly(mask, vertices, mask_color)
        masked_img = cv2.bitwise_and(img, mask)
        return masked_img

    def draw_roi(self, img, vertices):
        cv2.polylines(img, vertices, True, [255, 0, 0], thickness=2)

    def draw_lines(self, img, lines, color=[255, 0, 0], thickness=2):
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(img, (x1, y1), (x2, y2), color, thickness)

    def hough_lines(self, img, rho, theta, threshold, min_line_len, max_line_gap):
        lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len,
                                maxLineGap=max_line_gap)
        line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        # draw_lines(line_img, lines)
        self.draw_lanes(line_img, lines)
        return line_img

    def draw_lanes(self, img, lines, color=[255, 0, 0], thickness=8):
        left_lines, right_lines = [], []
        try:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    k = (y2 - y1) / (x2 - x1)
                    if k < 0:
                        left_lines.append(line)
                    else:
                        right_lines.append(line)
        except Exception as e:
            print(e)
        if len(left_lines) <= 0 or len(right_lines) <= 0:
            return img

        self.clean_lines(left_lines, 0.1)
        self.clean_lines(right_lines, 0.1)
        left_points = [(x1, y1) for line in left_lines for x1, y1, x2, y2 in line]
        left_points = left_points + [(x2, y2) for line in left_lines for x1, y1, x2, y2 in line]
        right_points = [(x1, y1) for line in right_lines for x1, y1, x2, y2 in line]
        right_points = right_points + [(x2, y2) for line in right_lines for x1, y1, x2, y2 in line]

        left_vtx = self.calc_lane_vertices(left_points, 325, img.shape[0])
        right_vtx = self.calc_lane_vertices(right_points, 325, img.shape[0])

        cv2.line(img, left_vtx[0], left_vtx[1], color, thickness)
        cv2.line(img, right_vtx[0], right_vtx[1], color, thickness)

    def clean_lines(self, lines, threshold):
        slope = [(y2 - y1) / (x2 - x1) for line in lines for x1, y1, x2, y2 in line]
        while len(lines) > 0:
            mean = np.mean(slope)
            diff = [abs(s - mean) for s in slope]
            idx = np.argmax(diff)
            if diff[idx] > threshold:
                slope.pop(idx)
                lines.pop(idx)
            else:
                break

    def calc_lane_vertices(self, point_list, ymin, ymax):
        x = [p[0] for p in point_list]
        y = [p[1] for p in point_list]
        fit = np.polyfit(y, x, 1)
        fit_fn = np.poly1d(fit)

        xmin = int(fit_fn(ymin))
        xmax = int(fit_fn(ymax))

        return [(xmin, ymin), (xmax, ymax)]

    def process_an_image(self, img):
        roi_vtx = np.array([[(0, img.shape[0]), (460, 325), (520, 325), (img.shape[1], img.shape[0])]])

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur_gray = cv2.GaussianBlur(gray, (self.blur_ksize, self.blur_ksize), 0, 0)
        edges = cv2.Canny(blur_gray, self.canny_lthreshold, self.canny_hthreshold)
        roi_edges = self.roi_mask(edges, roi_vtx)
        line_img = self.hough_lines(roi_edges, self.rho, self.theta, self.threshold, self.min_line_length,
                                    self.max_line_gap)
        res_img = cv2.addWeighted(img, 0.8, line_img, 1, 0)

        # plt.figure()
        # plt.imshow(gray, cmap='gray')
        # plt.savefig('../resources/gray.png', bbox_inches='tight')
        # plt.figure()
        # plt.imshow(blur_gray, cmap='gray')
        # plt.savefig('../resources/blur_gray.png', bbox_inches='tight')
        # plt.figure()
        # plt.imshow(edges, cmap='gray')
        # plt.savefig('../resources/edges.png', bbox_inches='tight')
        # plt.figure()
        # plt.imshow(roi_edges, cmap='gray')
        # plt.savefig('../resources/roi_edges.png', bbox_inches='tight')
        # plt.figure()
        # plt.imshow(line_img, cmap='gray')
        # plt.savefig('../resources/line_img.png', bbox_inches='tight')
        # plt.figure()
        # plt.imshow(res_img)
        # plt.savefig('../resources/res_img.png', bbox_inches='tight')
        # plt.show()

        return res_img

    def get_processed_frame(self):
        ret, frame = self.cap.read()
        if ret:
            processed_frame = self.process_an_image(frame)
            return processed_frame
        return None

    def detect(self):
        cap = self.cap  # 使用摄像头 0，如果有多摄像头可能需要调整这个数字
        if not cap.isOpened():
            print("无法打开摄像头，请检查设备连接和权限设置。")
            exit()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("无法获取帧，请检查摄像头是否正常工作。")
                break

            # 调用你的车道检测函数
            result_frame = self.process_an_image(frame)

            # 显示处理后的帧
            cv2.imshow('Lane Detection', result_frame)

            # 按'q'键退出循环
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # 清理
        cap.release()
        cv2.destroyAllWindows()


lane = LaneDetection()

# img = mplimg.imread("../resources/lane.jpg")
# process_an_image(img)
#
# output = '../resources/video_2_sol.mp4'
# clip = VideoFileClip("../resources/video_2.mp4")
# out_clip = clip.fl_image(process_an_image)
# out_clip.write_videofile(output, audio=False)
