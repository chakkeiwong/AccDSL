Read-only focused repair review. No tools, commands, edits or agents.
Prior source review returned VERDICT: AGREE with six nonblocking findings.
Review only these repairs against the original clauses supplied. At most 250
words; end VERDICT: AGREE or VERDICT: REVISE. No tables or long restatement.
No whole-ASBE compliance, actual tax-law/adoption/offset finding or E07 closure.

Findings/disposition:
1. Supply the missing issuance-page metadata; wording now identifies its source.
2. Record extraction order glitch without altering original PDF/text.
3. Clarify required comparative-period adjustments; the remaining year has DTA
27.5 and DTL 26.25 both reverse, giving deferred expense 1.25, alongside opening
RE +1.25. Source Section I(b) governs; Section III's no-comparative rule does not.
4. Early adoption explicitly needs the paragraph II affiliate and concurrent
standards conditions, not just an asserted adoption date.
5. Script now checks stored quote line numbers (58 checks pass).
6. Earlier article 1–33 inspection remains author-inspected with the bounded
review's narrower scope disclosed; no unsupported independent coverage claim.

Exact supplement diff:
--- reviewed
+++ final
@@ -33,7 +33,10 @@
 
 The Interpretation 16 notice is 财会〔2022〕31号, signed 30 November 2022 and
 published on its webpage on 13 December 2022. Its attached PDF is the operative
-interpretation text. Section I(a), physical page 1, excludes a qualifying single
+interpretation text. The number and signing/publication dates are verified from
+the retained issuance webpage; they are not printed in the attachment. The PDF
+text extraction interleaves part of the parenthetical definition on page 1;
+the original PDF preserves the continuous clause. Section I(a), physical page 1, excludes a qualifying single
 transaction from ASBE 18 articles 11(2) and 13's initial-recognition exemption
 when it is not a business combination, affects neither accounting profit nor
 taxable income/loss initially, and creates equal taxable and deductible temporary
@@ -88,7 +91,8 @@
 
 For an otherwise qualifying ASBE enterprise in the second group, a 2020
 reporting date alone does not establish mandatory use of the revised lease
-standard; verified early adoption would be needed. The same enterprise falls
+standard; verified early adoption satisfying paragraph II's affiliate and
+concurrent-standards conditions would be needed. The same enterprise falls
 within mandatory application from 2021. This is a source-backed selection
 example, not a claim that any particular company belongs to that group.
 
@@ -119,12 +123,20 @@
 
 For a separate transition illustration, assume the earliest comparative opening
 has cash 500, ROU 105, lease liability 110 and equity 495, with no recognized
-deferred tax. Assume the same supported tax bases, rate and recoverability.
+deferred tax. Assume the same illustrative tax bases, rate and recoverability.
 Recognition adds DTA 27.5, DTL 26.25 and opening retained earnings 1.25.
 Assets become 632.5; liabilities 136.25 plus equity 496.25 also equal 632.5.
 This demonstrates the opening-equity route; it is not a new current-period tax
 expense or a rewrite of the original disclosure. Actual adoption dates and
 comparative periods must be supplied by the entity.
+
+Section I(b) also requires adjusting the qualifying transactions within the
+comparative window. In this transition illustration, if the comparative year
+contains the remaining lease year, DTA 27.5 and DTL 26.25 both reverse by expiry,
+giving comparative deferred tax expense 1.25. The opening adjustment alone is
+therefore not a complete transition statement. Section III's instruction not to
+adjust comparative information applies to its different share-payment topic and
+must not be imported into Section I.
 
 Applying the old exemption to set both deferred balances to zero in the
 qualifying post-2023 example is wrong relative to Interpretation 16 Section I.


docs/design/proposal/readiness/sources-20261007/interpretation16.txt
SHA256 28321ab172fc50f887755a488739ab12e337710e6beb0ed8a249b6327599a2ff
关于印发《企业会计准则解释第16号》的通知
财政部微信
财政部视频号
财政部
官方抖音号
移动客户端
Android下载
移动客户端
iphone下载
会计司
2017年11月21日 星期二
会计司
会计司
搜索
返回主站
当前位置：
首页
>
工作通知
关于印发《企业会计准则解释第16号》的通知
财会〔2022〕31号
国务院有关部委、有关直属机构，各省、自治区、直辖市、计划单列市财政厅（局），新疆生产建设兵团财政局，财政部各地监管局，有关单位:
为了深入贯彻实施企业会计准则，解决执行中出现的问题，同时，保持企业会计准则与国际财务报告准则的持续趋同，我们制定了《企业会计准则解释第16号》，现予印发，请遵照执行。
执行中如有问题，请及时反馈我部。
附件：企业会计准则解释第16号
财  政  部
2022年11月30日
附件下载：
企业会计准则解释第16号.pdf
相关文章：
发布日期：2022年12月13日
分享到微信朋友圈
x
打开微信，点击底部的“发现”，
使用“扫一扫”即可将网页分享至朋友圈。
【
大
中
小
】
【打印此页】
【关闭窗口】
网站地图
联系我们
主办单位：中华人民共和国财政部
网站标识码：bm14000001
京ICP备05002860号
京公网安备11010202000006号
技术支持：财政部信息网络中心
中华人民共和国财政部  版权所有，如需转载，请注明来源

