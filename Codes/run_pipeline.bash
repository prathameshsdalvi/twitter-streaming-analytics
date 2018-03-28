# Run pipeline infinitely!

# Start cron service
sudo service cron start

# Schedule tasks using cron
crontab -e

# Define tasks and schedule time
48 5 2 12 * python ~/big_data_project/final_pipeline/twitter_to_kinesis.py
48 5 2 12 * python ~/big_data_project/final_pipeline/kinesis_to_dynamodb.py

# Press 'Ctrl + x' then 'y' then 'Enter' to save the tasks

# Check scheduled tasks
crontab -l

# Check if the tasks have started running
ps -o pid,sess,cmd afx | egrep "( |/)cron( -f)?$"

# There is only one way to stop the running tasks. Restart/stop/terminate EC2