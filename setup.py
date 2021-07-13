from distutils.core import setup
setup(
  name = 'http_async_client',
  packages = ['http_async_client'],
  version = '0.0.4',
  license='MIT',
  description = 'A simple http client for managing asynchronous requests',
  author = 'JossefAz',
  author_email = 'jossefaz@protonmail.com',
  url = 'https://github.com/jossefaz/http-async-client',
  download_url = 'https://github.com/jossefaz/http-async-client/archive/refs/tags/0.0.4.tar.gz',
  keywords = ['async', 'httpx', 'client', 'microservices', 'SOA'],
  install_requires=[
      'pytest',
      'pytest-asyncio',
      'pytest-httpx',
      'asyncio',
      'httpx',
      'nanoid'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)