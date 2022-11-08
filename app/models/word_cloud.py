from typing import Dict, List, Any

from pydantic import BaseModel

from app.models.base_responce import SuccessResponse


class WordCloudCutResult(BaseModel):
    word_data: Dict[str, Any]
    word_cloud_img_url: str


class WordCloudCutSetting(BaseModel):
    stop_words: List[str]
    similar_words: Dict[str, str]
    user_words: List[str]


class WordCloudData(BaseModel):
    cut_setting: WordCloudCutSetting
    cut_result: List[WordCloudCutResult]


class WordCloudFileData(BaseModel):
    file_name: str
    file_url: str


class WordCloudDownloadSuccessResponse(SuccessResponse):
    data: WordCloudFileData


class WordCloudSuccessResponse(SuccessResponse):
    data: WordCloudData
