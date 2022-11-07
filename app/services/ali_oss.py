import config
import oss2



class OssClient:
    def __init__(self, access_key_id=config.aliyun_access_key_id, access_key_secret=config.aliyun_access_key_secret,
                 endpoint=config.oss_endpoint, bucket=config.oss_bucket, domain=config.oss_domain_download):
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket)
        self.domain = domain


    def put_object(self, target_file, content):
        """
        上传文件至oss
        :return: oss_file_url
        """
        target_file = target_file.lstrip('/')

        res = self.bucket.put_object(target_file, content)
        if res.status == 200:
            # 返回文件oss地址
            oss_file_url = f'{self.domain}/{target_file}'
            return oss_file_url

        return ""
