"""Unit tests for the exercise detectors, form rules and progress stats.

They use synthetic (made-up) pose landmarks, so no camera or video is needed.
Run from the "Main App" folder:  python -m unittest discover tests -v
"""
import math
import unittest
from datetime import date
from types import SimpleNamespace

import pandas as pd

from detectors.squat import SquatDetector
from detectors.plank import PlankDetector
from detectors.jumping_jacks import JumpingJacksDetector
from detectors.situps import SitUpsDetector
from detectors.pushup import PushUpDetector
from services.coaching.form_rules import find_form_issue
from services.tracking.progress_stats import compute_streak, summary_stats, issues_per_10_reps, top_issues


def make_landmarks(points, visibility=0.99):
    """33 MediaPipe-style landmarks; unspecified points sit at the centre."""
    lms = [SimpleNamespace(x=0.5, y=0.5, visibility=visibility) for _ in range(33)]
    for idx, (x, y) in points.items():
        lms[idx] = SimpleNamespace(x=x, y=y, visibility=visibility)
    return lms


# ---------- Squat (side view) ----------

def squat_pose(knee_angle, torso_lean=0):
    ankle = (0.5, 0.9)
    knee = (0.5, 0.7)
    t = math.radians(knee_angle)
    hip = (knee[0] + 0.2 * math.sin(t), knee[1] + 0.2 * math.cos(t))
    lean = math.radians(torso_lean)
    shoulder = (hip[0] - 0.25 * math.sin(lean), hip[1] - 0.25 * math.cos(lean))
    pts = {}
    for s, h, k, a in [(11, 23, 25, 27), (12, 24, 26, 28)]:
        pts.update({s: shoulder, h: hip, k: knee, a: ankle})
    return make_landmarks(pts)


class SquatTests(unittest.TestCase):
    def run_angles(self, det, angles, lean=0):
        return [det.process(squat_pose(a, lean)) for a in angles]

    def test_full_rep_counts_and_no_false_too_high(self):
        det = SquatDetector()
        out = self.run_angles(det, [170, 140, 120, 90, 120, 150, 170])
        self.assertEqual(out[-1]["reps"], 1)
        # While standing back up from a deep squat it must not say TOO HIGH
        for m in out[3:]:
            self.assertNotEqual(m["depth_status"], "TOO HIGH")
            self.assertIsNone(find_form_issue("Squats", m))

    def test_shallow_rep_flagged_not_counted(self):
        det = SquatDetector()
        out = self.run_angles(det, [170, 130, 120, 130, 170])
        self.assertEqual(out[-1]["reps"], 0)
        self.assertEqual(out[-1]["depth_status"], "TOO HIGH")
        self.assertIn("not deep enough", find_form_issue("Squats", out[-1]))

    def test_going_down_is_not_an_issue(self):
        det = SquatDetector()
        out = self.run_angles(det, [170, 130])
        self.assertEqual(out[-1]["depth_status"], "GOING DOWN")
        self.assertIsNone(find_form_issue("Squats", out[-1]))

    def test_torso_lean(self):
        det = SquatDetector()
        ok = det.process(squat_pose(90, torso_lean=35))
        bad = det.process(squat_pose(90, torso_lean=65))
        self.assertIsNone(find_form_issue("Squats", ok))
        self.assertIn("leaning too far forward", find_form_issue("Squats", bad))


# ---------- Plank (side view) ----------

def plank_pose(hip_offset=0.0):
    shoulder, ankle = (0.3, 0.5), (0.8, 0.55)
    hip = (0.55, 0.525 + hip_offset)   # y grows downwards: + means sagging
    pts = {}
    for s, h, a in [(11, 23, 27), (12, 24, 28)]:
        pts.update({s: shoulder, h: hip, a: ankle})
    return make_landmarks(pts)


