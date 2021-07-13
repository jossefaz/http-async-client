from distutils.core import setup
setup(
  name = 'http_async_client',
  packages = ['http_async_client'],   # Chose the same as "name"
  version = '0.0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A simple http client for managing asynchronous requests',   # Give a short description about your library
  author = 'JossefAz',                   # Type in your name
  author_email = 'jossefaz@protonmail.com',      # Type in your E-Mail
  url = 'https://github.com/jossefaz/http-async-client',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/jossefaz/http-async-client/archive/refs/tags/0.0.1.tar.gz',    # I explain this later on
  keywords = ['async', 'httpx', 'client', 'microservices', 'SOA'],   # Keywords that define your package best
  install_requires=[
      'pytest',
      'pytest-asyncio',
      'pytest-httpx',
      'httpx',
      'nanoid'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)