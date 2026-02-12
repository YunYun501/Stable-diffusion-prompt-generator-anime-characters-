"""
ComfyUI Custom Node: Random Character Prompt Generator
Auto-generates anime character prompts for Stable Diffusion.

Installation:
1. Copy entire 'auto_prompt' folder to ComfyUI/custom_nodes/
2. Restart ComfyUI
3. Find "Random Character Prompt" in the node menu under "prompt"
"""

from .nodes import RandomCharacterPromptNode

NODE_CLASS_MAPPINGS = {
    "RandomCharacterPrompt": RandomCharacterPromptNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomCharacterPrompt": "Random Character Prompt"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
