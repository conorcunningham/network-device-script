#!/usr/bin/python -txt

# script to read from a file containing IP addresses and/or hostnames
# of Cisco IOS devices
# SSH into device and execute commands
# can suppress or print output of command

# author: Conor Cunningham (conor.cunningham@gmail.com)

# need to install paramiko libraries in order to run this script
# do so by running the following two commands
# pip install cryptography
# pip install paramiko
import paramiko
import socket
import re


# send commands
# also detects if enable secret must be input
def send_command(command, wait_string, should_print):

  shell.send(command)

  recv_buffer = ""

  while not wait_string in recv_buffer:
    recv_buffer += shell.recv(1024)
    if '>' in recv_buffer:
      print('Enable Detected. Sending Enable Secret')
      send_enable()
      break

  if should_print:
    print(recv_buffer)
    return recv_buffer

# sends enable secret in order to get into enable mode
def send_enable():

  shell.send("enable\n")
  enable_buffer = ""

  while not ":" in enable_buffer:
    enable_buffer += shell.recv(1024)

  shell.send(enable+"\n")
  pass_buffer = ""
  pass_buffer += shell.recv(1024)

  if "#" in pass_buffer:
    print "Logged in Successfully"
  else:
    print "Enable Login Failed"
    quit()

def print_error(error_msg,host):
  error =1
  print (host + ": Error. " +  error_msg)
  return error

# set username here
# this will be looked up in the login.txt file
# each line of the file should containt user:pass
# for example
# conor:password123
# bob:easypassword
username = 'conor'

creds = open('login.txt','r')
credlist = {}

for line in creds:

  line = line.strip()
  line = line.split(':')
  credlist[line[0]] = line[1]

password = credlist.get(username)

if not password:
  print ("Username" + username + "defined in script not present in login.txt")
  quit()

#define enable here, or set it equal to password
enable = 'cisco'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#open list of devices
devices = open('devices.txt','r')

# execute command on all devices
for line in devices:

  error = 0

  #ignore commented out lines
  if line.startswith("#"): continue
  #match only valid IP addresses and hostnames
  ip = re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', line)
  hostname = re.match(r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$',line)
  valid_host = ip or hostname

  if not valid_host: continue
  #get our now sanitised host
  host = line.rstrip()

  try:
    #set timeout to 10 seconds. You may want to increase this on high latency networks
    ssh.connect(host,username=username,password=password,allow_agent=False, look_for_keys=False,timeout=10)
  except paramiko.ssh_exception.AuthenticationException:
    error = print_error("Authentication Error",host)
    pass
  except paramiko.ssh_exception.SSHException:
    error = print_error("SSH Protocol Error",host)
    pass
  except paramiko.ssh_exception.NoValidConnectionsError:
    error = print_error("Connnection Refused",host)
    pass
  except:
    error = print_error('Socket Timeout',host)
    pass

  # use the send_command function to send commands.
  # first parameter is the command
  # second parameter is the character of the prompt (i.e. when do we
  # stop reading the buffer)
  # this parameter is whether we print the output or not (1 for pint,
  # 0 for not print)
  if error == 0:
    shell = ssh.invoke_shell()
    send_command('', '#',0)
    send_command('terminal length 0\n', '#',0)
    send_command('show ip int br\n', '#',0)
    print  host + ": Success. Commands sent!"
    ssh.close()