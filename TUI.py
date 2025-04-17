import multiprocessing
import os
import yaml
from textual.app import App, ComposeResult
from textual.widgets import Select, Label, Button, DataTable, Footer, Static
from textual.containers import Vertical, Container

from httpiewf import Crawler
from requestswf import make_requests_from_yaml

selected_file = ""

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

class FileSelectorApp(App):
    CSS = """
    #crawler_table {
        border: round white;
        height: 40%;
        width: 100%;
        margin: 1 0;
    }

    #file_dropdown {
        width: 100%;
        border: round cyan;
        padding: 1;
    }

    #confirm_btn {
        width: 100%;
        background: green;
        color: black;
        padding: 1;
        margin: 1 0;
    }

    #run_workflow {
        width: 100%;
        background: darkorange;
        color: black;
        padding: 1;
        margin-top: 1;
    }

    #fileSelected {
        color: yellow;
        margin-top: 1;
    }

    Label {
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        files = os.listdir(".")
        files = filter(lambda x: "yaml" in x or "yml" in x, files)
        options = [(f, f) for f in files]
        self.table = DataTable(id="crawler_table")
        self.table.add_columns("Scheme", "Method", "SSLVerify", "URL", "Auth Type")

        with Container():
            yield Label("[bold red]❌ To quit the application, press [underline]Ctrl + Q", id="quit_label")
            with Vertical():
                yield Label("[bold cyan]📂 Select a YAML file:")
                yield Select(options, id="file_dropdown")
                yield Button("✅ Confirm Selection", id="confirm_btn")
                yield Label("", id="fileSelected")
                yield self.table
                yield Button("🚀 Exit and Run Workflow", id="run_workflow")
                yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global selected_file
        if event.button.id == "confirm_btn":
            selected_file = self.query_one("#file_dropdown", Select).value
            fileSelected = self.query_one("#fileSelected", Label)
            fileSelected.update(f"[green]✔ Selected:[/] [bold yellow]{selected_file}")
            with open(selected_file, "r") as yamlFile:
                self.dict = yaml.safe_load(yamlFile)
            self.table.clear()  # Clear previous rows if any
            for crawler in self.dict.get('WorkFlow', {}).get('Crawler', []):
                row = [
                    crawler.get("Scheme", ""),
                    crawler.get("Method", ""),
                    str(crawler.get("SSLVerify", "")),
                    crawler.get("URL", ""),
                    crawler.get("Auth", {}).get("type", "") if crawler.get("Auth") else "",
                ]
                self.table.add_row(*row)
            self.table.refresh()

        elif event.button.id == "run_workflow":
            driver = self.dict.get('WorkFlow', {}).get('Driver', 'default')
            if driver == "default":
                driver = "requests library"
            self.exit(return_code=0, message=f"Running the script using {driver}")

if __name__ == "__main__":
    FileSelectorApp().run()
    yaml_config = load_yaml(selected_file)
    driver = yaml_config.get('WorkFlow', {}).get('Driver', 'default')
    if driver == "default":
        make_requests_from_yaml(yaml_config)
    elif driver == "httpie":
        multiprocessing.set_start_method("spawn", force=True)  # Ensures Windows uses spawn
        run = Crawler(selected_file)
        run.loadconfig()
        run.Execute()
