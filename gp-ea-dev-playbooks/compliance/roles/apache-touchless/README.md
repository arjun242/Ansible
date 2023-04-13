Description: Execute this playbook to set-up apache config files (ssl.conf & oidc.conf) on the target host

Scope: This document is setup to work with Linux hosts only

All the tasks of this playbook begins in the main.yml located in tasks folder.

* This playbook configures the oidc.conf and ssl.conf files required as a part of apache configuration for an instance. The inputs are read from an appConfig.json file and placed as respective parameters in the jinja templates for oidc and ssl.

* For applications with specific oidc.erb and ssl.erb templates stored in S3 bucket, the playbook fetches the templates convert them into jinja templates and further uses them to configure the oidc and ssl conf files using appConfig.json

* This playbook has the required checks to confirm apache installation, existing oidc and ssl configuration on an instance.

For now the playbook will be run on new instances configured with specific tags.