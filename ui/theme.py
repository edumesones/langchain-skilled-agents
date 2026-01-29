"""Custom dark theme inspired by Linear's design system."""

import gradio as gr


def create_linear_dark_theme() -> gr.themes.Base:
    """
    Create a dark theme inspired by Linear's design.

    Features:
    - Minimalist aesthetic
    - Generous spacing
    - Subtle borders and shadows
    - Monospace fonts for code/data
    """
    return gr.themes.Base(
        # Primary colors (Linear purple/violet accent)
        primary_hue=gr.themes.Color(
            c50="#faf5ff",
            c100="#f3e8ff",
            c200="#e9d5ff",
            c300="#d8b4fe",
            c400="#c084fc",
            c500="#a855f7",
            c600="#9333ea",
            c700="#7c3aed",
            c800="#6b21a8",
            c900="#581c87",
            c950="#3b0764",
        ),
        # Neutral colors (Linear's gray scale)
        neutral_hue=gr.themes.Color(
            c50="#fafafa",
            c100="#f4f4f5",
            c200="#e4e4e7",
            c300="#d4d4d8",
            c400="#a1a1aa",
            c500="#71717a",
            c600="#52525b",
            c700="#3f3f46",
            c800="#27272a",
            c900="#18181b",
            c950="#09090b",
        ),
        # Secondary (for success states)
        secondary_hue=gr.themes.Color(
            c50="#f0fdf4",
            c100="#dcfce7",
            c200="#bbf7d0",
            c300="#86efac",
            c400="#4ade80",
            c500="#22c55e",
            c600="#16a34a",
            c700="#15803d",
            c800="#166534",
            c900="#14532d",
            c950="#052e16",
        ),
        # Typography
        font=[
            gr.themes.GoogleFont("Inter"),
            "ui-sans-serif",
            "system-ui",
            "sans-serif",
        ],
        font_mono=[
            gr.themes.GoogleFont("JetBrains Mono"),
            "ui-monospace",
            "monospace",
        ],
        # Spacing
        spacing_size=gr.themes.sizes.spacing_lg,
        radius_size=gr.themes.sizes.radius_md,
        text_size=gr.themes.sizes.text_md,
    ).set(
        # Dark mode colors
        body_background_fill="#0a0a0b",
        body_background_fill_dark="#0a0a0b",
        body_text_color="#e4e4e7",
        body_text_color_dark="#e4e4e7",
        body_text_color_subdued="#a1a1aa",
        body_text_color_subdued_dark="#71717a",
        # Blocks
        block_background_fill="#18181b",
        block_background_fill_dark="#18181b",
        block_border_color="#27272a",
        block_border_color_dark="#27272a",
        block_border_width="1px",
        block_label_background_fill="#18181b",
        block_label_background_fill_dark="#18181b",
        block_label_text_color="#a1a1aa",
        block_label_text_color_dark="#a1a1aa",
        block_label_margin="0",
        block_label_padding="*spacing_sm *spacing_md",
        block_label_radius="*radius_md *radius_md 0 0",
        block_label_text_size="*text_sm",
        block_label_text_weight="500",
        block_padding="*spacing_lg",
        block_radius="*radius_lg",
        block_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.3)",
        block_shadow_dark="0 1px 3px 0 rgba(0, 0, 0, 0.5)",
        block_title_background_fill="transparent",
        block_title_text_color="#e4e4e7",
        block_title_text_weight="600",
        # Borders
        border_color_accent="#3f3f46",
        border_color_accent_dark="#3f3f46",
        border_color_primary="#27272a",
        border_color_primary_dark="#27272a",
        # Buttons
        button_primary_background_fill="#7c3aed",
        button_primary_background_fill_dark="#7c3aed",
        button_primary_background_fill_hover="#6b21a8",
        button_primary_background_fill_hover_dark="#6b21a8",
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",
        button_primary_border_color="transparent",
        button_primary_border_color_dark="transparent",
        button_secondary_background_fill="#27272a",
        button_secondary_background_fill_dark="#27272a",
        button_secondary_background_fill_hover="#3f3f46",
        button_secondary_background_fill_hover_dark="#3f3f46",
        button_secondary_text_color="#e4e4e7",
        button_secondary_text_color_dark="#e4e4e7",
        button_shadow="none",
        button_shadow_active="none",
        button_shadow_hover="none",
        button_large_padding="*spacing_lg *spacing_xl",
        button_large_radius="*radius_lg",
        button_large_text_size="*text_md",
        button_large_text_weight="500",
        button_small_padding="*spacing_sm *spacing_lg",
        button_small_radius="*radius_md",
        button_small_text_size="*text_sm",
        button_small_text_weight="500",
        # Inputs
        input_background_fill="#18181b",
        input_background_fill_dark="#18181b",
        input_background_fill_focus="#1f1f23",
        input_background_fill_focus_dark="#1f1f23",
        input_border_color="#27272a",
        input_border_color_dark="#27272a",
        input_border_color_focus="#7c3aed",
        input_border_color_focus_dark="#7c3aed",
        input_border_width="1px",
        input_padding="*spacing_md",
        input_placeholder_color="#71717a",
        input_placeholder_color_dark="#71717a",
        input_radius="*radius_md",
        input_shadow="none",
        input_shadow_focus="0 0 0 2px rgba(124, 58, 237, 0.2)",
        input_text_size="*text_md",
        input_text_weight="400",
        # Panels
        panel_background_fill="#18181b",
        panel_background_fill_dark="#18181b",
        panel_border_color="#27272a",
        panel_border_color_dark="#27272a",
        panel_border_width="1px",
        # Chatbot
        chatbot_code_background_color="#27272a",
        chatbot_code_background_color_dark="#27272a",
        # Tables
        table_border_color="#27272a",
        table_border_color_dark="#27272a",
        table_even_background_fill="#18181b",
        table_even_background_fill_dark="#18181b",
        table_odd_background_fill="#1f1f23",
        table_odd_background_fill_dark="#1f1f23",
        table_row_focus="#27272a",
        table_row_focus_dark="#27272a",
        # Shadows
        shadow_drop="0 4px 6px -1px rgba(0, 0, 0, 0.3)",
        shadow_drop_lg="0 10px 15px -3px rgba(0, 0, 0, 0.3)",
        shadow_inset="inset 0 2px 4px 0 rgba(0, 0, 0, 0.25)",
        shadow_spread="6px",
        # Links
        link_text_color="#a855f7",
        link_text_color_dark="#a855f7",
        link_text_color_active="#c084fc",
        link_text_color_active_dark="#c084fc",
        link_text_color_hover="#c084fc",
        link_text_color_hover_dark="#c084fc",
        link_text_color_visited="#9333ea",
        link_text_color_visited_dark="#9333ea",
        # Prose
        prose_text_size="*text_md",
        prose_text_weight="400",
        prose_header_text_weight="600",
        # Code
        code_background_fill="#27272a",
        code_background_fill_dark="#27272a",
        # Errors
        error_background_fill="#450a0a",
        error_background_fill_dark="#450a0a",
        error_border_color="#7f1d1d",
        error_border_color_dark="#7f1d1d",
        error_text_color="#fecaca",
        error_text_color_dark="#fecaca",
    )


