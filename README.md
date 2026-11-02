<p align="center">
  <img width="120" src="https://github.com/etesync/etesync-web/blob/master/src/images/logo.svg" />
  <h1 align="center">Etebase - Encrypt Everything</h1>
</p>

A Python library for Etebase

This package is implemented in Rust and exposes a Python API for people to use.

![GitHub tag](https://img.shields.io/github/tag/etesync/etebase-py.svg)
[![PyPI](https://img.shields.io/pypi/v/etebase.svg)](https://pypi.python.org/pypi/etebase/)
[![Build Status](https://github.com/etesync/etebase-py/workflows/Build/badge.svg)](https://github.com/etesync/etebase-py/actions/)
[![Chat on freenode](https://img.shields.io/badge/chat-IRC%20|%20Matrix%20|%20Web-blue.svg)](https://www.etebase.com/community-chat/)

# Documentation

In addition to the API documentation, there are docs available at https://docs.etebase.com

# Build

## Install deps

```
pip install maturin
```

## Build

```
maturin build --release
```

The extension is built against the Python stable ABI (abi3), so the resulting wheel works on Python 3.9 and newer.

For development, `maturin develop` builds and installs the package into the current virtualenv.
