# Freqtrade Download Assistant Requirements

1. **User Input Collection & Defaults:**
   - **Exchange Input Node:** Prompt the user for the exchange.
     - Continue prompting until a valid entry is received.
     - Allow "q" (or "quit") at any time to exit with a thank-you message.
     - Store the last valid exchange in shared memory and use it as default for subsequent prompts.
   - **Asset Pair Input Node:** Prompt the user for the asset pair.
     - Continue prompting until a valid entry is received.
     - Allow "q" (or "quit") at any time to exit with a thank-you message.
     - Store the last valid asset pair in shared memory and use it as default for subsequent prompts.
   - **Timeframe Input Node:** Prompt the user for the timeframe.
     - Continue prompting until a valid entry is received.
     - Allow "q" (or "quit") at any time to exit with a thank-you message.
     - Store the last valid timeframe in shared memory and use it as default for subsequent prompts.

2. **Input Validation:**
   - **Exchange Validation Node:** Validate exchange input via an LLM call using a structured prompt.
     - **Exchange:** Must be one of `binance`, `ftx`, `kucoin`, or `coinbase`.
     - If validation fails, loop back to the Exchange Input Node.
   - **Asset Pair Validation Node:** Validate asset pair input via an LLM call using a structured prompt.
     - **Asset Pair:** Should be in `BASE/QUOTE` format (default to `USDT` if missing; convert the base to its standardized short form if necessary).
     - If validation fails, loop back to the Asset Pair Input Node.
   - **Timeframe Validation Node:** Validate timeframe input via an LLM call using a structured prompt.
     - **Timeframe:** Must be one of `1d`, `3d`, `1w`, `2w`, `1M`, `3M`, `6M`, or `1y` (convert as required).
     - If validation fails, loop back to the Timeframe Input Node.

3. **Download Confirmation:**
   - **Confirmation Node:** After successful validation of all inputs, prompt the user to confirm the download.
     - If the user does not confirm, loop back to the Exchange Input Node (start input process again).

4. **Download Execution & Summarization:**
   - **Download Execution Node:** Execute the terminal command:
     ```
     freqtrade download-data --userdir ./freq-user-data --data-format-ohlcv json --exchange {exchange} -t {timeframe} --timerange=20200101- -p {pair}
     ```
     - Execute the command regardless of success or error.
     - Capture the output or error message.
   - **Summary Node:** Use an LLM call to parse and summarize the terminal command output, regardless of whether the download was successful or not.
     - Output a meaningful message summarizing the result.
     - Then, transition back to the Exchange Input Node for new input.

---

## Node Flow DOT Diagram (Transitions Only)

```dot
digraph freqtrade_assistant {
    "Exchange Input Node" -> "Exchange Validation Node" [ label="Valid Input (not 'q')" ];
    "Exchange Input Node" -> "Exit Node" [ label="'q' Entered" ];
    "Exchange Validation Node" -> "Asset Pair Input Node" [ label="Valid Input" ];
    "Exchange Validation Node" -> "Exchange Input Node" [ label="Invalid Input" ];
    "Asset Pair Input Node" -> "Asset Pair Validation Node" [ label="Valid Input (not 'q')" ];
    "Asset Pair Validation Node" -> "Timeframe Input Node" [ label="Valid Input" ];
    "Asset Pair Validation Node" -> "Asset Pair Input Node" [ label="Invalid Input" ];
    "Timeframe Input Node" -> "Timeframe Validation Node" [ label="Valid Input (not 'q')" ];
    "Timeframe Validation Node" -> "Confirmation Node" [ label="Valid Input" ];
    "Timeframe Validation Node" -> "Timeframe Input Node" [ label="Invalid Input" ];
    "Confirmation Node" -> "Download Execution Node" [ label="Confirmed" ];
    "Confirmation Node" -> "Exchange Input Node" [ label="Not Confirmed" ];
    "Download Execution Node" -> "Summary Node" [ label="Download Completed (success or error)" ];
    "Summary Node" -> "Exchange Input Node";
}
