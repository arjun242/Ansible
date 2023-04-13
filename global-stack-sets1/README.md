# global-stack-sets
This repo is used for Managing Stackset in gp-ops: 325381443140 AWS account.

This Repo is Intigrated with global-stacksets-pipeline in gp-ops account.
(https://us-east-1.console.aws.amazon.com/codesuite/codepipeline/pipelines/global-stacksets-pipeline/view?region=us-east-1 )
any commits to this repo will trigger this pipeline.

# Usage Instructions:
The pipeline can only create a new stackset or update the stackInstances of exisitng Stackset.
it cannot create new stackset instances in any stackset.

# How to create a new StackSet or update exisitng in gp-ops account ?

Follow the below Steps to create a StackSet:
* Create a folder structure as shown in this reference folder New-StackSet-Reference -> https://github.build.ge.com/gp-ops/globalstackset/New-StackSet-Reference 
* Raise PR with the changes and Codeowners can Approve the PR.
* After successfull Commiting the changes into the master branch, this will trigger the pipeline which manages Stackset.
* if the list of stacksets mentioned int stack_master.yml file are not present pipeline will create them, other wise pipeline will update the respective Stacksets.


# How to create a stackset Instance in any exisiting or new stackset ?

for this operation we have a different pipleine. PLease refer to this link https://github.build.ge.com/gp-ops/gr-accounts-setup#readme
