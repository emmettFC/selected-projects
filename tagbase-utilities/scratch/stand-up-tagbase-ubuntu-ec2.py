
*** For some reason this only works on your local machine where you are the only user, couldnt replicate for gaubelab account



####### STEP I: Building new EC2 instance

''' 
    - make new ec2 instance on AWS
    - select ubuntu 
    - downlaod new keypair call 'sharkbase'
    - cd ~/Downloads
    - chmod 400 sharkbase.pem 
    - ssh to machine:
        ssh -i sharkbase.pem ubuntu@ec2-3-17-180-165.us-east-2.compute.amazonaws.com
'''

ssh -i sharkbase.pem ubuntu@ec2-18-223-131-70.us-east-2.compute.amazonaws.com

###### STEP IA: 

cd ..
cd ..
cd etc/ssh
sudo vi sshd_config 
'''
# Logging
SyslogFacility AUTH
LogLevel INFO
GatewayPorts yes
'''
sudo service ssh restart

####### Local machine (this is very close, doing remote and not just local)

ssh -R :8080:localhost:8080 -i /Users/culhane/Downloads/sharkbase.pem ubuntu@ec2-18-223-166-147.us-east-2.compute.amazonaws.com


##### STEP II: configure environment on ubuntu (working)

''' configure github '''
sudo apt-get install git
cd sharkbase
git init
git clone https://github.com/tagbase/tagbase-server.git

''' configure docker '''
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
apt-cache policy docker-ce
sudo apt-get install -y docker-ce
sudo systemctl status docker
sudo usermod -a -G docker ubuntu

''' configure docker compose '''
sudo curl -L https://github.com/docker/compose/releases/download/1.24.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

''' stop and restart instance: After above steps start here on new EC2 machine instatiation '''
ssh -i sharkbase.pem ubuntu@ec2-18-218-98-133.us-east-2.compute.amazonaws.com
cd sharkbase
cd tagbase-server
sudo service docker start
docker-compose build
docker-compose up

''' navigate to this browser endpoint '''
ec2-18-218-98-133.us-east-2.compute.amazonaws.com:5433/v2/tagbase/ui/ 
http://ec2-18-223-131-70.us-east-2.compute.amazonaws.com:5434/browser/


###### Load APL data into tagbase server: trying more methods 

''' command from the documentation READMe on github '''
curl -X GET --header 'Accept: application/json' 'http://0.0.0.0:5433/v2/tagbase/ingest/etuff?granule_id=1234&file=file%3A%2F%2F%2Fusr%2Fsrc%2Fapp%2Fdata%2FeTUFF-sailfish-117259.txt'

''' This worked: lets now try and load the shark data '''
#scp -i sharkbase.pem /Users/culhane/Downloads/Re__lanks/159924_2013_128419_eTUFF_hdr.txt ubuntu@ec2-3-14-13-209.us-east-2.compute.amazonaws.com:~/sharkbase/data/
scp -i sharkbase.pem /Users/culhane/Downloads/Re__lanks/159903_2012_117464_eTUFF_hdr.txt ubuntu@ec2-3-14-13-209.us-east-2.compute.amazonaws.com:~/sharkbase/data/
curl -X GET --header 'Accept: application/json' 'http://0.0.0.0:5433/v2/tagbase/ingest/etuff?granule_id=098769&file=file%3A%2F%2F%2Fusr%2Fsrc%2Fapp%2Fdata%2F159903_2012_117464_eTUFF_hdr.txt'

''' NOTES ON THIS: '''
# works when you run the above command, staging db schema is at https://github.com/tagbase/tagbase-server/blob/master/sqldb/tagbase-schema.sql
# have to coerce data into acceptible format given the schema, to do this as test with shark data, we just delete everything except the first two lines 
# because after this we have a text value that has a schema defined as double precision 


###### STEP III: splitting terminal on remote machine to be able to do data ingestion etc 
sudo apt-get install tmux
tmux
ctl+b+% # split terminal horizontally
ctl+b+o # toggle between terminals 


###### STEP IV: trail ingestion of sailfish data 
docker-compose up
ctl+b+o
curl -X GET --header 'Accept: application/json' 'ec2-3-16-89-110.us-east-2.compute.amazonaws.com:5433/v2/tagbase/ingest/etuff?granule_id=1234&file=file%3A%2F%2F%2Fusr%2Fsrc%2Fapp%2Fdata%2FeTUFF-sailfish-117259.txt'

###### Access pgAdmin
http://ec2-18-223-131-70.us-east-2.compute.amazonaws.com:5434/browser/

http://ec2-18-223-131-70.us-east-2.compute.amazonaws.com:5434/browser/

'''
un: tagbase
pw: tagbase
'''
'''
Add New Server
General Tab --> name: tagbase
Connection Tab --> Host name/address: postgres
Connection Tab --> Port: 5432
Connection Tab --> Maintenance database: postgres
Connection Tab --> Username: tagbase
'''

# copy the query from this file & execute in query tool in tagbase serve 
tagbase-server/sql/tagbase-materialized-views.sql


###### STEP V: Sending shark data to machine ****** THIS IS WHERE WE ARE LEAVING OFF!! MAKING DATA AVAILABLE TO APP, INGESTION WORKS FOR THIER ETUFF BUT NOT OURS, OR THIERS WHEN WE RENAME

scp -i sharkbase.pem /Users/culhane/Downloads/159903_2012_117464_eTUFF_hdr.txt ubuntu@ec2-3-16-89-110.us-east-2.compute.amazonaws.com:~/sharkbase/data/

chmod --reference=eTUFF-sailfish-117259.txt 159903_2012_117464_eTUFF_hdr.txt











http://ec2-3-16-89-110.us-east-2.compute.amazonaws.com:5433/v2/tagbase/ui/#!/Products/ingest_etuff_get

curl -X GET --header 'Accept: application/json' 'ec2-3-16-89-110.us-east-2.compute.amazonaws.com:5433/v2/tagbase/ingest/etuff?granule_id=1234&file=file%3A%2F%2F%2Fusr%2Fsrc%2Fapp%2Fdata%2FeTUFF-test.txt'

curl -X GET --header 'Accept: application/json' 'ec2-3-16-89-110.us-east-2.compute.amazonaws.com:5433/v2/tagbase/ingest/etuff?granule_id=1599032012117464&file=file%3A%2F%2F%2Fusr%2Fsrc%2Fapp%2Fdata%2F159903_2012_117464_eTUFF_hdr.txt'





/home/ubuntu/sharkbase/data/159903_2012_117464_eTUFF_hdr.txt

curl -X GET --header 'Accept: application/json' 'ec2-3-16-89-110.us-east-2.compute.amazonaws.com:5433/v2/tagbase/ingest/etuff?granule_id=159903_2012_117464&file=file%3A%2F%2F%2Fusr%2Fsrc%2Fapp%2Fdata%2FeTUFF-sailfish-117259.txt'

curl -X GET "http://ec2-3-16-89-110.us-east-2.compute.amazonaws.com:5433/v2/tagbase/ingest/etuff?granule_id=159903_2012_117464&file=%2FUsers%2Fculhane%2FDownloads%2F159903_2012_117464_eTUFF_hdr.txt" -H "accept: application/json"

/Users/culhane/Downloads/159903_2012_117464_eTUFF_hdr.txt






