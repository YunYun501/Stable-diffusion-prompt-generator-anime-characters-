"""
Gradio Web UI for Random Character Prompt Generator.

Features:
- Per-slot: Randomize button, Dropdown, Color button, Disable toggle, Weight input
- Section randomize buttons
- Full-body toggle logic
- Color palette system
- Save/Load configurations
"""

import gradio as gr
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json
import random as rand_module
from datetime import datetime
import os
import signal

from .prompt_generator import PromptGenerator, SlotConfig, GeneratorConfig


def shutdown_server():
    """Shutdown the Gradio server."""
    print("\nShutting down server...")
    os.kill(os.getpid(), signal.SIGTERM)


# Custom CSS for compact, centered layout
CUSTOM_CSS = """
/* Use full width */
.gradio-container {
    max-width: 100% !important;
    padding: 10px 20px !important;
}

/* Slot row - horizontal layout */
.slot-row {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 6px 10px !important;
    margin: 2px 0 !important;
    border-radius: 6px !important;
}

/* Enabled state - green */
.slot-enabled {
    border: 2px solid #22c55e !important;
    background-color: rgba(34, 197, 94, 0.08) !important;
}
.slot-enabled label {
    color: #16a34a !important;
    font-weight: 600 !important;
}

/* Disabled state - red/grey */
.slot-disabled {
    border: 2px solid #ef4444 !important;
    background-color: rgba(239, 68, 68, 0.08) !important;
    opacity: 0.5 !important;
}
.slot-disabled label {
    color: #9ca3af !important;
}

/* Output box */
#prompt-output textarea {
    font-size: 14px !important;
    font-family: monospace !important;
}

/* Column headers */
.column-header {
    font-weight: bold !important;
    font-size: 1.1em !important;
    padding: 8px !important;
    border-bottom: 2px solid #ddd !important;
    margin-bottom: 8px !important;
}
"""


