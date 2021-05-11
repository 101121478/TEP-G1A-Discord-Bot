# TEP-G1A-Discord-Bot

COMMANDS
- **!display_topics**
    - Displays a graph the topics in the topics table, their counts and also tells the user what the most common topic is.
- **!add_topic 'topic'**
    - Adds the input topic to the topics table e.g. !add_topic python adds python to the table with a count of 0.
    - Will also check if topic is already in the table before attempting to add.
- **!delete_topic 'topic'**
    - Deletes the input topic from the table e.g. !delete_topic python will delete the row which contains python from the table.
    - Will also check if topic exists before attempting to delete.
