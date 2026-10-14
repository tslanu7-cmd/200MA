"""한국 시총 상위 200 + 미국 시총 상위 500(S&P500 구성종목)의 200주 이동평균 괴리율을 계산해 data.json으로 저장."""
import json, datetime as dt
import pandas as pd, yfinance as yf, FinanceDataReader as fdr

def universe():
    kr = fdr.StockListing("KRX")
    kr = kr[kr["Market"].isin(["KOSPI", "KOSDAQ"])].sort_values("Marcap", ascending=False).head(200)
    kr_rows = [(f"{r.Code}.{'KS' if r.Market == 'KOSPI' else 'KQ'}", r.Name, "KR") for r in kr.itertuples()]
    us = fdr.StockListing("S&P500")
    us_rows = [(s.replace(".", "-"), n, "US") for s, n in zip(us["Symbol"], us["Name"])][:500]
    return kr_rows + us_rows

def weekly_closes(tickers):
    out = {}
    for i in range(0, len(tickers), 100):
        chunk = tickers[i:i + 100]
        df = yf.download(chunk, period="6y", interval="1wk", auto_adjust=True,
                         progress=False, group_by="ticker", threads=True)
        for t in chunk:
            try:
                out[t] = df[t]["Close"].dropna()
            except Exception:
                pass
    return out

def main():
    uni = universe()
    closes = weekly_closes([u[0] for u in uni])
    rows = []
    for ticker, name, mkt in uni:
        s = closes.get(ticker)
        if s is None or len(s) < 200:
            continue  # 상장 4년 미만 등 데이터 부족
        price, ma = float(s.iloc[-1]), float(s.tail(200).mean())
        rows.append({"market": mkt, "ticker": ticker.split(".")[0], "name": name,
                     "price": round(price, 2), "ma200": round(ma, 2),
                     "gap": round((price / ma - 1) * 100, 2)})
    kst = dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"updated": kst.strftime("%Y-%m-%d %H:%M KST"), "rows": rows}, f, ensure_ascii=False)
    print(f"{len(rows)} stocks saved")

if __name__ == "__main__":
    main()
