- Implement the workflow and the runner in a single file with a meaningful name 
- Follow the pocketflow guidelines as close as possible
- Use syncronous code whenever possible.
- Avoid creating new fields in the node classes when data can be passed throught the prep -> exec -> post pipeline as in the pocketflow guidelines
- In the node post method, always return the next action that is used for the transition to the next node.
- Avoid returning '{}' in the nodes.
- Don't create node fields to copy stuff from the shared store. Pass the shared everywhere in the node methods.
- Use the following format when requesting user input or confirmation: Enter action (Retry/Input/Quit)[R] . It shoudl have a default option on empty input
- Keep requirements.txt in the root workspace folder in sync with the used packages
- Common utilities are under lib folder
- Tools used by llms are in lib/tools
- use config.yaml for app configuration values
- use this form whe defining a trasition from one node(review) to another(payment) based on an action(approved): {review - "approved" >> payment} 