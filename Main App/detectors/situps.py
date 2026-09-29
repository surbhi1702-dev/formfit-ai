from core.base_exercise import BaseExercise


class SitUpsDetector(BaseExercise):
    """Side view. Uses the shoulder-hip-knee angle: large when lying back, small when sitting up."""

    UP_THRESHOLD = 70         # hip angle when curled up
    DOWN_THRESHOLD = 115      # hip angle when lying back
    ATTEMPT_THRESHOLD = 100   # hip angle below which a sit-up attempt has started
    STRAIGHT_KNEE = 140       # knee angle above this means the legs are too straight
    MIN_VISIBILITY = 0.6

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()
        self._attempt_started = False
        self._last_rep_quality = None

    def reset(self):
        self.reps = 0
        self.stage = None
        self._attempt_started = False
        self._last_rep_quality = None

    def process(self, landmarks):
        if landmarks[self.LEFT_HIP].visibility >= landmarks[self.RIGHT_HIP].visibility:
            s, h, k, a = self.LEFT_SHOULDER, self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE
        else:
            s, h, k, a = self.RIGHT_SHOULDER, self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE

        hip_angle = self.calculate_angle(self.get_point(landmarks, s), self.get_point(landmarks, h), self.get_point(landmarks, k))
        knee_angle = self.calculate_angle(self.get_point(landmarks, h), self.get_point(landmarks, k), self.get_point(landmarks, a))

        visible = min(landmarks[s].visibility, landmarks[h].visibility, landmarks[k].visibility) >= self.MIN_VISIBILITY

        if visible:
            if hip_angle < self.ATTEMPT_THRESHOLD:
                self._attempt_started = True

            if hip_angle < self.UP_THRESHOLD:
                self.stage = "up"

            if hip_angle > self.DOWN_THRESHOLD:
                if self.stage == "up":
                    self.reps += 1
                    self._last_rep_quality = "GOOD"
                elif self._attempt_started:
                    self._last_rep_quality = "NOT HIGH ENOUGH"

                self.stage = "down"
                self._attempt_started = False

        if self.stage == "up":
            rep_quality = "GOOD"
        elif self._attempt_started:
            rep_quality = "CURLING UP"
        else:
            rep_quality = self._last_rep_quality or "READY"

        knee_status = "LEGS TOO STRAIGHT" if knee_angle > self.STRAIGHT_KNEE else "KNEES BENT"

        return {
            "reps": self.reps,
            "hip_angle": int(hip_angle),
            "knee_status": knee_status,
            "rep_quality": rep_quality,
        }