docs/design/proposal/readiness/sources-20261007/interpretation16-pdf.txt
SHA256 07b2bd3c3ab4b19d59366ce08f285eb569d37cf1a84e80a05e9af1eb55cdb071
附件



         企业会计准则解释第 16 号


     一、关于单项交易产生的资产和负债相关的递延所得税
不适用初始确认豁免的会计处理
     该问题主要涉及《企业会计准则第 18 号——所得税》
等准则。
     （一）相关会计处理。

     对于不是企业合并、交易发生时既不影响会计利润也不
影响应纳税所得额（或可抵扣亏损）、且初始确认的资产和
负债导致产生等额应纳税暂时性差异和可抵扣暂时性差异
的单项交易（包括承租人在租赁期开始日初始确认租赁负债
并计入使用权资产的租赁交易，以及因固定资产等存在弃置
义务而确认预计负债并计入相关资产成本的交易等，以下简
           ，不适用《企业会计准则第 18 号
称适用本解释的单项交易）
——所得税》第十一条（二）、第十三条关于豁免初始确认
递延所得税负债和递延所得税资产的规定。企业对该交易因
资产和负债的初始确认所产生的应纳税暂时性差异和可抵
扣暂时性差异，应当根据《企业会计准则第 18 号——所得
税》等有关规定，在交易发生时分别确认相应的递延所得税
负债和递延所得税资产。
                  1
  （二）新旧衔接。

  对于在首次施行本解释的财务报表列报最早期间的期
初至本解释施行日之间发生的适用本解释的单项交易，企业
应当按照本解释的规定进行调整。对于在首次施行本解释的
财务报表列报最早期间的期初因适用本解释的单项交易而
确认的租赁负债和使用权资产，以及确认的弃置义务相关预
计负债和对应的相关资产，产生应纳税暂时性差异和可抵扣
暂时性差异的，企业应当按照本解释和《企业会计准则第 18
号——所得税》的规定，将累积影响数调整财务报表列报最
早期间的期初留存收益及其他相关财务报表项目。企业进行
上述调整的，应当在财务报表附注中披露相关情况。
  本解释内容允许企业自发布年度提前执行，若提前执行
还应在财务报表附注中披露相关情况。
  二、关于发行方分类为权益工具的金融工具相关股利的
所得税影响的会计处理
  该问题主要涉及《企业会计准则第 18 号——所得税》
等准则。
  （一）相关会计处理。

  对于企业（指发行方，下同）按照《企业会计准则第 37
号——金融工具列报》等规定分类为权益工具的金融工具
（如分类为权益工具的永续债等），相关股利支出按照税收
政策相关规定在企业所得税税前扣除的，企业应当在确认应
               2
付股利时，确认与股利相关的所得税影响。该股利的所得税
影响通常与过去产生可供分配利润的交易或事项更为直接
相关，企业应当按照与过去产生可供分配利润的交易或事项
时所采用的会计处理相一致的方式，将股利的所得税影响计
入当期损益或所有者权益项目（含其他综合收益项目）。对
于所分配的利润来源于以前产生损益的交易或事项，该股利
的所得税影响应当计入当期损益；对于所分配的利润来源于
以前确认在所有者权益中的交易或事项，该股利的所得税影
响应当计入所有者权益项目。
  （二）新旧衔接。

  本解释规定的分类为权益工具的金融工具确认应付股
利发生在 2022 年 1 月 1 日至本解释施行日之间的，涉及所
得税影响且未按照以上规定进行处理的，企业应当按照本解
释的规定进行调整。本解释规定的分类为权益工具的金融工
具确认应付股利发生在 2022 年 1 月 1 日之前且相关金融工
具在 2022 年 1 月 1 日尚未终止确认的，涉及所得税影响且
未按照以上规定进行处理的，企业应当进行追溯调整。企业
进行上述调整的，应当在财务报表附注中披露相关情况。
  三、关于企业将以现金结算的股份支付修改为以权益结
算的股份支付的会计处理
  该问题主要涉及《企业会计准则第 11 号——股份支付》
