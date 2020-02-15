import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sentimental",
    version="0.1.1",
    author="Jones Maxime Murphy III",
    author_email="jones.murphy@onsight.ga",
    description="sentiment analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='sentiment analysis python',
    url="onsight.ga",
    packages=setuptools.find_packages(),
    license=None,
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=[
        "sqlalchemy",
        "holidays"
    ],
    entry_points={
        'console_scripts': [
            'sentimental=sentimental.__main__:main'
        ]
    },
    include_package_data=True
)