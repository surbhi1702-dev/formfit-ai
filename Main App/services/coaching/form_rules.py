"""Form-issue rules shared by the live camera, the voice coach and video analysis.

Each rule looks at the metrics a detector returns and, if something is wrong,
returns a short description of the problem (sent to the AI coach and saved to
the form-issue log). Returns None when the form looks fine.
"""

SQUAT_MAX_TORSO_LEAN = 55   # degrees from vertical; some forward lean is normal in a squat


def find_form_issue(exercise, metrics):
    if not metrics:
        return None

    if "issue" in metrics:
        return metrics["issue"]

    if exercise == "Squats":
        if metrics.get("depth_status") == "TOO HIGH":
            return "The user's squat is not deep enough — knees are not bending sufficiently."

        torso_lean = metrics.get("torso_lean")
        if isinstance(torso_lean, (int, float)) and torso_lean > SQUAT_MAX_TORSO_LEAN:
            return "The user is leaning too far forward during the squat."

    elif exercise == "Push-ups":
        alignment = metrics.get("body_alignment", "")
        hip_status = metrics.get("hip_status", "")

        if alignment == "Poor Form":
            return "The user's body is not straight during the push-up."

        if hip_status == "SAGGING":
            return "The user's hips are sagging down during the push-up."

        if hip_status == "PIKED UP":
            return "The user's hips are too high — lower them to form a straight line."

    elif exercise == "Biceps Curls (Dumbbell)":
        if metrics.get("swing_status") == "SWINGING":
            return "The user is swinging their torso during the curl — keep the body still."

        if metrics.get("shoulder_status") == "ELBOW DRIFTING":
            return "The user's elbow is drifting away from their side during the curl."

    elif exercise == "Shoulder Press":
        back_arch = metrics.get("back_arch_status", "")

        if back_arch == "Excessive Arch":
            return "The user is arching their lower back excessively during the press."

        if back_arch == "Slight Arch":
            return "Slight back arch detected — encourage the user to brace their core."

    elif exercise == "Lunges":
        if metrics.get("balance_status") == "OFF BALANCE":
            return "The user is losing balance during the lunge — feet should be hip-width apart."

    elif exercise == "Plank":
        hip_status = metrics.get("hip_status", "")

        if hip_status == "SAGGING":
            return "The user's hips are sagging during the plank — tighten the core and glutes."

        if hip_status == "PIKED UP":
            return "The user's hips are too high in the plank — lower them into a straight line."

    elif exercise == "Jumping Jacks":
        quality = metrics.get("rep_quality", "")

        if quality == "ARMS TOO LOW":
            return "The user's arms are not reaching overhead during the jumping jacks."

        if quality == "LEGS TOO NARROW":
            return "The user's feet are not jumping wide enough during the jumping jacks."

    elif exercise == "Sit-ups":
        if metrics.get("knee_status") == "LEGS TOO STRAIGHT":
            return "The user's legs are too straight during sit-ups — keep the knees bent to protect the lower back."

        if metrics.get("rep_quality") == "NOT HIGH ENOUGH":
            return "The user is not curling up high enough on the sit-up."

    return None
