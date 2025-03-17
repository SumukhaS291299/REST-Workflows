import json

import requests
from colorama import Fore, Style, init
from rich.console import Console, Group
from rich.panel import Panel

init(autoreset=True)
console = Console()


def pretty_print_dict(title, data, color="cyan"):
    # Build formatted content string
    content = "\n".join([f"[white]{key}:[cyan]{value}[/cyan]" for key, value in data.items()])

    # Print inside a rich-styled box
    return Panel(content, title=title, style=color, title_align="left")


def make_requests_from_yaml(config):
    workflow = config.get('WorkFlow', {})
    crawlers = workflow.get('Crawler', [])

    for crawler in crawlers:
        stringBlob = []
        session = requests.Session()
        url = f"{crawler.get('Scheme', 'http')}://{crawler.get('URL')}"
        method = crawler.get('Method', 'GET').upper()
        ssl_verify = crawler.get('SSLVerify', True)
        headers = {}
        auth = None
        payload = None

        if 'Headers' in crawler:
            for header in crawler['Headers']:
                headers.update(header)

        if 'Auth' in crawler:
            auth_type = crawler['Auth'].get('type', '').lower()
            if auth_type == 'basic':
                auth = (crawler['Auth']['Username'], crawler['Auth']['Password'])
            elif auth_type == 'bearer':
                headers['Authorization'] = f"Bearer {crawler['Auth']['Token']}"

        if 'PayLoad' in crawler:
            if crawler.get('PayLoad'):
                filePath = crawler.get('PayLoad').get("json")
                with open(filePath,"r") as payloadfile:
                    payloadDict = json.load(payloadfile)

        runs = crawler.get('Sessions', {}).get('Runs', 1)

        for _ in range(runs):
            response = session.request(method, url, headers=headers, auth=auth, verify=ssl_verify, json=payloadDict)

            stringBlob.append(Fore.CYAN + f"\n[{method}] {url}")

            request_info = {
                "method": response.request.method,
                "url": response.request.url,
                "headers": dict(response.request.headers),
                "body": response.request.body
            }
            if crawler.get('Verbose', False) == True:
                stringBlob.append(pretty_print_dict("Request Details:", request_info, "yellow"))
                stringBlob.append(pretty_print_dict("Response Headers:", dict(response.headers), "magenta"))
            stringBlob.append(Fore.GREEN + f"Status Code: {response.status_code}")
            try:
                stringBlob.append(Fore.BLUE + "JSON Response:")
                stringBlob.append(pretty_print_dict("", response.json(), "blue"))
            except requests.JSONDecodeError:
                stringBlob.append(Fore.RED + "Response Text:")
                stringBlob.append(Fore.RED + response.text)

            console.print(Panel(Group(*stringBlob), title=f"Crawler Run: [{method}] {url}", style="cyan"))
