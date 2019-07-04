# !/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2019-07-04 15:07
# @Author  : liukang.hero
# @FileName: image_manage.py

import os
import uuid
import pytesseract
from PIL import Image


class TmallImageRecognition(object):
    '''
    识别图片中的公司名称。
    1. 图片截图
    2. 图片去水印
    3. 图片汉字识别

    '''

    def __init__(self, image_path="image"):
        self.image_path = os.path.join(os.getcwd(), image_path)
        self.check_mkdir()

    def get_image_path(self, image_name):
        return os.path.join(self.image_path, image_name)

    def split_image(self, image_name, image_split_name, x=0, y=40, h=40):
        '''
        图片裁剪，用于降低cpu消耗，快速返回相关的结果
        '''
        image_path = image_name
        image_split_path = self.get_image_path(image_split_name)
        im = Image.open(image_path)
        '''
        裁剪：传入一个元组作为参数
        元组里的元素分别是：（距离图片左边界距离x， 距离图片上边界距离y，距离图片左边界距离+裁剪框宽度x+w，距离图片上边界距离+裁剪框高度y+h）
        '''
        try:
            w = im.size[1] + 100
            region = im.crop((x, y, x + w, y + h))
            region.save(image_split_path)

            return "succ"
        except:
            return "fail"

    def modify_pixel(self, image_split_name, image_res_name):
        '''
        去除水印，同时将背景色设置成白色
        :return:返回成功或者失败的表示，正常 succ 异常出错 fail
        '''
        try:
            image_split_path = self.get_image_path(image_split_name)
            image_res_path = self.get_image_path(image_res_name)
            im = Image.open(image_split_path)
            width = im.size[0]  # 宽度
            height = im.size[1]  # 长度

            # 遍历图片像素点，如果这里全部都是红色的的那么就删除
            for x in range(width):
                for y in range(height):
                    r, g, b, alpha = im.getpixel((x, y))
                    # 将黑色的底片，设置成白色
                    if r == 0 and g == 0 and b == 0:
                        r = g = b = 255
                        im.putpixel((x, y), (r, g, b, 255))

                    # 水印像素，将其设置成白色，去除水印
                    if r == 229 and g == 229 and b == 229:
                        r = g = b = 255
                        im.putpixel((x, y), (r, g, b, 255))
            im.save(image_res_path)
            return "succ"

        except:
            return "fail"

    def image_recognition(self, image_res_name, image_split_name):
        '''
        图片识别将文字转换成图片
        :return:
        '''

        try:
            image_split_path = self.get_image_path(image_split_name)
            image_res_path = self.get_image_path(image_res_name)
            image = Image.open(image_res_path)

            # 这里需要下载好相关的语料包 https://github.com/tesseract-ocr/tessdata/blob/master/chi_sim.traineddata
            # 默认都是中文的，所以需要下载好，将其放入到 安装目录下的 /usr/local/share/tessdata/chi_sim.traineddata

            # 设置 tesseract 的路径，如果已经配置好 系统变量。那么就不用使用这个
            # pytesseract.pytesseract.tesseract_cmd = "/usr/local/tesseract/bin/tesseract"

            code = pytesseract.image_to_string(image, lang="chi_sim")
            code = code.replace("\t", "").replace("\n", "").replace(" ", "").replace(" ", ""). \
                replace("AM", "").replace("企业名称:", "")
            self.delete_image([image_split_path, image_res_path])

            return "succ", code
        except Exception as e:
            print(e)
            return "fail", ""

    def delete_image(self, file_name_list):
        '''
        删除相关的目录
        :return:
        '''
        for file_name in file_name_list:
            if os.path.exists(file_name):
                # 删除文件，可使用以下两种方法。
                os.remove(file_name)
            else:
                print('no such file:%s' % file_name)

    def check_mkdir(self):
        '''
        如果没有改目录，那么就创建相应的目录
        :return:
        '''
        try:
            if not os.path.exists(self.image_path):
                os.mkdir(self.image_path)
        except:
            pass

    def get_image_type(self, image_name):
        try:
            image_type_list = image_name.split('.')
            image_type = image_type_list[-1]
            return image_type
        except Exception as e:
            return "png"

    def run(self, image_name):
        uuid_image_name = str(uuid.uuid1())
        image_type = self.get_image_type(image_name)
        image_split_name = "{}_split.{}".format(uuid_image_name, image_type)
        image_res_name = "{}_res.{}".format(uuid_image_name, image_type)
        split_status = self.split_image(image_name, image_split_name)
        if split_status == "succ":
            self.modify_pixel(image_split_name, image_res_name)
            status, company_name = self.image_recognition(image_res_name, image_split_name)

            return status, company_name
        else:
            return "fail", "切割图片失败"


if __name__ == '__main__':
    tmall_image_recognition = TmallImageRecognition()
    status, company_name = tmall_image_recognition.run(image_name="小米.png")
    print(company_name)
