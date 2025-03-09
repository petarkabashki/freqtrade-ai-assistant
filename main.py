import sys
import os
sys.path.append(os.path.abspath('.'))

import yaml
from nodes.main_flow.main_flow import MainFlow
import logging

# Define ANSI escape codes for gray color
GRAY_COLOR_CODE = "\033[90m"
RESET_COLOR_CODE = "\033[0m"

# Create a custom formatter that adds gray color to log messages
class GrayLogFormatter(logging.Formatter):
    def format(self, record):
        return GRAY_COLOR_CODE + super().format(record) + RESET_COLOR_CODE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger() # Get root logger
logger.handlers = [] # Clear existing handlers to ensure no conflicts

# Create a console handler and set the formatter
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Original formatter - not used directly now
gray_formatter = GrayLogFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Create gray formatter

console_handler.setFormatter(gray_formatter) # Set gray formatter to console handler

# Add the console handler to the root logger
logger.addHandler(console_handler)


if __name__ == '__main__':
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    main_flow = MainFlow(config)
    main_flow.run({})
