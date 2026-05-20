import sys

import glory_to_protocol.jobs  # noqa: F401

tui_loaded = any(m.startswith("glory_to_protocol.tui") for m in sys.modules)
settings_loaded = "glory_to_protocol.settings" in sys.modules
print(int(tui_loaded), int(settings_loaded))
