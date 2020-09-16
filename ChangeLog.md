# Changelog

## Version 0.20.2
* CI: statically link Windows C runtime on Windows
* CI: change how we build the wheels to fix Windows link issue

## Version 0.20.1
* Fix errors when setting item and collection metadata

## Version 0.20.0
* Expose access level values
* Rename API_URL to DEFAULT_SERVER_URL and update etebase dep.
* Add an API function to check if it's an etebase server.
* Update etebase dep

## Version 0.2.1
* Update etebase dep

## Version 0.2.0
* ItemManager: implement item revisions fetching.
* Fix `UserProfile` member manager and invitation manager.
* Expose `pretty_fingerprint` for pretty fingerprint printing
* Make `deps`/`fetch_options` parameters optional.
* Expose `randombytes` for generating random data
* Expose `API_URL` and add a default parameter to the Client constructor.
* Base64Url: improve the python bindings of this class

## Version 0.1.0
* Initial commit
