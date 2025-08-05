import time
import math
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController

class StandbyClass:
    def __init__(self, timeout=20):
        self.timeout = timeout  # Tiempo en segundos antes de mover el ratón
        self.last_activity = time.time()
        self.mouse_controller = MouseController()

        # Configurar los listeners
        self.mouse_listener = mouse.Listener(
            on_move=self.on_activity,
            on_click=self.on_activity,
            on_scroll=self.on_activity
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_activity
        )

    def on_activity(self, *args):
        """Actualiza el timestamp de la última actividad."""
        self.last_activity = time.time()

    def smooth_move(self, duration=5, radius=50, steps_per_second=60):
        """
        Mueve el ratón en un patrón circular suave durante `duration` segundos
        y lanza un click derecho al terminar.
        """
        # Capturamos la posición central
        center_x, center_y = self.mouse_controller.position
        total_steps = int(duration * steps_per_second)

        # Ejecutamos el movimiento circular
        for step in range(total_steps):
            angle = 2 * math.pi * step / total_steps
            dx = int(radius * math.cos(angle))
            dy = int(radius * math.sin(angle))
            self.mouse_controller.position = (center_x + dx, center_y + dy)
            time.sleep(1 / steps_per_second)

        # Al acabar el círculo, realizamos un click derecho
        # Nota: usamos mouse.Button.right porque importamos `mouse` arriba.
        self.mouse_controller.click(mouse.Button.right, 1)

    def run(self):
        """Inicia el monitor de inactividad."""
        self.mouse_listener.start()
        self.keyboard_listener.start()
        print("Iniciando monitor de inactividad... (Ctrl+C para salir)")

        try:
            while True:
                if time.time() - self.last_activity > self.timeout:
                    print("Sin actividad detectada. Moviendo el ratón y haciendo click derecho.")
                    self.smooth_move(duration=5)
                    # Reset del contador para no spamear
                    self.last_activity = time.time()
                time.sleep(1)
        except KeyboardInterrupt:
            print("Monitor detenido.")

if __name__ == "__main__":
    monitor = StandbyClass(timeout=10)
    monitor.run()