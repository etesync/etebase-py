import typing as t
import functools

import msgpack

from .etebase_python import CollectionAccessLevel, PrefetchOption, Utils  # noqa
from . import etebase_python


def cached_property(f):
    return property(functools.lru_cache(maxsize=1)(f))


def msgpack_encode(content: t.Union[t.Dict, t.List]) -> bytes:
    ret = msgpack.packb(content, use_bin_type=True)
    assert ret is not None
    return ret


def msgpack_decode(content: bytes):
    return msgpack.unpackb(content, raw=False)


def _inner(it):
    return getattr(it, "_inner", None)


DEFAULT_SERVER_URL = etebase_python.Client.get_default_server_url()


def random_bytes(size: int):
    return bytes(etebase_python.Utils.randombytes(size))


def pretty_fingerprint(content):
    return etebase_python.Utils.pretty_fingerprint(content)


class Base64Url:
    @classmethod
    def from_base64(cls, value):
        return bytes(Utils.from_base64(value))

    to_base64 = Utils.to_base64


class Client:
    def __init__(self, client_name, server_url=DEFAULT_SERVER_URL):
        self._inner = etebase_python.Client.new(client_name, server_url)

    @property
    def server_url(self) -> str:
        raise RuntimeError("This property has no getter!")

    @server_url.setter
    def server_url(self, value: str):
        self._inner.set_server_url(value)


class User:
    def __init__(self, username: str, email: str):
        self._inner = etebase_python.User(username, email)

    @property
    def username(self) -> str:
        return self._inner.get_username()

    @username.setter
    def username(self, value: str):
        self._inner.set_username(value)

    @property
    def email(self) -> str:
        return self._inner.get_email()

    @email.setter
    def email(self, value: str):
        self._inner.set_email(value)


class Account:
    def __init__(self, inner: etebase_python.Account):
        self._inner = inner

    @classmethod
    def is_etebase_server(cls, client: Client):
        return etebase_python.Account.is_etebase_server(client._inner)

    @classmethod
    def login(cls, client: Client, username: str, password: str):
        return cls(etebase_python.Account.login(client._inner, username, password))

    @classmethod
    def login_key(cls, client: Client, username: str, key: bytes):
        return cls(etebase_python.Account.login_key(client._inner, username, key))

    @classmethod
    def signup(cls, client: Client, user: User, password: str):
        return cls(etebase_python.Account.signup(client._inner, user._inner, password))

    @classmethod
    def signup_key(cls, client: Client, user: User, key: bytes):
        return cls(etebase_python.Account.signup_key(client._inner, user._inner, key))

    def fetch_token(self):
        self._inner.fetch_token()

    def force_server_url(self, api_base: str):
        self._inner.force_server_url(api_base)

    def change_password(self, password: str):
        self._inner.change_password(password)

    def logout(self):
        self._inner.logout()

    def get_collection_manager(self):
        return CollectionManager(self._inner.get_collection_manager())

    def get_invitation_manager(self):
        return CollectionInvitationManager(self._inner.get_invitation_manager())

    def save(self, encryption_key: t.Optional[bytes]):
        return self._inner.save(encryption_key)

    @classmethod
    def restore(cls, client: Client, account_data_stored: str, encryption_key: t.Optional[bytes]):
        return cls(etebase_python.Account.restore(client._inner, account_data_stored, encryption_key))


class RemovedCollection:
    def __init__(self, inner: etebase_python.RemovedCollection):
        self._inner = inner

    @property
    def uid(self):
        return self._inner.get_uid()


class CollectionListResponse:
    def __init__(self, inner: etebase_python.CollectionListResponse):
        self._inner = inner

    @cached_property
    def stoken(self):
        return self._inner.get_stoken()

    @property
    def data(self):
        return map(lambda x: Collection(x), self._inner.get_data())

    @cached_property
    def done(self):
        return self._inner.is_done()

    @property
    def removed_memberships(self):
        return map(lambda x: RemovedCollection(x), self._inner.get_removed_memberships())


