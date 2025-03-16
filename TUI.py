import multiprocessing
import os
import time

import yaml
from textual.app import App, ComposeResult
from textual.widgets import Select, Label, Button, DataTable, Footer
from textual.containers import Vertical

from httpiewf import Crawler
from requestswf import make_requests_from_yaml

selected_file = ""

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

class FileSelectorApp(App):
    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        # Get the list of files & directories
        files = os.listdir(".")
        files = filter(lambda x: True if "yaml" in x or "yml" in x else False, files)
        options = [(f, f) for f in files]  # (value, label) format for dropdown
        self.table = DataTable(id="crawler_table")
        self.table.add_columns("Scheme", "Method", "SSLVerify", "URL", "Auth Type")
        with Vertical():
            yield Label("[bold red]❌To quit thr application please hit control + q")
            yield Label("[bold cyan]Select a file:")
            yield Select(options, id="file_dropdown")
            yield Button("Confirm", id="confirm_btn")
            yield Label("", id="fileSelected")
            yield self.table
            yield Button("Exit and run workflow", id="run_workflow")
            yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button click."""
        global selected_file
        if event.button.id == "confirm_btn":
            selected_file = self.query_one("#file_dropdown", Select).value
            fileSelected = self.query_one("#fileSelected", Label)
            fileSelected.update(f"Selected: {selected_file}")
            with open(selected_file, "r") as yamlFile:
                self.dict = yaml.safe_load(yamlFile)
            for crawler in self.dict.get('WorkFlow').get('Crawler'):
                if crawler.get("Auth"):
                    self.table.add_row(
                        crawler.get("Scheme"),
                        crawler.get("Method"),
                        str(crawler.get("SSLVerify")),
                        crawler.get("URL"),
                        crawler.get("Auth").get("type"),
                    )
                else:
                    self.table.add_row(
                        crawler.get("Scheme"),
                        crawler.get("Method"),
                        str(crawler.get("SSLVerify")),
                        crawler.get("URL"),
                    )
                self.table.refresh()
        if event.button.id == "run_workflow":
            if self.dict.get('WorkFlow',{}).get('Driver','default'):
                driver = self.dict.get('WorkFlow', {}).get('Driver', 'default')
                if driver == "default":
                    driver = "requests library"
                self.exit(return_code=0, message=f"Running the script using {driver}")


if __name__ == "__main__":
    FileSelectorApp().run()
    yaml_config = load_yaml(selected_file)
    driver = yaml_config.get('WorkFlow',{}).get('Driver','default')
    if driver == "default":
        make_requests_from_yaml(yaml_config)
    elif driver == "httpie":
        multiprocessing.set_start_method("spawn", force=True)  # Ensures Windows uses spawn
        run = Crawler(selected_file)
        run.loadconfig()
        run.Execute()
