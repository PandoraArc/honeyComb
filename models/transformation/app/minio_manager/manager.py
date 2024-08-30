import io
import logging
from tempfile import NamedTemporaryFile

from minio import Minio, S3Error
from minio.commonconfig import Tags

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MinIoManager:
    def __init__(
        self,
        minio_endpoint: str = "minio:9000",
        bukket_name: str = "honeycomb",
        access_key: str = "minio",
        secret_key: str = "minioHoneycomb",
        secure: bool = False,
    ):
        self.minio_client = Minio(
            minio_endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )
        self.bukket_name = bukket_name
        found = self.minio_client.bucket_exists(bukket_name)
        if not found:
            self.minio_client.make_bucket(bukket_name)
        else:
            logger.info(f"Bucket {bukket_name} already exists")

    def list_objects(self, path_name, recursive=True):
        """
        List objects in a path. (List recursively by default)
        :param path_name: str
        :param recursive: boolean
        :return: [(object, tags)]
        """
        client = self.minio_client
        objects = client.list_objects(
            self.bukket_name, prefix=path_name, recursive=recursive
        )
        objs = []
        print("list_objects", path_name)
        for obj in objects:
            attr = "-"
            mtags = None
            if obj.is_dir:
                attr = "D"
            else:
                mtags = self.get_object_tags(obj.object_name)
            print("-", attr, obj.bucket_name, obj.object_name)
            print("--", mtags)
            objs.append((obj, mtags))
        return objs

    def get_object_content(self, path_name):
        """
        Get content of an object
        :param path_name:
        :return: content
        """
        client = self.minio_client
        try:
            res = client.get_object(self.bukket_name, path_name)
            content = res.data.decode()
        finally:
            res.close()
            res.release_conn()
        return content

    def get_object_tags(self, path_name) -> dict:
        client = self.minio_client
        try:
            tags = client.get_object_tags(self.bukket_name, path_name)
        except S3Error:
            tags = None
        return tags

    def put_object_stream(self, path_name, stream: io.BytesIO, length, tags=None):
        client = self.minio_client
        res = client.put_object(
            self.bukket_name, path_name, stream, length, part_size=5 * 1024 * 1024
        )
        self.set_object_tags(path_name, tags)
        return res

    def get_file_object(self, path_name, file_path=None):
        """
        Get an object as a file
        :param path_name:
        :param file_path:
        :return: (file_path, minio object)
        """
        client = self.minio_client
        if file_path is None:
            temp_file = NamedTemporaryFile(delete=False)
            file_path = temp_file.name
        try:
            res = client.fget_object(self.bukket_name, path_name, file_path)
            mtags = self.get_object_tags(res.object_name)
        except ValueError:
            return (None, None, None)
        except S3Error:
            return (None, None, None)
        return (file_path, res, mtags)

    def set_object_tags(self, path_name, tags):
        """
        set tags of an object. Use tags=None to remove all tags
        :param path_name:
        :param tags: {'key':'value'}
        :return:
        """
        client = self.minio_client
        if tags is None:
            client.delete_object_tags(self.bukket_name, path_name)
            return
        mtags = Tags.new_object_tags()
        if tags is not None:
            for k, v in tags.items():
                mtags[k] = str(v)
        client.set_object_tags(self.bukket_name, path_name, mtags)
        return