import time
from datetime import datetime
gtests = {}

def run_test(TestName):
    return gtests[TestName]()

def run_all_tests():
    startTime = time.time()
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
    endTime = time.time()
    print('  <time value=' + str(endTime- startTime) +'/>')
    print('</tests>')
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d  %H:%M:%S")
    file1 = open("tests/test_duration.txt", "a") 
    file1.write(current_time +"; " + str(endTime- startTime)+"\n") 
    file1.close() 


def add_test(TestName, testFunction):
    gtests[TestName] = testFunction