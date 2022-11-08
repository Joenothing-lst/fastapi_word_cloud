from typing import List, Dict

import pandas as pd
from fastapi import APIRouter, FastAPI, File, Form, UploadFile, Body

from app.apis import word_cloud
from app.models.word_cloud import WordCloudSuccessResponse, WordCloudDownloadSuccessResponse, WordCloudCutResult
from app.services.util import timestr2date

router = APIRouter(
    prefix="/word_cloud",
    tags=['WordCloud'],
)

app = FastAPI()


@router.post("/from_file", response_model=WordCloudSuccessResponse)
async def cut_word_from_file(
        file: UploadFile = File(),
        category: int = Form(),
        setting_file: UploadFile = File(None),
        allow_pos: str = Form('n|nr|ns|nt|nz|vn|a|eng'),
        topk: int = Form(100),
        min_word_count: int = Form(1),
):
    """
    上传文件并进行分词

    :param file: 上传的文件
    :param setting_file: 上传的设置文件
    :param category: 词云类型
    :param allow_pos: 词性
    :param topk: 词云词数
    :param min_word_count: 词云词频
    :return: 词云数据

    """

    file = await file.read()
    if setting_file:
        setting_file = await setting_file.read()

    # 读取文件
    file_data_df: pd.DataFrame = pd.read_excel(file)

    if category == 1:
        # 原文本处理
        text = ''.join(file_data_df['content'].tolist())
        # 分词设置
        stop_words, similar_words_map, user_words = parse_setting_file(setting_file, text)
        # 获取分词结果
        data = word_cloud.gen_word_cloud_data(content=text,
                                              allow_pos=tuple(allow_pos.split('|')),
                                              stop_words=stop_words,
                                              similar_words=similar_words_map,
                                              topk=topk,
                                              min_word_count=min_word_count)

        wc_data = {k: v['count'] for k, v in data.items()}
        # 生成词云图片
        word_cloud_img_url = word_cloud.word_cloud_img(wc_data)

        cut_results = [{
            "word_data": data,
            "word_cloud_img_url": word_cloud_img_url
        }]


    elif category == 2:
        cut_results = []
        # df转换为列表
        file_data_list = file_data_df.to_dict(orient='records')
        text = ''.join([i['content'] for i in file_data_list])
        stop_words, similar_words_map, user_words = parse_setting_file(setting_file, text)

        for i in range(1, 6):
            cut_result = {}
            text = ''.join([j['content'] for j in file_data_list if j[f'tag{i}'] >= 0.25])
            # 获取分词结果
            cut_result['word_data'] = word_cloud.gen_word_cloud_data(content=text,
                                                                     allow_pos=tuple(allow_pos.split('|')),
                                                                     stop_words=stop_words,
                                                                     similar_words=similar_words_map,
                                                                     topk=topk,
                                                                     min_word_count=min_word_count)

            wc_data = {k: v['count'] for k, v in cut_result['word_data'].items()}
            # 生成词云图片
            cut_result['word_cloud_img_url'] = word_cloud.word_cloud_img(wc_data)
            cut_results.append(cut_result)

    else:
        raise Exception('category error')

    return {
        "code": 0,
        "msg": "success",
        "data": {
            "cut_setting": {
                "stop_words": stop_words,
                "similar_words": similar_words_map,
                "user_words": user_words
            },
            "cut_result": cut_results
        }
    }


@router.post("/get_result_file", response_model=WordCloudDownloadSuccessResponse)
async def get_result_file(
        data: List[WordCloudCutResult] = Body(...),
        file_type: str = Body('xlsx'),
):
    """
    获取分词结果文件, 支持xlsx, csv, json, 返回oss地址

    :param data: 分词结果
    :param file_type: 文件类型, xlsx, csv, json
    :return:
    """
    assert file_type in ['xlsx', 'csv', 'json'], 'file_type must be xlsx, csv or json'
    file_name = f'word_cloud_result_{timestr2date(format="%Y_%m_%d_%H_%M")}.{file_type}'
    data = [i.dict() for i in data]

    file_url = word_cloud.save_word_cloud_result(file_name, data, file_type)

    return {
        "code": 0,
        "msg": "success",
        "data": {
            "file_url": file_url,
            "file_name": file_name,
        }
    }


def parse_setting_file(file, text):
    if file:
        # 读取设置文件
        similar_words_df: pd.DataFrame = pd.read_excel(file, sheet_name='similar_word')
        stop_words_df: pd.DataFrame = pd.read_excel(file, sheet_name='stop_word')
        user_words_df: pd.DataFrame = pd.read_excel(file, sheet_name='user_word')

        # 停词处理
        stop_words: List[str] = stop_words_df['stop_word'].tolist()
        # 同义词处理
        similar_words_map: Dict[str, str] = dict(zip(similar_words_df['main_word'].tolist(),
                                                     [i.replace('｜', '|') for i in similar_words_df['similar_word'].tolist()]))
        # 自定义词处理
        user_words: List[str] = word_cloud.load_user_dict(text,
                                                          user_words_df['user_word'].tolist() + [i for i in similar_words_map.keys()])
    else:
        stop_words = []
        similar_words_map = {}
        user_words = []

    return stop_words, similar_words_map, user_words
