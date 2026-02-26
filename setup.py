from setuptools import setup, find_packages

setup(
    name="myxl-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "python-dotenv",
        "pycryptodome",
    ],
    entry_points={
        "console_scripts": [
            "myxl = myxl.cli:cli",
        ],
    },
    author="Your Name",
    description="CLI untuk monitoring dan pembelian paket XL menggunakan API myXL",
    license="MIT",
    python_requires=">=3.8",
)
