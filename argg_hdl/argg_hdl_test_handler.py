gtests = {}

def run_test(TestName):
    return gtests[TestName]()

def run_all_tests():
    print('<tests>')
    for x in gtests.keys():
        result, message = gtests[x]()
        if result:
            print('  <test name="'+ str(x) +'"/>')
        else:
            print('  <test name="'+ str(x) +'">')
            print('    <result>'+ str(result) +'</result>')
            print('    <message>\n'+ str(message) +'\n    </message>')
            print('  </test>')
    
    print('</tests>')

def add_test(TestName, testFunction):
    gtests[TestName] = testFunction