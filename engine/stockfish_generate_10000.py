import subprocess, json, random, time

STOCKFISH = r"I:\FRAP\Screenshots\AI小遊戲\stockfish\stockfish.exe"
OUT = r"I:\FRAP\Screenshots\AI小遊戲\stockfish\engine_practice_10000.json"

TARGET = 10000
DEPTH = 10

START_MOVES = [
    "",
    "e2e4", "d2d4", "c2c4", "g1f3",
    "e2e4 e7e5", "d2d4 d7d5",
    "e2e4 c7c5", "d2d4 g8f6",
]

def send(p, cmd):
    p.stdin.write(cmd + "\n")
    p.stdin.flush()

def read_until_bestmove(p):
    best = None
    score = 0
    while True:
        line = p.stdout.readline().strip()
        if "score cp" in line:
            parts = line.split()
            if "cp" in parts:
                try:
                    score = int(parts[parts.index("cp") + 1])
                except:
                    pass
        if line.startswith("bestmove"):
            best = line.split()[1]
            break
    return best, score

def engine_best(p, moves, depth):
    pos = "position startpos"
    if moves:
        pos += " moves " + " ".join(moves)
    send(p, pos)
    send(p, f"go depth {depth}")
    return read_until_bestmove(p)

def main():
    p = subprocess.Popen(
        [STOCKFISH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    send(p, "uci")
    send(p, "isready")
    send(p, "ucinewgame")

    data = {
        "engine": "Stockfish",
        "depth": DEPTH,
        "target": TARGET,
        "positions": []
    }

    seen = set()

    for i in range(TARGET):
        base = random.choice(START_MOVES).split()
        moves = base[:]

        # 隨機延伸 4~24 手，用 Stockfish 自己走，避免亂局太爛
        extra_len = random.randint(4, 24)

        for _ in range(extra_len):
            best, score = engine_best(p, moves, 4)
            if not best or best == "(none)":
                break
            moves.append(best)

        position = "startpos"
        if moves:
            position += " moves " + " ".join(moves)

        if position in seen:
            continue
        seen.add(position)

        best, score = engine_best(p, moves, DEPTH)
        if not best or best == "(none)":
            continue

        data["positions"].append({
            "position": position,
            "best": best,
            "score": score
        })

        if len(data["positions"]) % 100 == 0:
            print(f"已完成 {len(data['positions'])}/{TARGET}")

    send(p, "quit")
    p.wait()

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("完成：", OUT)
    print("總局面：", len(data["positions"]))

if __name__ == "__main__":
    main()