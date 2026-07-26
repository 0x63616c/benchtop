"""Query JLCPCB's parts search — stock, price and basic/extended, per keyword.

    python3 pcb/tools/jlcsearch.py "0603 10k 1%" [more keywords...]

Every part that goes on a board has to be really buyable, and the LCSC web
pages are heavier than this endpoint. `base` in the type column means JLC
Basic (no assembly setup fee), which is why the column is printed.
"""

import json
import sys
import urllib.request

URL = ("https://jlcpcb.com/api/overseas-pcb-order/v1/"
       "shoppingCart/smtGood/selectSmtComponentList")


def search(keyword, n=6):
    req = urllib.request.Request(
        URL,
        data=json.dumps({"currentPage": 1, "pageSize": n, "keyword": keyword}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    for c in (body["data"]["componentPageInfo"] or {}).get("list") or []:
        price = min((p["productPrice"] for p in c.get("componentPrices") or []), default=0)
        print(f'  C{c["componentCode"].lstrip("C") if c.get("componentCode") else c["componentId"]}'
              if False else
              f'  {c.get("componentCode", "?"):>10} {c.get("componentLibraryType", ""):<8} '
              f'stock={c["stockCount"]:<8} ${price:<8.4f} {c.get("componentBrandEn", "")[:22]:<22} '
              f'{c.get("componentModelEn", "")[:28]:<28} {c.get("erpComponentName", "")[:24]} '
              f'{c.get("componentSpecificationEn", "")[:12]}')


if __name__ == "__main__":
    for kw in sys.argv[1:]:
        print(kw)
        search(kw)
