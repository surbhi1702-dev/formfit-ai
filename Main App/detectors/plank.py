import math
import time
from core.base_exercise import BaseExercise


class PlankDetector(BaseExercise):
    """Time-based exercise: 'reps' are seconds held in good form."""

    MIN_VISIBILITY = 0.6
    MAX_BODY_TILT = 35          # degrees from horizontal for shoulder-to-ankle line
    HIP_SAG_TOLERANCE = 0.05    # allowed hip offset from the shoulder-ankle line (normalized)
    MAX_FRAME_GAP = 0.5         # seconds; bigger gaps (dropped frames) are not counted

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()
        self.hold_seconds = 0.0
        self._last_time = None

    def reset(self):
        self.reps = 0
        self.stage = None
        self.hold_seconds = 0.0
        self._last_time = None

    def process(self, landmarks, timestamp_s=None):
        now = time.monotonic() if timestamp_s is None else timestamp_s
        dt = 0.0 if self._last_time is None else now - self._last_time
        self._last_time = now

        if landmarks[self.LEFT_HIP].visibility >= landmarks[self.RIGHT_HIP].visibility:
            shoulder_idx, hip_idx, ankle_idx = self.LEFT_SHOULDER, self.LEFT_HIP, self.LEFT_ANKLE
        else:
            shoulder_idx, hip_idx, ankle_idx = self.RIGHT_SHOULDER, self.RIGHT_HIP, self.RIGHT_ANKLE

        shoulder, hip, ankle = landmarks[shoulder_idx], landmarks[hip_idx], landmarks[ankle_idx]

        body_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, ankle_idx),
        )

        dx = ankle.x - shoulder.x
        dy = ankle.y - shoulder.y
        body_tilt = math.degrees(math.atan2(abs(dy), abs(dx))) if (dx or dy) else 90.0

        visible = min(shoulder.visibility, hip.visibility, ankle.visibility) >= self.MIN_VISIBILITY
        in_position = visible and body_tilt <= self.MAX_BODY_TILT

        # Where the hip should be if the body were a straight line (y grows downwards)
        if abs(dx) > 1e-6:
            expected_hip_y = shoulder.y + (hip.x - shoulder.x) * dy / dx
        else:
            expected_hip_y = (shoulder.y + ankle.y) / 2
        hip_deviation = hip.y - expected_hip_y

        if not in_position:
            hip_status = "N/A"
        elif abs(hip_deviation) <= self.HIP_SAG_TOLERANCE:
            hip_status = "LEVEL"
        elif hip_deviation > 0:
            hip_status = "SAGGING"
        else:
            hip_status = "PIKED UP"

        good_form = in_position and hip_status == "LEVEL"

        if good_form and 0 < dt <= self.MAX_FRAME_GAP:
            self.hold_seconds += dt

        self.stage = "holding" if good_form else ("adjust" if in_position else None)
        self.reps = int(self.hold_seconds)

        return {
            "reps": self.reps,
            "hold_time": int(self.hold_seconds),
            "body_angle": int(body_angle),
            "hip_status": hip_status,
            "plank_status": "HOLDING" if good_form else ("FIX HIPS" if in_position else "NOT IN POSITION"),
        }
