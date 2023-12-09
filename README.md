# Ex2.7
Exercise 2.7 for school.

I used the following protocol:

    <cmd_length><cmd><data_length><data>
    cmd_length - 4-byte unsigned int (network byte order), the length of the command.
    cmd - string, the command to be executed/the command that has executed.
    data_length - 4-byte unsigned int (network byte order), the length of the data.
    data - string, the arguments to the command/the data received from the command.
The arguments passed to the command are in the form of `"(arg1, arg2, ...)"`. When using `eval()` on that string, it
will be converted to a tuple of all these arguments, or if there's only one argument it will be that one argument.

I also chose to use only `/` (forward-slash) instead of `\​` (backslash) because it works better with `eval()` and
string literals.

Sequence diagram:

![sequence diagram](protocol.png)

Apparently the code of the keyboard interrupts that I also used in 2.6 works only on linux and not on windows, and I couldn't get anything else to work :( I tried signals, threading, and other stuff, and it didn't work. I still left it here because I believe that every OS equally important :)
