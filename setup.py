import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uyuni-logs-visualizer",
    version="0.1.1",
    author="Pablo Suárez Hernández",
    author_email="psuarezhernandez@suse.com",
    description="A tool to graphically visualize events from Uyuni logs and Salt events bus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meaksh/uyuni-logs-visualizer",
    project_urls={
        "Bug Tracker": "https://github.com/meaksh/uyuni-logs-visualizer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
    scripts=["uyuni-logs-visualizer"],
)
