# Random Anime Character Prompt Generator

A web-based tool for generating randomized character prompts for Stable Diffusion and other AI image generators. Features a slot-based system with 30+ customizable attributes, color palettes, and full localization support.

## Features

- **Slot-based Generation**: 30+ slots across appearance, body/expression/pose, and clothing categories
- **Color Palettes**: Pre-defined color palettes that automatically apply harmonious colors
- **Dual Language Support**: Independent UI language and prompt output language (English/Chinese)
- **Prompt Parsing**: Reverse-engineer existing prompts back to slot settings
- **Click-to-Scroll**: Click highlighted tokens in parsed prompts to jump to their slots
- **Save/Load Configurations**: Save character presets and load them later
- **Prompt History**: Track generated prompts with restore functionality
- **Keyboard Shortcuts**: Fully customizable shortcuts for all major actions
- **Weight Control**: Per-slot weight adjustment for prompt emphasis
- **Lock System**: Lock slots to preserve values during randomization

## Installation

### Requirements

- Python 3.11+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/Random-character-prompt-for-SD-.git
cd Random-character-prompt-for-SD-

# Install dependencies
pip install -r requirements.txt

# Run the server
python run_Fastapi.py
```

The server auto-selects a free port (8000-8099) and opens your browser.

## Usage

### Basic Workflow

1. **Generate**: Click "Generate Prompt" or press `Ctrl+G` to create a prompt from current slots
2. **Randomize**: Click "Randomize All" or press `Ctrl+R` to randomize all unlocked slots
3. **Copy**: Click "Copy" or press `Ctrl+Shift+C` to copy the prompt to clipboard
4. **Reset**: Click "Reset" or press `Ctrl+Shift+X` to clear all slot values

### Slot Controls

Each slot row has:
- **On/Off Toggle**: Enable or disable the slot in prompt output
- **Lock Button**: Prevent slot from being randomized
- **Dropdown**: Select a specific value
- **Color Dropdown**: Add color prefix (for applicable slots)
- **Weight Input**: Adjust prompt weight (default: 1.0)
- **Random Button**: Randomize just this slot

### Special Modes

| Mode | Description |
|------|-------------|
| **Full-body Mode** | Uses full-body outfit items (bodysuits, plugsuits), disables separate upper/lower body slots |
| **Upper-body Mode** | Focuses on upper body, disables lower body and feet slots |
| **Use Palette Colors** | Automatically applies colors from selected palette during randomization |

### Prompt Parsing

1. Paste or edit text in the prompt output field (it's editable!)
2. Click "Parse to Slots" or press `Ctrl+P`
3. Matched tokens highlight in orange (both in prompt and slot rows)
4. Click any orange token to scroll to its corresponding slot
5. Click "Save Parsed Config" to save the parsed result

### Prompt Prefix

Add a constant prefix to all generated prompts:
- Use the preset dropdown for common SD quality tags
- Or type your own custom prefix
- Toggle "Colorize prompt output" to see color-coded tokens

## Keyboard Shortcuts

| Action | Default Shortcut |
|--------|------------------|
| Generate Prompt | `Ctrl + G` |
| Randomize All | `Ctrl + R` |
| Copy Prompt | `Ctrl + Shift + C` |
| Reset All Slots | `Ctrl + Shift + X` |
| Parse to Slots | `Ctrl + P` |
| Toggle Click-to-Scroll | `Ctrl + J` |

All shortcuts are customizable via the **Keyboard Shortcuts** panel in the UI. Click "Change" next to any shortcut to record a new key combination.

## Project Structure

```
Random-character-prompt-for-SD-/
├── run_Fastapi.py              # Entry point - starts FastAPI server
├── requirements.txt            # Python dependencies
├── DEVMAP.md                   # Developer reference - where to change things
├── UI_logic.md                 # UI behavior specification
│
├── generator/
│   └── prompt_generator.py     # Core slot definitions & catalog loading
│
├── web/
│   ├── server.py               # FastAPI app setup
│   ├── routes/
│   │   ├── slots.py            # Slot data & randomization API
│   │   ├── prompt.py           # Prompt generation API
│   │   ├── configs.py          # Save/load configuration API
│   │   └── parser.py           # Prompt parsing API
│   └── static/
│       ├── index.html          # Main HTML page
│       ├── css/
│       │   ├── variables.css   # Theme colors & fonts
│       │   ├── layout.css      # Page layout & sections
│       │   ├── slots.css       # Slot row styles
│       │   └── controls.css    # Buttons & inputs
│       ├── js/
│       │   ├── app.js          # Entry point & initialization
│       │   ├── state.js        # Central state store
│       │   ├── api.js          # API calls
│       │   ├── components.js   # DOM creation
│       │   ├── handlers.js     # Event handlers
│       │   ├── prompt.js       # Prompt display logic
│       │   ├── history.js      # History management
│       │   ├── shortcuts.js    # Keyboard shortcuts
│       │   └── i18n.js         # Internationalization
│       └── i18n/
│           ├── en.json         # English translations
│           └── zh.json         # Chinese translations
│
└── prompt data/                # JSON catalog files
    ├── hair/                   # Hair options
    ├── eyes/                   # Eye options
    ├── body/                   # Body features
    ├── expressions/            # Facial expressions
    ├── clothing/               # Clothing items (with covers_legs metadata)
    ├── poses/                  # Poses (with uses_hands metadata)
    ├── backgrounds/            # Background options
    ├── colors/                 # Color palettes
    └── configs/                # Saved character presets
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/slots` | GET | Get slot definitions and section layout |
| `/api/slots/randomize` | POST | Randomize a single slot |
| `/api/slots/randomize-all` | POST | Randomize all unlocked slots |
| `/api/prompt/generate` | POST | Generate prompt from slot state |
| `/api/parse-prompt` | POST | Parse prompt text to slot settings |
| `/api/palettes` | GET | Get available color palettes |
| `/api/configs` | GET | List saved configurations |
| `/api/configs/{name}` | GET/POST | Load or save a configuration |

## Customizing Content

Edit JSON catalogs in `prompt data/` to add new options:

| Content | File |
|---------|------|
| Hair styles | `hair/hair_catalog.json` |
| Eye options | `eyes/eye_catalog.json` |
| Body features | `body/body_features.json` |
| Expressions | `expressions/female_expressions.json` |
| Clothing | `clothing/clothing_list.json` |
| Poses | `poses/poses.json` |
| Backgrounds | `backgrounds/backgrounds.json` |
| Color palettes | `colors/color_palettes.json` |

### Catalog Format

```json
{
  "category": "hair_style",
  "items": [
    {
      "id": "twin_tails",
      "name": "twin tails",
      "name_i18n": {
        "en": "twin tails",
        "zh": "双马尾"
      }
    }
  ]
}
```

### Special Metadata

- **Clothing `covers_legs`**: Set `true` on lower_body items that cover legs (long skirts, pants) to auto-disable legs slot
- **Poses `uses_hands`**: Set `true` on poses that define hand positions to auto-disable gesture slot

## Development

See [DEVMAP.md](DEVMAP.md) for detailed information on where to make changes.

### Adding New Slots

1. Add slot definition in `generator/prompt_generator.py` → `SLOT_DEFINITIONS`
2. Create/update catalog JSON in `prompt data/`
3. Add slot to section layout in `web/routes/slots.py` → `SECTION_LAYOUT`
4. Add slot to prompt order in `web/routes/prompt.py` → `SLOT_ORDER`
5. Add translations in `web/static/i18n/*.json`

### Adding New Languages

1. Create new translation file: `web/static/i18n/{code}.json`
2. Add locale to `SUPPORTED_LOCALES` in `web/static/js/i18n.js`
3. Add `name_i18n.{code}` entries to catalog items

## License

MIT License

## Contributing

Contributions are welcome! Please read [DEVMAP.md](DEVMAP.md) for guidance on the codebase structure.
