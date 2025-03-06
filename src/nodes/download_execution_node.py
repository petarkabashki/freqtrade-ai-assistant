from pocketflow import Node

class DownloadExecutionNode(Node):
    def prep(self, shared):
        validated_input = shared['validated_input']
        return validated_input

    def exec(self, prep_res, shared):
        exchange = prep_res['exchange']
        asset_pair = prep_res['asset_pair']
        timeframe = prep_res['timeframe']

        command = f"freqtrade download-data --userdir ./freq-user-data --data-format-ohlcv json --exchange {exchange} -t {timeframe} --timerange=20200101- -p {asset_pair}"
        print(f"\nExecuting command: {command}\n")

        import subprocess
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output_message = stdout.decode() + "\n" + stderr.decode()

        return {'command': command, 'output_message': output_message}


    def post(self, shared, prep_res, exec_res):
        shared['command_output'] = exec_res
        return 'summarize'
