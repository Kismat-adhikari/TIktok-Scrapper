from setuptools import setup, find_packages

setup(
    name="tiktok-bulk-scraper",
    version="1.0.0",
    description="High-speed TikTok metadata scraper for bulk URL processing",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "playwright>=1.40.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "hypothesis>=6.92.1",
        ]
    },
)
