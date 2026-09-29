from core.base_exercise import BaseExercise


class JumpingJacksDetector(BaseExercise):
    """Front view. A rep = arms go overhead and feet jump wide, then both return."""

    MIN_VISIBILITY = 0.6
    WIDE_RATIO = 1.5      # ankle gap / shoulder width that counts as "feet wide"
    CLOSED_RATIO = 1.1    # ankle gap / shoulder width that counts as "feet together"

    NOSE = 0
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()
        self._saw_arms_up = False
        self._saw_legs_wide = False
        self._last_rep_quality = None

    def reset(self):
        self.reps = 0
        self.stage = None
        self._saw_arms_up = False
        self._saw_legs_wide = False
        self._last_rep_quality = None

    def process(self, landmarks):
        ls, rs = landmarks[self.LEFT_SHOULDER], landmarks[self.RIGHT_SHOULDER]
        lw, rw = landmarks[self.LEFT_WRIST], landmarks[self.RIGHT_WRIST]
        la, ra = landmarks[self.LEFT_ANKLE], landmarks[self.RIGHT_ANKLE]
        nose = landmarks[self.NOSE]

        arm_angle = (
            self.calculate_angle(self.get_point(landmarks, self.LEFT_HIP), self.get_point(landmarks, self.LEFT_SHOULDER), self.get_point(landmarks, self.LEFT_WRIST))
            + self.calculate_angle(self.get_point(landmarks, self.RIGHT_HIP), self.get_point(landmarks, self.RIGHT_SHOULDER), self.get_point(landmarks, self.RIGHT_WRIST))
        ) / 2

        shoulder_width = abs(ls.x - rs.x)
        ankle_gap = abs(la.x - ra.x)
        visible = min(ls.visibility, rs.visibility, lw.visibility, rw.visibility, la.visibility, ra.visibility) >= self.MIN_VISIBILITY

        # y grows downwards: "above" means a smaller y
        arms_up = lw.y < nose.y and rw.y < nose.y
        arms_down = lw.y > ls.y and rw.y > rs.y

        if shoulder_width > 0.02:
            ratio = ankle_gap / shoulder_width
            legs_wide = ratio >= self.WIDE_RATIO
            legs_closed = ratio <= self.CLOSED_RATIO
        else:
            legs_wide = legs_closed = False

        if visible:
            if arms_up:
                self._saw_arms_up = True
            if legs_wide:
                self._saw_legs_wide = True

            if arms_down and legs_closed:
                if self._saw_arms_up and self._saw_legs_wide:
                    self.reps += 1
                    self._last_rep_quality = "GOOD"
                elif self._saw_legs_wide:
                    self._last_rep_quality = "ARMS TOO LOW"
                elif self._saw_arms_up:
                    self._last_rep_quality = "LEGS TOO NARROW"

                self._saw_arms_up = False
                self._saw_legs_wide = False
                self.stage = "closed"
            elif self._saw_arms_up or self._saw_legs_wide:
                self.stage = "open"

        if self._saw_arms_up or self._saw_legs_wide:
            rep_quality = "IN MOTION"
        else:
            rep_quality = self._last_rep_quality or "READY"

        return {
            "reps": self.reps,
            "arm_angle": int(arm_angle),
            "arm_status": "UP" if arms_up else ("DOWN" if arms_down else "MID"),
            "leg_status": "WIDE" if legs_wide else ("CLOSED" if legs_closed else "MID"),
            "rep_quality": rep_quality,
        }
