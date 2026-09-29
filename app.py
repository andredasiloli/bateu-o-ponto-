eimport os
import random
import re

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# ---- Configuração (pode sobrescrever com variáveis de ambiente) ----
START = os.getenv("PONTO_ENTRADA", "09:00")   # entrada padrão
END = os.getenv("PONTO_SAIDA", "18:48")       # saída padrão


def to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def to_hhmm(minutes: int) -> str:
    minutes %= 1440
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


START_MIN = to_min(START)
END_MIN = to_min(END)
DURATION = END_MIN - START_MIN  # 9h48 = 588 min

# ---- Frases ----
ENTRY = {
    "madrugada": [  # 90+ min antes
        "Caiu da cama, foi? 🛏️⬇️",
        "O galo ainda estava no primeiro café. 🐓",
        "Você é o zelador ou o funcionário? 🔑",
        "A empresa nem acendeu as luzes ainda. 💡",
    ],
    "cedo": [  # 15 a 90 min antes
        "Olha o pontual! Quem madruga, Deus ajuda... e o banco de horas também. ⏰",
        "Acordou com o pé direito (e o esquerdo também). 🦶",
        "Chegou cedo pra pegar o melhor lugar do café. ☕",
        "Alguém dormiu cedo ontem, hein? 😇",
    ],
    "pontual": [  # ±15 min
        "Britânico de tão pontual. 🎩",
        "Nem um minuto a mais, nem a menos. Cirúrgico. 🎯",
        "Horário padrão. O RH te ama. 💘",
    ],
    "atrasado": [  # 15 a 60 min depois
        "Dormiu aí, né? 😴",
        "O despertador tocou. Você que não ouviu. 🔔",
        "Só mais cinco minutinhos... que viraram cinquenta. 🛌",
        "O trânsito, claro. Foi o trânsito. Sempre é. 🚗",
    ],
    "muito_atrasado": [  # 60+ min depois
        "Vai dormir aí mesmo, já que veio até aqui. 🛏️",
        "Chegou junto com o almoço, parabéns! 🍽️",
        "O travesseiro mandou um abraço. 🫂",
        "Isso é entrada ou já é o lanche da tarde? 🥪",
    ],
}

EXIT = {
    "sol": [  # sai antes das 18h
        "Deu pra ver o sol hoje! 🌞",
        "Saiu com luz do dia, que luxo! 😎",
        "Vai aproveitar a vida lá fora, cidadão! 🌳",
    ],
    "normal": [
        "Saída padrão. Sem drama, sem hora extra. ✅",
        "Bateu, saiu, viveu. 🚪",
        "Tudo certo, missão cumprida! 🫡",
    ],
    "tarde": [  # 19h+ 
        "Já já dorme na empresa, hein? 🏢🌙",
        "Saiu de noite... dá até pra jantar no escritório. 🍕",
        "A faxineira já te conhece pelo nome. 🧹",
    ],
    "madrugada": [  # 21h+
        "Você mora aí? Manda o endereço pra correspondência. 📮",
        "Isso é saída ou um novo turno? 🦉",
        "Até o segurança já vai te chamar de colega. 👮",
    ],
}


def classify_entry(delta: int) -> str:
    if delta <= -90:
        return "madrugada"
    if delta < -15:
        return "cedo"
    if delta <= 15:
        return "pontual"
    if delta <= 60:
        return "atrasado"
    return "muito_atrasado"


def classify_exit(exit_min: int) -> str:
    if exit_min < 18 * 60:
        return "sol"
    if exit_min >= 21 * 60:
        return "madrugada"
    if exit_min >= 19 * 60 + 30:
        return "tarde"
    return "normal"


@app.route("/")
def index():
    return render_template("index.html", start=START, end=END, duration=DURATION)


@app.route("/api/calc")
def calc():
    entry = request.args.get("entry", "")
    if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", entry):
        return jsonify(error="Use o formato HH:MM, ex: 09:00"), 400

    entry_min = to_min(entry)
    exit_min = entry_min + DURATION
    delta = entry_min - START_MIN
    exit_delta = (exit_min % 1440) - END_MIN  # diferença vs saída padrão

    ek = classify_entry(delta)
    xk = classify_exit(exit_min % 1440) if exit_min < 1440 else "madrugada"

    return jsonify(
        entry=entry,
        exit=to_hhmm(exit_min),
        next_day=exit_min >= 1440,
        exit_min=exit_min,
        entry_min=entry_min,
        duration=DURATION,
        delta=delta,
        exit_delta=exit_delta,
        entry_mood=ek,
        exit_mood=xk,
        entry_msg=random.choice(ENTRY[ek]),
        exit_msg=random.choice(EXIT[xk]),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
