from colorama import Fore , init
import time 



class Reporter:
    """Used as a means to help fromat text nicely
    Note that this can be automatically disabled as well 
    and that this is purley to act as a namespace"""

    @staticmethod
    def init(no_color:bool=False):
        if no_color:
            # Disable color output.
            init(strip=True, convert=False)
        else:
            # Enable color output.
            init(autoreset=True)

    @staticmethod
    def Critical(status:str,msg:str):
        """Used to Warn about something really bad and threatening happening beyond the software's control"""
        print("[" + Fore.LIGHTRED_EX + status + Fore.RESET + "] %s" % msg)

    @staticmethod
    def Error(msg:str):
        """Something beyond our Scope of control has caused damage to the software and the system needs to evac"""
        print("[" + Fore.LIGHTRED_EX + "ERROR" + Fore.RESET + "] %s" % msg)

    @staticmethod 
    def Loading(msg:str):
        """"""
        print("[" + Fore.LIGHTYELLOW_EX + "..." + Fore.RESET + "] %s" % msg)

    @staticmethod
    def Success(msg:str):
        print("["+ Fore.LIGHTGREEN_EX + "+" + Fore.RESET + "] %s" % msg)

    @staticmethod
    def Warn(msg:str):
        print("[" + Fore.LIGHTRED_EX + "WARNING" + Fore.RESET + "] %s" % msg)

    @staticmethod 
    def Question(msg:str) -> bool:
        prompt = input("[" + Fore.LIGHTYELLOW_EX + "?" + Fore.RESET + "] %s Y/N: " % msg)
        return True if "y" in prompt.lower() else False

    @staticmethod
    def get_input(msg:str):
        return input("[" + Fore.LIGHTYELLOW_EX + "PROMPT" + Fore.RESET + "] %s" % msg)
  
    @staticmethod
    def Timer(msg:str,seconds:int,on_complete:str):
        """This is used when there's a ratelimit and we have to wait to get back in , 
        this will display a semi accurate timer for when we can go back to making requests 
        for more data..."""
        Reporter.Loading(msg)
        for i in range(seconds + 1):
            print("[%i:%i] " % divmod(seconds - i,60),end="\r")
            time.sleep(1)
        print(" " * 10)
        Reporter.Success(on_complete)

    @staticmethod
    def download_report(msg:str):
        """Shares output on how fast our download speeds are..."""
        print("[" + Fore.LIGHTYELLOW_EX + "v" + Fore.RESET + "] %s " % msg , end="\r")

    @staticmethod
    def item(msg:str,tabs:int=0):
        """Used to make nicer formats..."""
        print(("\t" * tabs) + Fore.LIGHTYELLOW_EX + "-" + Fore.RESET + " %s" % msg)
    
    @staticmethod
    def clean_download_report():
        """Clears up download report with a new line so that internetspeeds can be seen by the end user
        having a download report is good for debugging and for seeing if robtop's WAF 
        (Cloudflare) is maliciously trying to throttle us... """
        print("\n")


