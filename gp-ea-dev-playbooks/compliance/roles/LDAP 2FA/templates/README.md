Short Description and logic used for the dynamic templates:

1. access.conf.j2: First, it is checking for the netgroups array parsed from the main.yml in tasks. If the variable is defined, then a 'for' loop is being used. For all the elements in the netroups, it is splitting the elements by ':' and storing it in a new list. After this, it's simply printing the group names which is stored in list[0]. Ending the for loop and if statement.
2. ldap.conf.j2: A check for Account Id fetched from the instance level is being done with the Account Id of multiple accounts stored in the vars. If it matches with any one the Account IDs, then a check for Address happens, if it matches with Bastion IPs, then the BASE and URI will be printed. If the IP address of the target host does not match with that of the Bastion IPs, then all the servers is ldap_servers(in vars) is placed along with the ldap_protocol and ldap_port(all in vars). This process is same for all the mentioned Account IDs.  
3. netgroups_sudoers.j2: The default group is printed for all. Then it is checking for the 'netgroups' array parsed from the main.yml in tasks. If the variable is defined, then a 'for' loop is being used. For all the elements in the 'netroups', splitting the elements by ':' regex and storing it in a new array(list1). Now, the 'list1[0]' will contain the group name and 'list1[1]' will have all the permissions of that particular group. After that, the permissions will be stored in another variable named 'allpermissions'. Again, the string in the 'allpermission' is splitted into parts from regex ',' and storing the result in 'list2'. If the 'list2' contains 1 or more elements, then for all the elements in 'list2' the group name(which is stored in list1[0]) and corresponding permission is printed. 
4. server.j2: All the servers used in this template is being fetched from the 'raddb_servers' defined in vars. Conditional check is being done to template the secrets according to different accounts. **secret_keys are fetched from the secrets.yml in vars**
5. sssd.conf: 'ldap_bind_dn' and 'ldap_auth_token' is printed according to the conditional check for Account ID. 