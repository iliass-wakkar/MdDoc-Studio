"""
Theme definitions for MdDoc.
Each theme defines colors, fonts, margins, and component styling.
"""

from typing import Dict, Any

THEMES: Dict[str, Dict[str, Any]] = {
    "modern": {
        "name": "Modern Tech",
        "description": "Clean, contemporary design with deep navy headings, teal accents, and soft slate text.",
        "font_heading": "Cambria",
        "font_body": "Calibri",
        "font_code": "Consolas",
        "primary": "1E3A5F",          # Deep Navy
        "secondary": "2E8B8B",        # Deep Teal
        "accent": "E07A5F",           # Warm Coral
        "heading1": "1E3A5F",
        "heading2": "2E5A7E",
        "heading3": "4A7C94",
        "heading4": "5C8DA6",
        "text": "2D3748",             # Charcoal Body Text
        "light_text": "718096",       # Muted Grey Text
        "border": "E2E8F0",
        "code_bg": "F8FAFC",
        "code_border": "CBD5E1",
        "code_text": "0F172A",
        "quote_border": "2E8B8B",     # Teal accent bar
        "quote_bg": "F0FDF4",         # Soft light tint
        "quote_text": "334155",
        "table_header_bg": "1E3A5F",
        "table_header_text": "FFFFFF",
        "table_border": "CBD5E1",
        "table_row_alt": "F8FAFC",    # Zebra row
        "link": "0284C7",
        "hr_color": "CBD5E1",
        # Admonitions / Callout badges
        "alerts": {
            "NOTE": {"color": "0284C7", "bg": "F0F9FF", "title": "Note", "icon": "ℹ"},
            "TIP": {"color": "10B981", "bg": "F0FDF4", "title": "Tip", "icon": "💡"},
            "IMPORTANT": {"color": "8B5CF6", "bg": "F5F3FF", "title": "Important", "icon": "★"},
            "WARNING": {"color": "F59E0B", "bg": "FFFBEB", "title": "Warning", "icon": "⚠"},
            "CAUTION": {"color": "EF4444", "bg": "FEF2F2", "title": "Caution", "icon": "🛑"},
        }
    },
    "nordic": {
        "name": "Nordic Minimal",
        "description": "Minimalist Scandinavian design with slate charcoal, polar blue accents, and aurora red highlights.",
        "font_heading": "Segoe UI Semibold",
        "font_body": "Segoe UI",
        "font_code": "Consolas",
        "primary": "2E3440",          # Polar Night Dark
        "secondary": "5E81AC",        # Frost Blue
        "accent": "BF616A",           # Aurora Red
        "heading1": "2E3440",
        "heading2": "3B4252",
        "heading3": "434C5E",
        "heading4": "4C566A",
        "text": "3B4252",
        "light_text": "4C566A",
        "border": "D8DEE9",
        "code_bg": "ECEFF4",
        "code_border": "D8DEE9",
        "code_text": "2E3440",
        "quote_border": "5E81AC",
        "quote_bg": "F4F6F9",
        "quote_text": "2E3440",
        "table_header_bg": "2E3440",
        "table_header_text": "ECEFF4",
        "table_border": "D8DEE9",
        "table_row_alt": "F4F6F9",
        "link": "5E81AC",
        "hr_color": "D8DEE9",
        "alerts": {
            "NOTE": {"color": "5E81AC", "bg": "F4F6F9", "title": "Note", "icon": "ℹ"},
            "TIP": {"color": "A3BE8C", "bg": "F2F7F0", "title": "Tip", "icon": "💡"},
            "IMPORTANT": {"color": "B48EAD", "bg": "F8F4F7", "title": "Important", "icon": "★"},
            "WARNING": {"color": "EBCB8B", "bg": "FCF9F0", "title": "Warning", "icon": "⚠"},
            "CAUTION": {"color": "BF616A", "bg": "FDF4F4", "title": "Caution", "icon": "🛑"},
        }
    },
    "academic": {
        "name": "Academic Classic",
        "description": "Formal, elegant style with serif typography, rich oxford blue, and warm amber accents.",
        "font_heading": "Georgia",
        "font_body": "Georgia",
        "font_code": "Courier New",
        "primary": "1A365D",          # Oxford Blue
        "secondary": "744210",        # Deep Amber
        "accent": "C05621",           # Russet
        "heading1": "1A365D",
        "heading2": "2C5282",
        "heading3": "2B6CB0",
        "heading4": "3182CE",
        "text": "1A202C",
        "light_text": "4A5568",
        "border": "E2E8F0",
        "code_bg": "FFFAF0",
        "code_border": "E2E8F0",
        "code_text": "1A202C",
        "quote_border": "744210",
        "quote_bg": "FFFAF0",
        "quote_text": "2D3748",
        "table_header_bg": "1A365D",
        "table_header_text": "FFFFFF",
        "table_border": "CBD5E0",
        "table_row_alt": "F7FAFC",
        "link": "2B6CB0",
        "hr_color": "CBD5E0",
        "alerts": {
            "NOTE": {"color": "2B6CB0", "bg": "EBF8FF", "title": "Note", "icon": "ℹ"},
            "TIP": {"color": "2F855A", "bg": "F0FFF4", "title": "Tip", "icon": "💡"},
            "IMPORTANT": {"color": "6B46C1", "bg": "FAF5FF", "title": "Important", "icon": "★"},
            "WARNING": {"color": "DD6B20", "bg": "FFFAF0", "title": "Warning", "icon": "⚠"},
            "CAUTION": {"color": "C53030", "bg": "FFF5F5", "title": "Caution", "icon": "🛑"},
        }
    },
    "forest": {
        "name": "Forest Moss",
        "description": "Organic, natural palette with deep evergreen, sage green, and earthy ochre tones.",
        "font_heading": "Cambria",
        "font_body": "Calibri",
        "font_code": "Consolas",
        "primary": "1C4532",          # Deep Forest Green
        "secondary": "2F855A",        # Sage Emerald
        "accent": "D69E2E",           # Ochre Gold
        "heading1": "1C4532",
        "heading2": "276749",
        "heading3": "2F855A",
        "heading4": "38A169",
        "text": "1A202C",
        "light_text": "4A5568",
        "border": "C6F6D5",
        "code_bg": "F0FFF4",
        "code_border": "C6F6D5",
        "code_text": "1C4532",
        "quote_border": "2F855A",
        "quote_bg": "F0FFF4",
        "quote_text": "22543D",
        "table_header_bg": "1C4532",
        "table_header_text": "FFFFFF",
        "table_border": "C6F6D5",
        "table_row_alt": "F7FAFC",
        "link": "276749",
        "hr_color": "C6F6D5",
        "alerts": {
            "NOTE": {"color": "2F855A", "bg": "F0FFF4", "title": "Note", "icon": "ℹ"},
            "TIP": {"color": "38A169", "bg": "F0FFF4", "title": "Tip", "icon": "💡"},
            "IMPORTANT": {"color": "22543D", "bg": "E6FFFA", "title": "Important", "icon": "★"},
            "WARNING": {"color": "D69E2E", "bg": "FFFFF0", "title": "Warning", "icon": "⚠"},
            "CAUTION": {"color": "E53E3E", "bg": "FFF5F5", "title": "Caution", "icon": "🛑"},
        }
    },
    "corporate": {
        "name": "Corporate Blue",
        "description": "Executive enterprise look with rich navy, vibrant royal blue, and sleek borders.",
        "font_heading": "Arial",
        "font_body": "Arial",
        "font_code": "Consolas",
        "primary": "0F2942",          # Deep Executive Navy
        "secondary": "1E6091",        # Royal Blue
        "accent": "00A896",           # Teal Accent
        "heading1": "0F2942",
        "heading2": "184E77",
        "heading3": "1E6091",
        "heading4": "1A759F",
        "text": "1F2937",
        "light_text": "6B7280",
        "border": "D1D5DB",
        "code_bg": "F9FAFB",
        "code_border": "E5E7EB",
        "code_text": "111827",
        "quote_border": "1E6091",
        "quote_bg": "F0F7FF",
        "quote_text": "1F2937",
        "table_header_bg": "0F2942",
        "table_header_text": "FFFFFF",
        "table_border": "D1D5DB",
        "table_row_alt": "F9FAFB",
        "link": "1E6091",
        "hr_color": "D1D5DB",
        "alerts": {
            "NOTE": {"color": "1E6091", "bg": "F0F7FF", "title": "Note", "icon": "ℹ"},
            "TIP": {"color": "059669", "bg": "ECFDF5", "title": "Tip", "icon": "💡"},
            "IMPORTANT": {"color": "6366F1", "bg": "EEF2FF", "title": "Important", "icon": "★"},
            "WARNING": {"color": "D97706", "bg": "FFFBEB", "title": "Warning", "icon": "⚠"},
            "CAUTION": {"color": "DC2626", "bg": "FEF2F2", "title": "Caution", "icon": "🛑"},
        }
    }
}


def get_theme(theme_name: str) -> Dict[str, Any]:
    """Retrieve theme dict by name, falling back to 'modern'."""
    normalized = (theme_name or "modern").lower().strip()
    return THEMES.get(normalized, THEMES["modern"])
