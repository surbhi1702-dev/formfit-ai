import os
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from detectors.squat import SquatDetector
from detectors.pushup import PushUpDetector
from detectors.biceps_curl import BicepsCurlDetector
from detectors.shoulder_press import ShoulderPressDetector
from detectors.lunges import LungesDetector
from detectors.plank import PlankDetector
from detectors.jumping_jacks import JumpingJacksDetector
from detectors.situps import SitUpsDetector
from services.config.workout_config import POSE_CONNECTIONS, TIME_BASED_EXERCISES
from services.coaching.form_rules import find_form_issue


DETECTOR_CLASSES = {
    "Squats": SquatDetector,
    "Push-ups": PushUpDetector,
    "Biceps Curls (Dumbbell)": BicepsCurlDetector,
    "Shoulder Press": ShoulderPressDetector,
    "Lunges": LungesDetector,
    "Plank": PlankDetector,
    "Jumping Jacks": JumpingJacksDetector,
    "Sit-ups": SitUpsDetector,
}

# The main joint angle to plot for each exercise
PRIMARY_ANGLE = {
    "Squats": ("knee_angle", "Knee angle (°)"),
    "Push-ups": ("elbow_angle", "Elbow angle (°)"),
    "Biceps Curls (Dumbbell)": ("elbow_angle", "Elbow angle (°)"),
    "Shoulder Press": ("elbow_angle", "Elbow angle (°)"),
    "Lunges": ("front_knee_angle", "Front knee angle (°)"),
    "Plank": ("body_angle", "Body line angle (°)"),
    "Jumping Jacks": ("arm_angle", "Arm raise angle (°)"),
    "Sit-ups": ("hip_angle", "Hip angle (°)"),
}

TARGET_FPS = 15          # analyse ~15 frames per second, enough for rep counting
MAX_FRAME_WIDTH = 960    # downscale large videos to keep analysis fast
MIN_ISSUE_FRAMES = 3     # an issue must last this many analysed frames to be counted


def _create_landmarker():
    model_path = os.path.join(os.getcwd(), "ml_models", "pose_landmarker_full.task")

    options = vision.PoseLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=model_path),
        running_mode=vision.RunningMode.VIDEO,
        min_pose_detection_confidence=0.7,
        min_pose_presence_confidence=0.7,
        min_tracking_confidence=0.7,
        output_segmentation_masks=False,
    )

    return vision.PoseLandmarker.create_from_options(options)


def _draw_skeleton(img, landmarks):
    h, w = img.shape[:2]

    for start_idx, end_idx in POSE_CONNECTIONS:
        p1, p2 = landmarks[start_idx], landmarks[end_idx]

        if p1.visibility > 0.7 and p2.visibility > 0.7:
            cv2.line(img, (int(p1.x * w), int(p1.y * h)), (int(p2.x * w), int(p2.y * h)), (0, 255, 0), 4)

    for lm in landmarks:
        if lm.visibility > 0.7:
            cv2.circle(img, (int(lm.x * w), int(lm.y * h)), 5, (255, 0, 0), -1)


def analyze_video(video_path, exercise, progress_callback=None):
    """Run a recorded video through the same pose detection and exercise
    detectors used by the live camera, and return a summary of the workout."""

    if exercise not in DETECTOR_CLASSES:
        raise ValueError(f"Unsupported exercise: {exercise}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Could not open the video file.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0 or fps > 240:
        fps = 30.0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    step = max(1, round(fps / TARGET_FPS))

    detector = DETECTOR_CLASSES[exercise]()
    time_based = exercise in TIME_BASED_EXERCISES
    angle_key, angle_label = PRIMARY_ANGLE[exercise]

    angle_series = []
    rep_times = []
    issue_counts = {}
    issue_snapshots = {}

    frames_analysed = 0
    pose_frames = 0
    last_reps = 0
    pending_issue = None
    issue_streak = 0
    frame_idx = 0

    try:
        with _create_landmarker() as landmarker:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break

                if frame_idx % step != 0:
                    frame_idx += 1
                    continue

                h, w = frame.shape[:2]
                if w > MAX_FRAME_WIDTH:
                    scale = MAX_FRAME_WIDTH / w
                    frame = cv2.resize(frame, (MAX_FRAME_WIDTH, int(h * scale)))

                timestamp_ms = int(frame_idx * 1000 / fps)
                t = timestamp_ms / 1000

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = landmarker.detect_for_video(
                    mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp_ms
                )
                frames_analysed += 1

                if result.pose_landmarks:
                    landmarks = result.pose_landmarks[0]
                    pose_frames += 1

                    if time_based:
                        # Use video time, not wall-clock time, so the hold is measured correctly
                        metrics = detector.process(landmarks, timestamp_s=t)
                    else:
                        metrics = detector.process(landmarks)

                    angle_series.append({"Time (s)": round(t, 2), angle_label: metrics.get(angle_key, 0)})

                    if metrics["reps"] > last_reps:
                        if not time_based:
                            rep_times.append(round(t, 1))
                        last_reps = metrics["reps"]

                    # Count an issue once per continuous episode, ignoring one-frame flickers
                    issue = find_form_issue(exercise, metrics)

                    if issue == pending_issue:
                        issue_streak += 1
                    else:
                        pending_issue = issue
                        issue_streak = 1

                    if issue and issue_streak == MIN_ISSUE_FRAMES:
                        issue_counts[issue] = issue_counts.get(issue, 0) + 1

                        if issue not in issue_snapshots:
                            annotated = frame.copy()
                            _draw_skeleton(annotated, landmarks)
                            issue_snapshots[issue] = (round(t, 1), cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
                else:
                    pending_issue = None
                    issue_streak = 0

                if progress_callback and total_frames:
                    progress_callback(min(frame_idx / total_frames, 1.0))

                frame_idx += 1
    finally:
        cap.release()

    return {
        "exercise": exercise,
        "time_based": time_based,
        "reps": last_reps,
        "rep_times": rep_times,
        "duration": frame_idx / fps,
        "frames_analysed": frames_analysed,
        "pose_frames": pose_frames,
        "angle_label": angle_label,
        "angle_series": angle_series,
        "issue_counts": issue_counts,
        "issue_snapshots": issue_snapshots,
    }
