from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(
    name="etebase",
    version="0.2.2",
    rust_extensions=[RustExtension("etebase.etebase_python", binding=Binding.RustCPython)],
    packages=["etebase"],
    author='Tom Hacohen',
    author_email='tom@stosb.com',
    url='https://github.com/etesync/etebase-py',
    description='Python client library for Etebase',
    keywords=['etebase', 'encryption', 'sync', 'end-to-end encryption'],
    license='LGPL-3.0-only',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3',
    install_requires=[
        'msgpack>=1.0.0',
    ],
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
)
