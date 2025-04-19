import json
from typing import Any

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


def serialise(type: str, check: Any, matches: bool):
    return {"Type": type, "check": check, "Validation": matches}


def __deep_get(respJson: dict, key_path: str, default=None):
    keys = key_path.split(".")
    current = respJson
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def RunValidation(resp: requests.Response, validations: list):
    for validate in validations:
        if validate.get("status-code"):
            yield (serialise("status-code", f"Checks the status code for {validate.get('status-code')}",
                             validate.get("status-code") == resp.status_code))
        elif validate.get("reason"):
            yield (serialise("reason", f"Checks the reason for {validate.get('reason')}",
                             validate.get("reason") == resp.reason))
        elif validate.get("reason"):
            yield (serialise("reason", 'validate.get(status-code) == resp.status_code',
                             validate.get("status-code") == resp.reason))
        elif validate.get("response contains"):
            if validate.get("response contains").get("json"):
                _KEY_PATH = validate.get("response contains").get("json").get("key_path")
                _USER_VALUE = validate.get("response contains").get("json").get("value")
                _resp_val = __deep_get(resp.json(), _KEY_PATH)
                if _USER_VALUE.lower() == "any":
                    if _resp_val:
                        yield (serialise("response contains/json", f'Checking if key exists in path {_KEY_PATH}',
                                         _resp_val != None))
                else:
                    if _resp_val:
                        yield (serialise("response contains/json",
                                         f'Checking value in path {_KEY_PATH} matches {_resp_val}',
                                         _resp_val == _USER_VALUE))
                    else:
                        yield (serialise("response contains/json", 'Checking if key exists: Failed',
                                         False))
            # --------------------------------- headers ------------------------------------------ #
            if validate.get("response contains").get("headers"):
                _KEY_PATH = validate.get("response contains").get("headers").get("key")
                _USER_VALUE = validate.get("response contains").get("headers").get("value")
                _resp_val = resp.headers.get(_KEY_PATH)
                if _USER_VALUE.lower() == "any":
                    if _resp_val:
                        yield (
                            serialise("response contains/json", f'Checking if key exists in path {_KEY_PATH}',
                                      _resp_val != None))
                else:
                    if _resp_val:
                        yield (serialise("response contains/json",
                                         f'Checking value in path {_KEY_PATH} matches {_resp_val}',
                                         _resp_val == _USER_VALUE))
                    else:
                        yield (serialise("response contains/json", 'Checking if key exists: Failed',
                                         False))


def make_requests_from_yaml(config):
    running_validator = True
    workflow = config.get('WorkFlow', {})
    validation_level = workflow.get("validations", "")
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
        payloadDict = None
        if 'PayLoad' in crawler:
            if crawler.get('PayLoad'):
                filePath = crawler.get('PayLoad').get("json")
                with open(filePath, "r") as payloadfile:
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

            if validation_level == "warn":
                if crawler.get("validate"):
                    for validations in RunValidation(response, crawler.get("validate")):
                        if validations.get("Validation"):
                            stringBlob.append(
                                pretty_print_dict(f"Validations/{validations.get('Type')}", validations, "green"))
                        else:
                            stringBlob.append(
                                pretty_print_dict(f"Validations/{validations.get('Type')}", validations, "red"))
            elif validation_level == "strict":
                if crawler.get("validate"):
                    for validations in RunValidation(response, crawler.get("validate")):
                        if validations.get("Validation"):
                            stringBlob.append(
                                pretty_print_dict(f"Validations/{validations.get('Type')}", validations, "green"))
                        else:
                            stringBlob.append(
                                pretty_print_dict(f"Validations/{validations.get('Type')}", validations, "red"))
                        running_validator = running_validator and validations.get("Validation")
                        if not running_validator:
                            stringBlob.append(Fore.RED + "Stopping here as some validations have failed")

            console.print(Panel(Group(*stringBlob), title=f"Crawler Run: [{method}] {url}", style="cyan"))
