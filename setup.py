from setuptools import find_packages, setup

setup(
    name="ncep-wave-forecast",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "numpy",
        "matplotlib",
        "pyyaml"
    ],
    entry_points={
        "console_scripts": [
            "ncep-wave-plotter=ncep_wave_plotter:main"
        ]
    }
)
