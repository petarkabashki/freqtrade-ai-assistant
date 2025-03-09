import sys
import os
sys.path.append(os.path.abspath('.'))

import yaml
from nodes.main_flow.main_flow import MainFlow
import logging

logging.basicConfig(level=logging.INFO) # AI: Set basic logging level

if __name__ == '__main__':
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    main_flow = MainFlow(config)
    main_flow.run({})
