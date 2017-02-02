import time

import gemstone

if __name__ == '__main__':
    service = gemstone.RemoteService("http://localhost:8000/test/v1/api")

    # test some blocking method calls
    print(service.methods.say_hello("world"))
    print(service.methods.say_hello(name="world"))

    # test an async call
    res = service.methods.say_hello("workd", __async=True)
    print(res)
    print(res.wait())
    print(res.error())
    print(res.result())

    # test a long async call
    res = service.methods.slow_method(seconds=3, __async=True)
    while not res.finished():
        print("still waiting")
        time.sleep(0.5)

    print("Result is here!")
    print(res.result())

    # calling more stuff in parallel

    res1 = service.methods.slow_method(seconds=3, __async=True)
    res2 = service.methods.slow_method(seconds=4, __async=True)
    res3 = service.methods.slow_method(seconds=5, __async=True)

    while not res1.finished() or not res2.finished() or not res3.finished():
        print("res1='{}' ; res2='{}' ; res3='{}'".format(res1.result(), res2.result(), res3.result()))
        time.sleep(0.5)

    print(res1.result())
    print(res2.result())
    print(res3.result())
