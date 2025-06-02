# 網路小說推薦系統


**[DEMO影片(未改連結)](https://affinelayer.com/pixsrv/)  | by 資料庫第九組**


組員(依學號排列)
[資工2B 412410085 張子頡](https://github.com/jerrychang565)<br>
[資工2B 412410291 林鈺丞](https://github.com/Yu-Chang314)<br>
[資工2B 412410929 呂秉諺](https://github.com/Jimmy0510Lu)<br>
[資工2B 412411281 劉奕霈](https://github.com/rainyyy-yyy)<br>
[資工2B 412411315 張庭瑄](https://github.com/Yui004)<br>
[資工2B 412411810 金庭聿](https://github.com/jguavak)<br>

## 環境配置
1.請先確認電腦中有mySQL、Visual Studio Code

2.下載整個專案檔

3.於mySQL中執行databaseproject-G9/Database/mojoin中所有sql檔

4.確認Visual Studio Code中有python，可於左側欄搜尋Python安裝

5.使用以下指令安裝flask、recommendation、pymysql
```bash
bash pip install flask
```
```bash
bash pip install recommendation
```
```bash
bash pip install pymysql
```

## 執行程式
1.使用「取代」功能，將**app\.py**與**recommendation\.py**中所有的「12345678」取代為你的mySQL密碼

2.按下「執行python檔」

3.前往瀏覽器，輸入「**127.0.0.1:5000**」連到網站

## 網站功能
#### 註冊登入
1.右上角的「註冊」可註冊新帳號，帳號密碼須在20字元內

2.右上角的「登入」可登入帳號

#### 查找小說
1.可點選類別查詢該類別之小說

2.可點選作者姓名查詢該作者撰寫之小說

3.可點選出版社名稱查詢該出版社出版之小說

4.可點選狀態查詢該狀態之小說

5.可點選Tag查詢含有該Tag之小說

6.可於首頁上方搜尋欄輸入關鍵字，查找書名、作者、出版社中含有該關鍵字之小說

#### 收藏小說
1.使用者可點選收藏按鍵或封面圖右上角愛心收藏小說

2.再次點選收藏按鍵或愛心圖案可取消收藏該小說

3.點選右上角帳號名稱可看見該帳號所有收藏的小說

**收藏功能須登入後方可使用**

#### 小說推薦
1.點選任一本書可看見依該書之Tag所推薦之小說

2.點選右上角帳號名稱可看見依該帳號收藏與閱讀推薦之小說

## 參考資料
<p>資料來源：<a href="https://mojoin.com/novels">MOJOIN線上漫畫、小說平台</a></p>
<p>演算法結構：<a href="https://zhuanlan.zhihu.com/p/489861857">MySQL实现协同过滤推荐为用户推荐喜爱的商品</a></p>
</ul>
