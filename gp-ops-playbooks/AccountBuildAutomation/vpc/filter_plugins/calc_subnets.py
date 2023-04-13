from ipaddress import IPv4Network, IPv4Address
from collections import OrderedDict

def findSubnets(existingSubnets, vpcCIDR, appSubnetCIDRNumber, dbSubnetCIDRNumber, epSubnetCIDRNumber, extSubnetCIDRNumber, rbSubnetCIDRNumber, igrSubnetCIDRNumber):
    # existingSubnets - List of Strings
    # vpcCIDR, appSubnetCIDRNumber, dbSubnetCIDRNumber, epSubnetCIDRNumber, extSubnetCIDRNumber, rbSubnetCIDRNumber, igrSubnetCIDRNumber - String

    # Converting list of string to list of IPv4Address objects
    # Need to convert to str objects (instead of unicode) for Python higher versions
    existingSubnetsObjects = []
    for i in range(0,len(existingSubnets)):
        temp = str(existingSubnets[i])
        existingSubnetsObjects.append(IPv4Network(temp,strict=False))
        print(existingSubnets[i])
    vpcCIDR = str(vpcCIDR)
    existingSubnetsObjects.sort()

    CIDRBlockDict = {"appSubnetCIDR": int(appSubnetCIDRNumber), "dbSubnetCIDR": int(dbSubnetCIDRNumber), "epSubnet": int(epSubnetCIDRNumber), "extSubnet": int(extSubnetCIDRNumber), "rbSubnet": int(rbSubnetCIDRNumber), "igrSubnet": int(igrSubnetCIDRNumber)}
    sortedCIDRBlocks = OrderedDict(sorted(CIDRBlockDict.items(), key=lambda t: t[1]))
    print(sortedCIDRBlocks)

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
            startCIDR = str(str(startIP)+'/'+ str(CIDRNumberList[i][1]))
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
            startCIDR = str(str(startIP)+'/'+ str(CIDRNumberList[i][1]))
            if CIDRNumberList[i][0] not in returnDict:
                returnDict[CIDRNumberList[i][0]] = startCIDR
            returnList.append(startCIDR)
            existingSubnetsObjects.append(IPv4Network(startCIDR,strict=False))
            existingSubnetsObjects.sort()
        
    print(returnList)
    return returnDict

class FilterModule(object):
    def filters(self):
        return {
            'findSubnetsFilter': findSubnets
        }