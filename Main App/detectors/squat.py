import math
from core.base_exercise import BaseExercise


class SquatDetector(BaseExercise):
    DOWN_THRESHOLD = 100      # knee angle that counts as full depth
    UP_THRESHOLD = 160        # knee angle that counts as standing
    DESCENT_THRESHOLD = 150   # knee angle below which a squat attempt has started
    MIN_VISIBILITY = 0.7

    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27
    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    def __init__(self):
        super().__init__()
        self._descent_min_angle = None   # lowest knee angle in the current attempt
        self._last_rep_depth = None      # result of the last finished attempt

    def reset(self):
        self.reps = 0
        self.stage = None
        self._descent_min_angle = None
        self._last_rep_depth = None

    def process(self, landmarks):
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE)
        )

        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE)
        )

        left_vis = landmarks[self.LEFT_KNEE].visibility
        right_vis = landmarks[self.RIGHT_KNEE].visibility

        if left_vis >= right_vis:
            knee_angle = left_knee_angle
            hip_idx, knee_idx, ankle_idx, shoulder_idx = self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE, self.LEFT_SHOULDER
        else:
            knee_angle = right_knee_angle
            hip_idx, knee_idx, ankle_idx, shoulder_idx = self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE, self.RIGHT_SHOULDER

        back_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx)
        )

        # Torso lean measured from vertical (0° = upright). Unlike the hip angle,
        # this doesn't shrink just because the user squats deeper.
        dx = landmarks[shoulder_idx].x - landmarks[hip_idx].x
        dy = landmarks[shoulder_idx].y - landmarks[hip_idx].y
        torso_lean = math.degrees(math.atan2(abs(dx), abs(dy))) if (dx or dy) else 0.0

        key_landmark_visible = landmarks[hip_idx].visibility >= self.MIN_VISIBILITY and landmarks[knee_idx].visibility >= self.MIN_VISIBILITY and landmarks[ankle_idx].visibility >= self.MIN_VISIBILITY

        if key_landmark_visible:
            if knee_angle < self.DESCENT_THRESHOLD:
                if self._descent_min_angle is None or knee_angle < self._descent_min_angle:
                    self._descent_min_angle = knee_angle

            if knee_angle < self.DOWN_THRESHOLD:
                self.stage = "down"

            if knee_angle >= self.UP_THRESHOLD:
                if self.stage == "down":
                    self.stage = "up"
                    self.reps += 1
                    self._last_rep_depth = "GOOD DEPTH"
                elif self._descent_min_angle is not None:
                    # Went down part of the way and stood back up: shallow, not counted
                    self._last_rep_depth = "TOO HIGH"

                self._descent_min_angle = None

        # "TOO HIGH" is only reported after a shallow attempt is finished,
        # never while the user is still going down or coming up from a good rep.
        if self.stage == "down":
            depth_status = "GOOD DEPTH"
        elif self._descent_min_angle is not None:
            depth_status = "GOING DOWN"
        elif self._last_rep_depth:
            depth_status = self._last_rep_depth
        elif self.stage == "up":
            depth_status = "STANDING"
        else:
            depth_status = "N/A"

        return {
            "reps": self.reps,
            "knee_angle": int(knee_angle),
            "back_angle": int(back_angle),
            "torso_lean": int(torso_lean),
            "depth_status": depth_status
        }
