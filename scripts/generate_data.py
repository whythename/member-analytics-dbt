"""
Erzeugung von fiktiven Mitgliederdaten, output als CSV.

Fixer seed zur Reproduzierbarkeit
"""

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
OUT = Path(__file__).resolve().parents[1] / "data" / "raw"

START = date(2023, 1, 1)
END = date(2026, 6, 30)
N_MEMBERS = 4000

BRANDS = ["McFIT", "JOHN REED", "Gold's Gym"]
CITIES = ["Berlin", "Hamburg", "Muenchen", "Koeln", "Frankfurt", "Leipzig"]
PLANS = {"basic": 19.90, "plus": 29.90, "premium": 49.90}
CHANNELS = ["web", "walk_in", "referral", "campaign", "app"]
CANCEL_REASONS = ["price", "relocation", "usage", "service", "unknown"]


def daterange_days(a: date, b: date) -> int:
    return (b - a).days


def rand_date(a: date, b: date, rng: random.Random) -> date:
    return a + timedelta(days=rng.randint(0, max(daterange_days(a, b), 0)))


def signup_weight(d: date) -> float:
    return {1: 3.0, 2: 1.6, 3: 1.2, 4: 1.0, 5: 0.9, 6: 0.7,
            7: 0.6, 8: 0.7, 9: 1.4, 10: 1.2, 11: 0.9, 12: 0.6}[d.month]


def main() -> None:
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    studios = []
    for i in range(1, 13):
        brand = BRANDS[i % len(BRANDS)]
        studios.append({
            "studio_id": f"ST{i:03d}",
            "studio_name": f"{brand} {CITIES[i % len(CITIES)]} {i}",
            "brand": brand,
            "city": CITIES[i % len(CITIES)],
            "opened_at": rand_date(date(2015, 1, 1), date(2022, 12, 31), rng).isoformat(),
        })

    all_days = [START + timedelta(days=i) for i in range(daterange_days(START, END))]
    weights = [signup_weight(d) for d in all_days]

    members = []
    for i in range(1, N_MEMBERS + 1):
        signup = rng.choices(all_days, weights=weights, k=1)[0]
        birth = rand_date(date(1960, 1, 1), date(2007, 12, 31), rng)
        members.append({
            "member_id": f"M{i:06d}",
            # 2% fehlende Geburtsdaten
            "birth_date": "" if rng.random() < 0.02 else birth.isoformat(),
            "gender": rng.choice(["f", "m", "d"]),
            "signup_date": signup.isoformat(),
            "home_studio_id": rng.choice(studios)["studio_id"],
            # uneinheitliche Schreibweise
            "source_channel": rng.choice(CHANNELS).upper() if rng.random() < 0.3
                              else f" {rng.choice(CHANNELS)} ",
        })
        
    contracts = []
    churn_end = {}
    cid = 0
    for m in members:
        start = date.fromisoformat(m["signup_date"])
        plan = rng.choices(list(PLANS), weights=[0.5, 0.35, 0.15], k=1)[0]
        n_terms = rng.choices([1, 2, 3], weights=[0.62, 0.30, 0.08], k=1)[0]

        for term in range(n_terms):
            last = term == n_terms - 1
            months = max(1, int(rng.lognormvariate(2.5, 0.7)))
            end = start + timedelta(days=months * 30)

            churned = True
            if last:
                if end > END or rng.random() < 0.55:
                    end = None
                    churned = False

            cid += 1
            contracts.append({
                "contract_id": f"C{cid:07d}",
                "member_id": m["member_id"],
                "plan": plan,
                "monthly_price": PLANS[plan],
                "start_date": start.isoformat(),
                "end_date": end.isoformat() if end else "",
                "cancel_reason": rng.choice(CANCEL_REASONS) if (end and churned) else "",
            })

            if end is None:
                churn_end[m["member_id"]] = None
                break
            if last:
                churn_end[m["member_id"]] = end
            else:
                start = end + timedelta(days=rng.randint(15, 240))
                if start > END:
                    churn_end[m["member_id"]] = end
                    break
                plan = rng.choices(list(PLANS), weights=[0.4, 0.4, 0.2], k=1)[0]


    checkins = []
    kid = 0
    home_studio = {m["member_id"]: m["home_studio_id"] for m in members}
    for c in contracts:
        c_start = date.fromisoformat(c["start_date"])
        c_end = date.fromisoformat(c["end_date"]) if c["end_date"] else END
        c_end = min(c_end, END)
        if c_end <= c_start:
            continue
        base = rng.choice([0.4, 0.8, 1.4, 2.2, 3.2])
        studio = home_studio[c["member_id"]]

        day = c_start
        while day < c_end:
            days_to_end = (c_end - day).days
            decay = 1.0
            if c["end_date"] and days_to_end < 60:
                decay = max(0.05, days_to_end / 60.0)
            season = 1.25 if day.month in (1, 2, 9, 10) else (0.75 if day.month in (7, 8) else 1.0)
            p = (base / 7.0) * decay * season
            if rng.random() < p:
                kid += 1
                ts = datetime.combine(day, datetime.min.time()) + timedelta(
                    hours=rng.choices(range(6, 23),
                                      weights=[2, 4, 3, 2, 2, 3, 3, 3, 4, 5, 7, 9, 9, 7, 5, 3, 2],
                                      k=1)[0],
                    minutes=rng.randint(0, 59),
                )
                s = rng.choice(studios)["studio_id"] if rng.random() < 0.08 else studio
                checkins.append({
                    "checkin_id": f"K{kid:08d}",
                    "member_id": c["member_id"],
                    "studio_id": s,
                    "checkin_ts": ts.isoformat(sep=" "),
                })
            day += timedelta(days=1)


    for c in rng.sample(checkins, k=int(len(checkins) * 0.015)):
        checkins.append(dict(c))


    for i in range(200):
        kid += 1
        checkins.append({
            "checkin_id": f"K{kid:08d}",
            "member_id": f"X{rng.randint(1, 9999):06d}",
            "studio_id": rng.choice(studios)["studio_id"],
            "checkin_ts": rand_date(START, END, rng).isoformat() + " 12:00:00",
        })
    rng.shuffle(checkins)

    write(OUT / "studios.csv", studios)
    write(OUT / "members.csv", members)
    write(OUT / "contracts.csv", contracts)
    write(OUT / "checkins.csv", checkins)

    print(f"studios   {len(studios):>8,}")
    print(f"members   {len(members):>8,}")
    print(f"contracts {len(contracts):>8,}")
    print(f"checkins  {len(checkins):>8,}")
    print(f"-> {OUT}")


def write(path: Path, rows: list) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()