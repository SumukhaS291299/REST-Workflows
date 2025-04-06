# 🕷️ REST Workflows

```markdown
This project defines a structured YAML-based configuration for running HTTP REST workflows using tools like `httpie`, `requests from python` or custom drivers.
The `WorkFlow.yaml` file defines multiple request flows, supporting authentication, headers, payloads, sessions, and more.
```
---

## 🛠 Features

- ✅ Structured YAML with validation
- 🔐 Auth support: Basic, Digest, Bearer
- 🌐 Configurable Headers, SSL, Payloads
- 🧪 Debug and Verbose modes
- 🔁 Run sessions and control execution order

---

## 📑 Basic YAML Structure Overview
```yaml
WorkFlow:
  Driver: httpie
  Order: true
  Debug: false
  Crawler:
    - Scheme: https
      Method: GET
      URL: example.com
      Auth:
        type: basic
        Username: admin
        Password: pass
      PayLoad:                                    # The URL without Scheme
        json: ".\\testJson.json"
```

> ##### Full example file can be found with name **`Schema.yaml`**
> Full schema with descriptions and validations available in `schema/workflow.schema.json`.

---

## 🧠 JSON Schema Support

### 🔷 VS Code Setup

1. Install the **YAML plugin by Red Hat** from the marketplace.
2. Add this to `.vscode/settings.json`:

```json
{
  "yaml.schemas": {
    "./schema/workflow.schema.json": "WorkFlow.yaml"
  }
}
```

3. Now you’ll get:
   - Auto-complete
   - Type hints
   - Inline validation

---

### 💡 JetBrains IDEs (IntelliJ, PyCharm) Setup

1. Go to:
   - `File > Settings > Languages & Frameworks > Schemas and DTDs > JSON Schema Mappings`
2. Click **+** to add a new mapping:
   - **Name**: `Workflow`
   - **Schema file**: Select `workflow.schema.json`
   - **Schema type**: JSON Schema
   - **Mapped files**: Add `WorkFlow.yaml`

3. Done! You’ll get real-time autocomplete and validation in your YAML file.

---

## 📦 Future Plans

- [ ] Add validations workflow for output to next input sequence
- [ ] Extend support for additional drivers
- [ ] Extend support for downloading files from web
- [ ] Extend support for environment variables
- [ ] Extend support for regex patterns

---

## 🧾 License

MIT License
```

---