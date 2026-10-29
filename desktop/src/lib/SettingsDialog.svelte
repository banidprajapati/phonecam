<script lang="ts">
  import { Cable, Link, RefreshCw, Trash2 } from "@lucide/svelte";
  import { engine } from "./engine.svelte";
  import { onMount } from "svelte";

  type Phone = { fingerprint: string; name: string; address: string };

  let { open = false, onclose }: { open: boolean; onclose: () => void } = $props();

  let phones = $state<Phone[]>([]);
  let address = $state("");
  let message = $state<string | null>(null);
  let connectionMode = $state<"auto" | "wifi" | "usb">("auto");

  async function refresh() {
    try {
      phones = await engine.paired();
      message = null;
    } catch (e) {
      message = String(e);
    }
  }

  async function forget(p: Phone) {
    try {
      await engine.forget(p.fingerprint);
      await refresh();
      message = "Forgot " + p.name + ".";
    } catch (e) {
      message = String(e);
    }
  }

  async function connect() {
    try {
      if (connectionMode === "usb") {
        await engine.connect("127.0.0.1:8080");
        message = "Connecting to 127.0.0.1:8080 (USB). Ensure adb forward is active.";
        return;
      }
      if (connectionMode === "wifi") {
        await engine.connect(address.trim() || null);
        message = address.trim() ? "Connecting to " + address.trim() + " (Wi-Fi)." : "Searching over Wi-Fi.";
        return;
      }
      await engine.connect(address.trim() || null);
      message = address.trim() ? "Connecting to " + address.trim() + "." : "Searching automatically (USB first if available).";
    } catch (e) {
      message = String(e);
    }
  }

  async function reinstall() {
    try {
      message = (await engine.register()) ? "Virtual camera registered." : "Registration failed or not needed.";
    } catch (e) {
      message = String(e);
    }
  }

  async function uninstall() {
    try {
      message = (await engine.unregister()) ? "Virtual camera unregistered." : "Unregistration failed.";
    } catch (e) {
      message = String(e);
    }
  }

  onMount(() => {
    if (open) refresh();
  });

  $effect(() => {
    if (open) refresh();
  });
</script>

{#if open}
  <div class="backdrop" onclick={onclose}></div>
  <div class="dialog" role="dialog" aria-modal="true">
    <header>
      <h2>Settings</h2>
      <button class="ghost" onclick={onclose}>Close</button>
    </header>

    <section>
      <h3><Cable size={15} /> Paired phones</h3>
      <p class="faint">Phones you've connected to before. Forget one to pair again.</p>
      {#if phones.length === 0}
        <p class="empty">No paired phones yet.</p>
      {:else}
        <ul>
          {#each phones as p}
            <li>
              <div>
                <div class="name">{p.name}</div>
                <div class="faint">{p.address}</div>
              </div>
              <div class="row">
                <button class="ghost" onclick={() => { address = p.address; connectionMode = "wifi"; }}>Use</button>
                <button class="ghost" onclick={() => forget(p)}><Trash2 size={14} /></button>
              </div>
            </li>
          {/each}
        </ul>
      {/if}
      <button class="ghost" onclick={refresh}><RefreshCw size={14} /> Refresh</button>
    </section>

    <section>
      <h3><Link size={15} /> Connection</h3>
      <p class="faint">Choose how to connect. USB uses adb forward to 127.0.0.1:8080. Wi-Fi uses network discovery/manual IP.</p>
      <div class="mode">
        <button class:active={connectionMode === "auto"} onclick={() => (connectionMode = "auto")}>Auto (USB first)</button>
        <button class:active={connectionMode === "usb"} onclick={() => (connectionMode = "usb")}>USB</button>
        <button class:active={connectionMode === "wifi"} onclick={() => (connectionMode = "wifi")}>Wi-Fi</button>
      </div>
      {#if connectionMode !== "usb"}
        <p class="faint" style="margin-top:10px;">{connectionMode === "wifi" ? "Enter IP or leave empty to search on Wi-Fi." : "Leave empty to search (will prefer USB if available)."}</p>
        <div class="inline">
          <input bind:value={address} placeholder={connectionMode === "wifi" ? "192.168.1.42 — leave empty to search" : "192.168.1.42 — leave empty for automatic"} onkeydown={(e) => e.key === "Enter" && connect()} />
          <button class="primary" onclick={connect}>Connect</button>
        </div>
      {:else}
        <div class="inline" style="margin-top:10px;">
          <button class="primary" onclick={connect}>Connect via USB (127.0.0.1:8080)</button>
        </div>
      {/if}
    </section>

    <section>
      <h3>Virtual camera</h3>
      <p class="faint">Register the virtual camera so OBS/Zoom/etc can see it. Run as administrator if it doesn't stick.</p>
      <div class="row">
        <button class="ghost" onclick={reinstall}>Register</button>
        <button class="ghost" onclick={uninstall}>Unregister</button>
      </div>
    </section>

    {#if message}
      <p class="message">{message}</p>
    {/if}
  </div>
{/if}

<style>
  .backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.55); backdrop-filter: blur(4px); z-index: 20; }
  .dialog { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: min(520px, calc(100vw - 24px)); max-height: calc(100vh - 24px); overflow: auto; background: radial-gradient(120% 120% at 50% 0%, rgba(255,255,255,0.06), transparent), var(--panel); border: 1px solid var(--line); border-radius: 14px; box-shadow: 0 40px 80px rgba(0,0,0,0.45); z-index: 21; display: flex; flex-direction: column; gap: 16px; padding: 18px; }
  header { display: flex; align-items: center; justify-content: space-between; }
  h2 { margin: 0; font-size: 16px; }
  h3 { margin: 0 0 6px 0; font-size: 14px; display: flex; align-items: center; gap: 8px; }
  section { display: flex; flex-direction: column; gap: 8px; padding: 14px; border-radius: 12px; background: linear-gradient(180deg, rgba(255,255,255,0.02), transparent); border: 1px solid var(--line); }
  .faint { margin: 0; color: var(--dim); font-size: 13px; }
  .empty { margin: 0; color: var(--dim); font-size: 13px; }
  ul { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 8px; }
  li { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 12px; border-radius: 10px; background: var(--panel-2); border: 1px solid var(--line); }
  .name { font-weight: 600; }
  .row { display: flex; align-items: center; gap: 8px; }
  .inline { display: flex; gap: 8px; margin-top: 10px; }
  .mode { display: flex; gap: 6px; margin-top: 10px; background: var(--panel-2); padding: 4px; border-radius: 999px; border: 1px solid var(--line); width: fit-content; }
  .mode button { border: none; background: transparent; color: var(--dim); padding: 6px 12px; border-radius: 999px; font-size: 12.5px; cursor: pointer; }
  .mode button.active { background: var(--panel); color: var(--text); border: 1px solid var(--line); }
  input { flex: 1; border-radius: 999px; border: 1px solid var(--line); background: transparent; color: var(--text); padding: 8px 12px; font: inherit; }
  button { border-radius: 999px; border: 1px solid var(--line); background: var(--panel-2); color: var(--text); padding: 8px 14px; font: inherit; display: flex; align-items: center; gap: 8px; cursor: pointer; }
  button.ghost { background: transparent; }
  button.primary { background: linear-gradient(180deg, rgba(255,255,255,0.08), transparent); }
  .message { margin: 0; color: var(--dim); font-size: 13px; }
</style>
