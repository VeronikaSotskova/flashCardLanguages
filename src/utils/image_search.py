import abc
from enum import Enum

import requests
from requests import JSONDecodeError

from src.config import settings
from src.utils.uow import BaseUnitOfWork
from src.models import File


class HttpMethods(Enum):
    HTTP_GET = 'get'
    HTTP_POST = 'post'


class BaseImageSearchAPIClient(abc.ABC):
    method: HttpMethods = HttpMethods.HTTP_GET
    base_url: str
    search_method_name: str

    def __init__(self):
        self._data = {}
        self._headers = {}
        self._result_response = {}

    def _make_request(self, data: dict = None, headers: dict = None):
        if data:
            self._data = {
                **self._data,
                **data
            }
        if headers:
            self._headers = {
                **self._headers,
                **headers
            }
        return self

    def _send_request(self, method: HttpMethods, name: str):
        kwargs = {}
        if self._data and method == HttpMethods.HTTP_GET:
            kwargs['params'] = self._data
        elif self._data and method == HttpMethods.HTTP_POST:
            kwargs['data'] = self._data

        if self._headers:
            kwargs['headers'] = self._headers

        return requests.request(method.value, f"{self.base_url}/{name}", **kwargs)

    def _get(self):
        try:
            response = self._send_request(HttpMethods.HTTP_GET, self.search_method_name)
            self._result_response = response.json()
        except JSONDecodeError:
            pass
        return self

    def _get_headers(self, *args, **kwargs) -> dict:
        return {}

    @abc.abstractmethod
    def _get_params(self, query: str, lang: str) -> dict:
        ...

    @abc.abstractmethod
    def _prepare_result(self) -> str | None:
        ...

    def search_image(self, query: str, lang: str, *args, **kwargs) -> str | None:
        return self._make_request(
            data=self._get_params(query, lang),
            headers=self._get_headers(*args, **kwargs)
        )._get()._prepare_result()

    @abc.abstractmethod
    async def save_to_db(
        self,
        uow: BaseUnitOfWork,
        query: str,
        lang: str
    ) -> File | None:
        ...


class GiphyClient(BaseImageSearchAPIClient):
    base_url = 'https://api.giphy.com/v1/gifs'
    search_method_name = 'search'

    def _get_params(self, query: str, lang: str) -> dict:
        return {
            'api_key': settings.GIPHY_KEY,
            'q': query,
            'limit': 1,
            'offset': 0,
            'rating': 'g',
            'lang': lang,
        }

    def _prepare_result(self) -> str | None:
        if not self._result_response:
            return

        status = self._result_response.get('meta', {}).get('status')
        if status != 200:
            return

        images = self._result_response.get('data', [])
        if not images:
            return

        return images[0].get('images', {}).get('original', {}).get('url')

    async def save_to_db(
        self,
        uow: BaseUnitOfWork,
        query: str,
        lang: str
    ) -> File | None:
        return await uow.files.create_video(self.search_image(query, lang), query)


class UnsplashClient(BaseImageSearchAPIClient):
    base_url = 'https://api.unsplash.com/search'
    search_method_name = 'photos'

    def _get_params(self, query: str, lang: str) -> dict:
        return {
            'query': query,
            'per_page': 1
        }

    def _get_headers(self, *args, **kwargs) -> dict:
        return {
            'Authorization': f'Client-ID {settings.UNSPLASH_ACCESS_KEY}'
        }

    def _prepare_result(self) -> str | None:
        if not self._result_response:
            return

        images = self._result_response.get('results', [])
        if not images:
            return
        return images[0].get('urls', {}).get('small')

    async def save_to_db(
        self,
        uow: BaseUnitOfWork,
        query: str,
        lang: str
    ) -> File | None:
        image = self.search_image(query, lang)
        if image:
            return await uow.files.create_image(self.search_image(query, lang), query)


class ImageSearcher:
    def __init__(self, client: BaseImageSearchAPIClient):
        self._client = client

    @property
    def client(self) -> BaseImageSearchAPIClient:
        return self._client

    @client.setter
    def client(self, client: BaseImageSearchAPIClient):
        self._client = client

    async def find(
        self,
        uow: BaseUnitOfWork,
        query: str,
        lang: str
    ) -> File | None:
        return await self.client.save_to_db(uow, query, lang)
