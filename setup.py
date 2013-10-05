from setuptools import setup, find_packages

version = '0.2.2'

data = dict(
    name='jade',
    version=version,
    author="Ed Singleton",
    author_email="singletoned@gmail.com",
    description="A jade parser",
    py_modules=['jade'],
    include_package_data=True,
    zip_safe=False,
)

if __name__ == '__main__':
    setup(**data)
