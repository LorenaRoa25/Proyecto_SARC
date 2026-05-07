/**
 * Utilidades de audio para confirmaciones de la interfaz.
 */

/**
 * Reproduce un sonido breve al inscribir un curso.
 */
export function playSuccessSound() {
  try {
    const AudioContextRef = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextRef) return;

    const context = new AudioContextRef();
    const oscillator = context.createOscillator();
    const gain = context.createGain();

    oscillator.type = "sine";
    oscillator.frequency.setValueAtTime(523.25, context.currentTime);
    oscillator.frequency.setValueAtTime(659.25, context.currentTime + 0.08);
    gain.gain.setValueAtTime(0.0001, context.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.05, context.currentTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.22);

    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start();
    oscillator.stop(context.currentTime + 0.24);
  } catch (error) {
    // Algunos navegadores bloquean audio sin interacción previa.
  }
}
