# 跨倉庫現行政策自動核查

政策清單：`docs/repository-policy.json`。四倉庫清單必須逐值相同，變更政策須同一次更新四份；程式、會員RPC及正式平台排程仍各自為實際運行來源，本檢查不代替讀回驗收。

唯一自動執行位置為 `sleepingarhat/tianxi-racing` 的 `repository-consistency-audit.yml`，每小時 UTC :17（香港同為 :17），相關文件push及手動執行。`tianxi-web`只保存腳本與工作模板，不建立第二個工作；domain-brain／研究倉不啟動生產任務。

每次先取四個預設分支commit，再按固定commit的完整tree讀blob，避免中途更新混用版本。缺必需檔案、tree截斷、讀取失敗、無權讀私有研究倉、政策漂移一律exit 1。報告保存14日，只含倉庫／commit／路徑／規則ID，唔打印原文或憑證；GitHub工作失敗按GitHub通知設定通知，不額外假稱Telegram送達。

## 文案範圍
- README、服務README、現行核查摘要、腦圖概念頁、公開靜態腦圖、現行網站頁面與會員組件；freeStage數值另直接核對。
- 不檢查或修改賽事原始CSV、凍結、模型分數、研究原檔、已套用migration、legacy-site或舊commit。
- 明確標示「歷史／封存／當時草稿」標題的段落及dated開發者條目不當現行優惠；下一個同級或更高標題會恢復檢查。政策清單不受歷史豁免。
- 文案檢查為已知舊規則及數字漂移防線，不代表可理解所有自然語言或保證永遠零矛盾；新措辭須擴充規則並作人工審閱。

## 安全及執行
- 沿用現有GitHub授權，不寫任何憑證入檔案；Actions先用既有`TIANXI_BACKEND_PAT`，否則內建唯讀token；無私有倉讀取權會明確失敗，不能跳過。
- 本機：`python3 -m unittest discover -s scripts -p test_repository_consistency.py`；`python3 scripts/audit_repository_consistency.py --report /tmp/repository-consistency.json`。
- 不呼叫付款、通知、天氣或賽果endpoint，亦不修改收費閘、crypto或賽日提示。