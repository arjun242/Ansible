from ipaddress import IPv4Network, IPv4Address
from collections import OrderedDict

def converNumbertoCount(num):
    return 2**(32-num)

def findSubnets(existingSubnets, vpcCIDR, appSubnetCIDRNumber, dbSubnetCIDRNumber, epSubnetCIDRNumber, extSubnetCIDRNumber, rbSubnetCIDRNumber, igrSubnetCIDRNumber):
    # existingSubnets - List of Strings
    # vpcCIDR, appSubnetCIDRNumber, dbSubnetCIDRNumber, epSubnetCIDRNumber, extSubnetCIDRNumber, rbSubnetCIDRNumber, igrSubnetCIDRNumber - String

    # Converting list of string to list of IPv4Address objects
    # Need to convert to unicode objects for Python 2.7
    existingSubnetsObjects = []
    for i in range(0,len(existingSubnets)):
        temp = unicode(existingSubnets[i])
        existingSubnetsObjects.append(IPv4Network(temp,strict=False))
        print(existingSubnets[i])
    vpcCIDR = unicode(vpcCIDR)
    existingSubnetsObjects.sort()
    # 10.124 10.256 10.48.254.0/27

    CIDRBlockDict = {"appSubnet": int(appSubnetCIDRNumber), "dbSubnet": int(dbSubnetCIDRNumber), "epSubnet": int(epSubnetCIDRNumber), "extSubnet": int(extSubnetCIDRNumber), "rbSubnet": int(rbSubnetCIDRNumber), "igrSubnet": int(igrSubnetCIDRNumber)}
    sortedCIDRBlocks = OrderedDict(sorted(CIDRBlockDict.items(), key=lambda t: t[1]))
    print(sortedCIDRBlocks)

    # CIDRNumberList = [appSubnetCIDRNumber,dbSubnetCIDRNumber, epSubnetCIDRNumber, extSubnetCIDRNumber, rbSubnetCIDRNumber, igrSubnetCIDRNumber]
    CIDRNumberList = list(sortedCIDRBlocks.items()) # Can change to for key,value in sortedCIDRBlocks

    
    returnList=[]
    returnDict = {}
    for i in range(0,len(CIDRNumberList)):
        print(returnList)
        print('\n\n')
        if i == 0:
            startIP = IPv4Network(vpcCIDR,strict=False).network_address
        else:
            startIP = existingSubnetsObjects[0].network_address
        j=0
        while(j< len(existingSubnetsObjects)):
            startCIDR = unicode(str(startIP)+'/'+ str(CIDRNumberList[i][1]))
            if IPv4Network(startCIDR).overlaps(existingSubnetsObjects[j]) == False:
                if CIDRNumberList[i][0] not in returnDict:
                    returnDict[CIDRNumberList[i][0]] = startCIDR
                returnList.append(startCIDR)
                existingSubnetsObjects.append(IPv4Network(startCIDR,strict=False))
                existingSubnetsObjects.sort()
                break
            else:
                startIP = existingSubnetsObjects[j].network_address + len(list(existingSubnetsObjects[j].hosts())) + 2    
                        
            j+=1
        if j == len(existingSubnetsObjects):
            startCIDR = unicode(str(startIP)+'/'+ str(CIDRNumberList[i][1]))
            if CIDRNumberList[i][0] not in returnDict:
                returnDict[CIDRNumberList[i][0]] = startCIDR
            returnList.append(startCIDR)
            existingSubnetsObjects.append(IPv4Network(startCIDR,strict=False))
            existingSubnetsObjects.sort()
        
    print(returnList)
    return returnDict

def returnFirst(s):
    return s[0]

class FilterModule(object):
    def filters(self):
        return {
            'findSubnetsFilter': findSubnets
        }

# print(findSubnets(['10.230.255.96/27','10.230.255.192/28','10.230.255.208/28','10.230.255.224/28','10.230.255.224/28','10.230.255.240/28'],'10.230.254.0/23','26','27','28','26','27','28'))
# print(IPv4Network('10.230.255.224/28',strict=True).network_address)
# print(findSubnets(['100.64.0.0/19','100.64.32.0/19','100.64.64.0/19','100.64.96.0/19'],'100.64.0.0/16','26','27','28','26','27','28'))