class PlankTests(unittest.TestCase):
    def test_good_plank_accumulates_time(self):
        det = PlankDetector()
        for i in range(31):   # 3 seconds at 10 fps
            m = det.process(plank_pose(), timestamp_s=i * 0.1)
        self.assertEqual(m["hip_status"], "LEVEL")
        self.assertEqual(m["reps"], 3)
        self.assertIsNone(find_form_issue("Plank", m))

    def test_sagging_hips_do_not_count(self):
        det = PlankDetector()
        for i in range(31):
            m = det.process(plank_pose(hip_offset=0.12), timestamp_s=i * 0.1)
        self.assertEqual(m["hip_status"], "SAGGING")
        self.assertEqual(m["reps"], 0)
        self.assertIn("sagging", find_form_issue("Plank", m))

    def test_piked_hips(self):
        m = PlankDetector().process(plank_pose(hip_offset=-0.12), timestamp_s=0)
        self.assertEqual(m["hip_status"], "PIKED UP")

    def test_standing_is_not_a_plank(self):
        pts = {11: (0.5, 0.2), 12: (0.5, 0.2), 23: (0.5, 0.5), 24: (0.5, 0.5), 27: (0.5, 0.9), 28: (0.5, 0.9)}
        m = PlankDetector().process(make_landmarks(pts), timestamp_s=0)
        self.assertEqual(m["plank_status"], "NOT IN POSITION")


# ---------- Jumping jacks (front view) ----------

def jack_pose(arms_up, legs_wide):
    pts = {0: (0.5, 0.15), 11: (0.42, 0.25), 12: (0.58, 0.25), 23: (0.45, 0.55), 24: (0.55, 0.55)}
    if arms_up:
        pts.update({15: (0.45, 0.05), 16: (0.55, 0.05)})
    else:
        pts.update({15: (0.40, 0.55), 16: (0.60, 0.55)})
    if legs_wide:
        pts.update({27: (0.30, 0.9), 28: (0.70, 0.9)})
    else:
        pts.update({27: (0.46, 0.9), 28: (0.54, 0.9)})
    return make_landmarks(pts)


class JumpingJackTests(unittest.TestCase):
    def test_full_jacks_count(self):
        det = JumpingJacksDetector()
        for _ in range(3):
            det.process(jack_pose(False, False))
            det.process(jack_pose(True, True))
            m = det.process(jack_pose(False, False))
        self.assertEqual(m["reps"], 3)
        self.assertEqual(m["rep_quality"], "GOOD")

    def test_arms_too_low(self):
        det = JumpingJacksDetector()
        det.process(jack_pose(False, False))
        det.process(jack_pose(False, True))
        m = det.process(jack_pose(False, False))
        self.assertEqual(m["reps"], 0)
        self.assertEqual(m["rep_quality"], "ARMS TOO LOW")
        self.assertIn("arms", find_form_issue("Jumping Jacks", m))


# ---------- Sit-ups (side view) ----------

def situp_pose(hip_angle, knee_angle=90):
    hip = (0.5, 0.8)
    thigh = math.radians(-45)
    knee = (hip[0] + 0.2 * math.cos(thigh), hip[1] + 0.2 * math.sin(thigh))
    torso = thigh - math.radians(hip_angle)
    shoulder = (hip[0] + 0.25 * math.cos(torso), hip[1] + 0.25 * math.sin(torso))
    shin = thigh + math.pi - math.radians(knee_angle)
    ankle = (knee[0] + 0.2 * math.cos(shin), knee[1] + 0.2 * math.sin(shin))
    pts = {}
    for s, h, k, a in [(11, 23, 25, 27), (12, 24, 26, 28)]:
        pts.update({s: shoulder, h: hip, k: knee, a: ankle})
    return make_landmarks(pts)


