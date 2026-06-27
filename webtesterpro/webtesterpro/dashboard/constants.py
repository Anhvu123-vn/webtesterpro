"""
Hằng số dashboard: định nghĩa 8 module kiểm thử cho homepage.
"""

from typing import TypedDict


class ModuleInfo(TypedDict, total=False):
    id: str
    name: str
    description: str
    icon: str
    color: str
    featured: bool  # Full Test card lớn hơn


# 8 module cards — Full Test là featured card
TEST_MODULES: list[ModuleInfo] = [
    {
        "id": "full",
        "name": "Full Test",
        "description": "Chạy toàn bộ modules — SEO, Performance, Security, Accessibility và hơn thế nữa trong một lần.",
        "icon": "zap",
        "color": "from-blue-500 via-blue-600 to-indigo-600",
        "featured": True,
    },
    {
        "id": "seo",
        "name": "SEO Analysis",
        "description": "Meta tags, heading structure, Open Graph và keyword density.",
        "icon": "search",
        "color": "from-lime-500 to-green-500",
    },
    {
        "id": "performance",
        "name": "Performance",
        "description": "Core Web Vitals, thời gian tải trang và phân tích tài nguyên.",
        "icon": "gauge",
        "color": "from-amber-500 to-orange-500",
    },
    {
        "id": "security",
        "name": "Security Scan",
        "description": "Phát hiện XSS, SQLi, file nhạy cảm và security headers.",
        "icon": "shield-alert",
        "color": "from-red-500 to-rose-600",
    },
    {
        "id": "accessibility",
        "name": "Accessibility",
        "description": "Kiểm tra WCAG 2.1 với axe-core và manual checks.",
        "icon": "accessibility",
        "color": "from-emerald-500 to-teal-500",
    },
    {
        "id": "crawler",
        "name": "Crawler",
        "description": "Thu thập URL, phân tích cấu trúc site theo depth.",
        "icon": "network",
        "color": "from-cyan-500 to-blue-500",
    },
    {
        "id": "visual",
        "name": "Visual Testing",
        "description": "Screenshot đa viewport, so sánh responsive layout.",
        "icon": "camera",
        "color": "from-pink-500 to-fuchsia-500",
    },
    {
        "id": "monitor",
        "name": "Monitor",
        "description": "Theo dõi uptime, response time và cảnh báo downtime.",
        "icon": "activity",
        "color": "from-violet-500 to-purple-600",
    },
]

# IDs hợp lệ khi submit form test (backend WebTesterEngine)
MODULE_IDS = {"seo", "performance", "security", "accessibility", "crawler", "visual", "scanner", "analyzer", "monitor"}

# Preset Full Test — tất cả modules runnable (trừ monitor vì chạy lâu)
FULL_TEST_MODULES = ["seo", "performance", "security", "accessibility", "crawler", "visual", "scanner"]

# Modules hiển thị trong form checkbox (bỏ card Full Test)
FORM_MODULES = [m for m in TEST_MODULES if m["id"] != "full"]

# Viewport options cho Visual Testing
VIEWPORT_OPTIONS = [
    ("desktop", "Desktop", "1920×1080"),
    ("laptop", "Laptop", "1366×768"),
    ("tablet-portrait", "Tablet", "768×1024"),
    ("mobile-portrait", "Mobile", "390×844"),
]