class ItemListResponse:
    def __init__(self, inner: etebase_python.ItemListResponse):
        self._inner = inner

    @cached_property
    def stoken(self):
        return self._inner.get_stoken()

    @property
    def data(self):
        return map(lambda x: Item(x), self._inner.get_data())

    @cached_property
    def done(self):
        return self._inner.is_done()


class ItemRevisionsListResponse:
    def __init__(self, inner: etebase_python.ItemRevisionsListResponse):
        self._inner = inner

    @cached_property
    def iterator(self):
        return self._inner.get_iterator()

    @property
    def data(self):
        return map(lambda x: Item(x), self._inner.get_data())

    @cached_property
    def done(self):
        return self._inner.is_done()


class FetchOptions:
    def __init__(self):
        self._inner = etebase_python.FetchOptions()

    def limit(self, value: int):
        self._inner.limit(value)
        return self

    def prefetch(self, value: PrefetchOption):
        self._inner.prefetch(value)
        return self

    def with_collection(self, value: bool):
        self._inner.with_collection(value)
        return self

    def iterator(self, value: t.Optional[str]):
        self._inner.iterator(value)
        return self

    def stoken(self, value: t.Optional[str]):
        self._inner.stoken(value)
        return self


def _verify_col_meta(meta: t.Dict):
    if "name" not in meta:
        raise RuntimeError("Collection meta must have a name field")
    return meta


class CollectionManager:
    def __init__(self, inner: etebase_python.CollectionManager):
        self._inner = inner

    def fetch(self, col_uid: str, fetch_options: t.Optional[FetchOptions]=None):
        return Collection(self._inner.fetch(col_uid, _inner(fetch_options)))

    def create(self, col_type: str, meta: t.Dict, content: bytes):
        meta_packed = msgpack_encode(_verify_col_meta(meta))
        return self.create_raw(col_type, meta_packed, content)

    def create_raw(self, col_type: str, meta: bytes, content: bytes):
        return Collection(self._inner.create_raw(col_type, meta, content))

    def get_item_manager(self, col: "Collection"):
        return ItemManager(self._inner.get_item_manager(col._inner))

    def list(self, col_type: t.Union[str, t.List[str]], fetch_options: t.Optional[FetchOptions]=None):
        if isinstance(col_type, str):
            return CollectionListResponse(self._inner.list(col_type, _inner(fetch_options)))
        else:
            return CollectionListResponse(self._inner.list_multi(list(col_type), _inner(fetch_options)))

    def upload(self, collection: "Collection", fetch_options: t.Optional[FetchOptions]=None):
        self._inner.upload(collection._inner, _inner(fetch_options))

    def transaction(self, collection: "Collection", fetch_options: t.Optional[FetchOptions]=None):
        self._inner.transaction(collection._inner, _inner(fetch_options))

    def cache_load(self, cached: bytes):
        return Collection(self._inner.cache_load(cached))

    def cache_save(self, collection: "Collection", with_content: bool=True):
        if with_content:
            return bytes(self._inner.cache_save_with_content(collection._inner))
        else:
            return bytes(self._inner.cache_save(collection._inner))

    def get_member_manager(self, collection: "Collection"):
        return CollectionMemberManager(self._inner.get_member_manager(collection._inner))


