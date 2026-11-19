from setuptools import find_namespace_packages, setup

setup(
    name="cli-anything-devlens",
    version="1.0.0",
    description="Command-line harness for the Devlens Bangladesh website (Astro): stories, jobs, homepage, images and builds.",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    package_data={"cli_anything.devlens": ["skills/*.md", "README.md", "tests/TEST.md"]},
    install_requires=["click>=8.0.0", "prompt-toolkit>=3.0.0"],
    extras_require={"test": ["pytest>=7"]},
    entry_points={"console_scripts": ["cli-anything-devlens=cli_anything.devlens.devlens_cli:main"]},
    python_requires=">=3.10",
)
