import cv2
import numpy as np
import subprocess
import os
import time
import easyocr
from PIL import Image, ImageDraw, ImageFont
from logger_handler import logger

class ScreenAutomation:
    def __init__(self):
        self.reader = easyocr.Reader(['ch_sim'])
        self.text_to_find = ["进入避难所", "我知道了", "购物", "760,"]  # 要查找的文本列表
        self.save_path = "D:\\CODE\\AUTOMATED_YHTJ_QA\\out_files\\screenshots"
        self.marked_path = "D:\\CODE\\AUTOMATED_YHTJ_QA\\out_files\\marked_screens"

        self._create_directory(self.save_path)
        self._create_directory(self.marked_path)

    def _create_directory(self, path):
        """创建目录"""
        if not os.path.exists(path):
            os.makedirs(path)

    def _run_cmd(self, cmd):
        """运行命令并检查结果"""
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True)
            return result.stdout.decode()
        except subprocess.CalledProcessError as e:
            logger.error("命令执行失败", exc_info=True)
            raise

    def _capture_screen(self):
        """捕获屏幕截图"""
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f'screenshot_{timestamp}.png'
        full_path = os.path.join(self.save_path, filename)
        try:
            self._run_cmd(f'adb shell screencap -p /sdcard/{filename}')
            self._run_cmd(f'adb pull /sdcard/{filename} {full_path}')
            self._run_cmd(f'adb shell rm /sdcard/{filename}')  # 删除设备上的临时文件
            return full_path
        except Exception as e:
            logger.error("捕获屏幕截图失败", exc_info=True)
            return None

    def _draw_bbox(self, result_image, bbox, text):
        """在图像上绘制边界框和文本标记"""
        try:
            image = Image.fromarray(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(image)

            font_path = "C:\\Windows\\Fonts\\STKAITI.TTF"  # 确保这个路径是正确的
            font = ImageFont.truetype(font_path, 48)

            draw.rectangle([(bbox[0][0], bbox[0][1]), (bbox[2][0], bbox[2][1])], outline=(0, 255, 0), width=2)
            draw.text((bbox[0][0], bbox[0][1] - 20), text, font=font, fill=(225, 0, 255))

            result_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            return result_image
        except Exception as e:
            logger.error("绘制边界框和文本失败：{}".format(e), exc_info=True)
            return result_image

    def _draw_click_point(self, result_image, x, y, radius=15, color=(0, 255, 0)):
        """在图像上绘制点击点"""
        if 0 <= x < result_image.shape[1] and 0 <= y < result_image.shape[0]:
            cv2.circle(result_image, (x, y), radius, color, -1)
        return result_image

    def _click_position(self, x, y, result_image):
        """模拟点击操作，并在图像上绘制点击点"""
        try:
            self._run_cmd(f'adb shell input tap {x} {y}')
            time.sleep(2)
            # 绘制点击点
            result_image = self._draw_click_point(result_image, x, y, radius=15, color=(0, 255, 0))
            return result_image
        except Exception as e:
            logger.error("点击操作失败", exc_info=True)
            return result_image

    def _find_target_text(self, text):
        """检查文本是否包含目标文本"""
        return any(target_text in text for target_text in self.text_to_find)

    def _process_found_text(self, result_image, bbox, text, x_center, y_center):
        """处理找到的文本"""
        result_image = self._draw_bbox(result_image, bbox, text)
        result_image = self._draw_click_point(result_image, x_center, y_center, radius=15, color=(0, 255, 0))
        print(f"边界框中心坐标：({x_center}, {y_center})")
        return result_image

    def _handle_special_clicks(self, text, result_image):
        """处理特殊文本点击"""
        special_clicks = {
            "前往": (1815, 63),
            "收藏图鉴": (1815, 63),
            "神秘罗盘": (1815, 63),
            "常规活动": (1815, 63),
        }
        for keyword, (x, y) in special_clicks.items():
            if keyword in text:
                logger.info(f"检测到:{text} ,点击位置 {x},{y}")
                result_image = self._click_position(x, y, result_image)
                return True, result_image
        return False, result_image

    def _handle_special_texts(self, text, result_image, bbox, x_center, y_center):
        """处理特殊文本"""
        if text == "登录" or text == "商店":
            result_image = self._process_found_text(result_image, bbox, text, x_center, y_center)
            logger.info(f"匹配文本{text},点击位置 ({x_center}, {y_center})")
            result_image = self._click_position(x_center, y_center, result_image)

        elif self._handle_special_clicks(text, result_image)[0]:
            pass  # 如果已经处理了特殊点击，不需要进一步操作

        elif any(target_text in text for target_text in ["已达到购买上限", "商品库存不足"]):
            logger.info(f"找到结束条件：{text}")
            return True, result_image
        return False, result_image

    def find_and_click_text(self):
        """在屏幕截图中查找并点击特定文字"""
        screen_path = self._capture_screen()
        if screen_path is None:
            return False, None

        result_image = cv2.imread(screen_path)
        if result_image is None:
            logger.error("无法读取屏幕截图")
            return False, None

        result = self.reader.readtext(screen_path)
        save_image = False
        for (bbox, text, prob) in result:
            print(f"检测到文本：{text}")
            x_center = int((bbox[0][0] + bbox[2][0]) / 2)
            y_center = int((bbox[0][1] + bbox[2][1]) / 2)

            found, result_image = self._handle_special_texts(text, result_image, bbox, x_center, y_center)
            if found:
                save_image = True
                if "已达到购买上限" in text or "商品库存不足" in text:
                    # 如果找到结束条件，则保存图像并返回True以退出循环
                    if save_image:
                        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
                        marked_path = os.path.join(self.marked_path, f'marked_scr_{timestamp}.png')
                        cv2.imwrite(marked_path, result_image)
                        logger.info(f"标记后的图像已保存到 {marked_path}")
                    return True, result_image  # 直接返回True以退出循环

            if self._find_target_text(text):
                result_image = self._process_found_text(result_image, bbox, text, x_center, y_center)
                result_image = self._click_position(x_center, y_center, result_image)
                save_image = True
                time.sleep(2)
                logger.info(f"匹配文本:{text} ,点击位置 ({x_center}, {y_center})")

        if save_image:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            marked_path = os.path.join(self.marked_path, f'marked_scr_{timestamp}.png')
            cv2.imwrite(marked_path, result_image)
            logger.info(f"标记后的图像已保存到 {marked_path}")

        return False, result_image

    def run_main(self):
        """主函数"""
        max_loops = 30  # 设置最大循环次数
        loop_count = 0  # 初始化循环计数器

        while loop_count < max_loops:
            found, result_image = self.find_and_click_text()
            if found:
                break  # 如果找到“已达到购买上限”，则退出循环
            time.sleep(5)  # 等待5


if __name__ == '__main__':
    ScreenAutomation().run_main()