class ItemManager:
    def __init__(self, inner: etebase_python.ItemManager):
        self._inner = inner

    def fetch(self, col_uid, fetch_options: t.Optional[FetchOptions]=None):
        return Item(self._inner.fetch(col_uid, _inner(fetch_options)))

    def create(self, meta: t.Dict, content: bytes):
        meta_packed = msgpack_encode(meta)
        return self.create_raw(meta_packed, content)

    def create_raw(self, meta: bytes, content: bytes):
        return Item(self._inner.create_raw(meta, content))

    def list(self, fetch_options: t.Optional[FetchOptions]=None):
        return ItemListResponse(self._inner.list(_inner(fetch_options)))

    def item_revisions(self, item: "Item", fetch_options: t.Optional[FetchOptions]=None):
        return ItemRevisionsListResponse(self._inner.item_revisions(item._inner, _inner(fetch_options)))

    def fetch_updates(self, items: t.List["Item"], fetch_options: t.Optional[FetchOptions]=None):
        items_inner = list(map(lambda x: x._inner, items))
        return ItemListResponse(self._inner.fetch_updates(items_inner, _inner(fetch_options)))

    def fetch_multi(self, items_uids: t.List[str], fetch_options: t.Optional[FetchOptions]=None):
        return ItemListResponse(self._inner.fetch_multi(items_uids, _inner(fetch_options)))

    def batch(self, items: t.List["Item"], deps: t.List["Item"]=None, fetch_options: t.Optional[FetchOptions]=None):
        items_inner = list(map(lambda x: x._inner, items))
        deps_inner = list(map(lambda x: x._inner, deps)) if deps is not None else None
        self._inner.batch(items_inner, deps_inner, _inner(fetch_options))

    def transaction(self, items: t.List["Item"], deps: t.List["Item"]=None, fetch_options: t.Optional[FetchOptions]=None):
        items_inner = list(map(lambda x: x._inner, items))
        deps_inner = list(map(lambda x: x._inner, deps)) if deps is not None else None
        self._inner.transaction(items_inner, deps_inner, _inner(fetch_options))

    def download_content(self, item: "Item"):
        self._inner.download_content(item._inner)

    def upload_content(self, item: "Item"):
        self._inner.upload_content(item._inner)

    def cache_load(self, cached: bytes):
        return Item(self._inner.cache_load(cached))

    def cache_save(self, item: "Item", with_content: bool=True):
        if with_content:
            return bytes(self._inner.cache_save_with_content(item._inner))
        else:
            return bytes(self._inner.cache_save(item._inner))


class Collection:
    def __init__(self, inner: etebase_python.Collection):
        self._inner = inner

    def verify(self):
        return self._inner.verify()

    @cached_property
    def meta(self):
        return msgpack_decode(bytes(self._inner.get_meta_raw()))

    @meta.setter
    def meta(self, value: t.Any):
        self.__class__.meta.fget.cache_clear()
        self.__class__.meta_raw.fget.cache_clear()
        value = msgpack_encode(_verify_col_meta(value))
        self._inner.set_meta_raw(value)

    @cached_property
    def meta_raw(self):
        return self._inner.get_meta_raw()

    @meta_raw.setter
    def meta_raw(self, value: bytes):
        self.__class__.meta.fget.cache_clear()
        self.__class__.meta_raw.fget.cache_clear()
        self._inner.set_meta_raw(value)

    @cached_property
    def content(self):
        return bytes(self._inner.get_content())

    @content.setter
    def content(self, value: bytes):
        self.__class__.content.fget.cache_clear()
        self._inner.set_content(value)

    def delete(self):
        self._inner.delete()

    @property
    def deleted(self):
        return self._inner.is_deleted()

    @property
    def uid(self):
        return self._inner.get_uid()

    @property
    def etag(self):
        return self._inner.get_etag()

    @property
    def stoken(self):
        return self._inner.get_stoken()

    @property
    def access_level(self):
        return self._inner.get_access_level()

    @property
    def item(self):
        return Item(self._inner.get_item())

    @cached_property
    def collection_type(self):
        return self._inner.get_collection_type()


