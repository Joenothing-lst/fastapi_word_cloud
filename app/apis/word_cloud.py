import io
import json
from io import BytesIO

import pandas as pd
from wordcloud import WordCloud

import config
from app.services.ali_oss import OssClient
from app.services.jieba_cut import gen_word_cloud_data, load_user_dict      # 方便引用
from app.services.util import get_uuid4

ali_oss_client = OssClient()


def word_cloud_img(wc_data, mask=None, colors='Reds'):
    """
    生成词云

    :param wc_data: 词云数据
    :param img_name: 词云图片名称
    :return: 词云图片路径
    """

    wc = WordCloud(
        scale=6,  # 放大倍数
        height=100,  # 图片高度
        width=150,  # 图片宽度
        # mask=mask,                  # 背景图
        font_path=config.word_cloud_font_path,  # 字体路径
        # margin=1,                 # 字间隔
        max_font_size=50,  # 最大字号
        min_font_size=3,  # 最小字号
        background_color='White',  # 背景颜色
        relative_scaling=1,  # 词频和字体大小的关联性
        prefer_horizontal=1,  # 水平方向排版概率
        # stopwords=stopwords,      # 停用词
        mode='RGBA',  # 背景透明, 'RGB'为不透明
        colormap=colors,  # 颜色
        # include_numbers=False,    # 是否包含数字
        # repeat=True               # 是否重复
    )
    # 根据给定词频生成词云
    wc.generate_from_frequencies(wc_data)

    # 将词云对象转换为图片，再转换为二进制流
    img = wc.to_image()
    img_io = BytesIO()
    img.save(img_io, 'PNG')

    # 上传图片到oss
    img_name = get_uuid4()
    img_path = f'word_cloud/{img_name}.png'
    oss_img_path = ali_oss_client.put_object(img_path, img_io.getvalue())

    return oss_img_path


def save_word_cloud_result(file_name, file_data, file_type='xlsx'):
    """
    保存文件到oss

    :param file_name: 文件名
    :param file_data: 文件数据
    :param file_type: 文件类型
    :return: 文件路径
    """

    file = io.BytesIO()

    if isinstance(file_data, list):
        with pd.ExcelWriter(file) as writer:
            for data in file_data:
                df = pd.DataFrame(data['word_data']).T
                df.to_excel(writer, sheet_name=f"标签{file_data.index(data) + 1}")

    else:
        if file_type == 'xlsx':
            df = pd.DataFrame(file_data['word_data']).T
            df.to_excel(file)
        elif file_type == 'csv':
            df = pd.DataFrame(file_data['word_data']).T
            df.to_csv(file)
        elif file_type == 'json':
            json.dump(file_data['word_data'], file)
        else:
            return None

    file_path = f'word_cloud_file/{file_name}'
    oss_file_path = ali_oss_client.put_object(file_path, file.getvalue())

    return oss_file_path


if __name__ == '__main__':
    # load_user_dict()
    # wc_data = gen_word_cloud_data('/Users/lst/Downloads/word_cloud.xlsx')
    # word_cloud_img(wc_data)
    # save_word_cloud_result('word_cloud.xlsx', wc_data)
    print(save_word_cloud_result('test', [{'word_data': {'1': {'a': 1, 'b': 2, 'c': 3},
                                                         '2': {'a': 4, 'b': 5, 'c': 6}}},
                                          {'word_data': {'1': {'a': 7, 'b': 8, 'c': 9},
                                                         '2': {'a': 4, 'b': 5, 'c': 6}}}], 'xlsx')
          )
