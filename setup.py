from setuptools import setup, find_packages

setup(
    name="sql_antipattern_scanner",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlparse",
        "pyyaml",
        "jinja2",
        "re",
        "collections"
    ],
    author="Nicholas Piesco",
    author_email="nicholas.piesco@gmail.com",
    description="A tool to scan SQL for antipatterns",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sql_antipattern_scanner",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
