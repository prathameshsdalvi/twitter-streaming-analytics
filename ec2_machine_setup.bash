# Connect to your ubuntu EC2 instance
chmod 400 key.pem
ssh -i "key.pem" ubuntu@ec2-your-public-dns.xxxxxxxx-x.amazonaws.com


# Install python
sudo apt-get update
sudo apt-get install python


# Install pip
curl -O https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py

# Install python libraries
sudo pip install TwitterAPI
sudo pip install boto3
sudo pip install textblob
sudo pip install numpy


# Specify the AWS region
mkdir .aws
vi ~/.aws/config

"""
[default]
region=us-east-1c
"""

# Save your file and exit


# Set AWS credentials as environment variables
nano ~/.bash_profile


"""
export AWS_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxx
export AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
"""

# Save your file and exit

source ~/.bash_profile


# Create project directory
mkdir big_data_project
cd big_data_project
mkdir testing
mkdir final_pipeline


# Create twitter credentials file
cd final_pipeline
vi twitterCreds.py

"""
consumer_key = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
consumer_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
access_token_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
access_token_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
"""

# Create keywords file with variables that store keywords for various analyses
vi keywords.py

"""
Create variables that store keywords for various analyses
"""

# Save your file and exit

# Go back to your home folder
cd
