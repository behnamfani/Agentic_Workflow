"""
Catbot welcome / splash page.

    flow:   welcome  ->  (login - later)  ->  bot selection  ->  chat
"""
import html as _html
import os
import time

import streamlit as st

# ── things you will probably want to tweak ───────────────────────────────────
LINE_1 = "Meow! Hello, human 👋"
LINE_2 = "Pick a bot. I'm totally not watching 👀"
LINE_3 = "…nap time 😴"
TITLE = "Catbot"
SUBTITLE = "Three bots. One very suspicious cat."
ENTER_LABEL = "Enter 🐾"

# Automatic Advance
AUTO_ADVANCE_SECONDS = 9.0

_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UI", "static")

# ── the cat ──────────────────────────────────────────────────────────────────
_BODY = '<path d="M 84 372 C 84 292 134 254 200 254 C 266 254 316 292 316 372 Z"/>'
_HEAD = '<ellipse cx="200" cy="170" rx="122" ry="98"/>'
_EARS = '<polygon points="86,140 96,32 180,88"/><polygon points="314,140 304,32 220,88"/>'
_SIL = _BODY + _HEAD + _EARS

_TAIL_D = "M 124 340 C 50 350 12 290 40 238 C 54 212 84 218 78 244"

_ARM_SHAPES = '<rect x="-17" y="-104" width="34" height="112" rx="17"/><circle cx="0" cy="-104" r="24"/>'
_ARM = (
    '<g transform="translate(296 306)"><g class="arm">'
    f'<g class="rim">{_ARM_SHAPES}</g><g class="fill">{_ARM_SHAPES}</g>'
    '<ellipse cx="0" cy="-96" rx="12" ry="10" fill="#f472b6"/>'
    '<circle cx="-13" cy="-116" r="5.5" fill="#f472b6"/>'
    '<circle cx="0" cy="-122" r="5.5" fill="#f472b6"/>'
    '<circle cx="13" cy="-116" r="5.5" fill="#f472b6"/>'
    '</g></g>'
)


def _eye(cx: int, cy: int = 172) -> str:
    """One big glowing eye: halo, iris, slit pupil, highlights, eyelid (for blinks)."""
    return (
            '<g class="eye"><g class="halos">'
            + "".join(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx + 4}" fill="#22c55e" opacity="{a}"/>'
        for rx, a in ((51, .03), (48.5, .035), (46, .04), (43.5, .045), (41, .05), (38.5, .055), (36, .06))
    ) +
            '</g>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="31" ry="35" fill="#15803d"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="27" ry="31" fill="#22c55e"/>'
            f'<ellipse cx="{cx}" cy="{cy + 8}" rx="19" ry="21" fill="#86efac" opacity=".55"/>'
            f'<ellipse class="pupil" cx="{cx}" cy="{cy}" rx="8" ry="27" fill="#020617"/>'
            f'<circle cx="{cx - 10}" cy="{cy - 14}" r="6.5" fill="#fff" opacity=".95"/>'
            f'<circle cx="{cx + 9}" cy="{cy + 15}" r="3.2" fill="#fff" opacity=".75"/>'
            f'<ellipse class="lid" cx="{cx}" cy="{cy}" rx="33" ry="37" fill="#05070d"/>'
            '</g>'
    )


_SVG = (
    '<svg class="cat-svg" viewBox="0 -30 400 390" role="img" '
    'aria-label="A black cat with glowing green eyes waves hello" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<g class="cat-pop"><g class="cat-tilt">'
    f'<g class="tail"><path class="t-rim" d="{_TAIL_D}"/><path class="t-fill" d="{_TAIL_D}"/></g>'
    f'<g class="rim">{_SIL}</g><g class="fill">{_SIL}</g>'
    '<polygon class="inner-ear" points="104,118 108,58 156,92"/>'
    '<polygon class="inner-ear" points="296,118 292,58 244,92"/>'
    '<g class="whisk-l"><path class="whisk" d="M 120 214 L 44 196 M 120 222 L 36 224 M 122 230 L 46 252"/></g>'
    '<g class="whisk-r"><path class="whisk" d="M 280 214 L 356 196 M 280 222 L 364 224 M 278 230 L 354 252"/></g>'
    f'{_eye(148)}{_eye(252)}'
    '<g class="tongue"><path d="M 190 224 Q 200 268 211 224 Z" fill="#fb7185"/>'
    '<path d="M 200.5 231 L 200.5 249" fill="none" stroke="#e11d48" stroke-width="2.2" stroke-linecap="round" opacity=".55"/></g>'
    '<path d="M 189 200 Q 200 194 211 200 Q 206 213 200 216 Q 194 213 189 200 Z" fill="#f472b6"/>'
    '<path class="mouth" d="M 200 216 Q 193 232 178 224 M 200 216 Q 207 232 222 224"/>'
    f'{_ARM}'
    '</g></g>'
    '<rect class="ledge" x="0" y="300" width="400" height="60" rx="10"/>'
    '<rect class="ledge-line" x="0" y="300" width="400" height="3"/>'
    '</svg>'
)


def build_html(auto: bool = True) -> str:
    """The scene as ONE line of HTML.

    One line matters: Markdown ends an HTML block at the first blank line and turns
    4-space-indented lines into code, so multi-line HTML can silently break.
    """
    esc = _html.escape
    markup = f"""
    <div class="welcome-stage" data-auto="{1 if auto else 0}">
      <div class="bubble-row">
        <div class="bubble b1">{esc(LINE_1)}</div>
        <div class="bubble b2">{esc(LINE_2)}</div>
        <div class="bubble b3">{esc(LINE_3)}</div>
      </div>
      <div class="cat-window"><div class="cat-moon"></div>{_SVG}</div>
      <div class="w-title">{esc(TITLE)}</div>
      <div class="w-sub">{esc(SUBTITLE)}</div>
    </div>
    """
    return " ".join(part.strip() for part in markup.splitlines() if part.strip())


# ── page logic ───────────────────────────────────────────────────────────────
def _inject_css(filename: str) -> None:
    path = os.path.join(_STATIC_DIR, filename)
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fh:
            st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)


def _finish() -> None:
    st.session_state.welcome_done = True


@st.fragment(run_every=0.4)
def _auto_advance() -> None:
    """Checks the clock every 0.4 s without blocking, so the Enter button stays instant."""
    started = st.session_state.get("welcome_started")
    if started is not None and time.monotonic() - started >= AUTO_ADVANCE_SECONDS:
        st.session_state.welcome_done = True
        st.rerun()


def welcome_pending() -> bool:
    """True until the visitor has been through the welcome page."""
    return not st.session_state.get("welcome_done", False)


def render_welcome() -> None:
    st.session_state.setdefault("welcome_started", time.monotonic())

    _inject_css("style.css")  # cat theme: paw prints, green accents
    _inject_css("style_welcome.css")  # this page
    st.markdown(build_html(auto=AUTO_ADVANCE_SECONDS is not None), unsafe_allow_html=True)

    # ── LOGIN HOOK ───────────────────────────────────────────────────────────
    # To be replaced with button with login form. On success set
    #     st.session_state.authenticated = True
    #     st.session_state.welcome_done  = True
    #     st.rerun()
    # and set AUTO_ADVANCE_SECONDS = None above, so the page waits for the user.
    st.button(ENTER_LABEL, key="welcome_enter", on_click=_finish)

    if AUTO_ADVANCE_SECONDS is not None:
        _auto_advance()
