import functools

import msgpack

from .etebase_python import CollectionAccessLevel, PrefetchOption  # noqa
from . import etebase_python


def cached_property(f):
    return property(functools.lru_cache(maxsize=1)(f))


def msgpack_encode(content):
    return msgpack.packb(content, use_bin_type=True)


def msgpack_decode(content):
    return msgpack.unpackb(content, raw=False)


def _inner(it):
    return getattr(it, "_inner", None)


DEFAULT_SERVER_URL = etebase_python.Client.get_default_server_url()


def random_bytes(size):
    return bytes(etebase_python.Utils.randombytes(size))


def pretty_fingerprint(content):
    return etebase_python.Utils.pretty_fingerprint(content)


class Base64Url:
    @classmethod
    def from_base64(cls, value):
        return bytes(etebase_python.Utils.from_base64(value))

    @classmethod
    def to_base64(cls, value):
        return etebase_python.Utils.to_base64(value)


class Client:
    def __init__(self, client_name, server_url=DEFAULT_SERVER_URL):
        self._inner = etebase_python.Client.new(client_name, server_url)

    @property
    def set_server_url(self):
        raise RuntimeError("This property has no getter!")

    @set_server_url.setter
    def set_server_url(self, value):
        self._inner.set_server_url(value)


class User:
    def __init__(self, username, email):
        self._inner = etebase_python.User(username, email)

    @property
    def username(self):
        return self._inner.get_username()

    @username.setter
    def username(self, value):
        self._inner.set_username(value)

    @property
    def email(self):
        return self._inner.get_email()

    @email.setter
    def email(self, value):
        self._inner.set_email(value)


class Account:
    def __init__(self, inner):
        self._inner = inner

    @classmethod
    def is_etebase_server(cls, client):
        return etebase_python.Account.is_etebase_server(client._inner)

    @classmethod
    def login(cls, client, username, password):
        return cls(etebase_python.Account.login(client._inner, username, password))

    @classmethod
    def signup(cls, client, user, password):
        return cls(etebase_python.Account.signup(client._inner, user._inner, password))

    def fetch_token(self):
        self._inner.fetch_token()

    def force_server_url(self, api_base):
        self._inner.force_server_url(api_base)

    def change_password(self, password):
        self._inner.change_password(password)

    def logout(self):
        self._inner.logout()

    def get_collection_manager(self):
        return CollectionManager(self._inner.get_collection_manager())

    def get_invitation_manager(self):
        return CollectionInvitationManager(self._inner.get_invitation_manager())

    def save(self, encryption_key):
        return self._inner.save(encryption_key)

    @classmethod
    def restore(cls, client, account_data_stored, encryption_key):
        return cls(etebase_python.Account.restore(client._inner, account_data_stored, encryption_key))


class RemovedCollection:
    def __init__(self, inner):
        self._inner = inner

    @property
    def uid(self):
        return self._inner.get_uid()


class CollectionListResponse:
    def __init__(self, inner):
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
    def __init__(self, inner):
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
    def __init__(self, inner):
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

    def limit(self, value):
        self._inner.limit(value)
        return self

    def prefetch(self, value):
        self._inner.prefetch(value)
        return self

    def with_collection(self, value):
        self._inner.with_collection(value)
        return self

    def iterator(self, value):
        self._inner.iterator(value)
        return self

    def stoken(self, value):
        self._inner.stoken(value)
        return self


def _verify_col_meta(meta):
    if "type" not in meta:
        raise RuntimeError("Collection meta must have a type field")
    if "name" not in meta:
        raise RuntimeError("Collection meta must have a name field")
    return meta


class CollectionManager:
    def __init__(self, inner: str):
        self._inner = inner

    def fetch(self, col_uid, fetch_options=None):
        return Collection(self._inner.fetch(col_uid, _inner(fetch_options)))

    def create(self, meta, content):
        meta = msgpack_encode(_verify_col_meta(meta))
        return self.create_raw(meta, content)

    def create_raw(self, meta, content):
        return Collection(self._inner.create_raw(meta, content))

    def get_item_manager(self, col):
        return ItemManager(self._inner.get_item_manager(col._inner))

    def list(self, fetch_options=None):
        return CollectionListResponse(self._inner.list(_inner(fetch_options)))

    def upload(self, collection, fetch_options=None):
        self._inner.upload(collection._inner, _inner(fetch_options))

    def transaction(self, collection, fetch_options=None):
        self._inner.transaction(collection._inner, _inner(fetch_options))

    def cache_load(self, cached):
        return Collection(self._inner.cache_load(cached))

    def cache_save(self, collection, with_content=True):
        if with_content:
            return bytes(self._inner.cache_save_with_content(collection._inner))
        else:
            return bytes(self._inner.cache_save(collection._inner))

    def get_member_manager(self, collection):
        return CollectionMemberManager(self._inner.get_member_manager(collection._inner))


