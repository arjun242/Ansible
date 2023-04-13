def addQuotes(list):
    return [ '\'' + x + '\'' for x in list]

class FilterModule(object):
    def filters(self):
        return {
            'addQuotes': addQuotes
        }