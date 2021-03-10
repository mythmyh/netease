"""
Files Pipeline

See documentation in topics/media-pipeline.rst
"""
import functools
import hashlib
from scrapy.pipelines.images import ImagesPipeline
import os


class ImagesPipeline(ImagesPipeline):

    index = 0

    def file_path(self, request, response=None, info=None):
        url = request.url
        md51 = hashlib.md5(url.encode('utf-8')).hexdigest()

        return md51+'.jpg'



 