class ItemManager:
    def __init__(self, inner: str):
        self._inner = inner

    def fetch(self, col_uid, fetch_options=None):
        return Item(self._inner.fetch(col_uid, _inner(fetch_options)))

    def create(self, meta, content):
        meta = msgpack_encode(meta)
        return self.create_raw(meta, content)

    def create_raw(self, meta, content):
        return Item(self._inner.create_raw(meta, content))

    def list(self, fetch_options=None):
        return ItemListResponse(self._inner.list(_inner(fetch_options)))

    def item_revisions(self, item, fetch_options=None):
        return ItemRevisionsListResponse(self._inner.item_revisions(item._inner, _inner(fetch_options)))

    def fetch_updates(self, items, fetch_options=None):
        items = list(map(lambda x: x._inner, items))
        return ItemListResponse(self._inner.fetch_updates(items, _inner(fetch_options)))

    def batch(self, items, deps=None, fetch_options=None):
        items = list(map(lambda x: x._inner, items))
        deps = list(map(lambda x: x._inner, deps)) if deps is not None else None
        self._inner.batch(items, deps, fetch_options)

    def transaction(self, items, deps=None, fetch_options=None):
        items = list(map(lambda x: x._inner, items))
        deps = list(map(lambda x: x._inner, deps)) if deps is not None else None
        self._inner.transaction(items, deps, fetch_options)

    def cache_load(self, cached):
        return Item(self._inner.cache_load(cached))

    def cache_save(self, item, with_content=True):
        if with_content:
            return bytes(self._inner.cache_save_with_content(item._inner))
        else:
            return bytes(self._inner.cache_save(item._inner))


class Collection:
    def __init__(self, inner):
        self._inner = inner

    def verify(self):
        return self._inner.verify()

    @property
    def meta(self):
        return msgpack_decode(bytes(self._inner.get_meta_raw()))

    @meta.setter
    def meta(self, value):
        self.__class__.meta.fget.cache_clear()
        self.__class__.meta_raw.fget.cache_clear()
        value = msgpack_encode(_verify_col_meta(value))
        self._inner.set_meta_raw(value)

    @property
    def meta_raw(self):
        return self._inner.get_meta_raw()

    @meta_raw.setter
    def meta_raw(self, value):
        self.__class__.meta.fget.cache_clear()
        self.__class__.meta_raw.fget.cache_clear()
        self._inner.set_meta_raw(value)

    @cached_property
    def content(self):
        return bytes(self._inner.get_content())

    @content.setter
    def content(self, value):
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


class Item:
    def __init__(self, inner):
        self._inner = inner

    def verify(self):
        return self._inner.verify()

    @property
    def meta(self):
        return msgpack_decode(bytes(self._inner.get_meta_raw()))

    @meta.setter
    def meta(self, value):
        self.__class__.meta.fget.cache_clear()
        self.__class__.meta_raw.fget.cache_clear()
        value = msgpack_encode(value)
        self._inner.set_meta_raw(value)

    @property
    def meta_raw(self):
        return self._inner.get_meta_raw()

    @meta_raw.setter
    def meta_raw(self, value):
        self.__class__.meta.fget.cache_clear()
        self.__class__.meta_raw.fget.cache_clear()
        self._inner.set_meta_raw(value)

    @cached_property
    def content(self):
        return bytes(self._inner.get_content())

    @content.setter
    def content(self, value):
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


class UserProfile:
    def __init__(self, inner):
        self._inner = inner

    @property
    def pubkey(self):
        return bytes(self._inner.get_pubkey())


class InvitationListResponse:
    def __init__(self, inner):
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
    def __init__(self, inner):
        self._inner = inner

    def list_incoming(self, fetch_options=None):
        return InvitationListResponse(self._inner.list_incoming(_inner(fetch_options)))

    def list_outgoing(self, fetch_options=None):
        return InvitationListResponse(self._inner.list_outgoing(_inner(fetch_options)))

    def accept(self, signed_invitation):
        self._inner.accept(signed_invitation._inner)

    def reject(self, signed_invitation):
        self._inner.reject(signed_invitation._inner)

    def fetch_user_profile(self, username):
        return UserProfile(self._inner.fetch_user_profile(username))

    def invite(self, collection, username, pubkey, access_level):
        self._inner.invite(collection._inner, username, pubkey, access_level)

    def disinvite(self, signed_invitation):
        self._inner.disinvite(signed_invitation._inner)

    @property
    def pubkey(self):
        return self._inner.get_pubkey()


class SignedInvitation:
    def __init__(self, inner):
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
    def from_pubkey(self):
        return bytes(self._inner.get_from_pubkey())


class CollectionMember:
    def __init__(self, inner):
        self._inner = inner

    @property
    def username(self):
        return self._inner.get_username()

    @property
    def access_level(self):
        return self._inner.get_access_level()


class MemberListResponse:
    def __init__(self, inner):
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


class CollectionMemberManager:
    def __init__(self, inner):
        self._inner = inner

    def list(self, fetch_options=None):
        return MemberListResponse(self._inner.list(_inner(fetch_options)))

    def remove(self, username):
        self._inner.remove(username)

    def leave(self):
        self._inner.leave()

    def modify_access_level(self, username, access_level):
        self._inner.modify_access_level(username, access_level)