class Item:
    def __init__(self, inner: etebase_python.Item):
        self._inner = inner

    def verify(self):
        return self._inner.verify()

    @cached_property
    def meta(self):
        return msgpack_decode(bytes(self._inner.get_meta_raw()))

    @meta.setter
    def meta(self, value: t.Any):
        self.__class__.meta.fget.cache_clear()
        self.__class__.meta_raw.fget.cache_clear()
        value = msgpack_encode(value)
        self._inner.set_meta_raw(value)

    @cached_property
    def meta_raw(self):
        return self._inner.get_meta_raw()

    @meta_raw.setter
    def meta_raw(self, value: bytes):
        self.__class__.meta.fget.cache_clear()
        self.__class__.meta_raw.fget.cache_clear()
        self._inner.set_meta_raw(value)

    @cached_property
    def content(self):
        return bytes(self._inner.get_content())

    @content.setter
    def content(self, value: bytes):
        self.__class__.content.fget.cache_clear()
        self._inner.set_content(value)

    def delete(self):
        self._inner.delete()

    @property
    def deleted(self):
        return self._inner.is_deleted()

    @property
    def missing_content(self):
        return self._inner.is_missing_content()

    @property
    def uid(self):
        return self._inner.get_uid()

    @property
    def etag(self):
        return self._inner.get_etag()


class UserProfile:
    def __init__(self, inner: etebase_python.UserProfile):
        self._inner = inner

    @property
    def pubkey(self):
        return bytes(self._inner.get_pubkey())


class InvitationListResponse:
    def __init__(self, inner: etebase_python.InvitationListResponse):
        self._inner = inner

    @cached_property
    def iterator(self):
        return self._inner.get_iterator()

    @property
    def data(self):
        return map(lambda x: SignedInvitation(x), self._inner.get_data())

    @cached_property
    def done(self):
        return self._inner.is_done()


class CollectionInvitationManager:
    def __init__(self, inner: etebase_python.CollectionInvitationManager):
        self._inner = inner

    def list_incoming(self, fetch_options: t.Optional[FetchOptions]=None):
        return InvitationListResponse(self._inner.list_incoming(_inner(fetch_options)))

    def list_outgoing(self, fetch_options: t.Optional[FetchOptions]=None):
        return InvitationListResponse(self._inner.list_outgoing(_inner(fetch_options)))

    def accept(self, signed_invitation: "SignedInvitation"):
        self._inner.accept(signed_invitation._inner)

    def reject(self, signed_invitation: "SignedInvitation"):
        self._inner.reject(signed_invitation._inner)

    def fetch_user_profile(self, username: str):
        return UserProfile(self._inner.fetch_user_profile(username))

    def invite(self, collection: Collection, username: str, pubkey: bytes, access_level: "CollectionAccessLevel"):
        self._inner.invite(collection._inner, username, pubkey, access_level)

    def disinvite(self, signed_invitation: "SignedInvitation"):
        self._inner.disinvite(signed_invitation._inner)

    @property
    def pubkey(self):
        return self._inner.get_pubkey()


class SignedInvitation:
    def __init__(self, inner: etebase_python.SignedInvitation):
        self._inner = inner

    @property
    def uid(self):
        return self._inner.get_uid()

    @property
    def username(self):
        return self._inner.get_username()

    @property
    def collection(self):
        return self._inner.get_collection()

    @property
    def access_level(self):
        return self._inner.get_access_level()

    @property
    def from_username(self):
        return self._inner.get_username()

    @property
    def from_pubkey(self):
        return bytes(self._inner.get_from_pubkey())


class CollectionMember:
    def __init__(self, inner: etebase_python.CollectionMember):
        self._inner = inner

    @property
    def username(self):
        return self._inner.get_username()

    @property
    def access_level(self):
        return self._inner.get_access_level()


class MemberListResponse:
    def __init__(self, inner: etebase_python.MemberListResponse):
        self._inner = inner

    @cached_property
    def iterator(self):
        return self._inner.get_iterator()

    @property
    def data(self):
        return map(lambda x: CollectionMember(x), self._inner.get_data())

    @cached_property
    def done(self):
        return self._inner.is_done()


class CollectionMemberManager:
    def __init__(self, inner: etebase_python.CollectionMemberManager):
        self._inner = inner

    def list(self, fetch_options: t.Optional[FetchOptions]=None):
        return MemberListResponse(self._inner.list(_inner(fetch_options)))

    def remove(self, username: str):
        self._inner.remove(username)

    def leave(self):
        self._inner.leave()

    def modify_access_level(self, username: str, access_level: CollectionAccessLevel):
        self._inner.modify_access_level(username, access_level)
