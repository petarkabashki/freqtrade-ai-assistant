Freqtrade Download Assistant Requirements
User Input Collection & Defaults:

Input Node: Prompt the user for an asset pair, exchange, and timeframe.
Continue prompting for each item until a valid entry is received.
Allow "q" (or "quit") at any time to exit with a thank-you message.
Store the last valid inputs in shared memory and use them as defaults for subsequent prompts.
Input Validation:

Validation Node: Validate inputs via an LLM call using a structured prompt.
Exchange: Must be one of binance, ftx, kucoin, or coinbase.
Asset Pair: Should be in BASE/QUOTE format (default to USDT if missing; convert the base to its standardized short form if necessary).
Timeframe: Must be one of 1d, 3d, 1w, 2w, 1M, 3M, 6M, or 1y (convert as required).
If validation fails, loop back to the Input Node.
Download Confirmation:

Confirmation Node: After successful validation, prompt the user to confirm the download.
If the user does not confirm, loop back to the Input Node.
Download Execution & Summarization:

Download Execution Node: Execute the terminal command:

```bash
freqtrade download-data --userdir ./freq-user-data --data-format-ohlcv json --exchange {exchange} -t {timeframe} --timerange=20200101- -p {pair}
```
On download error, output an error message and loop back to the Input Node.
Summary Node: Use an LLM call to parse and summarize the terminal command output.
After summarization, transition back to the Input Node for new input.
Node Flow DOT Diagram (Transitions Only)
```dot
digraph {
"User Input Node" -> "Validation Node" [ label="Valid Input (not 'q')" ];
"User Input Node" -> "Exit Node" [ label="'q' Entered" ];
"Validation Node" -> "Confirmation Node" [ label="Valid Input" ];
"Validation Node" -> "User Input Node" [ label="Invalid Input" ];
"Confirmation Node" -> "Download Execution Node" [ label="Confirmed" ];
"Confirmation Node" -> "User Input Node" [ label="Not Confirmed" ];
"Download Execution Node" -> "Summary Node" [ label="Download Completed (success or error)" ];
"Summary Node" -> "User Input Node";
}