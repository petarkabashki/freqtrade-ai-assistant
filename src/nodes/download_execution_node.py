from pocketflow import Node
import subprocess

class DownloadExecutionNode(Node):
    def prep(self, shared):
        validated_input_values = shared['validated_input_values']
        self.command = f"freqtrade download-data --userdir ./freq-user-data --data-format-ohlcv json --exchange {validated_input_values['exchange']} -t {validated_input_values['timeframe']} --timerange=20200101- -p {validated_input_values['asset_pair']}"
        return {}

    def exec(self, prep_res, shared):
        print(f"Executing command: {self.command}")
        try:
            process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                shared['command_output'] = stdout.decode()
                return "summary"
            else:
                shared['command_output'] = stderr.decode()
                return "summary" # Still go to summary node to display error
        except Exception as e:
            shared['command_output'] = str(e)
            return "summary" # Still go to summary node to display error

    def post(self, shared, prep_res, exec_res):
        return {}