# Pre-built CSS for additional customization
LINEAR_DARK_CSS = """
/* Global styles */
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto;
}

/* Header styling */
.header-title {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #e4e4e7 !important;
    margin-bottom: 0.5rem !important;
}

.header-subtitle {
    font-size: 0.875rem !important;
    color: #71717a !important;
}

/* Chat container */
.chat-container {
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Message styling */
.message {
    padding: 1rem !important;
    margin: 0.5rem 0 !important;
    border-radius: 8px !important;
}

.user-message {
    background: #27272a !important;
    border-left: 3px solid #7c3aed !important;
}

.bot-message {
    background: #18181b !important;
    border-left: 3px solid #22c55e !important;
}

/* Sidebar panels */
.sidebar-panel {
    background: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

.sidebar-title {
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    color: #a1a1aa !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 0.75rem !important;
}

/* Status indicators */
.status-badge {
    display: inline-flex !important;
    align-items: center !important;
    padding: 0.25rem 0.75rem !important;
    border-radius: 9999px !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
}

.status-success {
    background: #052e16 !important;
    color: #4ade80 !important;
}

.status-warning {
    background: #451a03 !important;
    color: #fbbf24 !important;
}

.status-error {
    background: #450a0a !important;
    color: #f87171 !important;
}

.status-info {
    background: #1e1b4b !important;
    color: #a78bfa !important;
}

/* Agent indicators */
.agent-badge {
    display: inline-flex !important;
    align-items: center !important;
    padding: 0.25rem 0.5rem !important;
    border-radius: 4px !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.agent-orchestrator {
    background: #3b0764 !important;
    color: #d8b4fe !important;
}

.agent-risk {
    background: #7f1d1d !important;
    color: #fecaca !important;
}

.agent-compliance {
    background: #1e3a5f !important;
    color: #93c5fd !important;
}

/* Log entries */
.log-entry {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8125rem !important;
    padding: 0.25rem 0 !important;
    border-bottom: 1px solid #27272a !important;
}

.log-timestamp {
    color: #71717a !important;
}

.log-level-info {
    color: #60a5fa !important;
}

.log-level-warning {
    color: #fbbf24 !important;
}

.log-level-error {
    color: #f87171 !important;
}

/* Data tables */
.data-table {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8125rem !important;
}

/* Markdown content */
.markdown-content h2 {
    color: #e4e4e7 !important;
    font-size: 1.125rem !important;
    font-weight: 600 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.75rem !important;
    padding-bottom: 0.5rem !important;
    border-bottom: 1px solid #27272a !important;
}

.markdown-content h3 {
    color: #d4d4d8 !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin-top: 1rem !important;
    margin-bottom: 0.5rem !important;
}

.markdown-content ul {
    margin-left: 1.25rem !important;
}

.markdown-content li {
    margin-bottom: 0.25rem !important;
}

.markdown-content code {
    background: #27272a !important;
    padding: 0.125rem 0.375rem !important;
    border-radius: 4px !important;
    font-size: 0.875em !important;
}

/* Animation */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.loading-indicator {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #18181b;
}

::-webkit-scrollbar-thumb {
    background: #3f3f46;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #52525b;
}
"""
