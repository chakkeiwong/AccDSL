"""Existing P17/R03 asset examples with authored, independently checked outputs."""
from copy import deepcopy

def populate_assets(case, step):
    def rv(a, gross, accumulated, life, surplus, prior, status='active'):
        return dict(asset_id=a, gross=str(gross), accumulated=str(accumulated), life=str(life),
            surplus=str(surplus), prior_loss=str(prior), status=status)
    c = case('class-revaluation', 'revaluation_class', {'class_id': 'administrative-machines',
        'members': [rv('A',120,0,4,40,0),rv('B',24,0,3,0,6)], 'complete_membership_admitted': True,
        'zero_residual': True, 'administrative_use': True, 'valuation_sequence': 1, 'surplus_transferred': '0'},
        {'cash':'60','ppe':'144','capital':'-200','retained':'36','oci_revaluation':'-40'})
    c['source_family'] = 'AU_AASB'
    step(c,'revaluation.depreciate',{'years':'1','consumption_period_admitted':True},
        {'members':[rv('A',120,30,3,40,0),rv('B',24,8,2,0,6)]},{'ppe':'-38','expense':'38'})
    step(c,'revaluation.measure',{'values':[{'asset_id':'A','fair_value':'45'},{'asset_id':'B','fair_value':'22'}],
        'reliable_values':True,'whole_class_current':True},
        {'members':[rv('A',45,0,3,0,5),rv('B',22,0,2,0,0)],'valuation_sequence':2},
        {'ppe':'-39','oci_revaluation':'40','expense':'5','income':'-6'})
    step(c,'revaluation.depreciate',{'years':'1','consumption_period_admitted':True},
        {'members':[rv('A',45,15,2,0,5),rv('B',22,11,1,0,0)]},{'ppe':'-26','expense':'26'})
    step(c,'revaluation.measure',{'values':[{'asset_id':'A','fair_value':'50'},{'asset_id':'B','fair_value':'11'}],
        'reliable_values':True,'whole_class_current':True},
        {'members':[rv('A',50,0,2,15,0),rv('B',11,0,1,0,0)],'valuation_sequence':3},
        {'ppe':'20','income':'-5','oci_revaluation':'-15'})
    step(c,'revaluation.dispose',{'asset_ids':['A','B'],'cash':'61','control_passed':True,'depreciation_current':True},
        {'members':[rv('A',0,0,2,15,0,'disposed'),rv('B',0,0,1,0,0,'disposed')]},
        {'ppe':'-61','cash':'61'},{'investing':'61'})
    step(c,'revaluation.transfer',{'asset_id':'A','amount':'15','election_admitted':True},
        {'members':[rv('A',0,0,2,0,0,'disposed'),rv('B',0,0,1,0,0,'disposed')],'surplus_transferred':'15'},
        {'oci_revaluation':'15','retained':'-15'})
    for i,s in enumerate(c['steps']): s['event_date'] = '2024-12-31' if i < 2 else '2025-12-31'

    def ca(a,unit,value):
        return {'asset_id':a,'unit_id':unit,'carrying':str(value),'floor':'0','floor_assessed':True}
    c = case('corporate-asset-order','corporate_assets',{'group_id':'AB','corporate_asset_id':'HQ',
        'assets':[ca('A1','A',40),ca('A2','A',40),ca('B1','B',60),ca('B2','B',60),ca('HQ','AB',40)],
        'units':[{'unit_id':'A','tested':False,'recoverable':None},{'unit_id':'B','tested':False,'recoverable':None}],
        'group_recoverable':None,'smallest_group_admitted':True,'individual_allocation_unavailable':True,
        'group_tested':False,'loss_to_date':'0'}, {'cash':'100','ppe':'240','capital':'-340'})
    step(c,'corpassets.test_unit',{'unit_id':'A','recoverable':'70','perimeter_consistent':True},
        {'assets':[ca('A1','A',35),ca('A2','A',35),ca('B1','B',60),ca('B2','B',60),ca('HQ','AB',40)],
         'units':[{'unit_id':'A','tested':True,'recoverable':'70'},{'unit_id':'B','tested':False,'recoverable':None}],
         'loss_to_date':'10'}, {'ppe':'-10','expense':'10'})
    step(c,'corpassets.test_unit',{'unit_id':'B','recoverable':'130','perimeter_consistent':True},
        {'units':[{'unit_id':'A','tested':True,'recoverable':'70'},{'unit_id':'B','tested':True,'recoverable':'130'}]}, {})
    step(c,'corpassets.test_group',{'recoverable':'207','perimeter_consistent':True},
        {'assets':[ca('A1','A','63/2'),ca('A2','A','63/2'),ca('B1','B',54),ca('B2','B',54),ca('HQ','AB',36)],
         'group_tested':True,'group_recoverable':'207','loss_to_date':'33'}, {'ppe':'-23','expense':'23'})

    def part(pid,own,gw,test,assets):
        return {'part_id':pid,'ownership':own,'reported_goodwill':str(gw),'test_goodwill':str(test),
            'identifiable':str(assets),'proportionate_nci':own!='1','proportional_goodwill_admitted':True,
            'zero_floor_admitted':True}
    variants = [
        ('partial-goodwill-220','220',[part('Sub','4/5',40,50,200)],
         [part('Sub','4/5',16,20,200)],'24','6','24','0',{'goodwill':'-24','expense':'24'},'200','40','-340'),
        ('partial-goodwill-180','180',[part('Sub','4/5',40,50,200)],
         [part('Sub','4/5',0,0,180)],'60','10','56','4',{'goodwill':'-40','ppe':'-20','expense':'60'},'200','40','-340'),
        ('partial-goodwill-larger','270',[part('Sub','4/5',40,50,200),part('ParentPart','1',20,20,100)],
         [part('Sub','4/5',0,0,180),part('ParentPart','1',0,0,90)],'90','10','86','4',
         {'goodwill':'-60','ppe':'-30','expense':'90'},'300','60','-460'),
    ]
    for key,recover,parts,after,loss,notional,parent,nci,j,ppe,gw,capital in variants:
        c=case(key,'partial_goodwill',{'group_id':'NCI-unit','parts':parts,'tested':False,'recoverable':None,
            'recognized_loss':'0','unrecognized_loss':'0','parent_loss':'0','nci_loss':'0'},
            {'cash':'100','ppe':ppe,'goodwill':gw,'capital':capital})
        c['book_id']='Consolidated'
        step(c,'ncigoodwill.impair',{'recoverable':recover,'profit_allocation_matches_ownership':True,'perimeter_consistent':True},
            {'parts':after,'tested':True,'recoverable':recover,'recognized_loss':loss,'unrecognized_loss':notional,
             'parent_loss':parent,'nci_loss':nci},j)

    def ra(a,gross,acc,allowance,cap,life):
        return {'asset_id':a,'gross':str(gross),'accumulated':str(acc),'allowance':str(allowance),
            'no_impairment_carrying':str(cap),'life':str(life),'individual_recoverable':None,'individual_assessed':True}
    c=case('depreciated-reversal','reversal',{'unit_id':'floor-unit',
        'assets':[ra('A',60,0,5,60,5),ra('B',40,0,25,40,5)],'goodwill':'0','goodwill_loss':'20',
        'unit_recoverable':'70','phase':'impaired'}, {'cash':'80','ppe':'70','capital':'-200','retained':'50'})
    step(c,'reversal.depreciate',{'years':'1','zero_residual_straight_line':True},
        {'assets':[ra('A',60,11,5,48,4),ra('B',40,3,25,32,4)],'phase':'depreciated'}, {'ppe':'-14','expense':'14'})
    step(c,'reversal.restore',{'recoverable':'90','changed_estimates_admitted':True},
        {'assets':[ra('A',60,11,1,48,4),ra('B',40,3,5,32,4)],'unit_recoverable':'90','phase':'reversed'},
        {'ppe':'24','income':'-24'})

    variants=[
        ('restoration-revalued-increase','150',None,'50','20','0',False,'85',
         {'surplus':'0','prior_loss':'15','restoration_oci':'-20'},
         {'provision':'-35','oci_revaluation':'20','expense':'15'},
         {'cash':'100','ppe':'150','provision':'-50','capital':'-180','oci_revaluation':'-20'}),
        ('restoration-revalued-decrease','25','40','80','0','15',False,'30',
         {'surplus':'25','prior_loss':'0','restoration_oci':'25'},
         {'provision':'50','income':'-25','oci_revaluation':'-25'},
         {'cash':'100','ppe':'25','provision':'-80','capital':'-60','retained':'15'}),
        ('restoration-revalued-exhausted','0','0','20','10','0',True,'25',
         {}, {'provision':'-5','expense':'5'},
         {'cash':'100','provision':'-20','capital':'-70','oci_revaluation':'-10'}),
    ]
    for key,ppe,cost,liab,surplus,prior,exhausted,new,changes,j,b in variants:
        c=case(key,'restoration_revalued',{'asset_id':'site','liability_id':'restore-site','ppe':ppe,
            'cost_model_carrying':cost,'liability':liab,'surplus':surplus,'prior_loss':prior,'asset_exhausted':exhausted,
            'restoration_oci':'0','class_valuation_current':True},b)
        step(c,'rvrestoration.change',{'new_liability':new,'measurement_current':True,'class_review_supports_unchanged_ppe':True},
            {**changes,'liability':new},j)
