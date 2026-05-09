import time
from statistics import mean
from pytrends.request import TrendReq

def fetch_trends(keywords: list) -> list:
    results = []
    try:
        pt = TrendReq(hl="en-US", tz=360)
    except Exception as e:
        print(f"Pytrends init failed: {e}")
        return []
    if not isinstance(keywords, list):
        return []
    try:
        backoff_s = 2
        for keyword in keywords:
            try:
                kw = str(keyword)
                while True:
                    try:
                        pt.build_payload([kw], timeframe="today 3-m")
                        data = pt.interest_over_time()
                        backoff_s = 2
                        break
                    except Exception as e:
                        msg = str(e)
                        if "429" in msg or "Too Many Requests" in msg:
                            sleep_for = min(120, backoff_s)
                            print(f"Trends rate-limited (429). Sleeping {sleep_for}s then retrying.")
                            time.sleep(sleep_for)
                            backoff_s = min(120, backoff_s * 2)
                            continue
                        raise
                if data is None or data.empty or kw not in data.columns:
                    trend_score = 0.0
                    growth_rate = 0.0
                else:
                    series = data[kw].astype(float)
                    if len(series) >= 28:
                        last_window = series[-28:]
                    else:
                        last_window = series
                    try:
                        trend_score = float(mean(last_window)) if len(last_window) > 0 else 0.0
                    except Exception:
                        trend_score = 0.0
                    if len(series) >= 2:
                        mid = len(series) // 2
                        first_half = series[:mid]
                        second_half = series[mid:]
                        try:
                            first_mean = float(mean(first_half)) if len(first_half) > 0 else 0.0
                            second_mean = float(mean(second_half)) if len(second_half) > 0 else 0.0
                        except Exception:
                            first_mean = 0.0
                            second_mean = 0.0
                        if first_mean > 0:
                            growth_rate = float((second_mean - first_mean) / first_mean)
                        else:
                            growth_rate = 0.0
                    else:
                        growth_rate = 0.0
                results.append(
                    {
                        "keyword": kw,
                        "trend_score": float(trend_score),
                        "growth_rate": float(growth_rate),
                    }
                )
            except Exception as e:
                print(f"Trend fetch failed for '{keyword}': {e}")
            time.sleep(5)
        return results
    except Exception as e:
        print(f"Trend fetch failed: {e}")
        return []

if __name__ == "__main__":
    data = fetch_trends(["AI agents"])
    print(len(data))

