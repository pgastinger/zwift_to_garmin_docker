"""FIT file service for handling file modifications."""

import os
import tempfile
import logging
from typing import Optional

import jpype
from jpype.types import *
import os 
import csv
# 1. Start the JVM and point to the JAR

jar_path = os.path.abspath("/venv/FitCSVTool.jar")


class FitFileService:
    """Service for modifying FIT files."""

    def __init__(self):
        """Initialize FitFileService."""
        self.logger = logging.getLogger(__name__)
        
        if not os.path.exists(jar_path):
            raise FileNotFoundError(f"Could not find JAR at {jar_path}")

        jpype.startJVM(classpath=[jar_path])
        self.fit_csv_tool = jpype.JClass("com.garmin.fit.csv.CSVTool")


    def fit_to_csv(self, fit_file_path):
        # Arguments: -b (batch mode) converts .fit to .csv
        args = [fit_file_path]
        #FitCSVTool = jpype.JClass("com.garmin.fit.csv.CSVTool")
        try:
            self.fit_csv_tool.main(args)
            print(f"Conversion complete: {fit_file_path.replace('.fit', '.csv')}")
        except Exception as e:
            print(f"Error: {e}")


    def modify_csv_file(self, csv_file_in, csv_file_out):
        with open(csv_file_in, 'r') as f_in, open(csv_file_out, 'w', newline='') as f_out:    
            reader = csv.reader(f_in)
            writer = csv.writer(f_out)        
            for row in reader:
                if row[6] == "manufacturer":
                    row[7] = "1"
                    row[9] = "garmin_product"
                    row[10] = "3570"
                    #print(row)
                if row[0] == "Data" and row[12] == "manufacturer":
                    row[13] = "1"
                    row[15] = "garmin_product"
                    row[16] = "3570"
                    #print(row)
                writer.writerow(row)


    def csv_to_fit(self, csv_file, fit_file):
        # The main method in Java expects an array of strings (String[])
        args = ["-c", csv_file, fit_file]
        
        try:
            # Call the static main method
            self.fit_csv_tool.main(args)
            print(f"Successfully converted {csv_file} to {fit_file}")
        except Exception as e:
            print(f"Java Error: {e}")


    def modify_device_info(self, fit_file_path: str,
                          manufacturer: Optional[int] = None,
                          product: Optional[int] = None,
                          software_version: Optional[float] = None) -> str:
        """Modifies the device manufacturer and type in a .fit file.

        Args:
            fit_file_path: Path to the original FIT file
            manufacturer: Device manufacturer (defaults to Garmin)
            product: Device product (defaults to Edge 530)
            software_version: Software version (defaults to 9.75)

        Returns:
            Path to the modified FIT file

        Raises:
            FileNotFoundError: If the input file doesn't exist
            RuntimeError: If file modification fails
        """
        if not os.path.exists(fit_file_path):
            raise FileNotFoundError(f"FIT file not found: {fit_file_path}")

        self.fit_to_csv(fit_file_path)
        csv_file_in = fit_file_path.replace(".fit",".csv")
        csv_file_out = f"{csv_file_in}_mod"
        modified_fit_file_path = os.path.join("/tmp/", "modified_" + os.path.basename(fit_file_path))
        self.modify_csv_file(csv_file_in, csv_file_out)
        self.csv_to_fit(csv_file_out, modified_fit_file_path)
        return modified_fit_file_path

        # # Set defaults
        # manufacturer = manufacturer or Manufacturer.GARMIN.value
        # product = product or GarminProduct.EDGE_530.value
        # software_version = software_version or 9.75

        # self.logger.info(f"Modifying FIT file: {fit_file_path}")

        # try:
        #     fit_file = FitFile.from_file(fit_file_path)

        #     # CHANGE 1: Set auto_define to True to fix the RuntimeError
        #     builder = FitFileBuilder(auto_define=True)

        #     for record in fit_file.records:
        #         message = record.message
                
        #         # CHANGE 2: Update the FileIdMessage (Primary device identification)
        #         if isinstance(message, FileIdMessage):
        #             message.manufacturer = manufacturer
        #             message.garmin_product = product
                
        #         # CHANGE 3: Update DeviceInfoMessage (Hardware entries)
        #         elif isinstance(message, DeviceInfoMessage):
        #             # Only update the main device info, usually the first one
        #             if message.device_index in [None, 0, 255]: 
        #                 message.manufacturer = manufacturer
        #                 message.garmin_product = product
        #                 message.software_version = software_version

        #         # Add the message (the builder now handles definitions automatically)
        #         builder.add(message)


        #     # Save the modified FIT file
        #     temp_dir = tempfile.gettempdir()
        #     modified_fit_file_path = os.path.join(temp_dir, "modified_" + os.path.basename(fit_file_path))

        #     modified_file = builder.build()
        #     modified_file.to_file(modified_fit_file_path)

        #     self.logger.info(f"Modified FIT file saved to {modified_fit_file_path}")
        #     return modified_fit_file_path

        # except Exception as e:
        #     raise RuntimeError(f"Failed to modify FIT file: {e}") from e

    def cleanup_file(self, file_path: str) -> None:
        """Clean up a temporary file.

        Args:
            file_path: Path to the file to remove
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Cleaned up file: {file_path}")
        except OSError as e:
            self.logger.warning(f"Failed to cleanup file {file_path}: {e}")
