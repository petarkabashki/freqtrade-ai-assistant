from nodes.freqtrade.flow import *

if __name__ == "__main__":
    download_flow = freqtrade_flow()
    download_flow.run({})
