# device-webprobe

This project is forked from https://github.com/sunspec/device-webprobe and ported to Python 3.

## Sunspec device simulator
```
python modsim.py -m tcp mbmap_test_device.xml
```

- To test server

```
modpoll -m tcp -0 -a 1 -t 4 -r 40000 -c 5 -p 502 localhost 
```