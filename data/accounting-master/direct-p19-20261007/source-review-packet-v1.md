# P19 ASBE primary-source and arithmetic review
Independent skeptical read-only reviewer. No tools, edits, commands, agents or
external research. Use only the supplied retained Chinese primary text and
project deductions. Review translation, scope, effective dates, transition,
recoverability, recognition versus offset presentation, and numerical examples.
Return located material findings and end VERDICT: AGREE or VERDICT: REVISE.
AGREE is bounded support for this supplement, not full ASBE compliance or E07
closure. Distinguish actual source rules from illustrative parameters and actual
entity/tax-law facts that remain unknown.

Evidence contract: compare the proposed tax source correction directly with
ASBE 18 articles 4–25, Interpretation 16 I(a), I(b), IV, and the 2018 revised
lease issuance notice I–III. This is a source/mathematics review, not research
performance. Numerical parameters are the existing P17 synthetic case:
210 opening ROU/liability, 121 paid at each of two year ends, 10% discount,
straight-line ROU depreciation over two years, assumed zero tax bases, 25% tax,
and sufficient recoverability. No offset entitlement is assumed for a real firm.

Commands already run: check_source_repair.py exited 0 with 47 rational-arithmetic,
file and quote-location checks. 1,266 protected files and 518 upstream references
match. The old unsuccessful retrieval receipts remain intact. The official lease
notice and attachment were retrieved now with curl (HTTP 200). Attachment .doc
contains OOXML ZIP; direct XML text extraction omits automatic list numbering.
Source inspection/URL/hash record is supplied. No later amendment census exists.

Criteria: every asserted rule must follow from the actual provided clause;
calculations must follow from declared assumptions; 2019/2021 lease dates and
2023 tax date must not be conflated; missing entity application, law, amendments,
recoverability and actual offset eligibility remain explicit. An AGREE verdict
must not imply the frozen P18 PDF already contains this new correction.



FILE docs/design/proposal/readiness/asbe-tax-source-repair-v1.md
SHA256 706a35ad1f012832eb525353316caf1bd79ae48d89d252738c100d191a38af14
# ASBE lease tax: recovered primary sources

7 October 2026. This supplements the frozen P17/P18 source status. Their earlier
HTTP 502 records remain true records of those attempts. The Ministry of Finance
ASBE 18 page and the Interpretation 16 issuance page now return 200, and the
issuance page's linked five-page PDF has been retained and read in full.
During session recovery the separate 2018 lease issuance notice also returned
200, together with its linked standard. The earlier failed retrievals remain
preserved alongside these later successful responses.

Exact URLs, retained-file hashes and inspected provisions are recorded in
`sources-20261007/inspection-v1.json`. The ASBE 18 original text is available at
<https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46230.htm>;
Interpretation 16 and its operative attachment are linked from
<https://kjs.mof.gov.cn/gongzuotongzhi/202212/t20221212_3857395.htm>.

## Exact source and applicability findings

The official ASBE 18 page is titled 企业会计准则第18号——所得税 and gives a
publication date of 9 March 2006. The 2008 directory in its URL is not an
effective-date finding, and the site's template date is not the publication
date. Its original text must be read with subsequent interpretations; it is
not a consolidated statement of every amendment through 2026.

Articles 4–9 define carrying amounts, tax bases and taxable/deductible temporary
differences. Articles 11 and 13 contain the original initial-recognition
exceptions. Article 13 limits recognition of a deferred tax asset to the
probable taxable profit available for use of the deduction. Articles 16–20
specify current/deferred tax measurement, applicable rates, recovery/settlement
method, no discounting and subsequent review. Articles 21–23 address allocation
to profit/equity and separate noncurrent presentation. These provisions were
inspected in the retained Chinese text, not inferred from an IFRS comparison.

The Interpretation 16 notice is 财会〔2022〕31号, signed 30 November 2022 and
published on its webpage on 13 December 2022. Its attached PDF is the operative
interpretation text. Section I(a), physical page 1, excludes a qualifying single
transaction from ASBE 18 articles 11(2) and 13's initial-recognition exemption
when it is not a business combination, affects neither accounting profit nor
taxable income/loss initially, and creates equal taxable and deductible temporary
differences. The examples expressly include a lessee's initial lease liability
and right-of-use asset, and an asset with a decommissioning obligation.
Corresponding deferred tax liabilities and assets are recognized separately
under the applicable income-tax provisions. Equal asset/liability carrying
amounts alone are not the test, and asset recoverability is still required.

