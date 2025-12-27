import os
import jpype
from jpype.types import *

jar_path = os.path.abspath("/venv/FitCSVTool.jar")
if not os.path.exists(jar_path):
    raise FileNotFoundError(f"Could not find JAR at {jar_path}")
jpype.startJVM(classpath=[jar_path])

fit_csv_tool = jpype.JClass("com.garmin.fit.csv.CSVTool")
