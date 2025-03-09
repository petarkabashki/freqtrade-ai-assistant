import sys
import os
sys.path.append(os.path.abspath('.')) # Add project root to Python path

import yaml
from nodes.main_flow.main_flow import MainFlow

if __name__ == '__main__':
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    main_flow = MainFlow(config) # Pass config to MainFlow
    main_flow.run({})