Section I(b), physical page 2, requires adjustment of qualifying transactions
between the earliest comparative opening and application. For qualifying
existing balances at that opening, cumulative effects adjust opening retained
earnings and the relevant financial-statement items. Related disclosure is
required. Early application is allowed from the year of issuance with disclosure.
Section IV, physical page 5, makes Section I effective on 1 January 2023.
Sections II and III have different effective and transition provisions; the
lease-tax date must not be copied to those other treatments.

The remaining PDF sections were read to distinguish those boundaries: Section II
concerns income tax on dividends from instruments classified as equity, and
Section III concerns modifications from cash-settled to equity-settled
share-based payments. This supplement does not introduce implementations of
either method.

## Lease adoption dates recovered during continuation

The [2018 issuance notice](https://kjs.mof.gov.cn/zhengcefabu/201812/t20181213_3092629.htm)
is 财会〔2018〕35号, signed 7 December 2018 and published on the webpage on
14 December 2018. Its URL contains 13 December; the printed publication date
controls that metadata. Paragraph I requires application from 1 January 2019
for enterprises listed both domestically and overseas, and overseas-listed
enterprises preparing financial statements under IFRS or ASBE. Other enterprises
applying ASBE must apply the revised standard from 1 January 2021.

Paragraph II permits early application for enterprises whose parent or subsidiary
is listed overseas and prepares its overseas statements under IFRS or ASBE. That
early date cannot precede their simultaneous application of the specified 2017
financial-instruments and revenue standards. Paragraph III discontinues the 2006
lease standard and its application guidance when an enterprise applies the
revision. Thus article 68's general 2019 date does not establish every entity's
mandatory adoption date.

The notice's linked `P020181213596772599039.doc` is an OOXML ZIP despite its
`.doc` suffix. The original bytes and derived paragraph text are retained.
Inspected articles 1–8, 14–18, 20–23, 25–33 and 60–68 support the lessee scope,
recognition, measurement, modification and transition findings used here.
Automatic list labels in the Word document are not reproduced by the text
extractor; the original document and the earlier official HTML remain available.
Article 61 permits retrospective transition or adjustment of opening retained
earnings without comparative restatement, subject to its detailed conditions.
Neither route may be assigned to an actual issuer without its election evidence.

For an otherwise qualifying ASBE enterprise in the second group, a 2020
reporting date alone does not establish mandatory use of the revised lease
standard; verified early adoption would be needed. The same enterprise falls
within mandatory application from 2021. This is a source-backed selection
example, not a claim that any particular company belongs to that group.

## Consequences for the existing lease case

Keep the previously reviewed synthetic assumptions: initial lease liability
and ROU asset 210, two annual payments of 121, discount rate 10%, two-year
straight-line depreciation, tax deductions allocated to the liability, zero
tax bases, tax rate 25%, and sufficient taxable profit satisfying the DTA
recognition condition. The primary sources now support the exception analysis
for a qualifying ASBE case to which Section I applies from 1 January 2023;
the tax law and entity facts remain
explicit assumptions.

At commencement, taxable ROU difference 210 gives DTL 52.5; deductible liability
difference 210 gives DTA 52.5. Recognize debit DTA 52.5 / credit DTL 52.5. At the
first annual close, liability 110 and ROU 105 give DTA 27.5 and DTL 26.25.
The DTA reduction of 25 is deferred expense and the DTL reduction of 26.25 is
deferred benefit: net benefit 1.25. Both reverse by expiry. These are the same
amounts already checked in P17 and rendered on P18 physical page 63.

These are gross recognition and measurement amounts. Whether deferred tax
assets and liabilities may be offset on an actual balance sheet requires the
applicable presentation provisions and entity/tax-authority facts. Article 23's
noncurrent classification and Section I's separate recognition do not alone
settle that offset question. The transition illustration below displays gross
amounts to expose the adjustment; it does not determine an issuer's net display.

For a separate transition illustration, assume the earliest comparative opening
has cash 500, ROU 105, lease liability 110 and equity 495, with no recognized
deferred tax. Assume the same supported tax bases, rate and recoverability.
Recognition adds DTA 27.5, DTL 26.25 and opening retained earnings 1.25.
Assets become 632.5; liabilities 136.25 plus equity 496.25 also equal 632.5.
This demonstrates the opening-equity route; it is not a new current-period tax
expense or a rewrite of the original disclosure. Actual adoption dates and
comparative periods must be supplied by the entity.

Applying the old exemption to set both deferred balances to zero in the
qualifying post-2023 example is wrong relative to Interpretation 16 Section I.
It preserves the initial net equity by accident while omitting required gross
balances and the later 1.25 deferred benefit. Conversely, automatically creating
equal deferred balances whenever a lease has equal carrying amounts is also
wrong: the temporary differences, qualifying conditions and DTA recognition
criteria have to be established. Unknown tax deductions or recoverability
produce an unresolved assessment, not assumed eligibility.

## Decision and limits

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Recover ASBE 18/Interpretation 16 and the ASBE 21 issuance schedule | Official texts, exact provisions and effective/transition rules are retained and inspected | No source/title/content mismatch; historical failed requests retained | Full later amendment census, actual tax law, entity adoption, offset eligibility and recoverability remain unverified | Review this supplement, then incorporate its dated source correction in the next manuscript revision | Whole ASBE/current-2026 compliance, complete authority coverage or E07 closure |

The strongest competing reading applies the original ASBE 18 initial exemption
without Interpretation 16. Section I expressly excludes the qualifying case
from that exemption, so that reading is rejected for the stated target period
and facts. A later applicable amendment, a nonqualifying transaction, different
tax bases, or unavailable recoverable taxable profit would change the answer.
The source retrieval narrows E07; US, ASBE sector and other authority work remain
internal. No paid review is required to identify or repair this source gap.


FILE docs/design/proposal/readiness/sources-20261007/asbe18.txt
SHA256 953dac8c1892c7a3cfd6f3a3791ca7067be92bbbbcf83dabf9a40d29cfbf8346
企业会计准则第18号——所得税
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
专题
>
企业会计准则
>
企业会计准则
企业会计准则第18号——所得税
第一章  总则
第一条
为了规范企业所得税的确认、计量和相关信息的
列报
，根据《企业会计准则——基本准则》，制定本准则。
第二条
本准则所称
所得税包括企业以应纳税所得额为基础的各种境内和境外税额。
第三条
本准则不涉及政府补助的确认和计量，但因政府补助产生暂时性差异的所得税影响，应当按照本准则
进行
确认和计量。
第二章  计税基础
第四条
企业在取得资产、负债时，应当确定其计税基础。资产、负债的账面价值与其计税基础存在差异的，应当按照本准则规定确认所产生的递延所得税资产或递延所得税负债。
第五条
资产的计税基础，是指企业收回资产账面价值过程中，计算应纳税所得额时按照税法规定可以自应税经济利益中抵扣的金额。
第六条
负债的计税基础，是指负债的账面价值减去未来期间计算应纳税所得额时按照税法规定可予抵扣的金额。
第三章  暂时性差异
第七条
暂时性差异，是指资产或负债的账面价值与其计税基础之间的差额；未作为资产和负债确认的项目，按照税法规定可以确定其计税基础的，该计税基础与其账面价值之间的差额也属于暂时性差异。
按照暂时性差异对未来期间应税金额的影响，分为应纳税暂时性差异和可抵扣暂时性差异。
第八条
应纳税暂时性差异，是指在确定未来收回资产或清偿负债期间的应纳税所得额时，将导致产生应税金额的暂时性差异。
第九条
可抵扣暂时性差异，是指在确定未来收回资产或清偿负债期间的应纳税所得额时，将导致产生可抵扣金额的暂时性差异。
第四章
确认
第十条
企业应当将当期和以前期间应交未交的所得税确认为负债，将已支付的所得税超过应支付的部分确认为资产。
存在应纳税暂时性差异或可抵扣暂时性差异的，应当按照本准则规定确认递延所得税负债或递延所得税资产。
第十一条
除下列交易中产生的递延所得税负债以外，企业应当确认所有应纳税暂时性差异产生的递延所得税负债：
（一）商誉的初始确认
。
（二）同时具有下
列
特征的交易中产生的资产或负债的初始确认：
1．该项交易不是企业合并；
2．交易发生时既不影响会计利润也不影响应纳税所得额（或可抵扣亏损）。
与子公司、联营企业及合营企业的投资相关的应纳税暂时性差异产生的递延所得税负债，应
当
按照本准则第十二条的规定确认。
第十二条
企业对与子公司、联营企业及合营企业投资相关的应纳税暂时性差异，应当确认相应的递延所得税负债。但是，同时满足下列条件的除外：
（一）投资企业能够控制暂时性差异转回的时间；
（二）该暂时性差异在可预见的未来很可能不会转回。
第十三条
企业应当以很可能取得用来抵扣可抵扣暂时性差异的应纳税所得额为限，确认由可抵扣暂时性差异产生的递延所得税资产。但是
，
同时具有下
列
特征的交易中因资产或负债的初始确认所产生的递延所得税资产不予确认
：
（一）该项交易不是企业合并
；
（二）交易发生时既不影响会计利润也不影响应纳税所得额（或可抵扣亏损）。
资产负债表日，有确凿证据表明未来期间很可能获得足够的应纳税所得额用来抵扣可抵扣暂时性差异的，应当确认以前期间未确认的递延所得税资产。
第十四条
企业对与子公司、联营企业及合营企业投资相关的可抵扣暂时性差异，同时满足下列条件的，应当确认相应的递延所得税资产：
（一）暂时性差异在可预见的未来很可能转回；
（二）未来很可能获得用来抵扣可抵扣暂时性差异的应纳税所得额。
第十五条
企业对于能够结转以后年度的可抵扣亏损和税款抵减，应当以很可能获得用来抵扣可抵扣亏损和税款抵减的未来应纳税所得额为限，确认相应的递延所得税资产。
第五章  计量
第十六条
资产负债表日，对于当期和以前期间形成的当期所得税负债（或资产），应当按照税法规定计算的预期应交纳（或返还）的所得税金额计量。
第十七条
资产负债表日，对于递延所得税资产和递延所得税负债，应当
根
据税法规定，按照预期收回该资产或清偿该负债期间的适用税率计量。
适用税率发生变化的，应对已确认的递延所得税资产和递延所得税负债进行重新计量，除直接在
所有者
权益中确认的交易或者事项产生的递延所得税资产和
递延所得税
负债以外，应当将其影响数计入变化当期的所得税费用。
第十八条
递延所得税资产和递延所得税负债的计量，应当反映资产负债表日企业预期收回资产或清偿负债方式的
所得
税影响，即在计量递延所得税资产和递延所得税负债时，应当采用与收回资产或清偿债务的预期方式相一致的税率和计税基础。
第十九条
企业不应当对递延所得税资产和递延所得税负债进行折现。
第二十条
资产负债表日，企业应当对递延所得税资产的账面价值进行复核。如果未来期间很可能无法获得足够的应纳税所得额用以抵扣递延所得税资产的利益，应当减记递延所得税资产的账面价值。
在很可能获得足够的应纳税所得额时，减记的金额应当转回。
第二十一条
企业当期所得税和递延所得税应当作为所得税费用或收益计入当期损益，但不包括下列情况产生的所得税：
（一）企业合并
。
（二）直接在
所有者
权益中确认的交易或者事项。
第二十二条
与直接计入
所有者
权益的交易或者事项相关的当期所得税和递延所得税，应当计入
所有者
权益。
第六章  列报
第二十三条
递延所得税资产和递延所得税负债应当分别作为非流动资产和非流动负债在资产负债表中列示。
第二十四条
所得税费用应当在利润表中单独列示。
第二十五条
企业应当在附注中披露与所得税有关的下列信息：
（一）所得税费用（收益）的主要组成部分。
（二）所得税费用（收益）与会计利润关系
的说明
。
（三）未确认递延所得税资产的可抵扣暂时性差异、可抵扣亏损的金额（如果存在到期日，还应披露到期日）。
（四）对每一类暂时性差异和可抵扣亏损，在列报期间确认的递延所得税资产或递延所得税负债的金额
，
确认递延所得税资产的依据。
（五）未确认递延所得税负债的
，
与对子公司、联营企业及合营企业投资相关的暂时性差异金额。
附件下载:
相关文章:
发布日期:  2006年03月09日
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

FILE docs/design/proposal/readiness/sources-20261007/interpretation16-pdf.txt
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


FILE docs/design/proposal/readiness/sources-20261007/lease-notice-recovery.txt
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

FILE docs/design/proposal/readiness/sources-20261007/inspection-v1.json
SHA256 f48db7d8b3f5d13474b8f86c71bb91f5cb8bbd04cef92eacc644dd278fed4862
{
  "schema_version": "accdsl.p19.source-inspection.v1",
  "recorded_at": "2026-10-07T04:09:25.267491+00:00",
  "inspection_by": "Codex author; bounded independent review follows",
  "prior_retrieval": {
    "path": "docs/design/proposal/readiness/sources-20261007/retrieval.json",
    "sha256": "c99918c34128d039c86e41dab7e3d2b335574557027403e0820f37797c3350b5"
  },
  "sources": [
    {
      "id": "asbe18",
      "url": "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46230.htm",
      "title": "企业会计准则第18号——所得税",
      "publication_date": "2006-03-09",
      "files": [
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe18.html",
          "sha256": "15405839434a38f237d2c4c6f7bf8bba7c3eda4dbc35de33828e5c7dc9b19306"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe18.headers",
          "sha256": "61f689d8688b15c4c46b9d1af4301487a35ef66025048faee6d891a9f36c1df1"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe18.txt",
          "sha256": "953dac8c1892c7a3cfd6f3a3791ca7067be92bbbbcf83dabf9a40d29cfbf8346"
        }
      ],
      "inspected": "All 25 articles; focus on 4–9, 11–13 and 16–25. Original text, not a current consolidated amendment census.",
      "anchors": [
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe18.txt",
          "locator": "Article 13, recoverability",
          "quote": "企业应当以很可能取得用来抵扣可抵扣暂时性差异的应纳税所得额为限",
          "line": 74
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe18.txt",
          "locator": "Article 19, no discounting",
          "quote": "企业不应当对递延所得税资产和递延所得税负债进行折现。",
          "line": 107
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe18.txt",
          "locator": "Article 23, noncurrent classes",
          "quote": "递延所得税资产和递延所得税负债应当分别作为非流动资产和非流动负债在资产负债表中列示。",
          "line": 126
        }
      ],
      "http_status": 200,
      "accepted_as_source": true,
      "acceptance_scope": "Inspected historical primary provisions only; not complete current authority or an issuer admission."
    },
    {
      "id": "interpretation16",
      "url": "https://kjs.mof.gov.cn/gongzuotongzhi/202212/t20221212_3857395.htm",
      "attachment_url": "https://kjs.mof.gov.cn/gongzuotongzhi/202212/P020221213437987613379.pdf",
      "title": "企业会计准则解释第16号",
      "document_id": "财会〔2022〕31号",
      "signed_date": "2022-11-30",
      "publication_date": "2022-12-13",
      "lease_tax_effective_date": "2023-01-01",
      "early_application": "Permitted from issuance year with disclosure, Section I(b).",
      "files": [
        {
          "path": "docs/design/proposal/readiness/sources-20261007/interpretation16.html",
          "sha256": "08afb4b0869f904f612b42a98878c7e3dd54b22537fc4ff2d17626cda187affd"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/interpretation16.headers",
          "sha256": "4ade780d6b8864dfebec715b38c754ede951987f55a3c44bc1dbf2030ea6e71f"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/interpretation16.txt",
          "sha256": "28321ab172fc50f887755a488739ab12e337710e6beb0ed8a249b6327599a2ff"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/interpretation16.pdf",
          "sha256": "41d5c5be6d0333900b8c7f9eab1e8926b4b08fdd0291db6033445171fc4b1752"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/interpretation16-pdf.headers",
          "sha256": "e58feb4b5cb761ee08e8a3cf21e86984209ba6a350f629113a436e2a2bd0a1e2"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/interpretation16-pdf.txt",
          "sha256": "07b2bd3c3ab4b19d59366ce08f285eb569d37cf1a84e80a05e9af1eb55cdb071"
        }
      ],
      "inspected": "All five physical pages, Sections I–IV; Section I(a) recognition, I(b) transition, IV separate effective dates.",
      "anchors": [
        {
          "path": "docs/design/proposal/readiness/sources-20261007/interpretation16-pdf.txt",
          "locator": "Section I(a), physical page 1",
          "quote": "对于不是企业合并、交易发生时既不影响会计利润也不",
          "line": 14
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/interpretation16-pdf.txt",
          "locator": "Section I(a), physical page 1, qualifying differences",
          "quote": "负债导致产生等额应纳税暂时性差异和可抵扣暂时性差异",
          "line": 16
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/interpretation16-pdf.txt",
          "locator": "Section I(b), physical page 2, opening equity",
          "quote": "早期间的期初留存收益及其他相关财务报表项目。",
          "line": 39
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/interpretation16-pdf.txt",
          "locator": "Section IV, physical page 5",
          "quote": "税不适用初始确认豁免的会计处理”内容自 2023 年 1 月 1",
          "line": 112
        }
      ],
      "http_status": 200,
      "accepted_as_source": true,
      "acceptance_scope": "Inspected historical primary provisions only; not complete current authority or an issuer admission."
    },
    {
      "id": "lease-notice-recovered",
      "url": "https://kjs.mof.gov.cn/zhengcefabu/201812/t20181213_3092629.htm",
      "attachment_url": "https://kjs.mof.gov.cn/zhengcefabu/201812/P020181213596772599039.doc",
      "title": "关于修订印发《企业会计准则第21号——租赁》的通知",
      "document_id": "财会〔2018〕35号",
      "signed_date": "2018-12-07",
      "publication_date": "2018-12-14",
      "files": [
        {
          "path": "docs/design/proposal/readiness/sources-20261007/lease-notice-recovery.html",
          "sha256": "5d730285c5b3c6dbb977d1e14cc90dffed148cf85fc0914b6d63153f49438f70"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/lease-notice-recovery.headers",
          "sha256": "e9bd3608dec1acdc454f15064944b00a0053af66ad0739f34053d979558b67aa"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/lease-notice-recovery.txt",
          "sha256": "c37db31b3ed426fc49e3b8836f869c73c42f901f8322969ea6481d90977bb120"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe21-issued.doc",
          "sha256": "2bc3e4e9dc9b06c42c24da4da0fe820d20aabbb925049ab17a0fa354db869f55"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe21-issued.headers",
          "sha256": "6bafff8527a7d652c1cbcbf58a078394e1736449c134401360b7442eca1e8f7a"
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe21-issued.txt",
          "sha256": "f045e49b8dad7e58f6150acc41b7c2ffd0f1c242657a69645d1771a591350cdd"
        }
      ],
      "inspected": "Notice in full; attached articles 1–8, 14–18, 20–23, 25–33, 60–68. Mandatory schedule and constrained early adoption distinguished from entity-specific application.",
      "extraction": "Attachment has .doc URL but OOXML ZIP bytes. word/document.xml w:p/w:t extracted with standard-library XML. Automatic Word list numbering is omitted; original bytes and P17 official HTML are retained.",
      "anchors": [
        {
          "path": "docs/design/proposal/readiness/sources-20261007/lease-notice-recovery.txt",
          "locator": "Paragraph I, staged mandatory dates",
          "quote": "自2019年1月1日起施行；其他执行企业会计准则的企业自2021年1月1日起施行。",
          "line": 24
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/lease-notice-recovery.txt",
          "locator": "Paragraph II, conditional early adoption",
          "quote": "可以提前执行本准则，但不应早于其同时执行",
          "line": 25
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe21-issued.txt",
          "locator": "Article 61(2), transition route",
          "quote": "不调整可比期间信息。",
          "line": 208
        },
        {
          "path": "docs/design/proposal/readiness/sources-20261007/asbe21-issued.txt",
          "locator": "Article 68, general effective date",
          "quote": "第六十八条  本准则自2019年1月1日起施行。",
          "line": 232
        }
      ],
      "http_status": 200,
      "accepted_as_source": true,
      "acceptance_scope": "Inspected historical primary provisions only; not complete current authority or an issuer admission."
    }
  ],
  "fresh_retrieval_commands": [
    "curl -L --connect-timeout 10 --max-time 25 -sS -D /tmp/accdsl-p19-lease-notice-recovery.headers -o /tmp/accdsl-p19-lease-notice-recovery.html -w <http_code/url/bytes> https://kjs.mof.gov.cn/zhengcefabu/201812/t20181213_3092629.htm",
    "curl -L --connect-timeout 10 --max-time 25 -sS -D /tmp/accdsl-p19-asbe21-issued.headers -o /tmp/accdsl-p19-asbe21-issued.doc -w <http_code/url/bytes> https://kjs.mof.gov.cn/zhengcefabu/201812/P020181213596772599039.doc"
  ],
  "remaining": [
    "Later amendment census",
    "Actual entity/framework and adoption evidence",
    "Tax-law deductions and rates",
    "DTA recoverability",
    "Actual offset presentation prerequisites",
    "Broader US and ASBE sector authority"
  ],
  "forbidden_conclusions": [
    "E07 closed",
    "Current-2026 full ASBE compliance",
    "All leases create equal deferred tax balances",
    "Gross recognition alone determines actual balance-sheet offset display"
  ]
}


