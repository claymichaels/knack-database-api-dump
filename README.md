# knack-database-api-dump
A tool to dump data from the Knack API.

The purpose of this script was to pull down the data stored in a Knack (WYSIWYG webapp maker) database. 
Through painful trial and error, I determined the structure of the database and was able to pull it down into a SQLite3 database so that I could query with pure SQL.
That local database feeds the mechanism in the config-scanner tool that allows it to update the Knack webapp when changes are detected.
