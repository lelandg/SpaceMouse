import threading
import time
from queue import Queue

import space_mouse_event_handler
# from space_mouse_event_handler import SpaceMouseEventHandler


def move_object(pan_x: int, pan_y: int, zoom_factor: int) -> None:

    print(f"Moving object: pan_x={pan_x}, pan_y={pan_y}, zoom_factor={zoom_factor}")
    pass


def rotate_object(rot_amount: int, counter_clockwise: bool) -> None:
    print(f"Rotating object: rot_amount={rot_amount}, counter_clockwise={counter_clockwise}")
    pass


class SpaceMouseController:
    def __init__(self):
        """
        Initializes the SpaceMouseController with a provided 3D viewport instance.
        """
        self.running = False  # Flag to control the thread
        self.event_queue = Queue()
        self.handler = space_mouse_event_handler.SpaceMouseEventHandler()

    def _poll_and_process(self):
        while self.running:
            data = self.poll_input()
            if data:
                self.event_queue.put(data)  # Add data to queue
            time.sleep(0.05)

    def next_event(self):
        """
        Returns the next event from the event queue.
        :return: The next event from the queue.
        """
        return self.event_queue.get()

    def process_events(self):
        # Process all pending events in a thread-safe manner
        while not self.event_queue.empty():
            data = self.event_queue.get()
            self.process_input(data)
            self.event_queue.task_done()

    def poll_input(self):
        """
        Polls the space mouse for input. This method will simulate obtaining
        movement and rotation data from the space mouse.
        :return: Example data dictionary containing x, y, z, and rot directions.
        """
        self.handler.handle_event()
        data = self.handler.get_next_event()
        if data:
            self.process_input(data)

    def process_input(self, data):
        """
        Processes the space mouse data to move/rotate the object in the viewport.
        Parameters:
            data: A dictionary containing parsed information from the HID device,
            including time, position, button states, and other data fields extracted
            from the device report. Keys in the dictionary correspond to specific
            data fields, such as `t` for type of data, `x` for X-axis position, `y` for Y-axis, z for Z-axis
            and so on. rot is rotation, cc = counter-clockwise.
            p is up/down movement (0-255) and ya is direction. 255 when the device is moved up, 0 = down.
            f = 255 = direction of x & y-axis.
                for x: 0 =  left, 255 = right
                for y: 0 =  up, 255 = down
            r = direction of z:
                for z: 0 = back (toward user), 255 = forward (away from user)
            t =
                1 = move
                3 = button press
        """
        # Lazy import to avoid circular dependency

        if data["t"] == space_mouse_event_handler.SMP_MOVE_CHANNEL:
            pan_x = data["x"]
            pan_y = data["y"]
            zoom_factor = data["z"]
            # Move the object in the 3D viewport. Example methods:
            move_object(pan_x, pan_y, zoom_factor)

            rot_amount = data["rot"]
            counter_clockwise = data["cc"] == 255
            rotate_object(rot_amount, counter_clockwise)
        elif data["t"] == space_mouse_event_handler.SMP_BUTTON_CHANNEL:
            # TODO: Handle button press events
            pass
        elif data["t"] == space_mouse_event_handler.SMP_ROTATE_CHANNEL:
            # TODO: Determine what to do.
            #  Potentially rotate the object in the 3D viewport?
            pass

    def run(self):
        """
        Starts the controller in a separate thread.
        """
        self.running = True
        self.thread = threading.Thread(target=self._poll_and_process)
        self.handler.start_polling()
        self.thread.start()

    def stop(self):
        """
        Stops the controller and joins the thread.
        """
        self.running = False
        self.handler.stop_polling()
        if self.thread.is_alive():
            self.thread.join()


# Example usage
if __name__ == "__main__":
    # Lazy import to avoid circular dependency at the top level


    controller = SpaceMouseController()
    try:
        controller.run()
        while True:  # Keep the main program running
            time.sleep(1)
        data = controller.next_event()
    except KeyboardInterrupt:
        controller.stop()
        print("Space mouse event handler stopped.")