class SitUpTests(unittest.TestCase):
    def test_full_situp_counts(self):
        det = SitUpsDetector()
        for a in [130, 100, 80, 60, 90, 130]:
            m = det.process(situp_pose(a))
        self.assertEqual(m["reps"], 1)
        self.assertIsNone(find_form_issue("Sit-ups", m))

    def test_partial_situp_flagged(self):
        det = SitUpsDetector()
        for a in [130, 95, 85, 130]:
            m = det.process(situp_pose(a))
        self.assertEqual(m["reps"], 0)
        self.assertEqual(m["rep_quality"], "NOT HIGH ENOUGH")

    def test_straight_legs_flagged(self):
        m = SitUpsDetector().process(situp_pose(130, knee_angle=170))
        self.assertEqual(m["knee_status"], "LEGS TOO STRAIGHT")
        self.assertIn("legs are too straight", find_form_issue("Sit-ups", m))


# ---------- Push-ups (side view) ----------

def pushup_pose(elbow_angle, hip_offset=0.0):
    shoulder, ankle = (0.3, 0.45), (0.85, 0.6)
    elbow = (0.3, 0.6)                         # upper arm points straight down
    t = math.radians(elbow_angle)
    wrist = (elbow[0] + 0.15 * math.sin(t), elbow[1] - 0.15 * math.cos(t))
    hip_x = 0.5
    hip_y = shoulder[1] + (hip_x - shoulder[0]) * (ankle[1] - shoulder[1]) / (ankle[0] - shoulder[0]) + hip_offset
    pts = {}
    for s, e, w, h, a in [(11, 13, 15, 23, 27), (12, 14, 16, 24, 28)]:
        pts.update({s: shoulder, e: elbow, w: wrist, h: (hip_x, hip_y), a: ankle})
    return make_landmarks(pts)


class PushUpTests(unittest.TestCase):
    def test_real_world_depth_counts(self):
        # Bottoms around 95-105°, like real push-ups in recorded videos
        det = PushUpDetector()
        for bottom in [100, 95, 105]:
            det.process(pushup_pose(175))
            det.process(pushup_pose(bottom))
            m = det.process(pushup_pose(175))
        self.assertEqual(m["reps"], 3)

    def test_straight_body_is_level_and_sag_detected(self):
        det = PushUpDetector()
        self.assertEqual(det.process(pushup_pose(175))["hip_status"], "LEVEL")
        self.assertEqual(det.process(pushup_pose(175, hip_offset=0.12))["hip_status"], "SAGGING")


# ---------- Progress stats ----------

class ProgressStatsTests(unittest.TestCase):
    def test_streak(self):
        today = date(2026, 9, 25)
        days = [date(2026, 9, 25), date(2026, 9, 24), date(2026, 9, 23), date(2026, 9, 20)]
        self.assertEqual(compute_streak(days, today), 3)
        self.assertEqual(compute_streak([date(2026, 9, 24)], today), 1)   # yesterday still counts
        self.assertEqual(compute_streak([date(2026, 9, 22)], today), 0)

    def test_summary_and_issue_rate(self):
        d = date(2026, 9, 25)
        ex = pd.DataFrame([
            {"Exercise": "Squats", "Reps": 20, "Sets": 2, "Time (sec)": 120, "Date": d},
            {"Exercise": "Plank", "Reps": 45, "Sets": 1, "Time (sec)": 60, "Date": d},
        ])
        issues = pd.DataFrame([
            {"Exercise": "Squats", "Issue": "too high", "Count": 4, "Source": "live", "Date": d},
            {"Exercise": "Plank", "Issue": "sagging", "Count": 2, "Source": "live", "Date": d},
        ])
        stats = summary_stats(ex, today=d)
        self.assertEqual(stats["total_reps"], 20)
        self.assertEqual(stats["plank_seconds"], 45)
        self.assertEqual(stats["total_minutes"], 3)
        self.assertEqual(issues_per_10_reps(ex, issues).iloc[0, 0], 2.0)
        self.assertEqual(top_issues(issues).iloc[0]["Issue"], "too high")


if __name__ == "__main__":
    unittest.main()
