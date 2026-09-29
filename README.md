# FormFit AI — Real-Time Exercise Form Analysis

FormFit AI watches you exercise through your webcam (or a recorded video), counts your reps, checks your form using pose estimation, and coaches you by voice with an AI trainer. It tracks your workouts and form mistakes over time so you can see your technique improve.

## Features

- **Live form analysis** — real-time pose detection in the browser with MediaPipe, with a skeleton overlay and live metrics
- **8 exercises** — Squats, Push-ups, Biceps Curls, Shoulder Press, Lunges, Plank, Jumping Jacks, Sit-ups
- **Video upload analysis** — analyse a recorded workout without a camera: rep count, joint-angle chart, rep timestamps and snapshots of each form issue
- **AI voice coach** — short spoken feedback from an LLM (Groq) at the start, after each set, and when a form issue is detected
- **Progress dashboard** — reps per day, workout streak, total time, most common form mistakes, and a "form issues per 10 reps" trend
- **Workout history** — every workout and form issue is saved per user in SQLite

## Engineering highlights

- **Rep counting as small state machines** — each detector tracks joint angles across frames and only counts a rep after a full range of motion (e.g. a squat attempt is judged by its lowest knee angle, so feedback is never given mid-rep).
- **Time-based exercises** — the plank detector measures seconds held in good form, using video time in recorded clips and wall-clock time in live mode.
- **Shared form-rule engine** — one module turns detector metrics into form issues; it is reused by the live voice coach, video analysis and the issue log.
- **Debounced issue logging** — an issue must persist (≥1 s live, ≥3 frames in video) before it is recorded, so detection flicker doesn't inflate counts.
- **Resilient AI coaching** — LLM and text-to-speech failures are caught and logged so a network problem never interrupts a workout; the model is configurable via `GROQ_MODEL`.
- **Tested without a camera** — unit tests feed synthetic pose landmarks into the squat, plank, jumping-jack and sit-up detectors, the form rules and the progress calculations.

## Tech stack

Python · Streamlit · streamlit-webrtc · MediaPipe Pose Landmarker · OpenCV · Groq LLM API · gTTS · SQLite · pandas

## How it works

1. Each video frame goes through MediaPipe's pose landmarker, which returns 33 body keypoints.
2. An exercise detector computes joint angles (e.g. knee angle for squats) and runs a small state machine to count reps and judge each rep.
3. Shared form rules turn detector metrics into issues such as "hips sagging".
4. Issues are logged to SQLite and sent to the LLM, whose short reply is spoken with gTTS.

## Setup

```bash
git clone https://github.com/surbhi1702-dev/formfit-ai.git
cd formfit-ai
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
cd "Main App"
pip install -r requirements.txt
```

Create `Main App/.env`:

```
GROQ_API_KEY=your_groq_api_key      # free key from console.groq.com
GROQ_MODEL=openai/gpt-oss-120b
```

Run:

```bash
streamlit run main.py
```

Run the tests (from `Main App`):

```bash
python -m unittest discover tests -v
```

## Tips for accurate tracking

- Keep your full body in frame, with one person visible.
- Use a **side view** for squats, push-ups, lunges, plank and sit-ups, and a **front view** for jumping jacks, curls and shoulder press.
- Good, even lighting helps a lot.

## Project structure

```
Main App/
├── main.py                     # Streamlit app: modes, live workout, sidebar
├── core/base_exercise.py       # Base class with angle helpers
├── detectors/                  # One detector per exercise
├── services/
│   ├── coaching/               # LLM coach, text-to-speech, voice pipeline, form rules
│   ├── vision/                 # Live video processor and video file analyzer
│   ├── tracking/               # Metric syncing, form-issue logging, progress stats
│   ├── persistence/            # SQLite repository
│   └── ui/                     # Theme, video upload and progress pages, styling
└── tests/                      # Unit tests with synthetic pose data
```
