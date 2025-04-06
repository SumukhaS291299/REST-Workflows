import rich.table
import yaml
from rich import console, text
import subprocess
import multiprocessing
from rich.console import Console

blockConsole = Console()

class Crawler:
    def __init__(self, file):
        self.file = file
        self.console = console.Console(color_system="auto")
        self.console.print(text.Text("Initialization complete", style=self.styleBuilder()))
        self.console.print(text.Text("Loading...\r", style=self.styleBuilder("debug")))

    def styleBuilder(self, level="info"):
        styles = {
            "info": "bold blue on black",
            "warn": "bold yellow on black",
            "debug": "bold green on black",
            "error": "bold red on white",
        }
        return styles.get(level, "bold white on black")

    def DEBUG(self):
        return self.conf.get("WorkFlow", {}).get("Debug", False)

    def loadconfig(self):
        with open(self.file, "r") as configFile:
            self.conf = yaml.safe_load(configFile)
        if self.DEBUG():
            self.console.print_json(data=self.conf)

    @staticmethod
    def StringBuilder(httpcall: dict):
        builder = "http"
        if httpcall.get("Verbose"):
            builder += " --verbose"
        if httpcall.get("Auth"):
            authtype = httpcall["Auth"].get("type")  # Fixed key lookup
            username = httpcall["Auth"].get("Username")
            password = httpcall["Auth"].get("Password")
            bearer_tok = httpcall["Auth"].get("Token")
            if authtype == "basic":
                builder += f" -A basic -a {username}:{password}"
            elif authtype == "digest":
                builder += f" -A digest -a {username}:{password}"
            elif authtype == "bearer":
                builder += f" -A bearer -a {bearer_tok}"

        if not httpcall.get("SSLVerify", True):
            builder += " --verify=no"
        method = httpcall.get("Method", "GET")
        builder += f" {method}"

        scheme = httpcall.get("Scheme", "http")
        url = httpcall.get("URL", "")
        if url.startswith(("http://", "https://")):
            builder += f" {url}"
        else:
            builder += f" {scheme}://{url}"

        if httpcall.get("Headers"):
            header_list = []
            for header in httpcall["Headers"]:
                for key, value in header.items():
                    header_list.append(f"{key}:{value}")  # Collect headers

            if header_list:
                builder += " " + "; ".join(header_list)  # Join with "; "

        if httpcall.get("PayLoad"):
            jsonfilePath = httpcall["PayLoad"].get("json")
            builder += f' @"{jsonfilePath}"'

        return builder

    @staticmethod
    def runCrawler(crawler):
        """ Function runs in a separate process (must not use `self.console`). """
        rest_call = Crawler.StringBuilder(crawler)
        print(f"Executing: {rest_call}")  # Using print instead of `console.print`

        try:
            result = subprocess.run(rest_call, shell=True, timeout=10)
            blockConsole.print((result.stdout if result.stdout else result.stderr))
        except subprocess.TimeoutExpired:
            print("[ERROR] Command timed out")
        except Exception as e:
            print(f"[ERROR] Exception: {e}")

    def Execute(self):
        httpie_version = subprocess.run(
            "httpie --version", shell=True, timeout=5, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if httpie_version.stderr:
            self.console.print_exception()
        table = rich.table.Table(title="REST Workflows")
        table.add_column("Crawler Details", justify="right", style="cyan", no_wrap=True)
        table.add_column("Metadata", justify="right", style="blue", no_wrap=True)
        table.add_row("Httpie version:", httpie_version.stdout.decode())
        table.add_row("Ordering", "")
        self.console.print(table)

        process_list = []
        crawlers = self.conf.get("WorkFlow", {}).get("Crawler", [])
        order_mode = self.conf.get("WorkFlow", {}).get("Order", False)

        if order_mode:
            for crawler in crawlers:
                self.runCrawler(crawler)
        else:
            self.console.print("[bold yellow]Running in multi execute mode[/bold yellow]")
            for crawler in crawlers:
                process = multiprocessing.Process(target=Crawler.runCrawler, args=(crawler,))
                process_list.append(process)
                process.start()

            for process in process_list:
                process.join()
