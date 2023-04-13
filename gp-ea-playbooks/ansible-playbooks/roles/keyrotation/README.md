# Table of contents
1. Introduction
2. Design
3. Testing

## 1. Introduction
This playbook is used to rotate the old key pairs associated with Linux ec2 instances across all VPCs managed by Ops

## 2. Design
Below is the Flow chart diagram for keyrotation role.

![Flow Diagram](https://github.build.ge.com/gp-ansible/gp-ea-playbooks/blob/master/ansible-playbooks/roles/Images/keyrotation.png)

## 3. Testing 

<p align="center"><strong>LINUX</strong></p>

| Test Cases  | Expected Output   | Actual Output  |
|:-----------:|:-----------------:|:--------------:|
| python3 is installed | Python3 is installed or not on the server will be checked. python3 is installed, then the libselinux-python3 package will be installed with the latest version. And the keyrotation role will be included to execute the playbook | Checked python3 is present on the server, it installed the libselinux-python3 package with latest version on server and included keyrotation roles to execute playbook |
| python3 is not installed, python2 is installed | Python3 is installed or not on the server will be checked. python3 is not installed, then it will skip the task of installing libselinux-python3 package and include the keyrotation role to execute playbook. | Python3 is installed or not on the server has been checked. python3 is not installed, then it will skip the task of installing libselinux-python3 package and included the keyrotation role to execute playbook. |
| keyname is old, keyname != "" | Backup of the old gecloud will be taken on the server.Key pair name associated with server will be fetched, Corresponding vault pub secret will be called and contents of the public key will be copied to authorized gecloud user. Connection with new key will be checked. If connection successful, then backup from the server will be deleted | Backup of the old gecloud taken on the server.Key pair name of server is fetched.Corresponding vault pub secret called and contents of the public key are copied to authorized keys of gecloud user. Connection with new key checked. Connection is successful, backup from the server deleted |
| keyname == "" | Backup of the old gecloud will be taken on the server.Key pair name associated with server will be fetched, Corresponding vault pub secret will be called and contents of the public key will be copied to authorized gecloud user. Connection with new key will be checked. If connection successful, then backup from the server will be deleted | Backup of the old gecloud taken on the server.Key pair name of the server is fetched, Corresponding vault pub secret is included and contents of the public key are copied to authorized keys of gecloud user. Connection with new key checked. Connection is successful,backup from the server is deleted |
| New keys not updated successfully  | New keys will be updated successfully on server | New keys updated successfully on the server |
| old keys of the server need to be removed after successful rotation   | After successful rotation, the old keys needs to be removed from target server. So that old key will no longer be used for login |After successful rotation, the old keys are removed from target server. Connection to the server with old keys is denied|
| Old keys can no longer be used to login | After successful rotation, connection with old key should not be establish.It will prompt permission denied while trying to connect to the server with old key  |After successful rotation, connection with old key is not established.It has prompted permission denied while trying to connect to server with old key|