等准则。
                3
  （一）相关会计处理。
  企业修改以现金结算的股份支付协议中的条款和条件，
使其成为以权益结算的股份支付的，在修改日，企业应当按
照所授予权益工具当日的公允价值计量以权益结算的股份
支付，将已取得的服务计入资本公积，同时终止确认以现金
结算的股份支付在修改日已确认的负债，两者之间的差额计
入当期损益。上述规定同样适用于修改发生在等待期结束后
的情形。

  如果由于修改延长或缩短了等待期，企业应当按照修改
后的等待期进行上述会计处理（无需考虑不利修改的有关会
计处理规定）
     。
  如果企业取消一项以现金结算的股份支付，授予一项以
权益结算的股份支付，并在授予权益工具日认定其是用来替
代已取消的以现金结算的股份支付（因未满足可行权条件而
被取消的除外）的，适用本解释的上述规定。
  （二）新旧衔接。
  对于 2022 年 1 月 1 日至本解释施行日新增的本解释规

定的上述交易，企业应当按照本解释的规定进行调整。对于
2022 年 1 月 1 日之前发生的本解释规定的上述交易，未按照

以上规定进行处理的，企业应当进行调整，将累积影响数调

整 2022 年 1 月 1 日留存收益及其他相关财务报表项目，对

可比期间信息不予调整。企业应当在附注中披露该会计政策
                4
变更的性质、内容和原因，以及当期财务报表中受影响的项
目名称和调整金额。

  四、生效日期
  本解释“关于单项交易产生的资产和负债相关的递延所
得税不适用初始确认豁免的会计处理”内容自 2023 年 1 月 1
日起施行；“关于发行方分类为权益工具的金融工具相关股
利的所得税影响的会计处理”、
             “关于企业将以现金结算的股
份支付修改为以权益结算的股份支付的会计处理”内容自公
布之日起施行。




                5


docs/design/proposal/readiness/sources-20261007/lease-notice-recovery.txt
SHA256 c37db31b3ed426fc49e3b8836f869c73c42f901f8322969ea6481d90977bb120
关于修订印发《企业会计准则第21号——租赁》的通知
财政部微信
财政部视频号
财政部
官方抖音号
移动客户端
Android下载
移动客户端
iphone下载
会计司
2017年11月21日 星期二
会计司
会计司
搜索
返回主站
当前位置：
首页
>
政策发布
关于修订印发《企业会计准则第21号——租赁》的通知
财会〔2018〕35号
国务院有关部委、有关直属机构，各省、自治区、直辖市、计划单列市财政厅（局），新疆生产建设兵团财政局，财政部驻各省、自治区、直辖市、计划单列市财政监察专员办事处，有关中央管理企业：
为了适应社会主义市场经济发展需要，规范租赁的会计处理，提高会计信息质量，根据《企业会计准则——基本准则》，我部对《企业会计准则第21号——租赁》进行了修订，现予印发。有关事项通知如下：
一、在境内外同时上市的企业以及在境外上市并采用国际财务报告准则或企业会计准则编制财务报表的企业，自2019年1月1日起施行；其他执行企业会计准则的企业自2021年1月1日起施行。
二、母公司或子公司在境外上市且按照国际财务报告准则或企业会计准则编制其境外财务报表的企业，可以提前执行本准则，但不应早于其同时执行我部2017年3月31日印发的《企业会计准则第22号——金融工具确认和计量》和2017年7月5日印发的《企业会计准则第14号——收入》的日期。
三、执行本准则的企业，不再执行我部于2006年2月15日印发的《财政部关于印发<企业会计准则第1号——存货>等38项具体准则的通知》（财会〔2006〕3号）中的《企业会计准则第21号——租赁》，以及我部于2006年10月30日印发的《财政部关于印发<企业会计准则——应用指南>的通知》（财会〔2006〕18号）中的《〈企业会计准则第21号——租赁〉应用指南》。
执行中有何问题，请及时反馈我部。
附件：企业会计准则第21号——租赁
财政部
2018年12月7日
附件下载:
企业会计准则第21号——租赁.doc
相关文章:
财政部会计司有关负责人就新租赁准则发布实施答记者问
发布日期:  2018年12月14日
分享到微信朋友圈
x
打开微信，点击底部的“发现”，
使用“扫一扫”即可将网页分享至朋友圈。
【
大
中
小
】
【打印此页】
【关闭窗口】
网站地图
联系我们
主办单位：中华人民共和国财政部
网站标识码：bm14000001
京ICP备05002860号
京公网安备11010202000006号
技术支持：财政部信息网络中心
中华人民共和国财政部  版权所有，如需转载，请注明来源