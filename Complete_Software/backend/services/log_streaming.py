from flask_socketio import emit
from datetime import datetime
import queue
import threading

class LogStreamingService:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.clients = set()
        self._start_streaming()

    def _start_streaming(self):
        def stream_logs():
            while True:
                try:
                    log_entry = self.log_queue.get()
                    self._broadcast_log(log_entry)
                except Exception as e:
                    print(f"Error in log streaming: {e}")

        thread = threading.Thread(target=stream_logs, daemon=True)
        thread.start()

    def add_log(self, log_entry):
        self.log_queue.put({
            **log_entry,
            'timestamp': datetime.utcnow().isoformat()
        })

    def _broadcast_log(self, log_entry):
        emit('new_log', log_entry, namespace='/logs', broadcast=True)

    def register_client(self, client_id):
        self.clients.add(client_id)

    def remove_client(self, client_id):
        self.clients.discard(client_id)

log_streaming_service = LogStreamingService() 