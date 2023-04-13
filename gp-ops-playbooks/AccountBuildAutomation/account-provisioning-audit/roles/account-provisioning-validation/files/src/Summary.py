import os
import json
import yaml
import xlsxwriter

class Summary:

    def fetch_config_file(self):
        with open(self.ideal_account_path, 'r') as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    def __init__(self):

        # create placeholders for all key class-level variables
        self.reports = []
        self.reports_path = "/tmp/account-automation-folder/account-audit-service/output/json"
        self.ideal_account_path = "/tmp/account-automation-folder/account-audit-service/config/ideal_account.yml"
        self.primaryWorkbook = xlsxwriter.Workbook('/tmp/account-automation-folder/account-audit-service/output/account-audit-summary.xlsx')
        self.title_format, self.not_required_format, self.done_format, self.missing_format = self.build_xslx_format_objects()
        self.config_file = self.fetch_config_file()

        # create container for audit summary files:
        self.build_reports_list()
        
        # given base workbook object, add all worksheets and first column to each
        self.build_primary_workbook()

        # process each report generated
        self.process_reports()
        
        # write xslx to file system
        self.primaryWorkbook.close()

    def build_reports_list(self):

        # creating/update org based on all files within default config
        for dirName, subdirList, fileList in os.walk(self.reports_path):
            for fname in fileList:
                filePath = "{}/{}".format(dirName, fname) 

                # do not process placeholder text: process JSON reports only.
                if ".json" in fname:
                    with open(filePath) as f:
                        self.reports.append(
                            json.load(f)
                        )

    # return tuple of xslx format object to style various configuration results
    def build_xslx_format_objects(self):

        # instantiate format objects
        title_format = self.primaryWorkbook.add_format({'bold': True})
        not_required_format = self.primaryWorkbook.add_format({'bold': True})
        done_format = self.primaryWorkbook.add_format()
        missing_format = self.primaryWorkbook.add_format({'bold': True})

        # configure done & missing formats
        done_format.set_bg_color('green')
        missing_format.set_bg_color('red')
        not_required_format.set_bg_color('yellow')

        # return objects to be used globally
        return (
            title_format,
            not_required_format,
            done_format,
            missing_format
        )

    
    # create all child worksheet objects and initial columns
    def build_primary_workbook(self):

        # S3
        self.build_arbitrary_worksheet("Bucket-Policies", config={'main':"s3", 'secondary':"bucketPolicies"})
        
        # IAM
        self.build_arbitrary_worksheet("IAM-Roles", config={'main':"iam", 'secondary': "requiredRoles"})
        self.build_arbitrary_worksheet("IAM-Policies", config={'main':"iam", 'secondary':"requiredPolicies"})
        
        # VPC
        self.build_arbitrary_worksheet("VPC-Security-Groups", config={'main':"vpc", 'secondary':"requiredSecurityGroups"})
        self.build_arbitrary_worksheet("VPC-Subnet-Types", config={'main':"vpc", 'secondary':"allSubnetTypes"})
        self.build_arbitrary_worksheet("VPC-Route-Tables", config={'main':"vpc", 'secondary':"requiredTables"})
        self.build_arbitrary_worksheet("VPC-Misc", config={'main':"vpc", 'secondary':"n/a"})

        # SSM
        self.build_arbitrary_worksheet("SSM-Documents", config={'main':"ssm", 'secondary':"requiredDocuments"})
        self.build_arbitrary_worksheet("SSM-Windows", config={'main':"ssm", 'secondary':"requiredWindows"})
        self.build_arbitrary_worksheet("SSM-Parameters", config={'main':"ssm", 'secondary':"requiredSSMParameters"})
        self.build_arbitrary_worksheet("SSM-Associations", config={'main':"ssm", 'secondary':"requiredAssocationDocuments"})
        
        # NOT SURE HOW TO INCORPORATE THIS - LEAVING OUT SSM ASSOCIATIONS
        # self.build_arbitrary_worksheet("Maintenance-Window-Status", "ssm", "requiredWindows")

        # STACKS
        self.build_arbitrary_worksheet("Stacks-StackSets", config={'main':"stacks", 'secondary':"requiredStacks"})
        self.build_arbitrary_worksheet("Stacks-Subnet-Groups", config={'main':"stacks", 'secondary':"requiredSubnetGroups"})
        self.build_arbitrary_worksheet("Stacks-RDS-Parameter-Groups", config={'main':"stacks", 'secondary':"requiredRDSParameterGroups"})
        self.build_arbitrary_worksheet("Stacks-RDS-Option-Groups", config={'main':"stacks", 'secondary':"requiredRDSOptionGroups"})
        self.build_arbitrary_worksheet("Stacks-Misc", config={'main':"stacks", 'secondary':"n/a"})

        # MISC
        self.build_arbitrary_worksheet("Misc-Config-Rules", config={'main':"misc", 'secondary':"requiredConfigRules"})
        self.build_arbitrary_worksheet("Misc-Lambda-Functions", config={'main':"misc", 'secondary':"requiredLambdaFunctions"})
        self.build_arbitrary_worksheet("General-Misc", config={'main':"misc", 'secondary':"n/a"})


    # given worksheet name & configuration categories + sections, build the provided worksheet
    # & build all columns
    def build_arbitrary_worksheet(self, worksheetName, config):
        new_worksheet = self.primaryWorkbook.add_worksheet(worksheetName)
        new_worksheet.write(0,0, "Account Name", self.title_format)
        new_worksheet.write(0,1, "Account ID", self.title_format)
        new_worksheet.write(0,2, "Timestamp", self.title_format)

        # handling non-typical worksheet types
        if worksheetName == 'VPC-Misc':
            new_worksheet.write(0,3, "Non Default VPC Exists", self.title_format)
            new_worksheet.write(0,4, "Internet Gateway Exists", self.title_format)
            new_worksheet.write(0,5, "NAT Gateway Exists", self.title_format)

        elif worksheetName == 'VPC-Route-Tables':
            new_worksheet.write(0,3, "'rt-app' OR 'rt-Private'", self.title_format)

        elif worksheetName == 'Stacks-Misc':
            # new_worksheet.write(0,3, "Status Filter", self.title_format)
            new_worksheet.write(0,3, "Patch Window Correct", self.title_format)
            new_worksheet.write(0,4, "KMS Key Created", self.title_format)

        elif worksheetName == 'General-Misc':
            new_worksheet.write(0,3, "EBS Encryption By Default", self.title_format)
            new_worksheet.write(0,4, "Cloud Watch Topic Exists", self.title_format)

        elif worksheetName == 'SSM-Associations':

            # return assocation name & corresponding ssm doc
            def fetch_assocation_name(item):
                if item == 'SSM-App-Splunk-Linux-Windows-Config':
                    return "SplunkConfig (SSM-App-Splunk-Linux-Windows-Config)"
                elif item == 'SSM-App-Qualys-Linux-Windows-Config':
                    return "QualysConfig (SSM-App-Qualys-Linux-Windows-Config)"
                # elif item == 'app-QualysWindowsReg':
                #     return "QualysWindowsConfig (app-QualysWindowsReg)"
                # elif item == 'app-qualys-rereg-onfailure':
                #     return "QualysLinuxConfig (app-qualys-rereg-onfailure)"
                else:
                    return item

            # fetch list config object 
            configObject = self.config_file[config['main']][config['secondary']]

            # iterate through all required roles
            for item in configObject:

                # calculate next index to place role, account for placeholder values defined above
                columnIndex = configObject.index(item) + 3
                new_worksheet.write(
                    0,
                    columnIndex,
                    # support addition of future associations
                    fetch_assocation_name(item),
                    self.title_format
                )

        else:

            # fetch list config object 
            configObject = self.config_file[config['main']][config['secondary']]

            # Configuration must be a list or an object
            if type(configObject) is set:
                configObject = list(configObject)

            # iterate through all required roles
            for item in configObject:

                # calculate next index to place role, account for placeholder values defined above
                columnIndex = configObject.index(item) + 3
                new_worksheet.write(0, columnIndex, item, self.title_format)
    

    # injest report data, populate worksheet
    def build_results_by_config_worksheet_report(self, data):

        # obtain row index where we will stage data into specified worksheet, accounting for the header
        rowIndex = data["reportIndex"] + 1

        # publish account ID, account name and timestamp to specified worksheet 
        data["worksheet"].write(rowIndex, 0, data["accountInformation"]["AccountName"])
        data["worksheet"].write(rowIndex, 1, data["accountInformation"]["AccountId"])
        data["worksheet"].write(rowIndex, 2, data["accountInformation"]["Timestamp"])

         # handling non-typical worksheet types
        if data['worksheet'].get_name() == 'Bucket-Policies':

            ## NOTE: the audit report only contains items that are MISSING
            # Handle Non Default VPC 
            # this case is different because buckets will always be present in report: listed either as true/fase
            
            # gp-ops-ssm-logs
            if data["missingConfigurations"]['gp-ops-ssm-logs']:
                data["worksheet"].write(rowIndex, 3, "Present", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 3, "Missing", self.missing_format)

            # gp-us-east-ops-automation-common-artifacts
            if data["missingConfigurations"]['gp-us-east-ops-automation-common-artifacts']:
                data["worksheet"].write(rowIndex, 4, "Present", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 4, "Missing", self.missing_format)

            # gp-us-east-ops-automation-common-tools
            if data["missingConfigurations"]['gp-us-east-ops-automation-common-tools']:
                data["worksheet"].write(rowIndex, 5, "Present", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 5, "Missing", self.missing_format)
            
            # gp-eu-west-ops-automation-common-artifacts
            if data["missingConfigurations"]['gp-eu-west-ops-automation-common-artifacts']:
                data["worksheet"].write(rowIndex, 6, "Present", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 6, "Missing", self.missing_format)

            # gp-us-west-ops-automation-common-artifacts
            if data["missingConfigurations"]['gp-us-west-ops-automation-common-artifacts']:
                data["worksheet"].write(rowIndex, 7, "Present", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 7, "Missing", self.missing_format)

            # uai3027632-pw-sec-automation-gp-ops
            if data["missingConfigurations"]['uai3027632-pw-sec-automation-gp-ops']:
                data["worksheet"].write(rowIndex, 8, "Present", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 8, "Missing", self.missing_format)

        elif data['worksheet'].get_name() == 'VPC-Route-Tables':

            ## NOTE: the audit report only contains items that are MISSING
            # Handle Non Default VPC
            rtAppMissing = True if 'rt-app' in data["missingConfigurations"] else False
            rtPrivateMissing = True if 'rt-Private' in data["missingConfigurations"] else False

            if not rtAppMissing or not rtPrivateMissing:
                data["worksheet"].write(rowIndex, 3, "Present", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 3, "Missing", self.missing_format)

        elif data['worksheet'].get_name() == 'VPC-Subnet-Types':

            # convert set of subnet types to a list
            all_subnets_list = list(data["config"])

            # traverse through all subnet types
            for subnet in all_subnets_list:

                columnIndex = all_subnets_list.index(subnet) + 3

                # is this subnet required in this account?
                if subnet in data["missingConfigurations"]["ExpectedSubnets"]:

                    # is this subnet missing from the expected list if subnets?
                    if subnet in data["missingConfigurations"]["MissingSubnets"]:
                        data["worksheet"].write(rowIndex, columnIndex, "Missing", self.missing_format)
                    else:
                        data["worksheet"].write(rowIndex, columnIndex, "Present", self.done_format)
                else:
                    # write to spreadsheet: this subnet IS NOT required in THIS account
                    data["worksheet"].write(rowIndex, columnIndex, "Not Required", self.not_required_format)
                    
        elif data['worksheet'].get_name() == 'VPC-Misc':

            ## NOTE: the audit report only contains items that are MISSING
            # Handle Non Default VPC 
            if data["missingConfigurations"]["NonDefaultVPCExists"] == True:
                data["worksheet"].write(rowIndex, 3, "Present", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 3, "Missing", self.missing_format)

            # Handle Internet Gateway
            if data["missingConfigurations"]["InternetGateway"] == True:
                data["worksheet"].write(rowIndex, 4, "Present", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 4, "Missing", self.missing_format)
            
            # Handle Nat Gateway
            if data["missingConfigurations"]["NatGateway"] == True:
                data["worksheet"].write(rowIndex, 5, "Present", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 5, "Missing", self.missing_format)
        

        elif data['worksheet'].get_name() == 'Stacks-Misc':

            # Handle PatchWindowRegionCorrect
            if data["missingConfigurations"]["PatchWindowRegionCorrect"] == True:
                data["worksheet"].write(rowIndex, 3, "Correct", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 3, "Incorrect", self.missing_format)

            # Handle KMSKeyCreated
            if data["missingConfigurations"]["KMSKeyCreated"] == True:
                data["worksheet"].write(rowIndex, 4, "Done", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 4, "Missing", self.missing_format)

        elif data['worksheet'].get_name() == 'General-Misc':

            # Handle EBSEncryptionByDefault
            if data["missingConfigurations"]["EBSEncryptionByDefault"] == True:
                data["worksheet"].write(rowIndex, 3, "Done", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 3, "Missing", self.missing_format)

            # Handle CloudWatchTopicExists
            if data["missingConfigurations"]["CloudWatchTopicExists"] == True:
                data["worksheet"].write(rowIndex, 4, "Done", self.done_format)
            else:
                data["worksheet"].write(rowIndex, 4, "Missing", self.missing_format)

        elif data['worksheet'].get_name() == 'SSM-Associations':

            # gather missing assocations from report file
            faultyAssocations = data["missingConfigurations"]

            # iterate through all expected associations
            for requiredAssociation in data["config"]:

                # track whether control is present/not
                missingConfig = ""

                # fetch column index
                columnIndex = data["config"].index(requiredAssociation) + 3

                # iterate through all missing/incorrect assocations
                for key in faultyAssocations.keys():
                    
                    # check if document is found in assocation arn
                    if requiredAssociation in key:
                        missingConfig = key
                        break
                
                # is this control missing or not
                if missingConfig == "":
                    # the assocation appears as expected
                    data["worksheet"].write(rowIndex, columnIndex, "Enabled", self.done_format)
                else:
                    # missing config found
                    data["worksheet"].write(rowIndex, columnIndex, faultyAssocations[missingConfig], self.missing_format)

        elif data['worksheet'].get_name() == 'SSM-Windows':

            # fetch maintenance window from the report
            maintenanceWindows = data["missingConfigurations"].items()

            # traverse through all maintenance windows
            for window, status in maintenanceWindows:

                # fetch column index
                columnIndex = data["config"].index(window) + 3

                # the assocation appears as expected
                data["worksheet"].write(
                    rowIndex,
                    columnIndex,
                    status,
                    self.done_format if status == "Enabled" else self.missing_format
                )

        else:

            # THIS MUST BE A LIST
            if type(data["missingConfigurations"]) is set:
                data["missingConfigurations"] = list(data["missingConfigurations"])

            # CHANGING ALL SETS IN THE ACCOUNT_LIST TO USE LISTS
            if type(data["config"]) is set:
                data["config"] = list(data["config"])

            # traverse through all configuration items expected to exist in an account 
            for item in data["config"]:
                columnIndex = data["config"].index(item) + 3

                ## NOTE: the audit report only contains items that are MISSING 
                if item in data["missingConfigurations"]:
                    data["worksheet"].write(rowIndex, columnIndex, "Missing", self.missing_format)
                else:
                    data["worksheet"].write(rowIndex, columnIndex, "Done", self.done_format)

    # build payload
    def gather_workbook_parameters(self, report, worksheet):

        # define parameters set to be returned
        params = {
            "config": "",
            "accountInformation": report[0]["AccountAndTimeData"],
            "reportIndex": self.reports.index(report),
            "worksheet": worksheet,
            "missingConfigurations": ""
        }
        
        # provide parameters based on worksheet name
        if "Bucket-Policies" == worksheet.get_name():
            params["config"] = self.config_file["s3"]["bucketPolicies"]
            params["missingConfigurations"] = report[1]["BucketPolicyUpdates"]
        
        # =================================================================================

        if "IAM-Roles" == worksheet.get_name():
            params["config"] = self.config_file["iam"]["requiredRoles"]
            params["missingConfigurations"] = report[2]["IAM"]["MissingRoles"]

        elif "IAM-Policies" == worksheet.get_name():
            params["config"] = self.config_file["iam"]["requiredPolicies"]
            params["missingConfigurations"] = missingConfigurations=report[2]["IAM"]["MissingPolicies"]

        # =================================================================================

        elif "VPC-Security-Groups" == worksheet.get_name():
            params["config"] = self.config_file["vpc"]["requiredSecurityGroups"]
            params["missingConfigurations"] = report[3]["VPC"]["MissingSecurityGroups"]

        elif "VPC-Subnet-Types" == worksheet.get_name():   
            params["config"] = self.config_file["vpc"]["allSubnetTypes"]

            print("report[3]['VPC'] = {}".format(report[3]['VPC']))


            params["missingConfigurations"] = {
                "ExpectedSubnets": report[3]["VPC"]["ExpectedSubnets"],
                "MissingSubnets": report[3]["VPC"]["MissingSubnets"]
            }    

        elif "VPC-Route-Tables" == worksheet.get_name():   
            params["config"] = self.config_file["vpc"]["requiredTables"]
            params["missingConfigurations"] = report[3]["VPC"]["MissingRouteTables"]

        # handling special VPC-Misc case
        elif "VPC-Misc" == worksheet.get_name():
            params["config"] = self.config_file["vpc"]
            params["missingConfigurations"] = report[3]["VPC"]

        # =================================================================================

        elif "SSM-Documents" == worksheet.get_name():
            params["config"] = self.config_file["ssm"]["requiredDocuments"]
            params["missingConfigurations"] = report[4]["SSM"]["MissingDocuments"]

        elif "SSM-Windows" == worksheet.get_name():
            params["config"] = self.config_file["ssm"]["requiredWindows"]
            params["missingConfigurations"] = report[4]["SSM"]["MaintenanceWindowStatus"]

        elif "SSM-Parameters" == worksheet.get_name():
            params["config"] = self.config_file["ssm"]["requiredSSMParameters"]
            params["missingConfigurations"] = report[4]["SSM"]["ErroneousSSMParameters"] 

        # ISSUE: NOT SURE OF HOW TO NOTATE ERRONEOUS ASSOCIATIONS IN ACCOUNT CONFIG FILE
        elif "SSM-Associations" == worksheet.get_name():
            params["config"] = self.config_file["ssm"]["requiredAssocationDocuments"]
            params["missingConfigurations"] = report[4]["SSM"]["ErroneousAssociations"]

        # =================================================================================


        elif "Stacks-StackSets" == worksheet.get_name():
            params["config"] = self.config_file["stacks"]["requiredStacks"]
            params["missingConfigurations"] = report[5]["Stacks"]["MissingStacks"]

        elif "Stacks-Subnet-Groups" == worksheet.get_name():
            params["config"] = self.config_file["stacks"]["requiredSubnetGroups"]
            params["missingConfigurations"] = report[5]["Stacks"]["MissingRDSSubnetGroups"]

        elif "Stacks-RDS-Parameter-Groups" == worksheet.get_name():
            params["config"] = self.config_file["stacks"]["requiredRDSParameterGroups"]
            params["missingConfigurations"] = report[5]["Stacks"]["MissingRDSParameterGroups"]

        elif "Stacks-RDS-Option-Groups" == worksheet.get_name():
            params["config"] = self.config_file["stacks"]["requiredRDSOptionGroups"]
            params["missingConfigurations"] = report[5]["Stacks"]["MissingRDSOptionGroups"]

        elif "Stacks-Misc" == worksheet.get_name():
            params["config"] = self.config_file["stacks"]
            params["missingConfigurations"] = report[5]["Stacks"]

        # =================================================================================

        # NOT SURE OF HOW TO ADD STACK STATUS FILTER.. MISSING IN SOME REPORT FILES

        elif "Misc-Config-Rules" == worksheet.get_name():
            params["config"] = self.config_file["misc"]["requiredConfigRules"]
            params["missingConfigurations"] = report[6]["Miscellaneous"]["MissingConfigRules"]

        elif "Misc-Lambda-Functions" == worksheet.get_name():
            params["config"] = self.config_file["misc"]["requiredLambdaFunctions"]
            params["missingConfigurations"] = report[6]["Miscellaneous"]["MissingLambdaFunctions"]

        elif "General-Misc" == worksheet.get_name():
            params["config"] = self.config_file["misc"]
            params["missingConfigurations"] = report[6]["Miscellaneous"]

        # provide configuration parameter object
        return params

                
    # iterate through each report file, cross reference between account data and ideal_account list
    def process_reports(self):

        # traverse through each account
        for report in self.reports:

            # traverse through all worksheets
            for worksheet in self.primaryWorkbook.worksheets():

                # process report results onto given worksheet
                self.build_results_by_config_worksheet_report(
                    self.gather_workbook_parameters(report, worksheet)    
                )           