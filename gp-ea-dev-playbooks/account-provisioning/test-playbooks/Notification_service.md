## Purpose
This document is intended to explain the design and implementation of the Notification service playbook.

## Description
When the playbook is executed,an email notification from the sender is sent to the security team by using SMTP server.

- **SMTP Server** is Simple Mail Transfer Protocol which is an application that sends,receives emails.
SMTP also has it's own ip address and domain.

   Here the domain used is **alpmlip01.e2k.ad.ge.com [3.159.17.48]** ,the referece of which was been taken from the following - [link](https://geit.service-now.com/nav_to.do?uri=%2Fkb_view.do%3Fsys_kb_id%3D8b3b78ebdb33a0509a06f7d6f3961945) 

- **Ansible Mail Module**
    ```
     - mail:
        host: <value>
        port: <value>
        from: <value>
        to: <value>
        bcc: <value>
        subject: <value>
        body: <value>
      delegate_to: localhost
    ```
   This module is useful for sending mails using SMTP servers from playbooks.Module also facilitates to attach the multiple files and customizing body according to the user requirement.


## Assumption

- Connectivity to SMTP servers

## Tasks
Send mail to the security team regarding the account provisioning .
## Variables
| Variable Name | Description | Required before independent execution?(Yes/No) |
| -- | -- | -- |
| aws_account_name | Unique name to identify the AWS account | Yes |
| aws_account_id | It is a 12-digit number ,used to identify a AWS account | Yes |
| vpc_id | AWS virtual network dedicated to the AWS account | Yes |

## Directory Structure
```
+---tasks
|       main.yml
+---vars
|       main.yml
```
## Directory Structure Explanation

*Parent directory:- parallel-actions/roles/Notification_service*

- **tasks/**
    | | |
    | -- | -- |
    | main.yml | Contains task with mail module to send an email to the security team |

- **vars/**
    | | |
    | -- | -- |
    | mail.yml | This Var file contains the aws account variables and vpc id which are mentioned under the account details in the email.  |

## Outputs

An email to the security team is been sent with the account details.

## Unit Testing

| S . No | Test case | Expected Output | Actual Output |
| -- | -- | -- | -- |
| 1 | alpmlip01.e2k.ad.ge.com [3.159.17.48]  | Able to send mail on this server | Mail sent
| 2 | cinmlip01.e2k.ad.ge.com [3.159.213.48] | Able to send mail on this server | Mail sent
| 3 | cinmlip03.e2k.ad.ge.com [3.159.212.78]e | Able to send mail on this server | Mail not sent
| 4 | alpmlip03.e2k.ad.ge.com [3.159.19.78] | Able to send mail on this server | Mail not sent