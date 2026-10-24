# 四倉庫一致性核查（2026-10-24）

首200名創始會員於開閘日起享52週Pro（HK$4,056）；門檻200不自動開閘，付款驗收及用戶明確批准後才收款。Stripe HK$78／週自動續訂；Crypto US$416／52週一次付，展示HK$3,244.80八折，不自動續期。現時不收款，Crypto及賽日提示未啟用，付款環境維持live；愛駒上限30／3／90，愛駒通知不加開閘檢查。

正式站 https://tianxi.racing 已發布。平台驗證排程：weather-archive-managed每5分鐘、weather-sync-github-managed每日23:50 HKT、race-results-dispatch-managed每日23:31／01:31 HKT；首次均200，兩項天氣安全略過，賽果派送獲接納但不等於收齊。正常首次後已停舊weather-archive-5min、weather-sync-github-nightly及race-results-dispatch。逐場收料保留，全日首次核實官方完場後30分鐘主收料；固定深夜只為後備。

鎖前官方更改只重算受影響場次；鎖後不補位，保留原四揀，退出／未完賽逐匹無效，命中分母固定4；鎖前退出未及重算亦按原四揀／4。實際換騎另記，不重算原凍結。官方彩池替補／退款只用於原注结算，不能改模型四揀。

## 核查範圍及修正
- 網站README、兩個腦圖、藍圖及公開會員日誌舊500名／自動開閘已統一200。
- 腦圖六個概念頁引用舊commit，把舊規則明確標為歷史並補現行更正；原始chunks不改，知識來源新增會員規則及本核查報告。
- 賽馬README／服務README舊拆倉及固定23:30主收料更正；研究README不再把退役足球當現行產品。
- 網站legacy-site靜態Whop／日月費頁只屬歷史，現行TanStack網站沒有該付款入口；不修改歷史檔案。
- Stripe建立付款先獨立核伺服器gate_open_at，關閘或無效日期即停止，過往扣款失敗不可繞過。

## 保留及限制
- 不改500字樣的模型分數、輪數、可調門檻測試、歷史migration、研究原檔及舊commit。
- 文檔同步不代表其他倉Worker重新部署；現行模型公式差異需以版本／原凍結證據核對，不為統一文字改模型。
- NOWPayments及Stripe正式收款、會員Telegram／iPhone送達、直接WorkerPro保護仍待實際驗收。
- 本輪網站修正尚未發布；不開閘、不開Crypto或賽日提示。
