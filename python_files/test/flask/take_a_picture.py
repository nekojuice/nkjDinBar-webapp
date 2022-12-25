### 12/11增加拍照功能

import argparse
import os
import sys

# -o為輸出路徑(必要)，-s為拍照編號從幾號開始(預設0)
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
    help="path to output directory")
ap.add_argument("-s", "--start", type=int, default=0,
    help="start number, default is 0")
args = vars(ap.parse_args())

# 告訴你輸出 -o 的路徑存在不
if not os.path.isdir(args['output']):
    print(f'Output directory {args["output"]} does not exist, create first...')
    sys.exit(2)

# 顯示視頻，  p,q = 拍照,離開
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
idx = args['start']
total = 0

while True:
    frame = vs.read()
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("p"):
        p = os.path.sep.join([args["output"], f"{str(idx).zfill(5)}.png"
            ])
        cv2.imwrite(p, frame)
        idx += 1
        total += 1
        print(f'{total} pictures saved...')
    elif key == ord("q"):
        break

print(f"[INFO] {total} images stored")
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()