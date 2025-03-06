================================================
File: docs/design.md
================================================
---
layout: default
title: "Design"
---

# System Design

## Node Flow Diagram

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
```

## Data Schema

*(This section can be expanded to detail the shared data structure if needed)*

- **Shared Memory (shared_memory.json):**
  - Stores the last valid inputs for `exchange`, `asset_pair`, and `timeframe` to be used as defaults.
  - Stores intermediate validation results and command outputs.

## Utility Functions

- **`utils/call_llm.py`**:  Handles calls to the Language Model for input validation and summary generation.

## Node Descriptions

- **Exchange Input Node**: Prompts the user for the exchange, using the last entered exchange as a default. Allows quitting with 'q'.
- **Exchange Validation Node**: Validates the exchange input using an LLM against a predefined list of exchanges.
- **Asset Pair Input Node**: Prompts the user for the asset pair, using the last entered asset pair as a default. Allows quitting with 'q'.
- **Asset Pair Validation Node**: Validates the asset pair input using an LLM, ensuring it's in the correct format.
- **Timeframe Input Node**: Prompts the user for the timeframe, using the last entered timeframe as a default. Allows quitting with 'q'.
- **Timeframe Validation Node**: Validates the timeframe input using an LLM against a predefined list of timeframes.
- **Confirmation Node**: Asks the user to confirm the download parameters before proceeding.
- **Download Execution Node**: Executes the `freqtrade download-data` command with the validated parameters.
- **Summary Node**: Summarizes the output of the download command using an LLM and provides feedback to the user.
- **Exit Node**:  Provides a thank you message and ends the program.

This completes the refactoring of the input and validation process into separate nodes. Let me know if you have any questions or further adjustments!