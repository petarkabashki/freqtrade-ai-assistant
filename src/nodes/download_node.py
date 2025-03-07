from pocketflow import Node
import subprocess
class DownloadNode(Node):
    def prep(self, shared):
        collected_values = shared['collected']
        self.command = f"freqtrade download-data --userdir ./freq-user-data --data-dir ./freq-data --data-format-ohlcv json --exchange {collected_values['exchange']} -t {collected_values['timeframe']} --timerange=20200101- -p {collected_values['asset_pair']}"
        return {}

    def exec(self, prep_res, shared):
        print(f"Executing command: {self.command}")
        try:
            process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                shared['download_output'] = stdout.decode()
                shared['download_success'] = True
                return "summary"
            else:
                shared['download_output'] = stderr.decode()
                shared['download_success'] = False
                return "summary" # Still go to summary node to display error
        except Exception as e:
            shared['download_output'] = str(e)
            shared['download_success'] = False
            return "summary" # Still go to summary node to display error

    def post(self, shared, prep_res, exec_res):
        return exec_res
