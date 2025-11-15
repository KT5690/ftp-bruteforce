## FTP Bruteforcer

A Python tool for testing FTP credentials against a target host using a password wordlist. Usage: `python main.py --host <target> -u <username> -w <wordlist.txt>`

We can use this as:
```python
python main.py --host 192.168.1.1 -u admin -w /usr/share/wordlists/rockyou.txt
```