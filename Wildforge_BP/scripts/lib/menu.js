// menu.js — @minecraft/server-ui wrappers (pet commands, turret mode, keypad).
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";

/**
 * Show a simple button menu. `buttons` = [{ text, icon? }].
 * Resolves to the selected index, or undefined if cancelled.
 */
export async function actionMenu(player, title, body, buttons) {
  const form = new ActionFormData().title(title);
  if (body) form.body(body);
  for (const b of buttons) form.button(b.text, b.icon);
  try {
    const res = await form.show(player);
    if (res.canceled) return undefined;
    return res.selection;
  } catch (_) {
    return undefined;
  }
}

/**
 * Prompt for a text code (keypad). Resolves to the string, or undefined.
 */
export async function textPrompt(player, title, label, placeholder = "") {
  const form = new ModalFormData().title(title).textField(label, placeholder);
  try {
    const res = await form.show(player);
    if (res.canceled) return undefined;
    return res.formValues?.[0];
  } catch (_) {
    return undefined;
  }
}
