# TEP-G1A-Discord-Bot

COMMANDS
- **!display_strikes**
    - Displays a graph of the strikes table.
- **!display_topics**
    - Displays a graph of the topics in the topics table, their counts and also tells the user what the most common topic is.
- **!add_topic 'topic'**
    - Adds the input topic to the topics table e.g. !add_topic python adds python to the table with a count of 0.
    - Will also check if topic is already in the table before attempting to add.
- **!delete_topic 'topic'**
    - Deletes the input topic from the table e.g. !delete_topic python will delete the row which contains python from the table.
    - Will also check if topic exists before attempting to delete.
- **!reminder 'day' 'hour' 'minute' 'desc'**
    - Users can set a reminder by entering in the !reminder command followed the reminder's day's date, hour and minute followed by a description for the reminder. e.g. to set a reminder for the 25th at 3:30pm for a web assignment the command would be !reminder 25 15 30 web assignment
    - When it comes time for the reminder to be sent a DM will be sent to the user with the desctiption they provided.
