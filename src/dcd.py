import datetime
from flags import ObfuscationLevel, configure_flags
from dcdclient import DCDClient
from reporter import Reporter
import random 
import time 
import sys 
import os 

import click
from typing import Optional, Union
from io import TextIOWrapper
import functools


class Backoff:
    def __init__(self,times:tuple[float]) -> None:
        self.min = min(times)
        self.max = max(times)
        self.current:float = 0

    def sleep(self):
        """Sleeps for a random amount of seconds to prevent servers from refusing to serve us up content..."""
        t = round(random.uniform(self.min,self.max), 3)
        self.current = t 
        Reporter.Loading(f"Sleeping for {t} seconds...")
        time.sleep(t)

def calc_pagesum(total:int,count:int):
    """Used to caculate how many pages should be harvested up from geometry dash back to us"""
    rem = 1 if (total % count) > 0 else 0
    ps = (total // count) + rem 
    return ps 


def estimate_time_left(seconds:float,on:int,pagesum:int):
    """Used to estimate how long a download will take to complete this is done via measuring the request's time
    taken and multiplying it by the number of pages left"""
    pages_left = pagesum - on 
    # Estimate with backoff's highest random delay for better accuracy, this will be rounded to the nearest second to keep the reports less messy
    est = datetime.timedelta(seconds=round(pages_left * seconds,0))
    Reporter.Loading(f"EST Time Left: - {est}     Pages Left: {on}/{pagesum}")
    return est


_Title = """
┌──────────────────────────────────────────────────┐
|  ░░░░░░   ░░░░░░ ░░░░░░   Helping hunt Retarded  |                      
|  ▒▒   ▒▒ ▒▒      ▒▒   ▒▒   People Since 2022     |
|  ▒▒   ▒▒ ▒▒      ▒▒   ▒▒                         |     
|  ▓▓   ▓▓ ▓▓      ▓▓   ▓▓  Daily chat Downloader  |
|  ██████   ██████ ██████  Level Comment Harvester |
├──────────────────────────────────────────────────┤
|  Daily Chat Downloader 4.0.2   By Calloc         |
└──────────────────────────────────────────────────┘
"""
default_time = datetime.datetime.now().strftime("%Y-%m-%d-_%I-%M-%S_%p")

_Credits = """
┌──────────────────────────────────────────────────┐
| Anonymous [x] /\/\/\                             |
| Some things were developed via threading to make |
| up for the bottlenecks of python in order to be  |
| as fast as possible...                           |
|                                                  |
| Many things such as http was written this time   |
| to speedup the request rate and reduce the       |
| computing power required to communicate to the   |
| server so that even a potato could handle it well|
|                                                  |
| Only python is used for the sake of protability. |
| Other methods with C & C++ were attempted but    |
| none of them ended up yeilding promising results |
| because the servers kept on screwing us over.    |          
| Some the of rewrites threatened development      |
| because of the amount of the cursed 429's given  |
| back to us. Which is why the decision            | 
| was made to move from optimization into better   |
| obfuscation. All are User-Configured.            |
|                                                  |                
| In 3.4.0 we introduced proxies because my proxy  |
| theory was proven to be debunked, I assumed      |
| That Robtop blocked all proxies but as long as   |
| the ip has good reputation and can bypass the WAF|
| you should be fine... However a word of Caution! |
| Just because it works doesn't mean  that it can't| 
| still screw you over. You may find Captcha errors| 
| while using proxies or vpns w/ proxy support!    |
|                                                  |
| Until Robtop finds a better Firewall to enchance |
| user privacy. Blame Cloudflare, not us...        |
|                                                  |
| USER GUI is coming Soon because discord has      |
| upped thier upload limit from 8MB to 25 MB!      |
| THANK YOU DISCORD!                               |
├──────────────────────────────────────────────────┤
| Honerable Mentions and Libraries Used            |
├──────────────────────────────────────────────────┤
| Click is now used instead of argparse for        |
| simplicity and for making it easier for even the |
| lower level people to be able to pick up and     |
| start hacking.                                   |
|                                                  |
| We now use Httpx because Httpx respects our      |
| headers escpecially ones that must be spoofed for|
| some to even have privacy from robtop's          |
| Theoretical amounts of Telemetry put in place    |
| as well as Cloudflare's own Telemetry            |
|                                                  |
├──────────────────────────────────────────────────┤
| Terms Of Service                                 |
├──────────────────────────────────────────────────┤
| THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT        |
| WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,        |
| INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF   | 
| MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE|
| AND NONINFRINGEMENT. IN NO EVENT SHALL THE       |
| AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY   |
| CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN | 
| ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING   |
| FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE  |
| OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.    |
└──────────────────────────────────────────────────┘
"""





def add_options(*args):
    def _add_options(func):
        options = [x for n in args for x in n]
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options



def get_credits(ctx:click.Context,param,value):
    if not value or ctx.resilient_parsing:
        # Don't do anything!!!
        return 
    else:
        print(_Credits)
        sys.exit(0)


def pass_flags(ctx:click.Context,param,value:Union[str,int,tuple[Union[str,int]]]):
    ob:ObfuscationLevel = ObfuscationLevel.NONE 
    if len(value) > 0:
        if isinstance(value,(list,tuple)):
            for flag in value:
                ob |= configure_flags(flag)
        else:
            ob |= configure_flags(value)
    # pass off our new values to the params to be used later and 
    # discard the pervious value...
    ctx.params["flags"] = ob



main_args = [click.option("-o","--obfuscation",
            type=click.Choice(ObfuscationLevel._member_names_,case_sensitive=False),
            show_choices=True,multiple=True,callback=pass_flags,expose_value=False, is_eager=True,
            help="Helps you choose your obfuscation levels "\
                "GDBROWSER (1): makes a fake gdbrowser instance by changing a parameter to make boomlings server think your a gdbrowser instance "\
                "XFAKEIP (2): generates a fake decoy like NMAP decoys except it also allows for proxies as well. it will generate one"\
                    " for you if you do not provide a --decoy parameter "\
                "ALL (3): do everything with all parameters set to true."),
    click.option("--proxy","-p","proxy",type=str,default=None,help="Forwards a proxy for connecting to the boomlings server"\
                  " Note that robtop has a very agressive WAF and not all proxies will make it through example: socks5://127.0.0.1:5051",show_default=True),
    click.option("--decoy","-d","decoy",type=str,default=None,help="Forwards a X-Real-IP header as the decoy you provide to it..."\
                  " if you don't want to configure it yourself -o XFAKEIP will generate a random one for you"),
    click.option("--bandwith","-b","bandwith",default=8192,type=click.IntRange(min=1024, clamp=True),help="increases response's bandwith if required , mimimum is 1024",show_default=True)
]

downloader_args = [
    click.option("--most-liked/--most-recent","_mode",default=False,help="helps configure the mode parameter of which order you would like to go by")
    ,click.option("--backoff","-bo","backoff",nargs=2,default=(2,5),type=float,help="adjusts the preonfigured backofftimes for 2 - 5 seconds to whatever you need, this will sleep after every request to boomling's servers...",show_default=True)
    ,click.option("--file","file",default=datetime.datetime.now().strftime("%Y-%m-%d-_%I-%M-%S_%p"),type=str,help="a file to save your comments to default name will be based on what time it is...")
    ,click.option("--count","-c","count",default=100,type=click.IntRange(min=20,clamp=True,max=100),help="Increases and decreases comment count going lower can be easier on the servers but ultimately harder to download")
]

mass_file_options = [
   click.option("--most-liked/--most-recent","_mode",default=False,help="helps configure the mode parameter of which order you would like to go by")
    ,click.option("--backoff","-bo","backoff",nargs=2,default=(2,5),type=float,help="adjusts the preonfigured backofftimes for 2 - 5 seconds to whatever you need, this will sleep after every request to boomling's servers...",show_default=True)
    ,click.option("--count","-c","count",default=100,type=click.IntRange(min=20,clamp=True,max=100),help="Increases and decreases comment count going lower can be easier on the servers but ultimately harder to download")
]




def toggle_color_options(ctx:click.Context,param:click.Parameter,value:bool):
    Reporter.init(True if value else False)


def bash(ctx:click.Context,param:click.Parameter,value:Optional[str]):
    """Writes a bash script for your commands"""
    if not value or ctx.resilient_parsing:
        # Don't do anything!!!
        return 
    else:
        Reporter.Loading("Preparing Parameters for writing a new bash Script/Command...")
        args = sys.argv

        if args[0].endswith(".py"):
            args.insert(0, "python" if sys.platform == "win32" else "python3")
        args.remove(value)
        if "--bash" in args:
            args.remove("--bash")

        if "-b" in args:
            args.remove("-b")

        script = " ".join(args)
        # debugging only...
        print(script)

        name = value
        name += ".bat" if sys.platform == "win32" else ".sh"

        with open(f"{name}","w") as shell:
            shell.write(script)
        if sys.platform == "linux":
            name = f"source {name}"
        else:
            response_name = name 
        Reporter.Success(f"finished wiriting bash script {name} you can invoke it by typing \"{response_name}\" into your terminal now exiting...")
        sys.exit(0)

# chain=True maybe...
@click.group()
@click.option(
        '--bash',"-b", type=str, callback=bash,
        expose_value=False, is_eager=True,help="Writes a bash script for"\
            " all arguments seen in it and then exits when the new command"\
            " that has been created for you, this will ignore all other commands"\
                " you have in place but will instead write all of them down...")
@click.option("--no-color/--color","no_color",help="disables color in the terminal , it is turned on by default",expose_value=False, is_eager=True,callback=toggle_color_options)
@click.option("--credits",is_flag=True,help="displays credits, verison , legal information as well as Terms Of Service (TOS)",expose_value=False, is_eager=True,callback=get_credits)
def cli():
    r"""The Sneakiest , Most Advanced & Agressive Geometry Dash Level Comment 
    harvester on the planet. Created for OSINT , datamining and silent data collection of gd level comments.  
Also includes smart obfuscation techniques that are all user-configured to pevent DCD From being 
stopped. Level comments are Guaranteed No Matter how slow robtop makes the rate limit!
Making this tool impossible to stop!"""
    pass 



@cli.command()
@add_options(main_args,downloader_args)
@click.pass_context
def daily(ctx:click.Context,**attrs):
    """extracts the daily level's comments and downloads them to the ouput file , this will set the levelID to -1"""
    return ctx.forward(level,levelid=-1,**attrs)


@cli.command()
@add_options(main_args,downloader_args)
@click.pass_context
def weekly(ctx:click.Context,**attrs):
    """extracts the weekly's level's comments and downloads them to the ouput file , this will set the levelID to -2"""
    return ctx.forward(level,levelid=-2,**attrs)


@cli.command()
@click.argument("levelID",type=int,required=True)
@add_options(main_args,downloader_args)
def level(
    levelid:int,
    flags:ObfuscationLevel,
    proxy:Optional[str], 
    decoy:Optional[str],
    file:str, 
    bandwith:int, 
    count:int,
    _mode:bool,
    backoff:tuple[float]):
    """extracts the  level comments and downloads them to the ouput file"""
    # print(f"LevelID:{levelid}")
    # Reporter.Loading("Work in progress... it is not ready yet...")
    mode = 1 if _mode else 0 
    total = 0
    bo = Backoff(backoff)
    with DCDClient(flags,proxy,bandwith=bandwith,decoy=decoy) as client:
        level = client.downloadGJLevel(levelid)
        client.set_targetID(level.id)
        Reporter.Success("Got Level")
        Reporter.Success(f"Level: {level.name}")
        Reporter.Success(f"Resolved ID: {level.id}")
        Reporter.Success(f"Creator's name: {level.creator.name}")
        Reporter.Success(f"Creator's AccountID: {level.creator.AccountID}")
        bo.sleep()
        Reporter.Loading(f"Preparing to start calculating Pagesum...")
        start = time.perf_counter()
        page = client.getGJComments(0,mode,count,total)
        idx = page.find(b"#")
        total = int(page[idx + 1: page.find(b":",idx)])
        pagesum = calc_pagesum(total, count)
        estimate_time_left(time.perf_counter() - start, 0, pagesum)
        Reporter.Loading(f"Calculated Pagesum (Comments total / pages needed): {total}")
        with open(f"{file}.txt","wb") as wf:
            wf.write(page + b"\n")
            for p in range(1,pagesum):
                start = time.perf_counter()
                bo.sleep()
                page = client.getGJComments(p, mode=mode,count=count,total=total)
                wf.write(page + b"\n")
                estimate_time_left(time.perf_counter() - start, p, pagesum)
        Reporter.Success("Done")
# TODO Add Level Search tool and other features but don't overdo it...
# TODO maybe Add ability to search by user...

@cli.command()
@add_options(main_args)
@click.argument("query",type=str)
@click.option("--page","-p","page",type=int,help="The first page of levels to grab",default=0,show_default=True)
@click.option("--amount","-a","amount",type=int,help="The number of pages to grab based on where --page is", default=1)
@click.option("--backoff","-bo","_backoff",nargs=2,default=(2,5),type=float,help="adjusts the preonfigured backofftimes for 2 - 5 seconds to whatever you need, this will sleep after every request to boomling's servers...",show_default=True)
@click.option("--file","-f","file",type=click.File("w"),help="if you have chosen this option all level IDs will be written down for later this later be used to do a mass download of all the comments of all those levels")
def search(
    query:str,
    page:int,
    amount:int,
    flags:ObfuscationLevel,
    proxy:Optional[str],
    bandwith:int,
    decoy:str,
    file:Optional[TextIOWrapper],
    _backoff:tuple[float],
    ):
    """Harvestes Levels by search query and yeilds back the results, these results can be used to harvest up other levels at our pleasure and disposal..."""
    
    backoff = Backoff(_backoff)
    with DCDClient(flags,proxy=proxy,bandwith=bandwith,decoy=decoy) as client:
        for p in range(page, page + amount):
            Reporter.Loading(f"Extracting page {p}...")
            levels = client.search_level(query, p)
            
            for level in levels:
                Reporter.item(f"LevelID : {level.id}")
                Reporter.item(f"Name: {level.name}")
                Reporter.item(f"desc: {level.description.decode(errors='replace')}")
                Reporter.item(f"Creator: {level.creator.name}")
                Reporter.item(f"AccountID: {level.creator.AccountID}", 1)
                Reporter.item(f"PlayerID: {level.creator.PlayerID}", 1)
                if file:
                    file.write(f"{level.id}\n")
            if p != (page + amount - 1):
                backoff.sleep()

            
    if file:
        name = file.name
        Reporter.Loading(f"Saving {name}")
        file.close()
        # TODO Add sort algroythm, do it oursleves incase sort command doesn't work...
        Reporter.Success(f"File {name} was saved!")


def make_prefix(prefix:str,id:int):
    while True:
        name = f"{prefix}-{id}"
        if not os.path.exists(name + ".txt"):
            yield name
        id += 1 



@cli.command()
@click.argument("files",nargs=-1,type=click.Path(exists=True))
@click.option("--prefix",type=str,help="uses a prefix instead of a timestamp this ")
@add_options(main_args,mass_file_options)
@click.pass_context
def fromfile(
    ctx:click.Context,
    files:list[str],
    prefix:Optional[str],
    **kwds):
    """Handle a list of textfiles with 1 levelid per line, this will fetch all the levelid's comments for each textfile given """
    
    
    file_gen = make_prefix(prefix,0) if prefix else None

    for file in files:
        Reporter.Loading(f"Loading {file}...")
        with click.open_file(file,"r") as f:
            for l in map(lambda x :x.rstrip(), f):
                # don't allow one line to break up our code! if the user gets it wrong ignore it instead
                if l.isdigit():
                    ctx.invoke(level,levelid=int(l), file=datetime.datetime.now().strftime("%Y-%m-%d-_%I-%M-%S_%p") if not file_gen else next(file_gen), **kwds)
        


if __name__ == "__main__":
    print(_Title)
    cli()
    
