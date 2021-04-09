# Roma Capoccia Web Server

## Execution Steps

In oder to run the server, just type in the terminal the following line

```bash
python3 ./server.py {PORT_N}
```

Where ```PORT_N``` is the port number (default is 80). In order to view one of the websites in the web browser, change the first index of hosts. 0 = Edoardo Riggio, 1 = Matteo Bernaschina, 2 = Matteo Alberici (located in server.py):

```python
190   # CHANGE THIS LINE IN ORDER TO SEE A STUDENT'S WEBSITE IN THE BROWSER
191   HOST = hosts[0][0]
...
248   # CHANGE THIS LINE IN ORDER TO SEE A STUDENT'S WEBSITE IN THE BROWSER
249   HOST = hosts[0][0]
...
298   # CHANGE THIS LINE IN ORDER TO SEE A STUDENT'S WEBSITE IN THE BROWSER
299   HOST = hosts[0][0]
...
342   # CHANGE THIS LINE IN ORDER TO SEE A STUDENT'S WEBSITE IN THE BROWSER
343   HOST = hosts[0][0]
```

## Contributions

| Student            | Tasks                                                                           |
|--------------------|---------------------------------------------------------------------------------|
| Edoardo Riggio     | Task A, Task B, Task C, Task D, Task E, Task F, Task G, Task H, Optional Task A |
| Matteo Alberici    | Task A, Task B, Task C, Task D, Task E, Task F, Task G, Task H, Optional Task B |
| Matteo Bernaschina | Task A, Task B, Task C, Task D, Task E, Task F, Task G, Task H                  |

## Notes

- The server does not work well with requests that exceed the size of 1024 kB.
- Socket hangs when an error code is sent in the browser, closes connection properly when error code is sent form Postman
