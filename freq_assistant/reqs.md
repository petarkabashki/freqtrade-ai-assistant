# Freqtrade Download Assistant Requirements (Revised)

Below is the updated specification for a Freqtrade Download Assistant that utilizes a single input-validate loop with a comprehensive prompt to manage the entire flow.

---

## 1. Unified Input Prompt & Loop

- **Comprehensive Prompt:** Present the user with one prompt that requests all three input fields simultaneously:
  - **Exchange**
  - **Asset Pair**
  - **Timeframe**
- **Exit Option:** At any point during input, if the user types `"q"` or `"quit"`, immediately exit and display a thank-you message.
- **Default Handling:** For the asset pair, if the quote is missing, default to `"USDT"` and standardize the base if necessary.

---

## 2. Unified Input Validation

- **Structured Validation:** After collecting the complete input, validate each field in one go using an LLM call with a structured prompt:
  - **Exchange:** Must be one of `binance`, `ftx`, `kucoin`, or `coinbase`.
  - **Asset Pair:** Must follow the `BASE/QUOTE` format (default to `USDT` if the quote is missing and convert the base to its standardized short form if needed).
  - **Timeframe:** Must be one of `1d`, `3d`, `1w`, `2w`, `1M`, `3M`, `6M`, or `1y` (conversion applied as required).
- **Error Reporting:** If one or more fields are invalid, re-display the comprehensive prompt with clear feedback on which inputs need correction. The user will then re-enter all values in the same unified prompt.

---

## 3. Download Confirmation

- **Summary & Confirm:** Once all inputs pass validation, display a summary of the collected inputs and prompt the user for confirmation.
  - **If Confirmed:** Proceed to execute the download.
  - **If Not Confirmed:** Restart the process by re-displaying the unified input prompt.

---

## 4. Download Execution & Summarization

- **Command Execution:** Run the terminal command:
  ```bash
  freqtrade download-data --userdir ./freq-user-data --data-format-ohlcv json --exchange {exchange} -t {timeframe} --timerange=20200101- -p {pair}
