MicroPython lighthouse controls
===============================

    $ ln -s ../micropython-wifi-setup/lib .

    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install --upgrade pip
    $ pip install rshell

`avahi-resolve` vs `dig -p 5353 @224.0.0.251` Server Fault question: <https://serverfault.com/q/1023994/282515>


    $ avahi-resolve --name ding-5cd80b3.local
    ding-5cd80b3.local  192.168.0.248

    $ dig +short -p 5353 @224.0.0.251 ding-5cd80b3.local
    ;; Warning: ID mismatch: expected ID 60466, got 0
