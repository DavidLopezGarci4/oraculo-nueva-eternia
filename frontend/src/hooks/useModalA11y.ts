import { useEffect, useRef } from 'react';

const FOCUSABLE_SELECTOR =
  'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

const openModalStack: symbol[] = [];
let previousBodyOverflow: string | null = null;

export function hasOpenModal(): boolean {
  return openModalStack.length > 0;
}

/**
 * Fase AAA-3c: comportamiento accesible compartido para los modales del
 * Oráculo (antes cada uno reimplementaba el overlay a mano, sin foco
 * atrapado, sin cierre por Escape y sin devolver el foco al cerrar).
 * No cambia el marcado visual de cada modal — solo añade el comportamiento
 * de teclado/foco en pila LIFO y bloqueo de scroll del body.
 */
export function useModalA11y(isOpen: boolean, onClose: () => void, containerRef: React.RefObject<HTMLElement | null>) {
  const previouslyFocused = useRef<HTMLElement | null>(null);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  useEffect(() => {
    if (!isOpen) return;

    const modalId = Symbol('modal');
    openModalStack.push(modalId);
    if (openModalStack.length === 1) {
      previousBodyOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
    }

    previouslyFocused.current = document.activeElement as HTMLElement | null;

    const container = containerRef.current;
    const focusFirst = () => {
      const focusable = container?.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR);
      (focusable?.[0] ?? container)?.focus();
    };
    // Espera al siguiente frame para que framer-motion haya montado el nodo.
    const raf = requestAnimationFrame(focusFirst);

    const handleKeyDown = (e: KeyboardEvent) => {
      if (openModalStack[openModalStack.length - 1] !== modalId) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopImmediatePropagation();
        onCloseRef.current();
        return;
      }
      if (e.key !== 'Tab' || !container) return;

      const focusable = Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(
        (el) => el.offsetParent !== null || el.getClientRects().length > 0,
      );
      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      cancelAnimationFrame(raf);
      document.removeEventListener('keydown', handleKeyDown);
      const idx = openModalStack.lastIndexOf(modalId);
      if (idx !== -1) openModalStack.splice(idx, 1);
      if (openModalStack.length === 0) {
        document.body.style.overflow = previousBodyOverflow ?? '';
        previousBodyOverflow = null;
      }
      previouslyFocused.current?.focus();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);
}