class PromptGeneratorUI:
    """Gradio-based UI for the prompt generator."""
    
    def __init__(self, generator: Optional[PromptGenerator] = None):
        """Initialize the UI."""
        if generator is None:
            generator = PromptGenerator()
        self.generator = generator
        self.config = generator.create_default_config()
        self.configs_dir = generator.data_dir / "configs"
        self.configs_dir.mkdir(exist_ok=True)
        
        # Track UI component references
        self.slot_components: Dict[str, Dict[str, Any]] = {}
    
    def get_slot_choices(self, slot_name: str) -> List[str]:
        """Get choices for a slot dropdown, including 'None' option."""
        options = self.generator.get_slot_option_names(slot_name)
        return ["(None)"] + options
    
    def get_color_choices(self) -> List[str]:
        """Get color choices from palettes or individual colors."""
        colors = self.generator.individual_colors.copy()
        if not colors:
            colors = ["white", "black", "red", "blue", "pink", "purple", 
                     "green", "yellow", "orange", "brown", "grey", "silver", "gold"]
        return ["(No Color)"] + colors
    
    def get_palette_choices(self) -> List[str]:
        """Get palette choices for dropdown."""
        names = self.generator.get_palette_names()
        return ["(None)"] + names
    
    def get_saved_configs(self) -> List[str]:
        """Get list of saved configuration names."""
        configs = self.generator.list_saved_configs(self.configs_dir)
        return configs if configs else []
    
    def _get_default_ui_values(self) -> List:
        """Get default values for all UI components."""
        values = []
        for slot_name in self.generator.SLOT_DEFINITIONS.keys():
            values.extend([
                True,  # enabled
                "(None)",  # value
                "(No Color)",  # color
                1.0  # weight
            ])
        return values

    def build_ui(self) -> gr.Blocks:
        """Build the complete Gradio UI."""
        
        with gr.Blocks(css=CUSTOM_CSS, title="Character Prompt Generator") as app:
            gr.Markdown("# 🎨 Random Anime Character Prompt Generator")
            
            # Store all slot components for event handling
            all_enabled = []
            all_dropdowns = []
            all_colors = []
            all_weights = []
            all_random_btns = []
            all_color_btns = []
            
            # Define slot order matching our column layout
            appearance_slots = ["hair_style", "hair_length", "hair_color", "hair_texture", "eye_color", "eye_style"]
            body_slots = ["body_type", "height", "skin", "age_appearance", "special_features", "expression", "pose", "gesture"]
            clothing_slots = ["head", "neck", "upper_body", "waist", "lower_body", "full_body", "outerwear", "hands", "legs", "feet", "accessory", "background"]
            slot_names_list = appearance_slots + body_slots + clothing_slots
            
            # ===== GENERATE PROMPT SECTION (at top) =====
            with gr.Row():
                with gr.Column(scale=3):
                    output_prompt = gr.Textbox(
                        label="Generated Prompt",
                        lines=2,
                        max_lines=4,
                        interactive=True,
                        elem_id="prompt-output"
                    )
                with gr.Column(scale=1):
                    with gr.Row():
                        generate_btn = gr.Button("✨ Generate", variant="primary")
                        randomize_all_btn = gr.Button("🎲 Randomize All", variant="secondary")
                    with gr.Row():
                        copy_btn = gr.Button("📋 Copy")
                        reset_btn = gr.Button("🔄 Reset")
                        shutdown_btn = gr.Button("⏹ Stop", variant="stop")
            
            # ===== SETTINGS ROW =====
            with gr.Row():
                full_body_mode = gr.Checkbox(value=True, label="Full-body mode")
                color_mode = gr.Radio(
                    choices=["None", "Palette", "Random"],
                    value="None",
                    label="Color Mode"
                )
                palette_dropdown = gr.Dropdown(
                    choices=self.get_palette_choices(),
                    value="(None)",
                    label="Color Palette"
                )
            
            section_components = {}
            
            # ===== ROW 1: Appearance (left) + Body (right) =====
            with gr.Row():
                # === COLUMN 1: Appearance ===
                with gr.Column(scale=1):
                    gr.Markdown("### 👤 Appearance")
                    with gr.Row():
                        section_random_btn_1 = gr.Button("🎲 Random", size="sm")
                        section_disable_btn_1 = gr.Button("❌ Disable", size="sm")
                        section_enable_btn_1 = gr.Button("✅ Enable", size="sm")
                    section_enabled_1 = []
                    section_dropdown_1 = []
                    section_color_1 = []
                    section_weight_1 = []
                    
                    for slot_name in appearance_slots:
                        if slot_name not in self.generator.SLOT_DEFINITIONS:
                            continue
                        slot_def = self.generator.SLOT_DEFINITIONS[slot_name]
                        display_name = slot_name.replace("_", " ").title()
                        has_color = slot_def.get("has_color", False)
                        row_id = f"slot-row-{slot_name}"
                        
                        with gr.Group(elem_id=row_id, elem_classes=["slot-row", "slot-enabled"]):
                            with gr.Row():
                                enabled = gr.Checkbox(value=True, label="", min_width=30, elem_id=f"chk-{slot_name}")
                                dropdown = gr.Dropdown(
                                    choices=self.get_slot_choices(slot_name),
                                    value="(None)",
                                    label=display_name,
                                    scale=2
                                )
                                random_btn = gr.Button("🎲", min_width=35)
                                weight = gr.Number(value=1.0, label="Wt", minimum=0.1, maximum=2.0, step=0.1, min_width=50)
                        
                        # Hidden color dropdown for non-color slots
                        color_dropdown = gr.Dropdown(choices=["(No Color)"], value="(No Color)", visible=False)
                        color_random_btn = gr.Button("🎨", visible=False)
                        
                        all_enabled.append(enabled)
                        all_dropdowns.append(dropdown)
                        all_colors.append(color_dropdown)
                        all_weights.append(weight)
                        all_random_btns.append((random_btn, slot_name))
                        all_color_btns.append((color_random_btn, slot_name))
                        section_enabled_1.append(enabled)
                        section_dropdown_1.append(dropdown)
                        section_color_1.append(color_dropdown)
                        section_weight_1.append(weight)
                    
                    section_components["appearance"] = {
                        "enabled": section_enabled_1, "dropdowns": section_dropdown_1,
                        "colors": section_color_1, "weights": section_weight_1,
                        "random_btn": section_random_btn_1, "disable_btn": section_disable_btn_1,
                        "enable_btn": section_enable_btn_1, "slots": appearance_slots
                    }
                
                # === COLUMN 2: Body & Expression & Pose ===
                with gr.Column(scale=1):
                    gr.Markdown("### 🧍 Body / Expression / Pose")
                    with gr.Row():
                        section_random_btn_2 = gr.Button("🎲 Random", size="sm")
                        section_disable_btn_2 = gr.Button("❌ Disable", size="sm")
                        section_enable_btn_2 = gr.Button("✅ Enable", size="sm")
                    section_enabled_2 = []
                    section_dropdown_2 = []
                    section_color_2 = []
                    section_weight_2 = []
                    
                    for slot_name in body_slots:
                        if slot_name not in self.generator.SLOT_DEFINITIONS:
                            continue
                        slot_def = self.generator.SLOT_DEFINITIONS[slot_name]
                        display_name = slot_name.replace("_", " ").title()
                        row_id = f"slot-row-{slot_name}"
                        
                        with gr.Group(elem_id=row_id, elem_classes=["slot-row", "slot-enabled"]):
                            with gr.Row():
                                enabled = gr.Checkbox(value=True, label="", min_width=30, elem_id=f"chk-{slot_name}")
                                dropdown = gr.Dropdown(
                                    choices=self.get_slot_choices(slot_name),
                                    value="(None)",
                                    label=display_name,
                                    scale=2
                                )
                                random_btn = gr.Button("🎲", min_width=35)
                                weight = gr.Number(value=1.0, label="Wt", minimum=0.1, maximum=2.0, step=0.1, min_width=50)
                        
                        color_dropdown = gr.Dropdown(choices=["(No Color)"], value="(No Color)", visible=False)
                        color_random_btn = gr.Button("🎨", visible=False)
                        
                        all_enabled.append(enabled)
                        all_dropdowns.append(dropdown)
                        all_colors.append(color_dropdown)
                        all_weights.append(weight)
                        all_random_btns.append((random_btn, slot_name))
                        all_color_btns.append((color_random_btn, slot_name))
                        section_enabled_2.append(enabled)
                        section_dropdown_2.append(dropdown)
                        section_color_2.append(color_dropdown)
                        section_weight_2.append(weight)
                    
                    section_components["body"] = {
                        "enabled": section_enabled_2, "dropdowns": section_dropdown_2,
                        "colors": section_color_2, "weights": section_weight_2,
                        "random_btn": section_random_btn_2, "disable_btn": section_disable_btn_2,
                        "enable_btn": section_enable_btn_2, "slots": body_slots
                    }
            
            # ===== ROW 2: Clothing (left) + Output/Controls (right) =====
            with gr.Row():
                # === COLUMN: Clothing & Background ===
                with gr.Column(scale=1):
                    gr.Markdown("### 👗 Clothing & Background")
                    with gr.Row():
                        section_random_btn_3 = gr.Button("🎲 Random", size="sm")
                        section_disable_btn_3 = gr.Button("❌ Disable", size="sm")
                        section_enable_btn_3 = gr.Button("✅ Enable", size="sm")
                    section_enabled_3 = []
                    section_dropdown_3 = []
                    section_color_3 = []
                    section_weight_3 = []
                    
                    for slot_name in clothing_slots:
                        if slot_name not in self.generator.SLOT_DEFINITIONS:
                            continue
                        slot_def = self.generator.SLOT_DEFINITIONS[slot_name]
                        display_name = slot_name.replace("_", " ").title()
                        has_color = slot_def.get("has_color", False)
                        row_id = f"slot-row-{slot_name}"
                        
                        with gr.Group(elem_id=row_id, elem_classes=["slot-row", "slot-enabled"]):
                            with gr.Row():
                                enabled = gr.Checkbox(value=True, label="", min_width=30, elem_id=f"chk-{slot_name}")
                                dropdown = gr.Dropdown(
                                    choices=self.get_slot_choices(slot_name),
                                    value="(None)",
                                    label=display_name,
                                    scale=2
                                )
                                random_btn = gr.Button("🎲", min_width=35)
                                if has_color:
                                    color_dropdown = gr.Dropdown(
                                        choices=self.get_color_choices(),
                                        value="(No Color)",
                                        label="Color",
                                        scale=1
                                    )
                                    color_random_btn = gr.Button("🎨", min_width=35)
                                else:
                                    color_dropdown = gr.Dropdown(choices=["(No Color)"], value="(No Color)", visible=False)
                                    color_random_btn = gr.Button("🎨", visible=False)
                                weight = gr.Number(value=1.0, label="Wt", minimum=0.1, maximum=2.0, step=0.1, min_width=50)
                        
                        all_enabled.append(enabled)
                        all_dropdowns.append(dropdown)
                        all_colors.append(color_dropdown)
                        all_weights.append(weight)
                        all_random_btns.append((random_btn, slot_name))
                        all_color_btns.append((color_random_btn, slot_name))
                        section_enabled_3.append(enabled)
                        section_dropdown_3.append(dropdown)
                        section_color_3.append(color_dropdown)
                        section_weight_3.append(weight)
                    
                    section_components["clothing"] = {
                        "enabled": section_enabled_3, "dropdowns": section_dropdown_3,
                        "colors": section_color_3, "weights": section_weight_3,
                        "random_btn": section_random_btn_3, "disable_btn": section_disable_btn_3,
                        "enable_btn": section_enable_btn_3, "slots": clothing_slots
                    }
            
            # ===== SAVE/LOAD SECTION =====
            with gr.Accordion("💾 Save / Load Configuration", open=False):
                with gr.Row():
                    config_name_input = gr.Textbox(label="Config Name", placeholder="my_character", scale=2)
                    save_btn = gr.Button("💾 Save", scale=1)
                with gr.Row():
                    load_dropdown = gr.Dropdown(
                        choices=self.get_saved_configs(),
                        value=None,
                        label="Load Config",
                        scale=2,
                        allow_custom_value=False
                    )
                    load_btn = gr.Button("📂 Load", scale=1)
                    refresh_configs_btn = gr.Button("🔄", scale=0, min_width=40)
                save_status = gr.Textbox(label="Status", interactive=False, max_lines=1)
            
            # ===== EVENT HANDLERS =====
            
            # All components for prompt building (in slot order)
            all_components = []
            for i in range(len(all_enabled)):
                all_components.extend([all_enabled[i], all_dropdowns[i], all_colors[i], all_weights[i]])
            
            # Just the dropdowns and colors for randomize output
            dropdown_and_color_outputs = []
            for i in range(len(all_dropdowns)):
                dropdown_and_color_outputs.extend([all_dropdowns[i], all_colors[i]])
            
            # Generate prompt
            def generate_prompt(*args):
                parts = ["1girl"]
                idx = 0
                for slot_name in slot_names_list:
                    if idx + 4 > len(args):
                        break
                    enabled, value, color, weight = args[idx:idx+4]
                    idx += 4
                    
                    if not enabled or value == "(None)" or not value:
                        continue
                    
                    part = f"{color} {value}" if color and color != "(No Color)" else value
                    
                    try:
                        w = float(weight)
                        if w != 1.0:
                            part = f"({part}:{w:.1f})"
                    except:
                        pass
                    
                    parts.append(part)
                
                return ", ".join(parts)
            
            generate_btn.click(fn=generate_prompt, inputs=all_components, outputs=[output_prompt])
            
            # Randomize All - also generates prompt immediately
            def randomize_all_handler(palette_name, color_mode_val, full_body_on, *current_values):
                outputs = []
                prompt_parts = ["1girl"]
                palette_id = None
                
                if color_mode_val == "Palette" and palette_name and palette_name != "(None)":
                    for p in self.generator.palettes.values():
                        if p.get("name") == palette_name:
                            palette_id = p["id"]
                            break
                
                full_body_value = None
                
                # Get current enabled states (every 4th value starting at 0)
                enabled_states = []
                for i in range(0, len(current_values), 4):
                    enabled_states.append(current_values[i] if i < len(current_values) else True)
                
                idx = 0
                for slot_name in slot_names_list:
                    is_enabled = enabled_states[idx] if idx < len(enabled_states) else True
                    
                    item = self.generator.sample_slot(slot_name)
                    new_val = item.get("name", "(None)") if item else "(None)"
                    
                    if slot_name == "full_body":
                        full_body_value = new_val
                    
                    if full_body_on and slot_name in ["upper_body", "lower_body"]:
                        if full_body_value and full_body_value != "(None)":
                            new_val = "(None)"
                    
                    new_color = "(No Color)"
                    has_color = self.generator.SLOT_DEFINITIONS[slot_name].get("has_color", False)
                    if has_color:
                        if color_mode_val == "Palette" and palette_id:
                            new_color = self.generator.sample_color_from_palette(palette_id) or "(No Color)"
                        elif color_mode_val == "Random":
                            new_color = self.generator.sample_random_color() or "(No Color)"
                    
                    outputs.extend([new_val, new_color])
                    
                    # Build prompt part if enabled
                    if is_enabled and new_val and new_val != "(None)":
                        part = f"{new_color} {new_val}" if new_color and new_color != "(No Color)" else new_val
                        prompt_parts.append(part)
                    
                    idx += 1
                
                # Add generated prompt as last output
                generated_prompt = ", ".join(prompt_parts)
                outputs.append(generated_prompt)
                
                return outputs
            
            randomize_all_btn.click(
                fn=randomize_all_handler,
                inputs=[palette_dropdown, color_mode, full_body_mode] + all_components,
                outputs=dropdown_and_color_outputs + [output_prompt]
            )
            
            # Auto-enable Palette mode when selecting a palette
            def on_palette_select(palette_name):
                if palette_name and palette_name != "(None)":
                    return "Palette"
                return gr.update()
            
            palette_dropdown.change(
                fn=on_palette_select,
                inputs=[palette_dropdown],
                outputs=[color_mode]
            )
            
            # Reset All
            def reset_all_handler():
                outputs = []
                for _ in slot_names_list:
                    outputs.extend([True, "(None)", "(No Color)", 1.0])
                return outputs
            
            reset_btn.click(fn=reset_all_handler, inputs=[], outputs=all_components)
            
            # Section buttons
            for section_id, section_data in section_components.items():
                slots = section_data["slots"]
                enabled_list = section_data["enabled"]
                dropdown_list = section_data["dropdowns"]
                color_list = section_data["colors"]
                
                section_dd_color_outputs = []
                for i in range(len(dropdown_list)):
                    section_dd_color_outputs.extend([dropdown_list[i], color_list[i]])
                
                # Section randomize
                def make_section_randomize(slots_list):
                    def handler(palette_name, color_mode_val):
                        outputs = []
                        palette_id = None
                        
                        if color_mode_val == "Palette" and palette_name and palette_name != "(None)":
                            for p in self.generator.palettes.values():
                                if p.get("name") == palette_name:
                                    palette_id = p["id"]
                                    break
                        
                        for slot_name in slots_list:
                            if slot_name not in self.generator.SLOT_DEFINITIONS:
                                continue
                            
                            item = self.generator.sample_slot(slot_name)
                            new_val = item.get("name", "(None)") if item else "(None)"
                            
                            new_color = "(No Color)"
                            has_color = self.generator.SLOT_DEFINITIONS[slot_name].get("has_color", False)
                            if has_color:
                                if color_mode_val == "Palette" and palette_id:
                                    new_color = self.generator.sample_color_from_palette(palette_id) or "(No Color)"
                                elif color_mode_val == "Random":
                                    new_color = self.generator.sample_random_color() or "(No Color)"
                            
                            outputs.extend([new_val, new_color])
                        
                        return outputs
                    return handler
                
                section_data["random_btn"].click(
                    fn=make_section_randomize(slots),
                    inputs=[palette_dropdown, color_mode],
                    outputs=section_dd_color_outputs
                )
                
                # Section disable/enable
                def make_toggle_handler(count, value):
                    def handler():
                        return [value] * count
                    return handler
                
                section_data["disable_btn"].click(
                    fn=make_toggle_handler(len(enabled_list), False),
                    inputs=[],
                    outputs=enabled_list
                )
                section_data["enable_btn"].click(
                    fn=make_toggle_handler(len(enabled_list), True),
                    inputs=[],
                    outputs=enabled_list
                )
            
            # Per-slot random buttons
            for i, (btn_tuple, _) in enumerate(zip(all_random_btns, slot_names_list)):
                btn, slot_name = btn_tuple
                
                def make_slot_random(sn, idx):
                    def handler(palette_name, color_mode_val):
                        item = self.generator.sample_slot(sn)
                        new_val = item.get("name", "(None)") if item else "(None)"
                        
                        new_color = "(No Color)"
                        has_color = self.generator.SLOT_DEFINITIONS[sn].get("has_color", False)
                        if has_color:
                            palette_id = None
                            if color_mode_val == "Palette" and palette_name and palette_name != "(None)":
                                for p in self.generator.palettes.values():
                                    if p.get("name") == palette_name:
                                        palette_id = p["id"]
                                        break
                            
                            if palette_id:
                                new_color = self.generator.sample_color_from_palette(palette_id) or "(No Color)"
                            elif color_mode_val == "Random":
                                new_color = self.generator.sample_random_color() or "(No Color)"
                        
                        return new_val, new_color
                    return handler
                
                btn.click(
                    fn=make_slot_random(slot_name, i),
                    inputs=[palette_dropdown, color_mode],
                    outputs=[all_dropdowns[i], all_colors[i]]
                )
            
            # Per-slot color random buttons
            for i, (btn_tuple, _) in enumerate(zip(all_color_btns, slot_names_list)):
                btn, slot_name = btn_tuple
                
                def make_color_random(sn):
                    def handler(palette_name, color_mode_val):
                        has_color = self.generator.SLOT_DEFINITIONS[sn].get("has_color", False)
                        if not has_color:
                            return "(No Color)"
                        
                        palette_id = None
                        if color_mode_val == "Palette" and palette_name and palette_name != "(None)":
                            for p in self.generator.palettes.values():
                                if p.get("name") == palette_name:
                                    palette_id = p["id"]
                                    break
                        
                        if palette_id:
                            return self.generator.sample_color_from_palette(palette_id) or "(No Color)"
                        else:
                            return self.generator.sample_random_color() or "(No Color)"
                    return handler
                
                btn.click(
                    fn=make_color_random(slot_name),
                    inputs=[palette_dropdown, color_mode],
                    outputs=[all_colors[i]]
                )
            
            # Checkbox change handlers - toggle green/red styling via JS
            for i, slot_name in enumerate(slot_names_list):
                row_id = f"slot-row-{slot_name}"
                js_code = f"""
                (checked) => {{
                    const row = document.getElementById('{row_id}');
                    if (row) {{
                        row.classList.remove('slot-enabled', 'slot-disabled');
                        row.classList.add(checked ? 'slot-enabled' : 'slot-disabled');
                    }}
                    return checked;
                }}
                """
                all_enabled[i].change(
                    fn=lambda x: x,
                    inputs=[all_enabled[i]],
                    outputs=[all_enabled[i]],
                    js=js_code
                )
            
            # ===== SAVE/LOAD HANDLERS =====
            
            # Save config
            def save_config_handler(config_name, *slot_values):
                if not config_name or config_name.strip() == "":
                    return gr.update(value="❌ Please enter a configuration name")
                
                config = GeneratorConfig(name=config_name.strip())
                config.created_at = datetime.now().isoformat()
                
                idx = 0
                for slot_name in slot_names_list:
                    if idx + 4 > len(slot_values):
                        break
                    
                    enabled = slot_values[idx]
                    value = slot_values[idx + 1]
                    color = slot_values[idx + 2]
                    weight = slot_values[idx + 3]
                    idx += 4
                    
                    slot_config = SlotConfig(
                        enabled=bool(enabled),
                        value=value if value != "(None)" else None,
                        color=color if color != "(No Color)" else None,
                        color_enabled=bool(color and color != "(No Color)"),
                        weight=float(weight) if weight else 1.0
                    )
                    config.slots[slot_name] = slot_config
                
                filepath = self.configs_dir / f"{config_name.strip()}.json"
                self.generator.save_config(config, filepath)
                
                return gr.update(value=f"✅ Saved: {config_name}")
            
            save_btn.click(
                fn=save_config_handler,
                inputs=[config_name_input] + all_components,
                outputs=[save_status]
            )
            
            # Load config
            def load_config_handler(config_name):
                if not config_name:
                    return self._get_default_ui_values() + [gr.update(value="❌ Please select a config")]
                
                filepath = self.configs_dir / f"{config_name}.json"
                if not filepath.exists():
                    return self._get_default_ui_values() + [gr.update(value=f"❌ Config not found: {config_name}")]
                
                try:
                    config = self.generator.load_config(filepath)
                    values = []
                    
                    for slot_name in slot_names_list:
                        slot = config.slots.get(slot_name, SlotConfig())
                        values.extend([
                            slot.enabled,
                            slot.value or "(None)",
                            slot.color or "(No Color)",
                            slot.weight if slot.weight else 1.0
                        ])
                    
                    values.append(gr.update(value=f"✅ Loaded: {config_name}"))
                    return values
                except Exception as e:
                    print(f"Error loading config: {e}")
                    return self._get_default_ui_values() + [gr.update(value=f"❌ Error: {str(e)}")]
            
            load_btn.click(
                fn=load_config_handler,
                inputs=[load_dropdown],
                outputs=all_components + [save_status]
            )
            
            # Refresh configs list
            def refresh_configs():
                configs = self.get_saved_configs()
                return gr.update(choices=configs, value=None)
            
            refresh_configs_btn.click(fn=refresh_configs, inputs=[], outputs=[load_dropdown])
            
            # Also refresh after saving
            save_btn.click(fn=refresh_configs, inputs=[], outputs=[load_dropdown])
            
            # Copy button - in Gradio 6.x we use js for clipboard
            copy_btn.click(
                fn=lambda x: x,
                inputs=[output_prompt],
                outputs=[output_prompt],
                js="(text) => { navigator.clipboard.writeText(text); return text; }"
            )
            
            # Shutdown button - cleanly stops server and releases port
            shutdown_btn.click(
                fn=shutdown_server,
                inputs=[],
                outputs=[]
            )
        
        return app


def create_app() -> gr.Blocks:
    """Create and return the Gradio app."""
    ui = PromptGeneratorUI()
    return ui.build_ui()


if __name__ == "__main__":
    app = create_app()
    app.launch()