FILE data/accounting-master/direct-p19-20261007/check_source_repair.py
SHA256 d23f472310f5f4e38d54731e11585753110b0d63a155a06be469dc8b41493ef1
"""Reproduce the source supplement's rational arithmetic; no product engine."""
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'docs/design/proposal/readiness/sources-20261007'
start = time.monotonic()
checks = []


def check(name, actual, expected):
    checks.append({'name': name, 'actual': str(actual), 'expected': str(expected),
                   'passed': actual == expected})


def ref(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


# Compute from cash flows; the expected values are the reviewed manuscript's
# literal examples, not values obtained from the same recurrence.
rate, tax, payment = F(1, 10), F(1, 4), F(121)
pv = sum((payment / (1 + rate) ** t for t in (1, 2)), F(0))
check('cash-flow present value', pv, F(210))
liability = [pv]
interest = []
for _ in range(2):
    interest.append(liability[-1] * rate)
    liability.append(liability[-1] + interest[-1] - payment)
rou = [pv - t * pv / 2 for t in range(3)]
check('liability roll-forward', liability, [F(210), F(110), F(0)])
check('interest expense', interest, [F(21), F(11)])
check('ROU straight-line balances', rou, [F(210), F(105), F(0)])
check('total interest equals payments less principal', sum(interest), 2*payment-pv)
check('lease expense by period', [pv/2+x for x in interest], [F(126), F(116)])

# Zero tax bases and sufficient recoverability are assumptions of this example.
dta = [x*tax for x in liability]
dtl = [x*tax for x in rou]
check('gross DTA', dta, [F('52.5'), F('27.5'), F(0)])
check('gross DTL', dtl, [F('52.5'), F('26.25'), F(0)])
deferred = [(dtl[t]-dtl[t-1])-(dta[t]-dta[t-1]) for t in (1, 2)]
check('deferred expense (negative means benefit)', deferred, [F('-1.25'), F('1.25')])
check('lifetime deferred expense', sum(deferred), F(0))
check('commencement gross entry balances', dta[0], dtl[0])
check('first-close gross recognition differs despite equal opening', dta[1]-dtl[1], F('1.25'))

cash, old_equity = F(500), F(495)
check('transition opening book balances', cash+rou[1], liability[1]+old_equity)
equity_adjustment = dta[1]-dtl[1]
assets = cash+rou[1]+dta[1]
liabilities = liability[1]+dtl[1]
equity = old_equity+equity_adjustment
check('opening retained earnings adjustment', equity_adjustment, F('1.25'))
check('transition assets', assets, F('632.5'))
check('transition liabilities', liabilities, F('136.25'))
check('transition equity', equity, F('496.25'))
check('transition balance-sheet identity', assets, liabilities+equity)
check('transition journal balances', dta[1], dtl[1]+equity_adjustment)

inspection = json.loads((SOURCE/'inspection-v1.json').read_text())
for source in inspection['sources']:
    for item in source['files']:
        p = ROOT/item['path']
        check('source hash: '+item['path'], hashlib.sha256(p.read_bytes()).hexdigest(), item['sha256'])
    for anchor in source['anchors']:
        check('located excerpt: '+source['id']+' / '+anchor['locator'],
              anchor['quote'] in (ROOT/anchor['path']).read_text(), True)
check('Interpretation 16 original PDF', (SOURCE/'interpretation16.pdf').read_bytes().startswith(b'%PDF-'), True)
check('issued lease standard OOXML original', (SOURCE/'asbe21-issued.doc').read_bytes().startswith(b'PK\x03\x04'), True)

report = {
    'schema_version': 'accdsl.p19.source-repair-check.v1',
    'recorded_at': datetime.now(timezone.utc).isoformat(),
    'passed': all(x['passed'] for x in checks), 'checks': checks,
    'command': ['python3', str(Path(__file__).relative_to(ROOT))],
    'environment': 'Python '+platform.python_version()+'; standard-library exact fractions',
    'cpu_gpu': 'CPU arithmetic and file reads; no GPU framework imported',
    'random_seeds': 'N/A: deterministic rational checks',
    'wall_seconds': time.monotonic()-start,
    'inputs': [ref(Path(__file__)), ref(SOURCE/'inspection-v1.json'),
               ref(ROOT/'docs/design/proposal/readiness/asbe-tax-source-repair-v1.md')],
    'plan': 'docs/plans/accounting-p19-session-recovery-20261007.md',
    'scope': 'Example arithmetic, original-byte integrity and quote locations only. Source interpretation is reviewed separately. No actual tax law, recoverability, offset eligibility or whole-framework compliance is established.'}
(OUT/'source-repair-checks-v1.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
print(json.dumps({'passed': report['passed'], 'checks': len(checks),
                  'failures': [x for x in checks if not x['passed']]}))
raise SystemExit(0 if report['passed'] else 1)


Issued lease attachment, article 60 onward (original auto-list labels not extracted):
第六十条  对于首次执行日前已存在的合同，企业在首次执行日可以选择不重新评估其是否为租赁或者包含租赁。选择不重新评估的，企业应当在财务报表附注中披露这一事实，并一致应用于前述所有合同。
第六十一条  承租人应当选择下列方法之一对租赁进行衔接会计处理，并一致应用于其作为承租人的所有租赁：
（一）按照《企业会计准则第28号——会计政策、会计估计变更和差错更正》的规定采用追溯调整法处理。
（二）根据首次执行本准则的累积影响数，调整首次执行本准则当年年初留存收益及财务报表其他相关项目金额，不调整可比期间信息。采用该方法时，应当按照下列规定进行衔接处理：
1. 对于首次执行日前的融资租赁，承租人在首次执行日应当按照融资租入资产和应付融资租赁款的原账面价值，分别计量使用权资产和租赁负债。
2. 对于首次执行日前的经营租赁，承租人在首次执行日应当根据剩余租赁付款额按首次执行日承租人增量借款利率折现的现值计量租赁负债，并根据每项租赁选择按照下列两者之一计量使用权资产：
（1）假设自租赁期开始日即采用本准则的账面价值（采用首次执行日的承租人增量借款利率作为折现率）；
（2）与租赁负债相等的金额，并根据预付租金进行必要调整。
3. 在首次执行日，承租人应当按照《企业会计准则第8号——资产减值》的规定，对使用权资产进行减值测试并进行相应会计处理。
第六十二条  首次执行日前的经营租赁中，租赁资产属于低价值资产且根据本准则第三十二条的规定选择不确认使用权资产和租赁负债的，承租人无需对该经营租赁按照衔接规定进行调整，应当自首次执行日起按照本准则进行会计处理。
第六十三条  承租人采用本准则第六十一条第（二）项进行衔接会计处理时，对于首次执行日前的经营租赁，可根据每项租赁采用下列一项或多项简化处理：
1. 将于首次执行日后12个月内完成的租赁，可作为短期租赁处理。
2. 计量租赁负债时，具有相似特征的租赁可采用同一折现率；使用权资产的计量可不包含初始直接费用。
3. 存在续租选择权或终止租赁选择权的，承租人可根据首次执行日前选择权的实际行使及其他最新情况确定租赁期，无需对首次执行日前各期间是否合理确定行使续租选择权或终止租赁选择权进行估计。
4. 作为使用权资产减值测试的替代，承租人可根据《企业会计准则第13号——或有事项》评估包含租赁的合同在首次执行日前是否为亏损合同，并根据首次执行日前计入资产负债表的亏损准备金额调整使用权资产。
5. 首次执行本准则当年年初之前发生租赁变更的，承租人无需按照本准则第二十八条、第二十九条的规定对租赁变更进行追溯调整，而是根据租赁变更的最终安排，按照本准则进行会计处理。
第六十四条  承租人采用本准则第六十三条规定的简化处理方法的，应当在财务报表附注中披露所采用的简化处理方法以及在合理可能的范围内对采用每项简化处理方法的估计影响所作的定性分析。
第六十五条  对于首次执行日前划分为经营租赁且在首次执行日后仍存续的转租赁，转租出租人在首次执行日应当基于原租赁和转租赁的剩余合同期限和条款进行重新评估，并按照本准则的规定进行分类。按照本准则重分类为融资租赁的，应当将其作为一项新的融资租赁进行会计处理。
除前款所述情形外，出租人无需对其作为出租人的租赁按照衔接规定进行调整，而应当自首次执行日起按照本准则进行会计处理。
第六十六条  对于首次执行日前已存在的售后租回交易，企业在首次执行日不重新评估资产转让是否符合《企业会计准则第14号——收入》作为销售进行会计处理的规定。
对于首次执行日前应当作为销售和融资租赁进行会计处理的售后租回交易，卖方（承租人）应当按照与首次执行日存在的其他融资租赁相同的方法对租回进行会计处理，并继续在租赁期内摊销相关递延收益或损失。
对于首次执行日前应当作为销售和经营租赁进行会计处理的售后租回交易，卖方（承租人）应当按照与首次执行日存在的其他经营租赁相同的方法对租回进行会计处理，并根据首次执行日前计入资产负债表的相关递延收益或损失调整使用权资产。
第六十七条  承租人选择按照本准则第六十一条第（二）项规定对租赁进行衔接会计处理的，还应当在首次执行日披露以下信息：
首次执行日计入资产负债表的租赁负债所采用的承租人增量借款利率的加权平均值；
首次执行日前一年度报告期末披露的重大经营租赁的尚未支付的最低租赁付款额按首次执行日承租人增量借款利率折现的现值，与计入首次执行日资产负债表的租赁负债的差额。

 附则
第六十八条  本准则自2019年1月1日起施行。



Check summary: {"passed": true, "wall_seconds": 0.001131631899625063, "scope": "Example arithmetic, original-byte integrity and quote locations only. Source interpretation is reviewed separately. No actual tax law, recoverability, offset eligibility or whole-framework compliance is established."}
