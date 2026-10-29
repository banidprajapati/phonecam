path = r"D:/Projects/phonecam/desktop/src/lib/SettingsDialog.svelte"
with open(path, encoding="utf-8") as f:
    s = f.read()

old = """  async function connect() {
    try {
      await engine.connect(address.trim() || null);
      message = address.trim() ? `Connecting to ${address.trim()}.` : "Searching automatically";
    } catch (e) {
      message = String(e);
    }
  }"""

new = """  async function connect() {
    try {
      if (connectionMode === "usb") {
        await engine.connect("127.0.0.1:8080");
        message = "Connecting to 127.0.0.1:8080 (USB). Ensure adb forward is active.";
        return;
      }
      if (connectionMode === "wifi") {
        await engine.connect(address.trim() || null);
        message = address.trim() ? `Connecting to ${address.trim()} (Wi-Fi).` : "Searching over Wi-Fi.";
        return;
      }
      await engine.connect(address.trim() || null);
      message = address.trim() ? `Connecting to ${address.trim()}.` : "Searching automatically (USB first if available).";
    } catch (e) {
      message = String(e);
    }
  }"""

if old not in s:
    print("not found")
else:
    s2 = s.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(s2)
    print("ok")
