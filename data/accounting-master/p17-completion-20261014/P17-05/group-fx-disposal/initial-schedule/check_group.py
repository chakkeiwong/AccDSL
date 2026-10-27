"""Exact independent state/statement reconciliation for a documentary group case."""
from collections import defaultdict
from fractions import Fraction as F
import json
from pathlib import Path
import time

OUT = Path(__file__).resolve().parent


def main():
    started = time.perf_counter()
    case = json.loads((OUT/"group-cases.json").read_text())
    facts = case["facts"]
    q = lambda k: F(facts[k])
    checks = []

    def check(name, actual, expected=True):
        checks.append({"name":name,"passed":actual == expected,
                       "observed":str(actual),"expected":str(expected)})

    r0,r1,r2 = q("acquisition_rate"),q("operation_rate"),q("closing_disposal_rate")
    own,nci = q("ownership"),q("nci")
    cash0,stock0,liab0 = q("sub_cash_eur"),q("sub_inventory_eur"),q("sub_payable_eur")
    na0 = cash0+stock0-liab0
    goodwill = q("consideration_eur") + nci*na0-na0
    cash_parent = q("parent_opening_usd")-q("consideration_eur")*r0
    profit_eur = q("sale_revenue_eur")-q("cost_sold_eur")
    cash_end_eur = cash0+q("sale_revenue_eur")-q("payable_paid_eur")
    profit = profit_eur*r1
    cta_na = na0*(r2-r0)+profit_eur*(r2-r1)
    cta_gw = goodwill*(r2-r0)
    cta_parent = own*cta_na+cta_gw
    cta_nci = nci*cta_na
    nci_end = nci*na0*r0 + nci*profit + cta_nci
    parent_equity = q("parent_opening_usd")+own*profit+cta_parent
    cfo = (q("sale_revenue_eur")-q("payable_paid_eur"))*r1
    cfi_acq = -(q("consideration_eur")-cash0)*r0
    cash_fx = cash0*(r2-r0)+(q("sale_revenue_eur")-q("payable_paid_eur"))*(r2-r1)
    m = {
        "identifiable_net_eur":na0,"nci_initial_eur":nci*na0,"goodwill_eur":goodwill,
        "parent_investment_usd":q("consideration_eur")*r0,"parent_cash_after_acquisition":cash_parent,
        "group_cash_after_acquisition":cash_parent+cash0*r0,"group_inventory_after_acquisition":stock0*r0,
        "group_payable_after_acquisition":liab0*r0,"goodwill_initial_usd":goodwill*r0,"nci_initial_usd":nci*na0*r0,
        "profit_eur":profit_eur,"sub_cash_closing_eur":cash_end_eur,"profit_usd":profit,
        "parent_profit_usd":own*profit,"nci_profit_usd":nci*profit,"sub_cash_closing_usd":cash_end_eur*r2,
        "goodwill_closing_usd":goodwill*r2,"net_asset_translation_oci":cta_na,"goodwill_translation_oci":cta_gw,
        "parent_translation_oci":cta_parent,"nci_translation_oci":cta_nci,"total_translation_oci":cta_na+cta_gw,
        "nci_closing_usd":nci_end,"parent_equity_before_disposal":parent_equity,"group_equity_before_disposal":parent_equity+nci_end,
        "group_cash_before_disposal":cash_parent+cash_end_eur*r2,"acquisition_cash_flow":cfi_acq,
        "operating_cash_flow":cfo,"cash_exchange_effect":cash_fx}
    for k,v in case["expected"].items(): check("independent:"+k,m[k],F(v))
    check("sub_currency_balance",cash_end_eur,na0+profit_eur)
    check("nci_no_goodwill",nci_end,nci*cash_end_eur*r2)
    check("translated_entity_balance",cash_end_eur*r2,na0*r0+profit+cta_na)
    check("group_balance_before_sale",m["group_cash_before_disposal"]+goodwill*r2,parent_equity+nci_end)
    check("cash_bridge_before_sale",q("parent_opening_usd")+cfi_acq+cfo+cash_fx,m["group_cash_before_disposal"])
    check("indirect_cfo",profit+q("cost_sold_eur")*r1-q("payable_paid_eur")*r1,cfo)

    balances=defaultdict(F,{"Cash":q("parent_opening_usd"),"Parent capital":-q("parent_opening_usd")})
    def post(b,lines,name):
        check("balanced:"+name,sum((F(v) for _,v in lines),F(0)),F(0))
        for a,v in lines:b[a]+=F(v)
        check("trial_balance:"+name,sum(b.values()),F(0))
    for j in case["group_journals"]:post(balances,j["lines"],j["id"])
    for account,expected in {"Cash":m["group_cash_before_disposal"],"Inventory":F(0),"Payable":F(0),"Goodwill":goodwill*r2,"NCI":-nci_end,"Parent CTA":-cta_parent,"Parent operating retained profit":-own*profit}.items():
        check("ledger_before_disposal:"+account,balances[account],expected)

    outputs={}
    for name,arm in case["alternatives"].items():
        p,v=F(arm["proceeds_usd"]),F(arm["retained_fv_usd"])
        gain0=p+v+nci_end-(cash_end_eur+goodwill)*r2
        gain=gain0+cta_parent
        ending_cash=cash_parent+p
        ending_equity=ending_cash+v
        o={"gain_before_recycling":gain0,"recycled_parent_reserve":cta_parent,"disposal_gain":gain,
           "net_disposal_cash":p-cash_end_eur*r2,"ending_cash":ending_cash,"ending_investment":v,"ending_equity":ending_equity,
           "total_profit":profit+gain,"profit_attributable_parent":own*profit+gain,"total_oci_after_recycling":cta_nci,
           "parent_oci_after_recycling":F(0),"nci_ending":F(0)}
        for k,expected in arm["expected"].items(): check(name+":"+k,o[k],F(expected))
        b=balances.copy()
        post(b,arm["journal"],name+":deconsolidate")
        post(b,[["Parent CTA",str(cta_parent)],["Disposal gain",str(-cta_parent)]],name+":recycle")
        for a,expected in {"Cash":ending_cash,"Retained investment":v,"NCI":F(0),"Goodwill":F(0),"Parent CTA":F(0),"Disposal gain":-gain}.items():
            check(name+":closing_ledger:"+a,b[a],expected)
        check(name+":cash_bridge",q("parent_opening_usd")+cfi_acq+cfo+cash_fx+o["net_disposal_cash"],ending_cash)
        check(name+":parent_equity_bridge",q("parent_opening_usd")+o["profit_attributable_parent"],ending_equity)
        check(name+":group_equity_bridge",q("parent_opening_usd")+nci*na0*r0+o["total_profit"]+o["total_oci_after_recycling"]-nci_end,ending_equity)
        check(name+":nci_rollforward",nci*na0*r0+nci*profit+cta_nci-nci_end,F(0))
        check(name+":same_whole_interest_value",p+v,F(169))
        check(name+":ownership_units",F(arm["sold_fraction"])+F(arm["retained_fraction"]),own)
        outputs[name]=o
    check("full_parent_separate_gain_equals_lifetime_parent_profit",F(169)-q("consideration_eur")*r0,outputs["full_sale"]["profit_attributable_parent"])
    # Adverse variants preserve some totals; compare the correct dates and components.
    check("frozen_goodwill_understates_interim_asset",goodwill*r2-goodwill*r0,F("1.6"))
    check("wrong_goodwill_nci_attribution",nci*cta_gw,F("0.32"))
    check("recycle_all_oci_overstates_profit",cta_na+cta_gw-cta_parent,F("2.2"))
    check("partial_recycle_leaves_wrong_reserve",cta_parent*(1-F("3/5")/own),F("2.6"))
    check("retained_value_not_cash",outputs["retain_twenty_percent"]["ending_investment"],F("42.25"))
    check("positive_parent_receipt_negative_group_disposal_cash",F(case["alternatives"]["retain_twenty_percent"]["proceeds_usd"])>0 and outputs["retain_twenty_percent"]["net_disposal_cash"]<0)
    frozen_gain0=F(169)+nci_end-cash_end_eur*r2-goodwill*r0
    check("frozen_goodwill_error_can_cancel_at_disposal",frozen_gain0+own*cta_na,outputs["full_sale"]["disposal_gain"])
    check("cash_fx_differs_from_total_translation_oci",cash_fx != cta_na+cta_gw)
    result={"passed":all(c["passed"] for c in checks),"check_count":len(checks),"checks":checks,
            "role":"exact documentary journals/statements; no runtime, source-applicability or empirical inference",
            "wall_seconds":time.perf_counter()-started}
    (OUT/"calculation-checks.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ["passed","check_count","wall_seconds"]}))
    if not result["passed"]:
        print([c for c in checks if not c["passed"]]); raise SystemExit(1)


if __name__ == "__main__":main()
